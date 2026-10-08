/**
 * Shared helpers of the installable, offline site's suite (plan 105 Phase E):
 * - `NetLog`: every request of the browser context, recorded at context level, which includes the
 *   requests the service workers make themselves (Playwright reports them in Chromium), with how
 *   each ended (served by a service worker, from the network, or failed), plus every console
 *   error and uncaught page error, and the document loads of each frame.
 * - `assertOfflineContract`: the plan's offline contract, after both servers are stopped: the
 *   only requests that may reach the network are the update checks, at most one failed
 *   `GET /release.json` per document load on each origin; zero others, and no console error.
 * - `assertAllowlisted`: every request (online too: browsing, precache, update) is a body-less
 *   GET for a file of the release under test, on the site or the runner origin.
 * - `downloadBook`, `offlineRecords` and `cacheNames` for both origins.
 */
import { existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import type { BrowserContext, Frame, Page, Request } from '@playwright/test';
import { allowedQuery } from '../e2e/helpers/net';
import { BASE_URL, DIST, RUNNER_DIST, RUNNER_URL } from '../e2e/helpers/env';
import { expect } from './servers';

export const SITE_ORIGIN = new URL(BASE_URL).origin;
export const RUNNER_ORIGIN = new URL(RUNNER_URL).origin;

export interface Entry {
  method: string;
  url: string;
  resourceType: string;
  body: string | null;
  /** Made by a service worker itself (its own fetch), not by a page, frame or dedicated worker. */
  bySw: boolean;
  /** The frame's document load it belongs to (`<frame index>#<load>`), or `(worker)`. */
  doc: string;
  outcome: 'pending' | 'served-by-sw' | 'network' | 'failed';
  status: number | null;
  failure: string | null;
}

export class NetLog {
  /** Since the last `reset()`. */
  readonly entries: Entry[] = [];
  /** Since the log was attached, whatever `reset()` did. */
  readonly all: Entry[] = [];
  readonly errors: string[] = [];
  /** Document loads per origin while recording (a frame committing a navigation). */
  readonly loads: Record<string, number> = {};
  private recording = true;
  private byRequest = new Map<Request, Entry>();
  private frames = new Map<Frame, { id: number; load: number }>();
  private nextFrame = 0;

  constructor(private readonly context: BrowserContext) {
    context.on('request', (request) => this.onRequest(request));
    // The response (not the request's end): a worker that is terminated mid-body (a fresh check
    // worker is dropped after its case) never reports the end of its requests.
    context.on('response', (response) => {
      const e = this.byRequest.get(response.request());
      if (!e) return;
      e.status = response.status();
      e.outcome = response.fromServiceWorker() ? 'served-by-sw' : 'network';
    });
    context.on('requestfailed', (request) => {
      const e = this.byRequest.get(request);
      if (!e) return;
      e.outcome = 'failed';
      e.failure = request.failure()?.errorText ?? 'failed';
    });
    context.on('console', (message) => {
      if (this.recording && message.type() === 'error') this.errors.push(`console: ${message.text()} (${message.location().url})`);
    });
    context.on('weberror', (error) => {
      if (this.recording) this.errors.push(`page error: ${error.error().message}`);
    });
    const watch = (page: Page) =>
      page.on('framenavigated', (frame) => {
        const f = this.frameInfo(frame);
        f.load += 1;
        if (this.recording) {
          const origin = new URL(frame.url()).origin;
          this.loads[origin] = (this.loads[origin] ?? 0) + 1;
        }
      });
    context.pages().forEach(watch);
    context.on('page', watch);
  }

  /** Forget everything so far and record from now on. */
  reset(): void {
    this.entries.length = 0;
    this.errors.length = 0;
    for (const k of Object.keys(this.loads)) delete this.loads[k];
    this.recording = true;
  }

  private frameInfo(frame: Frame): { id: number; load: number } {
    let f = this.frames.get(frame);
    if (!f) {
      f = { id: this.nextFrame++, load: 0 };
      this.frames.set(frame, f);
    }
    return f;
  }

  private onRequest(request: Request): void {
    if (!this.recording) return;
    let doc = '(worker)';
    try {
      const f = this.frameInfo(request.frame());
      // A navigation request belongs to the document it is about to load.
      doc = `${f.id}#${request.isNavigationRequest() ? f.load + 1 : f.load}`;
    } catch {
      // Requests from a dedicated or service worker have no frame.
    }
    const e: Entry = {
      method: request.method(),
      url: request.url(),
      resourceType: request.resourceType(),
      body: request.postData(),
      bySw: request.serviceWorker() !== null,
      doc,
      outcome: 'pending',
      status: null,
      failure: null,
    };
    this.entries.push(e);
    this.all.push(e);
    this.byRequest.set(request, e);
  }

  /** Wait until no new request has been recorded for `quietMs` (at most `ms`). */
  async settle(quietMs = 1_500, ms = 15_000): Promise<void> {
    const end = Date.now() + ms;
    let seen = -1;
    while (Date.now() < end && seen !== this.entries.length) {
      seen = this.entries.length;
      await new Promise((r) => setTimeout(r, quietMs));
    }
  }
}

const isHttp = (url: string) => /^https?:/.test(url);
const describe = (e: Entry) => `${e.method} ${e.url} [${e.bySw ? 'service worker' : e.doc}] ${e.outcome}${e.status ? ` ${e.status}` : ''}${e.failure ? ` (${e.failure})` : ''}`;

/** Paths each origin's service worker never intercepts (network only): what a page can send past it. */
export const NOT_INTERCEPTED = { [SITE_ORIGIN]: ['/release.json', '/sw.js', '/_offline/'], [RUNNER_ORIGIN]: ['/release.json', '/sw.js'] };
const bypasses = (url: URL) => (NOT_INTERCEPTED[url.origin] ?? []).some((p) => (p.endsWith('/') ? url.pathname.startsWith(p) : url.pathname === p));

/**
 * The offline contract, over everything recorded since the servers were stopped. With both
 * servers down, a request reaches the network only if a service worker fetches it itself, or if
 * a page or worker sends it past the service worker (a path the worker never intercepts, or another
 * origin). So:
 * - a service worker makes no request of its own (it served everything from its caches);
 * - no page, frame or worker request goes past it but the update checks: `GET /release.json` from
 *   a document, failing, at most one per document load on each origin;
 * - no request a service worker answered failed, and none came from the network;
 * - no console error and no uncaught page error.
 * (A request whose end Playwright never reports, as when a check's worker is dropped mid-body, is
 * one the service worker intercepted: had it gone to the network, its own fetch would be recorded.)
 * Returns the update checks per origin.
 */
export function assertOfflineContract(log: NetLog): Record<string, number> {
  const http = log.entries.filter((e) => isHttp(e.url));
  expect(http.length, 'requests were recorded offline').toBeGreaterThan(0);
  expect(http.filter((e) => e.bySw).map(describe), 'requests a service worker made offline').toEqual([]);
  const past = http.filter((e) => ![SITE_ORIGIN, RUNNER_ORIGIN].includes(new URL(e.url).origin) || bypasses(new URL(e.url)));
  const checks = past.filter((e) => new URL(e.url).pathname === '/release.json');
  expect(past.filter((e) => !checks.includes(e)).map(describe), 'requests sent past the service workers').toEqual([]);
  const intercepted = http.filter((e) => !past.includes(e));
  expect(intercepted.filter((e) => e.outcome === 'failed' || e.outcome === 'network').map(describe), 'requests not answered from the caches').toEqual([]);
  expect(intercepted.filter((e) => e.outcome === 'served-by-sw').length, 'requests answered from the caches').toBeGreaterThan(0);
  for (const e of checks) {
    expect(e.method, describe(e)).toBe('GET');
    expect(e.body, describe(e)).toBeNull();
    expect(e.outcome, `${describe(e)}: the update check cannot succeed with both servers down`).not.toMatch(/network|served-by-sw/);
    expect(e.doc, `${describe(e)}: an update check outside a document`).not.toBe('(worker)');
  }
  const perDoc = new Map<string, number>();
  for (const e of checks) perDoc.set(`${new URL(e.url).origin} ${e.doc}`, (perDoc.get(`${new URL(e.url).origin} ${e.doc}`) ?? 0) + 1);
  expect([...perDoc].filter(([, n]) => n > 1), 'more than one update check in a document load').toEqual([]);
  const perOrigin: Record<string, number> = {};
  for (const e of checks) perOrigin[new URL(e.url).origin] = (perOrigin[new URL(e.url).origin] ?? 0) + 1;
  for (const [origin, n] of Object.entries(perOrigin)) expect(n, `update checks on ${origin} vs its document loads`).toBeLessThanOrEqual(log.loads[origin] ?? 0);
  // Chromium itself logs every failed load as "Failed to load resource" (a network log entry, not
  // the page's own console call, and not one a page can suppress): one per allowed update check is
  // tolerated; any other console error, and any page error, fails.
  const checkUrls = new Set(checks.map((e) => e.url));
  const browserLog = (m: string) => /^console: Failed to load resource: net::ERR_CONNECTION_REFUSED \((.*)\)$/.exec(m)?.[1];
  const logged = log.errors.filter((m) => checkUrls.has(browserLog(m) ?? ''));
  expect(logged.length, 'browser network log lines vs update checks').toBeLessThanOrEqual(checks.length);
  expect(log.errors.filter((m) => !logged.includes(m)), 'console errors and page errors offline').toEqual([]);
  return perOrigin;
}

/** The file of one of `roots` a same-origin path is served from, or null. */
function fileIn(roots: string[], pathname: string): string | null {
  const parts = decodeURIComponent(pathname).split('/').filter(Boolean);
  for (const root of roots) {
    const full = join(root, ...parts);
    if (pathname.endsWith('/')) {
      if (existsSync(join(full, 'index.html'))) return join(full, 'index.html');
    } else if (existsSync(full) && statSync(full).isFile()) return full;
  }
  return null;
}

/**
 * Every recorded request (page, frame, dedicated worker and service worker alike) is a body-less
 * GET on the site or the runner origin for a file of one of the releases under test (`roots`),
 * with no query string but the service worker's `?r=<release_id>` and Pagefind's own.
 */
export function assertAllowlisted(log: NetLog, roots: { site: string[]; runner: string[] } = { site: [DIST], runner: [RUNNER_DIST] }): void {
  const http = log.all.filter((e) => isHttp(e.url));
  expect(http.length, 'requests were recorded').toBeGreaterThan(0);
  const bad: string[] = [];
  for (const e of http) {
    const url = new URL(e.url);
    const why: string[] = [];
    if (e.method !== 'GET') why.push('not a GET');
    if (e.body !== null) why.push('has a body');
    if (e.resourceType === 'ping') why.push('a beacon');
    if (url.origin === SITE_ORIGIN) {
      if (!fileIn(roots.site, url.pathname)) why.push('not a file of the site release');
      if (!allowedQuery(url)) why.push('query string');
    } else if (url.origin === RUNNER_ORIGIN) {
      if (!fileIn(roots.runner, url.pathname)) why.push('not a file of the runner release');
      if (!allowedQuery(url) || url.pathname.startsWith('/pagefind/')) why.push('query string');
    } else why.push('another origin');
    if (why.length) bad.push(`${describe(e)}: ${why.join(', ')}`);
  }
  expect(bad, 'requests off the allowlist').toEqual([]);
  // The service workers' own requests are seen too (the recorder covers them).
  expect(http.some((e) => e.bySw), 'service-worker requests were recorded').toBe(true);
}

/** Press "Download this book" and wait for "Available offline." */
export async function downloadBook(page: Page, book: string, timeout = 300_000): Promise<void> {
  await page.goto(`/${book}/`);
  const panel = page.locator('[data-offline-book]');
  await expect(panel.locator('[data-offline-status]')).toHaveText('Not downloaded yet.', { timeout: 30_000 });
  await panel.getByRole('button', { name: 'Download this book' }).click();
  await expect(panel.locator('[data-offline-status]')).toHaveText('Available offline.', { timeout });
}

export interface StoredRecord {
  book: string;
  content_hash: string;
  release_id: string;
  runner_release_id?: string;
  confirmed_at: string;
}

/** The confirmed records in `py4kids-offline` on the origin of `target` (a page or the runner frame). */
export function offlineRecords(target: Page | Frame): Promise<StoredRecord[]> {
  return target.evaluate(
    () =>
      new Promise<StoredRecord[]>((resolve, reject) => {
        const open = indexedDB.open('py4kids-offline');
        open.onerror = () => reject(open.error);
        open.onsuccess = () => {
          const db = open.result;
          if (!db.objectStoreNames.contains('books')) return resolve([]);
          const all = db.transaction('books').objectStore('books').getAll();
          all.onsuccess = () => {
            db.close();
            resolve(all.result as StoredRecord[]);
          };
        };
      }),
  );
}

export const cacheNames = (target: Page | Frame): Promise<string[]> => target.evaluate(() => caches.keys());

/** The test hooks of a PY4KIDS_TEST_HOOKS=1 build. */
export interface Hooks {
  pause(point: string): void;
  resume(point: string): void;
  fail(step: string, times?: number): void;
  stepTimeoutMs: number;
  downloadDelayMs: number;
  state: string;
  log: string[];
}
export const HOOKS = process.env.PY4KIDS_TEST_HOOKS === '1';
export const hookState = (page: Page) => page.evaluate(() => (window as unknown as { __py4kidsPwaTest: Hooks }).__py4kidsPwaTest.state);

/** The WCAG 2.2 level A and AA rule tags (as e2e/a11y.spec.ts): any violation carrying one fails. */
const WCAG_AA = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];

/** axe on `include` (or the whole page): zero WCAG 2.2 AA violations. */
export async function axe(page: Page, what: string, include?: string): Promise<void> {
  const { default: AxeBuilder } = await import('@axe-core/playwright');
  let builder = new AxeBuilder({ page }).withTags([...WCAG_AA, 'best-practice']);
  if (include) builder = builder.include(include);
  const results = await builder.analyze();
  const blocking = results.violations.filter((v) => v.tags.some((t) => WCAG_AA.includes(t)));
  const line = (v: (typeof results.violations)[number]) => `${v.impact} ${v.id}: ${v.help} — ${v.nodes.map((n) => n.target.join(' ')).slice(0, 3).join(' | ')}`;
  expect(blocking.map(line), `axe: ${what}`).toEqual([]);
  expect(results.passes.length, `axe: ${what} checked something`).toBeGreaterThan(0);
}

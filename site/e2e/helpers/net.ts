/**
 * Request recording for the no-network proof (plan 103 Phase F). Every request any page, frame or
 * worker of the browser context makes is recorded (not blocked: a page that silently recovers
 * from a blocked call must still fail), with its method, URL, headers and body. WebSockets,
 * beacons and service workers are recorded too.
 */
import { existsSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { test as base, expect, type BrowserContext, type Page } from '@playwright/test';
import { BASE_URL, DIST, RUNNER_DIST, RUNNER_URL } from './env';

export interface Recorded {
  method: string;
  url: string;
  resourceType: string;
  headers: Record<string, string>;
  body: string | null;
  page: string;
  /** Made by a service worker itself (plan 105: recorded at context level too). */
  serviceWorker: boolean;
}

export class Recorder {
  readonly requests: Recorded[] = [];
  readonly sockets: string[] = [];
  readonly serviceWorkers: string[] = [];
  readonly workers: string[] = [];

  attach(context: BrowserContext): void {
    context.on('request', (request) => {
      let page = '';
      try {
        page = request.frame().url();
      } catch {
        page = '(worker)';
      }
      this.requests.push({
        method: request.method(),
        url: request.url(),
        resourceType: request.resourceType(),
        headers: request.headers(),
        body: request.postData(),
        page,
        serviceWorker: request.serviceWorker() !== null,
      });
    });
    context.on('serviceworker', (worker) => this.serviceWorkers.push(worker.url()));
    const watch = (page: Page) => {
      page.on('websocket', (socket) => this.sockets.push(socket.url()));
      page.on('worker', (worker) => this.workers.push(worker.url()));
    };
    context.pages().forEach(watch);
    context.on('page', watch);
  }
}

/**
 * The only query strings a same-origin request may carry: Pagefind's own cache-buster, and the
 * service worker's release (`/sw.js?r=<release_id>`, plan 105).
 */
export function allowedQuery(url: URL): boolean {
  if (url.search === '') return true;
  if (url.pathname === '/sw.js') return /^\?r=[0-9a-f]{64}$/.test(url.search);
  return url.pathname.startsWith('/pagefind/') && /^\?ts=\d+$/.test(url.search);
}

/** The release both dists were built as (their release.json), or null before plan 105's build step. */
function builtRelease(): string | null {
  try {
    return (JSON.parse(readFileSync(join(DIST, 'release.json'), 'utf-8')) as { release_id: string }).release_id;
  } catch {
    return null;
  }
}

/** The `dist/` file a same-origin path is served from, or null. */
export function distFile(pathname: string, root: string = DIST): string | null {
  const parts = decodeURIComponent(pathname).split('/').filter(Boolean);
  const full = join(root, ...parts);
  if (pathname.endsWith('/')) return existsSync(join(full, 'index.html')) ? join(full, 'index.html') : null;
  return existsSync(full) && statSync(full).isFile() ? full : null;
}

/**
 * The no-network assertions over everything recorded:
 * - nothing left the local server's origin (no other host, no WebSocket, no service worker);
 * - every request is a body-less GET or HEAD (so no `sendBeacon`, no form post);
 * - every path exists in dist/ and carries no query string but Pagefind's own;
 * - no request URL or header carries any of `secrets` (the typed answers and other state).
 *
 * With `runner: true` (plan 104 Phase D), the Python runner's origin is allowed too, by the same
 * rules against its own build (runner/dist/), and with no query string at all.
 */
export function assertNoNetwork(recorder: Recorder, secrets: string[], options: { runner?: boolean } = {}): void {
  const origin = new URL(BASE_URL).origin;
  const runner = options.runner ? new URL(RUNNER_URL).origin : null;
  expect(recorder.requests.length, 'requests were recorded').toBeGreaterThan(0);
  expect(recorder.sockets, 'WebSockets').toEqual([]);
  // Service workers (plan 105): only each origin's own, for the built release.
  const release = builtRelease();
  const ownWorkers = new Set([`${origin}/sw.js?r=${release}`, ...(runner ? [`${runner}/sw.js?r=${release}`] : [])]);
  expect(recorder.serviceWorkers.filter((w) => !ownWorkers.has(w)), 'service workers').toEqual([]);
  // With service workers allowed (playwright.config.ts project `site-sw`), they must really have
  // run: each origin's own registered, and the recorder saw requests they made themselves.
  if (base.info().project.use.serviceWorkers === 'allow') {
    expect([...ownWorkers].filter((w) => !recorder.serviceWorkers.includes(w)), 'service workers that never started').toEqual([]);
    expect(recorder.requests.some((r) => r.serviceWorker), 'requests made by a service worker').toBe(true);
  }
  const foreign = recorder.requests.filter((r) => new URL(r.url).origin !== origin && new URL(r.url).origin !== runner).map((r) => `${r.method} ${r.url} (from ${r.page})`);
  expect(foreign, 'requests to another origin').toEqual([]);
  for (const r of recorder.requests) {
    const url = new URL(r.url);
    const what = `${r.method} ${r.url}`;
    expect(['GET', 'HEAD'], `${what}: method`).toContain(r.method);
    expect(r.body, `${what}: body`).toBeNull();
    expect(r.resourceType, `${what}: beacon`).not.toBe('ping');
    if (url.origin === runner) {
      expect(distFile(url.pathname, RUNNER_DIST), `${what}: not a file in runner/dist/`).not.toBeNull();
      expect(allowedQuery(url) && !url.pathname.startsWith('/pagefind/'), `${what}: query string`).toBe(true);
    } else {
      expect(distFile(url.pathname), `${what}: not a file in dist/`).not.toBeNull();
      expect(allowedQuery(url), `${what}: query string`).toBe(true);
    }
    const carried = `${r.url}\n${Object.entries(r.headers).map(([k, v]) => `${k}: ${v}`).join('\n')}`;
    for (const secret of secrets) expect(carried.includes(secret), `${what} carries "${secret}"`).toBe(false);
  }
}

/** `test` with a context-level request recorder attached before the first page opens. */
export const test = base.extend<{ recorder: Recorder }>({
  recorder: async ({ context }, use) => {
    const recorder = new Recorder();
    recorder.attach(context);
    await use(recorder);
  },
});

export { expect };

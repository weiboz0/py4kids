/**
 * The runner boundary in a real browser (plan 104 Phase D, "Isolation", "Navigation", "CSP on
 * both origins" and "No network"). The site page embeds the real runner with the real client
 * (e2e/helpers/runner.ts); messages are sent for real (postMessage between real windows) except
 * where a test needs an origin no real window can have, which it states.
 *
 * - The runner iframe cannot read the site's IndexedDB or localStorage.
 * - The runner drops a message from a wrong origin, and a valid-looking one from another window
 *   on the allowed (site) origin; the site client drops a reply from a wrong origin, from another
 *   window on the runner origin, with an unknown id, and an invalid envelope.
 * - A runner iframe navigated to another origin receives no code, and the page shows the runner
 *   as unavailable and offers a reload.
 * - Zero CSP violations on the runner page while Pyodide loads and runs; only the two local
 *   origins are contacted, and no request carries code or answers.
 */
import { createServer, type IncomingMessage, type Server } from 'node:http';
import type { AddressInfo } from 'node:net';
import { expect, test as base, type Page } from '@playwright/test';
import type { LessonRun } from '../src/lib/check-model';
import type { Verdict } from '../src/lib/runner-client';
import { watchCsp } from './helpers/csp';
import { BASE_URL, RUNNER_URL } from './helpers/env';
import { findItem, fixturePairs, lookupProgram } from './helpers/content';
import { assertNoNetwork, test as recorded } from './helpers/net';
import { check, open, setCode } from './helpers/practice';
import { fresh, openRunner, run, runnerFrame, type Browserside } from './helpers/runner';

const test = base;
test.describe.configure({ mode: 'parallel' });

const SITE = new URL(BASE_URL).origin;
const RUNNER = new URL(RUNNER_URL).origin;

/** A valid run request (what the site would send). */
const runRequest = (id: string, code = 'print("ran")') => ({
  type: 'run',
  id,
  session: `s-${id}`.slice(0, 64),
  code,
  stdin: '',
  files: [],
  check: null,
  budget_ms: 5000,
});

/** Record, in the site page, the id of every message that reaches it. */
async function recordReplies(page: Page): Promise<void> {
  await page.evaluate(() => {
    const seen: string[] = [];
    (window as unknown as { seen: string[] }).seen = seen;
    window.addEventListener('message', (e) => {
      const id = (e.data as { id?: unknown } | null)?.id;
      if (typeof id === 'string') seen.push(id);
    });
  });
}
const replies = (page: Page) => page.evaluate(() => [...(window as unknown as { seen: string[] }).seen]);

/** Spy on the client's verdict for every message it receives. */
async function spyVerdicts(page: Page): Promise<void> {
  await page.evaluate(() => {
    const w = window as unknown as Browserside & { verdicts: string[] };
    w.verdicts = [];
    const receive = w.runner.receive.bind(w.runner);
    w.runner.receive = (event) => {
      const verdict = receive(event);
      w.verdicts.push(verdict);
      return verdict;
    };
  });
}
const verdicts = (page: Page) => page.evaluate(() => [...(window as unknown as { verdicts: Verdict[] }).verdicts]);

test('the runner iframe cannot read the site\'s IndexedDB or localStorage', async ({ page }) => {
  await openRunner(page);
  // The site's own storage, with a sentinel.
  await page.evaluate(async () => {
    localStorage.setItem('py4kids-sentinel', 'zq9site');
    await new Promise<void>((resolve, reject) => {
      const req = indexedDB.open('py4kids-sentinel-db');
      req.onupgradeneeded = () => req.result.createObjectStore('s');
      req.onsuccess = () => {
        const tx = req.result.transaction('s', 'readwrite');
        tx.objectStore('s').put('zq9site', 'k');
        tx.oncomplete = () => (req.result.close(), resolve());
      };
      req.onerror = () => reject(req.error);
    });
  });
  const frame = runnerFrame(page);
  const seen = await frame.evaluate(async () => {
    const out: Record<string, unknown> = {};
    out.origin = location.origin;
    out.local = localStorage.getItem('py4kids-sentinel');
    out.localKeys = Object.keys(localStorage);
    out.databases = (await indexedDB.databases()).map((d) => d.name);
    try {
      out.parentStorage = String(window.parent.localStorage.length);
    } catch (e) {
      out.parentStorage = (e as Error).name;
    }
    try {
      out.parentDocument = String(window.parent.document.title);
    } catch (e) {
      out.parentDocument = (e as Error).name;
    }
    return out;
  });
  expect(seen.origin).toBe(RUNNER);
  expect(seen.local).toBeNull();
  expect(seen.localKeys).toEqual([]);
  expect(seen.databases).not.toContain('py4kids-sentinel-db');
  expect(seen.databases).not.toContain('py4kids');
  expect(seen.parentStorage).toBe('SecurityError');
  expect(seen.parentDocument).toBe('SecurityError');
  // The Python worker has neither (and no window to reach one through).
  const worker = page.workers().find((w) => w.url().startsWith(`${RUNNER_URL}/assets/worker-`))!;
  expect(await worker.evaluate(async () => ({ hasLocal: 'localStorage' in self, dbs: (await indexedDB.databases()).map((d) => d.name) }))).toEqual({ hasLocal: false, dbs: [] });
  const py = await run(page, { session: fresh(), code: 'import js\nprint(hasattr(js, "localStorage"), hasattr(js, "document"))', check: { kind: 'output', turtle: false } });
  expect(py.stdout).toBe('False False\n');
});

test('the runner ignores a message from a wrong origin, and a valid-looking one from another window on the site origin', async ({ page, context }) => {
  await openRunner(page);
  await recordReplies(page);
  const frame = runnerFrame(page);

  // A real message from the runner's own window (origin: the runner, source: not the parent).
  await frame.evaluate((req) => window.postMessage(req, '*'), runRequest('self-post'));
  // The origin check alone: a message from the parent window claiming another origin. (No real
  // window can be the parent and have another origin, so this one is a synthetic MessageEvent.)
  await frame.evaluate((req) => window.dispatchEvent(new MessageEvent('message', { data: req, origin: 'http://evil.example', source: window.parent })), runRequest('wrong-origin'));

  // A popup on the site's own origin reaches the runner iframe through its opener and posts a
  // valid run with the exact runner origin.
  const [popup] = await Promise.all([context.waitForEvent('page'), page.evaluate(() => void window.open('/about/', 'other'))]);
  await popup.waitForLoadState();
  expect(new URL(popup.url()).origin).toBe(SITE);
  const posted = await popup.evaluate(
    ({ req, runner }) => {
      const iframe = window.opener?.document.querySelector(`iframe[src^="${runner}"]`) as HTMLIFrameElement | null;
      if (!iframe?.contentWindow) return false;
      iframe.contentWindow.postMessage(req, runner);
      return true;
    },
    { req: runRequest('popup', 'print("from the popup")'), runner: RUNNER },
  );
  expect(posted).toBe(true);

  // Control: the same synthetic event with the right origin and source IS accepted.
  await frame.evaluate((req) => window.dispatchEvent(new MessageEvent('message', { data: req, origin: window.location.ancestorOrigins[0], source: window.parent })), runRequest('control'));
  await expect.poll(() => replies(page), { timeout: 30_000 }).toContain('control');
  await page.waitForTimeout(1000);
  const got = await replies(page);
  expect(got).not.toContain('self-post');
  expect(got).not.toContain('wrong-origin');
  expect(got).not.toContain('popup');
});

test('the site drops a reply from a wrong origin, from another runner-origin window, with an unknown id, and an invalid envelope', async ({ page, context }) => {
  await openRunner(page);
  await spyVerdicts(page);
  // A run that stays pending for a while (a busy loop of about 4 s).
  const id = await page.evaluate(() => {
    const w = window as unknown as Browserside & { pending: Promise<unknown> };
    const { id, result } = w.runner.run({ session: 'u-iso', code: 'import time\nend = time.time() + 4\nwhile time.time() < end:\n    pass\nprint("real")' });
    w.pending = result;
    return id;
  });
  // A current (version 2, plan 105) envelope, so only the binding can drop it.
  const forged = { v: 2, type: 'result', id, session: 'u-iso', stdout: 'FORGED\n', stderr: '', results: [], timing: { boot_ms: 0, run_ms: 0, restart_ms: 0 }, status: 'ok', interrupts: 'sab', session_new: false, truncated: false, segments: [] };

  // From the real runner window: an unknown id, then an invalid envelope with the pending id.
  const frame = runnerFrame(page);
  await frame.evaluate(({ msg, site }) => window.parent.postMessage({ ...msg, id: 'not-a-pending-id' }, site), { msg: forged, site: SITE });
  await frame.evaluate(({ msg, site }) => window.parent.postMessage({ type: 'result', id: msg.id }, site), { msg: forged, site: SITE });
  // From a second runner iframe (the runner origin, but not the client's iframe): the pending id.
  await page.evaluate((runner) => {
    const second = document.createElement('iframe');
    second.setAttribute('sandbox', 'allow-scripts allow-same-origin');
    second.src = `${runner}/`;
    second.name = 'second-runner';
    document.body.append(second);
  }, RUNNER);
  await expect.poll(() => page.frames().filter((f) => f.url().startsWith(`${RUNNER_URL}/`)).length).toBe(2);
  const second = page.frames().find((f) => f.url().startsWith(`${RUNNER_URL}/`) && f !== frame)!;
  await second.waitForLoadState();
  await second.evaluate(({ msg, site }) => window.parent.postMessage(msg, site), { msg: forged, site: SITE });
  // From a popup on the site origin (the wrong origin for a reply): the pending id.
  const [popup] = await Promise.all([context.waitForEvent('page'), page.evaluate(() => void window.open('/about/', 'other'))]);
  await popup.waitForLoadState();
  await popup.evaluate(({ msg, site }) => window.opener.postMessage(msg, site), { msg: forged, site: SITE });

  await expect.poll(() => verdicts(page)).toHaveLength(4);
  expect(await page.evaluate((i) => (window as unknown as Browserside).runner.isPending(i), id)).toBe(true);
  // The real result then arrives and is the one accepted.
  const result = (await page.evaluate(() => (window as unknown as { pending: Promise<{ stdout: string }> }).pending)) as { stdout: string };
  expect(result.stdout).toBe('real\n');
  const all = await verdicts(page);
  expect(all.slice(0, 4).sort()).toEqual(['invalid', 'unknown-id', 'wrong-origin', 'wrong-source']);
  expect(all).toContain('accepted');
  expect(all.filter((v) => v === 'accepted')).toHaveLength(1);
});

// ---------------------------------------------------------------------------------------------
// Navigation: a runner iframe navigated elsewhere gets no code

/** A local page on another origin that reports every message it receives to its own server. */
async function otherOrigin(): Promise<{ server: Server; url: string; hits: string[] }> {
  const hits: string[] = [];
  const page = `<!doctype html><title>other</title><script>
addEventListener('message', (e) => fetch('/got?' + encodeURIComponent(JSON.stringify(e.data).slice(0, 200))));
</script>`;
  const server = createServer((req: IncomingMessage, res) => {
    hits.push(req.url ?? '');
    res.writeHead(200, {
      'content-type': 'text/html; charset=utf-8',
      'cross-origin-embedder-policy': 'require-corp',
      'cross-origin-resource-policy': 'cross-origin',
    });
    res.end(page);
  });
  await new Promise<void>((r) => server.listen(0, '127.0.0.1', r));
  return { server, url: `http://127.0.0.1:${(server.address() as AddressInfo).port}`, hits };
}

for (const bypass of [false, true]) {
  const name = bypass
    ? 'navigation (CSP bypassed, so the other page loads): the navigated iframe receives no code; the page offers a reload'
    : 'navigation: the site CSP blocks the iframe from leaving the runner origin; no code is delivered; the page offers a reload';
  test.describe(() => {
    test.use({ bypassCSP: bypass });
    test(name, async ({ page }) => {
      test.setTimeout(180_000);
      const other = await otherOrigin();
      try {
        const book = 'python-projects';
        const entry = 'unit-03-turtle-art-studio';
        // A short lesson budget (the client waits budget + grace + its slack for an answer).
        await page.route(`**/${book}/${entry}/run.json`, async (route) => {
          const response = await route.fetch();
          await route.fulfill({ response, json: { ...((await response.json()) as LessonRun), budget_ms: 100 } });
        });
        await page.goto(`/${book}/${entry}/`);
        const holder = page.locator('[data-run]').first();
        await holder.scrollIntoViewIfNeeded();
        await holder.locator('[data-lesson-run]').click();
        await expect(holder.locator('[data-lesson-run]')).toBeDisabled();
        await expect(holder.locator('[data-lesson-run]')).toBeEnabled({ timeout: 60_000 });
        await expect(holder.locator('.runner-unavailable')).toHaveCount(0);
        expect(page.frames().some((f) => f.url().startsWith(`${RUNNER_URL}/`))).toBe(true);
        // Navigate the runner iframe to the other origin.
        await page.evaluate((url) => {
          const iframe = document.querySelector<HTMLIFrameElement>('.runner-holder iframe')!;
          iframe.src = `${url}/`;
        }, other.url);
        await expect.poll(() => page.frames().some((f) => f.url().startsWith(`${RUNNER_URL}/`))).toBe(false);
        if (bypass) await expect.poll(() => other.hits).toContain('/');
        else await page.waitForTimeout(1000);
        await holder.locator('[data-lesson-run]').click();
        await expect(holder.locator('.runner-unavailable')).toBeVisible({ timeout: 90_000 });
        await expect(holder.locator('.runner-unavailable button')).toHaveText('Reload the page');
        expect(other.hits.filter((h) => h.startsWith('/got'))).toEqual([]);
        if (!bypass) expect(other.hits).toEqual([]);
      } finally {
        other.server.close();
      }
    });
  });
}

// ---------------------------------------------------------------------------------------------
// CSP on the runner origin, and no network

test('zero CSP violations on the runner page while Pyodide loads and runs (a lesson run, a check, turtle)', async ({ context, page }) => {
  const csp = await watchCsp(context);
  await openRunner(page);
  await run(page, { session: 'u-csp', code: 'print("hello")' });
  await run(page, { session: fresh(), code: 'import turtle\nt = turtle.Turtle()\nfor _ in range(4):\n    t.forward(10)\n    t.left(90)', check: { kind: 'output', turtle: true } });
  await run(page, { session: fresh(), code: 'import sys\nprint(sys.stdin.read())', stdin: 'x', check: { kind: 'fixture', expected: 'x', match: 'token', turtle: false } });
  await page.waitForTimeout(300);
  expect(csp.violations).toEqual([]);
  expect(csp.console).toEqual([]);
});

recorded('no network: a Check and a lesson Run contact only the site and the runner origins, with no code or answers in any request', async ({ page, recorder }) => {
  const marker = `zq9code${Math.random().toString(36).slice(2, 10)}`;
  const found = findItem((f) => f.book === 'usaco-bronze' && f.item.check.kind === 'fixtures' && f.item.check.cases.length >= 2, 'a usaco item');
  const pairs = fixturePairs(found);
  const item = await open(page, found);
  await setCode(page, item, `# ${marker}\n${lookupProgram(Object.fromEntries(pairs.map((c) => [c.input, c.output])))}`);
  expect(await check(item)).toMatch(/^Passed/);
  // A typed answer too.
  const answer = findItem((f) => f.item.check.kind === 'answer', 'an answer item');
  const typed = `zq9typed${Math.random().toString(36).slice(2, 10)}`;
  const answerItem = await open(page, answer);
  await answerItem.locator('textarea[data-answer]').fill(typed);
  await answerItem.locator('form[data-answer-form] button[type="submit"]').click();
  await expect(answerItem.locator('[data-result] .verdict')).toHaveText(/^Not yet/);
  // A lesson Run.
  await page.goto('/python-projects/unit-03-turtle-art-studio/');
  const holder = page.locator('[data-run]').first();
  await holder.scrollIntoViewIfNeeded();
  await holder.locator('[data-lesson-run]').click();
  await expect(holder.locator('[data-lesson-run]')).toBeDisabled();
  await expect(holder.locator('[data-lesson-run]')).toBeEnabled({ timeout: 60_000 });
  expect(recorder.requests.some((r) => new URL(r.url).origin === RUNNER)).toBe(true);
  expect(recorder.workers.some((w) => w.startsWith(`${RUNNER_URL}/assets/worker-`))).toBe(true);
  assertNoNetwork(recorder, [marker, typed], { runner: true });
});

/**
 * The installable, offline site (plan 105 Phases A and B), in Chromium with service workers on:
 * - the web app manifest is valid and installable (name, start URL, standalone, PNG icons of the
 *   sizes it names, a maskable one);
 * - both origins register their service worker as `/sw.js?r=<release_id>` for the built release,
 *   and serve `/sw.js` with their isolation headers;
 * - "Download this book" on python-projects shows the size first, then a progress bar, and says
 *   "Available offline" once both origins have confirmed records for the same release;
 * - with both servers stopped, the downloaded book still opens, and `crossOriginIsolated` is still
 *   true in the site, the runner page and the runner's worker: Python runs from the cached
 *   Pyodide and a hang is stopped by the SharedArrayBuffer interrupt.
 * The full offline and update-path suite (plan 105 Phase E) is offline.spec.ts (every book),
 * update.spec.ts and ui.spec.ts.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Page } from '@playwright/test';
import { DIST, RUNNER_DIST, RUNNER_URL } from '../e2e/helpers/env';
import { loadClient, runnerFrame, type Browserside } from '../e2e/helpers/runner';
import { expect, test } from './servers';

const BOOK = 'python-projects';
const release = (dir: string) => JSON.parse(readFileSync(join(dir, 'release.json'), 'utf-8')) as { release_id: string; books?: Record<string, { content_hash: string }> };
const SITE_RELEASE = release(DIST);
const RUNNER_RELEASE = release(RUNNER_DIST);

/** PNG width and height from the IHDR chunk. */
function pngSize(png: Buffer): [number, number] {
  expect([...png.subarray(0, 8)]).toEqual([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  expect(png.subarray(12, 16).toString('latin1')).toBe('IHDR');
  return [png.readUInt32BE(16), png.readUInt32BE(20)];
}

async function downloadBook(page: Page): Promise<void> {
  await page.goto(`/${BOOK}/`);
  const panel = page.locator('[data-offline-book]');
  await expect(panel).toBeVisible();
  await expect(panel.locator('[data-offline-status]')).toHaveText('Not downloaded yet.', { timeout: 30_000 });
  // The size first.
  await expect(panel.locator('[data-offline-size]')).toHaveText(/^Download size: [\d.]+ MB for this book \(\d+ files\), plus [\d.]+ MB for Python/);
  await panel.getByRole('button', { name: 'Download this book' }).click();
  // Then the progress bar, then "Available offline" once both origins confirmed.
  await expect(panel.locator('[data-offline-status]')).toHaveText('Available offline.', { timeout: 180_000 });
  await expect(panel.locator('[data-offline-persist]')).toHaveText(/^Storage on this device: .*; Python's storage: /);
}

test('the web app manifest is valid and installable', async ({ page, request, servers: _ }) => {
  await page.goto('/');
  const href = await page.locator('link[rel="manifest"]').getAttribute('href');
  expect(href).toMatch(/^\/manifest\.[0-9a-f]{10}\.webmanifest$/);
  const response = await request.get(href!);
  expect(response.status()).toBe(200);
  expect(response.headers()['content-type']).toBe('application/manifest+json');
  const manifest = (await response.json()) as {
    id: string;
    name: string;
    short_name: string;
    start_url: string;
    scope: string;
    display: string;
    theme_color: string;
    background_color: string;
    icons: { src: string; sizes: string; type: string; purpose: string }[];
  };
  expect(manifest).toMatchObject({ id: '/', name: 'py4kids', short_name: 'py4kids', start_url: '/', scope: '/', display: 'standalone' });
  expect(await page.locator('meta[name="theme-color"]').getAttribute('content')).toBe(manifest.theme_color);
  expect(manifest.background_color).toMatch(/^#[0-9a-f]{6}$/);
  const png = manifest.icons.filter((i) => i.type === 'image/png');
  expect(png.map((i) => `${i.sizes} ${i.purpose}`).sort()).toEqual(['192x192 any', '512x512 any', '512x512 maskable']);
  for (const icon of manifest.icons) {
    const file = await request.get(icon.src);
    expect(file.status(), icon.src).toBe(200);
    expect(file.headers()['content-type'], icon.src).toBe(icon.type);
    if (icon.type === 'image/png') expect(pngSize(await file.body()).join('x')).toBe(icon.sizes);
  }
  const touch = await page.locator('link[rel="apple-touch-icon"]').getAttribute('href');
  expect(pngSize(await (await request.get(touch!)).body())).toEqual([180, 180]);
});

test('both origins register /sw.js?r=<release_id> for the built release, served with their headers', async ({ page, request, servers: _ }) => {
  expect(SITE_RELEASE.release_id).toBe(RUNNER_RELEASE.release_id);
  const id = SITE_RELEASE.release_id;
  await page.goto('/');
  const site = await page.evaluate(async () => (await navigator.serviceWorker.ready).active?.scriptURL);
  expect(new URL(site!).pathname + new URL(site!).search).toBe(`/sw.js?r=${id}`);
  const swHeaders = (await request.get('/sw.js')).headers();
  expect(swHeaders['cross-origin-embedder-policy']).toBe('require-corp');
  expect(swHeaders['content-type']).toMatch(/^text\/javascript/);

  // The runner registers its own, from inside the site's iframe.
  await page.goto(`/${BOOK}/`);
  await loadClient(page);
  await page.evaluate(() => {
    const w = window as unknown as Browserside;
    w.runner = w.py4kidsRunnerClient.connectRunner(document.body).client;
  });
  await expect.poll(() => page.frames().some((f) => f.url().startsWith(`${RUNNER_URL}/`)), { timeout: 30_000 }).toBe(true);
  const runner = await runnerFrame(page).evaluate(async () => (await navigator.serviceWorker.ready).active?.scriptURL);
  expect(new URL(runner!).pathname + new URL(runner!).search).toBe(`/sw.js?r=${id}`);
  // The runner's _headers `/*` rule covers /sw.js: COEP and CORP (Chrome checks a worker script's COEP).
  const runnerSw = (await request.get(`${RUNNER_URL}/sw.js`)).headers();
  expect(runnerSw['cross-origin-embedder-policy']).toBe('require-corp');
  expect(runnerSw['cross-origin-resource-policy']).toBe('cross-origin');
  expect(runnerSw['content-security-policy']).toContain('frame-ancestors');
});

test('download a book: size first, a progress bar, then "available offline" with both origins confirmed', async ({ page, servers: _ }) => {
  await page.goto(`/${BOOK}/`);
  const panel = page.locator('[data-offline-book]');
  await expect(panel.locator('[data-offline-status]')).toHaveText('Not downloaded yet.', { timeout: 30_000 });
  await panel.getByRole('button', { name: 'Download this book' }).click();
  const bar = panel.locator('[data-offline-progress]');
  await expect(bar).toBeVisible();
  await expect.poll(async () => Number(await bar.getAttribute('max')), { timeout: 60_000 }).toBeGreaterThan(1);
  await expect(panel.locator('[data-offline-status]')).toHaveText('Available offline.', { timeout: 180_000 });
  await expect(bar).toBeHidden();

  // Both origins hold a confirmed record for the same release, and the caches it names.
  const id = SITE_RELEASE.release_id;
  const hash = SITE_RELEASE.books![BOOK]!.content_hash;
  const readRecords = () =>
    new Promise<unknown[]>((resolve, reject) => {
      const open = indexedDB.open('py4kids-offline');
      open.onerror = () => reject(open.error);
      open.onsuccess = () => {
        const all = open.result.transaction('books').objectStore('books').getAll();
        all.onsuccess = () => resolve(all.result);
      };
    });
  const siteRecords = (await page.evaluate(readRecords)) as { book: string; content_hash: string; release_id: string; runner_release_id: string }[];
  expect(siteRecords).toEqual([expect.objectContaining({ book: BOOK, content_hash: hash, release_id: id, runner_release_id: id })]);
  expect(await page.evaluate(() => caches.keys())).toEqual(expect.arrayContaining([`shell-${id}`, `book-${BOOK}-${hash}`]));
  const runner = runnerFrame(page);
  const runnerRecords = (await runner.evaluate(readRecords)) as { book: string; release_id: string }[];
  expect(runnerRecords).toEqual([expect.objectContaining({ book: BOOK, content_hash: hash, release_id: id })]);
  expect(await runner.evaluate(() => caches.keys())).toEqual(expect.arrayContaining([`shell-${id}`, 'pyodide-0.27.8']));

  // A reload keeps the status.
  await page.reload();
  await expect(panel.locator('[data-offline-status]')).toHaveText('Available offline.', { timeout: 30_000 });
});

test('offline (both servers stopped): the book opens and crossOriginIsolated holds in the site, the runner and its worker', async ({
  page,
  servers,
}) => {
  await downloadBook(page);
  await servers.stop();
  // Really gone: both origins refuse connections.
  await expect(page.request.get('/release.json')).rejects.toThrow();
  await expect(page.request.get(`${RUNNER_URL}/release.json`)).rejects.toThrow();

  // The book page, from the site's service worker.
  await page.reload();
  await expect(page.locator('h1')).toBeVisible();
  await expect(page.locator('[data-offline-book] [data-offline-status]')).toHaveText('Available offline.', { timeout: 30_000 });
  expect(await page.evaluate(() => crossOriginIsolated)).toBe(true);
  // A lesson page of the book too.
  const lesson = await page.locator('[data-contents] a.contents-title').first().getAttribute('href');
  await page.goto(lesson!);
  await expect(page.locator('main h1')).toBeVisible();
  expect(await page.evaluate(() => crossOriginIsolated)).toBe(true);

  // The runner page and its Python worker, from the runner's service worker.
  await loadClient(page);
  const ready = await page.evaluate(async () => {
    const w = window as unknown as Browserside;
    w.runner = w.py4kidsRunnerClient.connectRunner(document.body).client;
    return w.runner.ping();
  });
  expect(ready.isolated, 'the runner page and its worker are cross-origin isolated offline').toBe(true);
  expect(await runnerFrame(page).evaluate(() => crossOriginIsolated)).toBe(true);
  const hello = await page.evaluate(() => (window as unknown as Browserside).runner.run({ session: 'offline', code: 'print(6 * 7)' }).result);
  expect(hello.stdout).toBe('42\n');
  // The interrupt works offline: the isolation headers survived the cache.
  const hang = await page.evaluate(() =>
    (window as unknown as Browserside).runner.run({ session: 'offline-hang', code: 'while True:\n    pass\n', budget_ms: 1000 }).result,
  );
  expect(hang.status).toBe('timeout');
  expect(hang.interrupts).toBe('sab');
});

test('the update-handshake test hooks exist only in a test build (PY4KIDS_TEST_HOOKS=1)', { tag: '@hooks' }, async ({ page, servers: _ }) => {
  await page.goto('/');
  await page.evaluate(async () => navigator.serviceWorker.ready);
  const hooks = await page.evaluate(() => {
    const h = (window as unknown as { __py4kidsPwaTest?: { state: string; stepTimeoutMs: number } }).__py4kidsPwaTest;
    return h ? { state: h.state, stepTimeoutMs: h.stepTimeoutMs } : null;
  });
  if (process.env.PY4KIDS_TEST_HOOKS === '1') expect(hooks).toEqual({ state: 'idle', stepTimeoutMs: 10_000 });
  else expect(hooks).toBeNull();
  // Nothing of the hooks is shipped in a production build's scripts.
  const scripts = await page.locator('script[src]').evaluateAll((s) => s.map((e) => (e as HTMLScriptElement).src));
  for (const src of scripts) {
    const text = await (await page.request.get(src)).text();
    if (process.env.PY4KIDS_TEST_HOOKS !== '1') expect(text, src).not.toContain('__py4kidsPwaTest');
  }
});

test('test hooks: a download stopped midway (servers down) confirms nothing', { tag: '@hooks' }, async ({ page, servers }) => {
  test.skip(process.env.PY4KIDS_TEST_HOOKS !== '1', 'needs a build with PY4KIDS_TEST_HOOKS=1');
  await page.goto(`/${BOOK}/`);
  const panel = page.locator('[data-offline-book]');
  await expect(panel.locator('[data-offline-status]')).toHaveText('Not downloaded yet.', { timeout: 30_000 });
  await page.evaluate(() => {
    (window as unknown as { __py4kidsPwaTest: { downloadDelayMs: number } }).__py4kidsPwaTest.downloadDelayMs = 300;
  });
  await panel.getByRole('button', { name: 'Download this book' }).click();
  const bar = panel.locator('[data-offline-progress]');
  await expect.poll(async () => Number(await bar.getAttribute('value')), { timeout: 60_000 }).toBeGreaterThan(0);
  await servers.stop();
  await expect(panel.locator('[data-offline-status]')).toHaveText(/^The download did not finish/, { timeout: 60_000 });
  const records = await page.evaluate(
    () =>
      new Promise<unknown[]>((resolve) => {
        const open = indexedDB.open('py4kids-offline');
        open.onsuccess = () => {
          const all = open.result.transaction('books').objectStore('books').getAll();
          all.onsuccess = () => resolve(all.result);
        };
      }),
  );
  expect(records).toEqual([]);
  await expect(panel.getByRole('button', { name: 'Try again' })).toBeVisible();
});

/**
 * The update path, happy case (plan 105 "Release identity and updates"; the full suite with
 * paused and failing steps is Phase E): release A and release B, where B changes only the runner
 * (its Pyodide moves to another versioned folder, so every runner URL that matters differs) and
 * the site's files are unchanged but for release.json.
 * - With A active and a book downloaded, B's workers install and wait; the page offers the update.
 * - Accepting runs the page-mediated handshake (runner, then site, then reload) and the page
 *   reloads under B on both origins.
 * - The book's content hash is unchanged, so it is re-confirmed under B in the same cache (verify
 *   and re-stamp), and reads "Available offline" again.
 * - A page of B asks for cleanup: A's shell and Pyodide caches go; the book cache stays.
 */
import { spawnSync } from 'node:child_process';
import { cpSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { DIST, RUNNER_DIST, SITE } from '../e2e/helpers/env';
import { runnerFrame } from '../e2e/helpers/runner';
import { computeReleaseId, writeRelease } from '../../deploy/release.mjs';
import type { Locator, Page } from '@playwright/test';
import { expect, test, type Servers } from './servers';

const BOOK = 'python-projects';
const RUNNER = join(SITE, '..', 'runner');

interface Releases {
  work: string;
  A: { site: string; runner: string };
  B: { site: string; runner: string };
  idA: string;
  idB: string;
  hash: string;
}

/** Release A is the build; release B is the same site with a rebuilt runner (Pyodide moved). */
function releases(): Releases {
  const scratch = join(SITE, 'node_modules', '.cache');
  mkdirSync(scratch, { recursive: true });
  const work = mkdtempSync(join(scratch, 'py4kids-update-'));
  const A = { site: join(work, 'site-a'), runner: join(work, 'runner-a') };
  const B = { site: join(work, 'site-b'), runner: join(work, 'runner-b') };
  cpSync(DIST, A.site, { recursive: true });
  cpSync(RUNNER_DIST, A.runner, { recursive: true });
  cpSync(DIST, B.site, { recursive: true });
  const built = spawnSync(process.execPath, [join(RUNNER, 'scripts', 'build.ts')], {
    cwd: RUNNER,
    env: { ...process.env, PY4KIDS_RUNNER_OUT: B.runner, PY4KIDS_TEST_HOOKS: '1', PY4KIDS_TEST_PYODIDE_DIR: '0.27.8-b' },
    encoding: 'utf-8',
  });
  expect(built.status, built.stderr).toBe(0);
  const idA = (JSON.parse(readFileSync(join(A.site, 'release.json'), 'utf-8')) as { release_id: string }).release_id;
  expect(computeReleaseId(A)).toBe(idA);
  const idB = writeRelease(B);
  expect(idB).not.toBe(idA);
  const hash = (JSON.parse(readFileSync(join(B.site, 'release.json'), 'utf-8')) as { books: Record<string, { content_hash: string }> }).books[BOOK]!.content_hash;
  return { work, A, B, idA, idB, hash };
}

/** Under release A, download the book; then deploy B and wait for the update offer. */
async function downloadThenDeployB(page: Page, servers: Servers, r: Releases): Promise<Locator> {
  await servers.stop();
  await servers.start(r.A);
  await page.goto(`/${BOOK}/`);
  const panel = page.locator('[data-offline-book]');
  await expect(panel.locator('[data-offline-status]')).toHaveText('Not downloaded yet.', { timeout: 30_000 });
  await panel.getByRole('button', { name: 'Download this book' }).click();
  await expect(panel.locator('[data-offline-status]')).toHaveText('Available offline.', { timeout: 180_000 });
  // Release B is deployed: the page keeps running on A and offers the update.
  await servers.stop();
  await servers.start(r.B);
  await page.reload();
  await expect(panel.locator('[data-offline-status]')).toHaveText('Available offline.', { timeout: 30_000 });
  const update = page.locator('[data-pwa-update]');
  await expect(update).toBeVisible({ timeout: 60_000 });
  await expect(update).toContainText('A new version of py4kids is available.');
  expect(await page.evaluate(() => navigator.serviceWorker.controller?.scriptURL)).toContain(`r=${r.idA}`);
  return update;
}

test('a runner-only release B: the update waits, the handshake activates both origins, the book is re-confirmed', async ({ page, servers }) => {
  test.setTimeout(300_000);
  const r = releases();
  const { idA, idB, hash } = r;
  try {
    const update = await downloadThenDeployB(page, servers, r);
    const panel = page.locator('[data-offline-book]');

    // Accept: runner, then site, then the reload.
    await Promise.all([page.waitForEvent('load', { timeout: 60_000 }), update.getByRole('button', { name: 'Reload to update' }).click()]);
    await expect.poll(() => page.evaluate(() => navigator.serviceWorker.controller?.scriptURL ?? ''), { timeout: 30_000 }).toContain(`r=${idB}`);

    // Under B: the book is re-confirmed (same content hash, same cache) on both origins.
    await expect(panel.locator('[data-offline-status]')).toHaveText('Available offline.', { timeout: 120_000 });
    const runner = runnerFrame(page);
    expect(await runner.evaluate(() => navigator.serviceWorker.controller?.scriptURL ?? '')).toContain(`r=${idB}`);
    const records = () =>
      new Promise<{ book: string; release_id: string; content_hash: string; runner_release_id?: string }[]>((resolve) => {
        const open = indexedDB.open('py4kids-offline');
        open.onsuccess = () => {
          const all = open.result.transaction('books').objectStore('books').getAll();
          all.onsuccess = () => resolve(all.result);
        };
      });
    expect(await page.evaluate(records)).toEqual([expect.objectContaining({ book: BOOK, content_hash: hash, release_id: idB, runner_release_id: idB })]);
    expect(await runner.evaluate(records)).toEqual([expect.objectContaining({ book: BOOK, content_hash: hash, release_id: idB })]);

    // Cleanup from B pages: A's shell and Pyodide caches go, the book cache stays.
    await expect.poll(() => page.evaluate(() => caches.keys()), { timeout: 30_000 }).toEqual(expect.arrayContaining([`shell-${idB}`, `book-${BOOK}-${hash}`]));
    await expect.poll(async () => (await page.evaluate(() => caches.keys())).includes(`shell-${idA}`), { timeout: 30_000 }).toBe(false);
    await expect.poll(() => runner.evaluate(() => caches.keys()), { timeout: 30_000 }).toEqual(expect.arrayContaining([`shell-${idB}`, 'pyodide-0.27.8-b']));
    await expect
      .poll(async () => (await runner.evaluate(() => caches.keys())).filter((n) => n === `shell-${idA}` || n === 'pyodide-0.27.8'), { timeout: 30_000 })
      .toEqual([]);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

// The test hooks (a PY4KIDS_TEST_HOOKS=1 build only): pause the handshake after the runner
// activated, then force the site step to fail once; the page recovers forward.
test('test hooks: a paused handshake has runner B and site A; a failed site step is retried to completion', async ({ page, servers }) => {
  test.skip(process.env.PY4KIDS_TEST_HOOKS !== '1', 'needs a build with PY4KIDS_TEST_HOOKS=1');
  test.setTimeout(300_000);
  const r = releases();
  try {
    const update = await downloadThenDeployB(page, servers, r);
    await page.evaluate(() => {
      const h = (window as unknown as { __py4kidsPwaTest: { pause(p: string): void; fail(s: string, n?: number): void; stepTimeoutMs: number } }).__py4kidsPwaTest;
      h.stepTimeoutMs = 2000;
      h.pause('after-runner');
      h.fail('site', 1);
    });
    const state = () => page.evaluate(() => (window as unknown as { __py4kidsPwaTest: { state: string } }).__py4kidsPwaTest.state);
    await update.getByRole('button', { name: 'Reload to update' }).click();
    await expect.poll(state, { timeout: 30_000 }).toBe('paused:after-runner');
    // The interval: runner on B, site still on A.
    expect(await runnerFrame(page).evaluate(() => navigator.serviceWorker.controller?.scriptURL ?? '')).toContain(`r=${r.idB}`);
    expect(await page.evaluate(() => navigator.serviceWorker.controller?.scriptURL ?? '')).toContain(`r=${r.idA}`);
    const loaded = page.waitForEvent('load', { timeout: 60_000 });
    await page.evaluate(() => (window as unknown as { __py4kidsPwaTest: { resume(p: string): void } }).__py4kidsPwaTest.resume('after-runner'));
    await expect(update).toContainText('Finishing the update…', { timeout: 30_000 });
    await loaded;
    await expect.poll(() => page.evaluate(() => navigator.serviceWorker.controller?.scriptURL ?? ''), { timeout: 30_000 }).toContain(`r=${r.idB}`);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

/**
 * The update path (plan 105 "Release identity and updates"; Phase E "Update path", steps 1-7).
 * Release A is the build under test; release B is either
 * - **runner B**: the same site with a rebuilt runner whose Pyodide moves to another versioned
 *   folder (`/pyodide/0.27.8-b/`), so the book's content hash is unchanged but `release_id`
 *   differs, and the runner's Pyodide URLs differ, so serving the wrong release's file shows up as
 *   a failure rather than hiding behind equal bytes;
 * - **content B**: one page of the book changed (a new content hash), the runner unchanged.
 *
 * Steps (test names below):
 *   1-3. A downloads the book; B is deployed; an A page keeps checking code on A's caches (a fresh
 *        exercise worker boots) while B waits and the prompt shows; with a second A tab open,
 *        accepting asks to close it and B stays waiting.
 *   4.   The activation interval, paused after both origins activated, before the reload: the A
 *        page runs code and checks a fixtures item with zero network requests and no 404, its
 *        fresh workers loading A's worker script and A's Pyodide from the retained caches.
 *   5.   After the reload under B, cleanup deletes A's shell and Pyodide caches.
 *   6.   Failure at each step, forward-only recovery: the runner step times out (both stay on A);
 *        the site step fails after the runner activated (runner B, site A, still working; the retry
 *        completes); the reload fails after the site activated (the page works; the retry
 *        completes). A's caches exist throughout.
 *   7.   An unchanged content hash is re-confirmed without a refetch; a changed one downloads into a
 *        new cache and the old one is deleted only after confirmation; a download interrupted
 *        midway leaves A's book cache and record intact, and the partial cache is swept on the
 *        next worker start.
 * And the content review's cases (plan 105 "Content Review"):
 *   - B installed (and kept running) before a book was downloaded under A: once B is active it
 *     serves the book offline (it re-reads the records on activate, and on an offline miss);
 *   - a visitor who never downloads a book: the update's cleanup still deletes A's shell (and the
 *     runner's shell and Pyodide);
 *   - the runner's next release still installing (a slow Pyodide): "Preparing the update…", then
 *     the handshake, instead of a 10 s step that fails;
 *   - a site step that keeps failing is given up after 5 attempts: the page simply reloads.
 * Every request of every test, the service workers' own included, is a body-less GET for a file
 * of release A or B (helpers.ts `assertAllowlisted`).
 */
import { spawnSync } from 'node:child_process';
import { appendFileSync, cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import type { BrowserContext, Frame, Page } from '@playwright/test';
import { DIST, RUNNER_DIST, RUNNER_URL, SITE } from '../e2e/helpers/env';
import { allItems, fixturePairs, lookupProgram, type Found } from '../e2e/helpers/content';
import { check, setCode } from '../e2e/helpers/practice';
import { loadClient, runnerFrame, type Browserside } from '../e2e/helpers/runner';
import { computeReleaseId, writeRelease } from '../../deploy/release.mjs';
import { writeBookManifests } from '../scripts/offline-manifest';
import { assertAllowlisted, assertOfflineContract, axe, cacheNames, downloadBook, HOOKS, hookState, NetLog, offlineRecords, type Hooks } from './helpers';
import { expect, test, type Servers } from './servers';

const RUNNER = join(SITE, '..', 'runner');
const PYODIDE_A = 'pyodide-0.27.8';
const PYODIDE_B = 'pyodide-0.27.8-b';

interface Pair {
  site: string;
  runner: string;
}
interface Releases {
  work: string;
  book: string;
  A: Pair;
  B: Pair;
  idA: string;
  idB: string;
  hashA: string;
  hashB: string;
  roots: { site: string[]; runner: string[] };
}

const releaseJson = (site: string) =>
  JSON.parse(readFileSync(join(site, 'release.json'), 'utf-8')) as { release_id: string; books: Record<string, { content_hash: string; manifest: string }> };

/** Release A is the build; release B changes the runner only, or one page of `book`. */
function releases(book: string, change: 'runner' | 'content'): Releases {
  const scratch = join(SITE, 'node_modules', '.cache');
  mkdirSync(scratch, { recursive: true });
  const work = mkdtempSync(join(scratch, 'py4kids-update-'));
  const A = { site: join(work, 'site-a'), runner: join(work, 'runner-a') };
  const B = { site: join(work, 'site-b'), runner: join(work, 'runner-b') };
  cpSync(DIST, A.site, { recursive: true });
  cpSync(RUNNER_DIST, A.runner, { recursive: true });
  cpSync(DIST, B.site, { recursive: true });
  if (change === 'runner') {
    const built = spawnSync(process.execPath, [join(RUNNER, 'scripts', 'build.ts')], {
      cwd: RUNNER,
      env: { ...process.env, PY4KIDS_RUNNER_OUT: B.runner, PY4KIDS_TEST_HOOKS: '1', PY4KIDS_TEST_PYODIDE_DIR: '0.27.8-b' },
      encoding: 'utf-8',
    });
    expect(built.status, built.stderr).toBe(0);
  } else {
    cpSync(RUNNER_DIST, B.runner, { recursive: true });
    appendFileSync(join(B.site, book, 'index.html'), '\n<!-- release B: this book changed -->\n');
    writeBookManifests(B.site);
  }
  const idA = releaseJson(A.site).release_id;
  expect(computeReleaseId(A)).toBe(idA);
  const idB = writeRelease(B);
  expect(idB).not.toBe(idA);
  const hashA = releaseJson(A.site).books[book]!.content_hash;
  const hashB = releaseJson(B.site).books[book]!.content_hash;
  if (change === 'runner') expect(hashB).toBe(hashA);
  else expect(hashB).not.toBe(hashA);
  return { work, book, A, B, idA, idB, hashA, hashB, roots: { site: [A.site, B.site], runner: [A.runner, B.runner] } };
}

/** Under release A, download the book. */
async function downloadUnderA(page: Page, servers: Servers, r: Releases): Promise<void> {
  await servers.stop();
  await servers.start(r.A);
  await downloadBook(page, r.book);
}

/** Deploy release B and open `path`: the page loads under A, B installs and waits, the prompt shows. */
async function deployB(page: Page, servers: Servers, r: Releases, path: string) {
  await servers.stop();
  await servers.start(r.B);
  await page.goto(path);
  const update = page.locator('[data-pwa-update]');
  await expect(update).toBeVisible({ timeout: 60_000 });
  await expect(update).toContainText('A new version of py4kids is available.');
  expect(await siteController(page)).toContain(`r=${r.idA}`);
  return update;
}

const siteController = (page: Page) => page.evaluate(() => navigator.serviceWorker.controller?.scriptURL ?? '');
const runnerController = (page: Page) => runnerFrame(page).evaluate(() => navigator.serviceWorker.controller?.scriptURL ?? '');
const waitingOf = (target: Page | Frame) => target.evaluate(async () => (await navigator.serviceWorker.getRegistration('/'))?.waiting?.scriptURL ?? '');

/** Set the test hooks of the page (a PY4KIDS_TEST_HOOKS=1 build). */
function setHooks(page: Page, o: { pause?: string; fail?: [string, number][]; stepTimeoutMs?: number }): Promise<void> {
  return page.evaluate((o) => {
    const h = (window as unknown as { __py4kidsPwaTest: Hooks }).__py4kidsPwaTest;
    if (o.stepTimeoutMs) h.stepTimeoutMs = o.stepTimeoutMs;
    if (o.pause) h.pause(o.pause);
    for (const [step, n] of o.fail ?? []) h.fail(step, n);
  }, o);
}
const resume = (page: Page, point: string) => page.evaluate((p) => (window as unknown as { __py4kidsPwaTest: Hooks }).__py4kidsPwaTest.resume(p), point);

/** A fixtures item of `book` small enough that a fresh worker per case stays quick. */
function smallFixtures(book: string): Found {
  const found = allItems().find(
    (f) =>
      f.book === book &&
      f.item.check.kind === 'fixtures' &&
      f.item.check.cases.length >= 2 &&
      fixturePairs(f).reduce((n, c) => n + c.input.length + c.output.length, 0) < 20_000,
  );
  if (!found) throw new Error(`${book}: no small fixtures item`);
  return found;
}
const assertsItem = (book: string): Found => allItems().find((f) => f.book === book && f.item.check.kind === 'asserts' && f.item.kind === 'unit')!;
const itemOf = (page: Page, found: Found) => page.locator(`section.practice-item[data-item-key="${found.item.key}"]`);

/** Check an asserts item (`pass` fails it): one fresh exercise worker. */
async function checkAsserts(page: Page, found: Found): Promise<void> {
  const item = itemOf(page, found);
  await item.scrollIntoViewIfNeeded();
  await setCode(page, item, 'pass\n');
  expect(await check(item)).toMatch(/^Not yet/);
}

/** Run, then check, a fixtures item (a fresh worker per case), on the page as it is. */
async function runAndCheckFixtures(page: Page, found: Found): Promise<void> {
  const item = itemOf(page, found);
  await item.scrollIntoViewIfNeeded();
  const answer = lookupProgram(Object.fromEntries(fixturePairs(found).map((c) => [c.input, c.output])));
  await setCode(page, item, `print("run in the interval")\n`);
  await item.locator('[data-run-item]').click();
  await expect(item.locator('[data-result] .io-output code').first()).toContainText('run in the interval', { timeout: 90_000 });
  await setCode(page, item, answer);
  expect(await check(item)).toMatch(/^Passed/);
}

async function bothOnA(page: Page, r: Releases): Promise<void> {
  expect(await siteController(page)).toContain(`r=${r.idA}`);
  expect(await runnerController(page)).toContain(`r=${r.idA}`);
  expect(await waitingOf(page)).toContain(`r=${r.idB}`);
  expect(await waitingOf(runnerFrame(page))).toContain(`r=${r.idB}`);
}

async function aCachesKept(page: Page, r: Releases): Promise<void> {
  expect(await cacheNames(page), "the site keeps A's shell and book caches").toEqual(expect.arrayContaining([`shell-${r.idA}`, `book-${r.book}-${r.hashA}`]));
  expect(await cacheNames(runnerFrame(page)), "the runner keeps A's shell and Pyodide caches").toEqual(expect.arrayContaining([`shell-${r.idA}`, PYODIDE_A]));
}

/** Under B: A's shell and Pyodide caches are cleaned up on both origins; B's and the book's stay. */
async function cleanedUp(page: Page, r: Releases): Promise<void> {
  const runner = runnerFrame(page);
  await expect.poll(() => cacheNames(page), { timeout: 30_000 }).toEqual(expect.arrayContaining([`shell-${r.idB}`, `book-${r.book}-${r.hashB}`]));
  await expect.poll(async () => (await cacheNames(page)).includes(`shell-${r.idA}`), { timeout: 30_000 }).toBe(false);
  await expect.poll(() => cacheNames(runner), { timeout: 30_000 }).toEqual(expect.arrayContaining([`shell-${r.idB}`, PYODIDE_B]));
  await expect.poll(async () => (await cacheNames(runner)).filter((n) => n === `shell-${r.idA}` || n === PYODIDE_A), { timeout: 30_000 }).toEqual([]);
}

/** Stop every service worker of the context (Chromium DevTools): the next event starts them afresh. */
async function restartServiceWorkers(context: BrowserContext, page: Page): Promise<void> {
  const cdp = await context.newCDPSession(page);
  await cdp.send('ServiceWorker.enable');
  await cdp.send('ServiceWorker.stopAllWorkers');
  await cdp.detach();
}

const accept = (update: ReturnType<Page['locator']>) => update.getByRole('button', { name: 'Reload to update' });

/**
 * Keep every page's waiting site worker running (a message every 2 s), as a browser may: a worker
 * started while it installed keeps what it read then, which is what the stale-records case needs.
 */
async function keepWaitingWorkersAlive(context: BrowserContext): Promise<void> {
  await context.addInitScript(() => {
    setInterval(() => {
      void navigator.serviceWorker
        ?.getRegistration('/')
        .then((reg) => reg?.waiting?.postMessage({ type: 'keep-alive' }))
        .catch(() => {});
    }, 2000);
  });
}

const STATUS = '[data-offline-book] [data-offline-status]';

test('steps 1-3, 5, 7: the update waits (a fresh worker boots on A; a second tab blocks it), the handshake activates both origins, the unchanged book is re-confirmed without a refetch, cleanup', async ({
  page,
  context,
  servers,
}) => {
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'runner');
  const log = new NetLog(context);
  try {
    await downloadUnderA(page, servers, r);
    // 3. B deployed: an A page (loaded under A's worker) keeps checking code, booting a fresh
    // exercise worker from A's caches, while B waits on both origins and the prompt shows.
    const found = assertsItem(book);
    const update = await deployB(page, servers, r, found.page);
    await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
    await checkAsserts(page, found);
    await expect.poll(() => waitingOf(runnerFrame(page)), { timeout: 60_000 }).toContain(`r=${r.idB}`);
    await bothOnA(page, r);
    await axe(page, 'the update notice', '[data-pwa]');

    // A second A tab: accepting asks to close it, and B stays waiting.
    const second = await context.newPage();
    await second.goto('/');
    await accept(update).click();
    await expect(update).toContainText('Close your other py4kids tabs to update.');
    await expect(accept(update)).toBeEnabled();
    await bothOnA(page, r);
    await axe(page, 'the update notice asking to close the other tabs', '[data-pwa]');
    await second.close();

    // Accept again: runner, then site, then the reload; both origins on B.
    const mark = log.entries.length;
    await Promise.all([page.waitForEvent('load', { timeout: 60_000 }), accept(update).click()]);
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idB}`);

    // 7. The unchanged book is verified and re-stamped under B on both origins, with no refetch.
    await page.goto(`/${book}/`);
    await expect(page.locator('[data-offline-book] [data-offline-status]')).toHaveText('Available offline.', { timeout: 120_000 });
    expect(await runnerController(page)).toContain(`r=${r.idB}`);
    expect(await offlineRecords(page)).toEqual([expect.objectContaining({ book, content_hash: r.hashA, release_id: r.idB, runner_release_id: r.idB })]);
    expect(await offlineRecords(runnerFrame(page))).toEqual([expect.objectContaining({ book, content_hash: r.hashA, release_id: r.idB })]);
    const manifest = JSON.parse(readFileSync(join(r.B.site, releaseJson(r.B.site).books[book]!.manifest), 'utf-8')) as { files: { url: string }[] };
    // The book's own files (its folder), not the shared assets B's new shell cache holds too.
    const bookUrls = new Set(manifest.files.map((f) => f.url).filter((u) => u.startsWith(`/${book}/`)));
    expect(bookUrls.size).toBeGreaterThan(100);
    const refetched = log.entries.slice(mark).filter((e) => e.bySw && bookUrls.has(new URL(e.url).pathname));
    expect(refetched.map((e) => e.url), 'book files fetched again for an unchanged content hash').toEqual([]);

    // 5. Cleanup from B pages: A's shell and Pyodide caches go, the book cache stays.
    await cleanedUp(page, r);
    await log.settle();
    assertAllowlisted(log, r.roots);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test("steps 4-6: the activation interval (both origins on B before the reload): the A page runs code and checks a fixtures item from A's retained files, zero network, no 404; a failed reload is retried; cleanup", { tag: '@hooks' }, async ({
  page,
  context,
  servers,
}) => {
  test.skip(!HOOKS, 'needs a build with PY4KIDS_TEST_HOOKS=1');
  test.setTimeout(400_000);
  const book = 'usaco-bronze';
  const r = releases(book, 'runner');
  const log = new NetLog(context);
  const workers: string[] = [];
  page.on('worker', (w) => workers.push(w.url()));
  try {
    await downloadUnderA(page, servers, r);
    const found = smallFixtures(book);
    const update = await deployB(page, servers, r, found.page);
    await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
    await setHooks(page, { pause: 'after-site', fail: [['reload', 1]] });
    await accept(update).click();
    await expect.poll(() => hookState(page), { timeout: 60_000 }).toBe('paused:after-site');
    // Both origins activated B; this page is still release A's.
    expect(await siteController(page)).toContain(`r=${r.idB}`);
    expect(await runnerController(page)).toContain(`r=${r.idB}`);

    // The interval: run and check on the A page, recorded from here.
    log.reset();
    const before = workers.length;
    await runAndCheckFixtures(page, found);
    await log.settle();
    expect(assertOfflineContract(log), 'no update check: no document loaded').toEqual({});
    expect(log.entries.filter((e) => e.status !== null && e.status >= 400).map((e) => `${e.status} ${e.url}`), 'no 404').toEqual([]);
    // The fresh workers ran A's worker script and loaded A's Pyodide (B's are at other URLs).
    const fresh = workers.slice(before).filter((w) => w.includes('/assets/worker-'));
    expect(fresh.length, 'a fresh worker per run and per case').toBeGreaterThan(2);
    for (const w of fresh) {
      const path = new URL(w).pathname;
      expect(existsSync(join(r.A.runner, path)), `${path} is release A's`).toBe(true);
    }
    expect(log.entries.filter((e) => e.url.includes('/pyodide/0.27.8/') && e.outcome === 'served-by-sw').length).toBeGreaterThan(0);
    expect(log.entries.filter((e) => e.url.includes('/pyodide/0.27.8-b/')).map((e) => e.url)).toEqual([]);
    await aCachesKept(page, r);

    // Resume: the reload fails once ("finishing the update…") and is retried.
    const loaded = page.waitForEvent('load', { timeout: 60_000 });
    await resume(page, 'after-site');
    await expect(update).toContainText('Finishing the update…', { timeout: 30_000 });
    await loaded;
    expect(await siteController(page)).toContain(`r=${r.idB}`);
    // 5. Cleanup under B (the book is re-confirmed in the background, which loads the runner).
    await page.goto(`/${book}/`);
    await expect(page.locator('[data-offline-book] [data-offline-status]')).toHaveText('Available offline.', { timeout: 120_000 });
    await cleanedUp(page, r);
    await log.settle();
    assertAllowlisted(log, r.roots);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test("B installed and running before a book is downloaded under A: once B is active, the book's pages are served offline", async ({ page, context, servers }) => {
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'runner');
  await keepWaitingWorkersAlive(context);
  try {
    // A only, not downloaded: the site's worker A controls the book page.
    await servers.stop();
    await servers.start(r.A);
    await page.goto(`/${book}/`);
    await expect(page.locator(STATUS)).toHaveText('Not downloaded yet.', { timeout: 30_000 });
    await page.reload();
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idA}`);
    const lesson = (await page.locator('[data-contents] a.contents-title').first().getAttribute('href'))!;

    // Site B is deployed (the runner stays A): B installs, with no record to read, and waits.
    await servers.stop();
    await servers.start({ site: r.B.site, runner: r.A.runner });
    await page.goto(`/${book}/`);
    await expect.poll(() => waitingOf(page), { timeout: 60_000 }).toContain(`r=${r.idB}`);
    // Then the book is downloaded, by A's workers (still active).
    await expect(page.locator(STATUS)).toHaveText('Not downloaded yet.', { timeout: 30_000 });
    await page.locator('[data-offline-book]').getByRole('button', { name: 'Download this book' }).click();
    await expect(page.locator(STATUS)).toHaveText('Available offline.', { timeout: 300_000 });
    expect(await offlineRecords(page)).toEqual([expect.objectContaining({ book, release_id: r.idA })]);
    expect(await waitingOf(page)).toContain(`r=${r.idB}`);

    // B everywhere: the book page loads the runner (to confirm the book), which installs runner B.
    await servers.stop();
    await servers.start(r.B);
    await page.goto(`/${book}/`);
    await expect(page.locator(STATUS)).toHaveText('Available offline.', { timeout: 60_000 });
    await expect.poll(() => waitingOf(runnerFrame(page)), { timeout: 120_000 }).toContain(`r=${r.idB}`);
    // Accept on a page outside the book (a book page would re-download the book under B at once,
    // which re-reads the records anyway).
    await page.goto('/about/');
    const update = page.locator('[data-pwa-update]');
    await expect(update).toBeVisible({ timeout: 60_000 });
    await Promise.all([page.waitForEvent('load', { timeout: 120_000 }), accept(update).click()]);
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idB}`);

    // Offline, under B: the lesson comes from the book's confirmed cache, not the offline page.
    await servers.stop();
    await page.goto(lesson);
    await expect(page.locator('article.lesson')).toBeVisible({ timeout: 30_000 });
    await expect(page).toHaveURL(lesson);
    expect(await siteController(page)).toContain(`r=${r.idB}`);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test("a visitor who never downloads a book: after the update, cleanup deletes A's shell on the site and A's shell and Pyodide on the runner", async ({ page, servers }) => {
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'runner');
  try {
    // Under A: the site's worker controls the page, and the runner has run Python once.
    await servers.stop();
    await servers.start(r.A);
    await page.goto('/');
    await page.evaluate(async () => void (await navigator.serviceWorker.ready));
    await page.reload();
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idA}`);
    // Twice: the runner page that registered the runner's worker A is not controlled by it; the
    // second one is, and its Python boot caches A's Pyodide on first use.
    for (let i = 0; i < 2; i++) {
      if (i > 0) await page.reload();
      await loadClient(page);
      await page.evaluate(() => {
        const w = window as unknown as Browserside;
        w.runner = w.py4kidsRunnerClient.connectRunner(document.body).client;
        return w.runner.ping();
      });
    }
    await expect.poll(() => cacheNames(runnerFrame(page)), { timeout: 30_000 }).toEqual(expect.arrayContaining([`shell-${r.idA}`, PYODIDE_A]));
    expect(await cacheNames(page)).toContain(`shell-${r.idA}`);
    expect(await offlineRecords(page)).toEqual([]);

    // B: accept the update, from a page that never downloaded anything.
    const update = await deployB(page, servers, r, '/about/');
    await Promise.all([page.waitForEvent('load', { timeout: 120_000 }), accept(update).click()]);
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idB}`);
    // B's shell was never completed (nothing was downloaded), yet A's goes.
    await expect.poll(async () => (await cacheNames(page)).filter((n) => n.startsWith('shell-')), { timeout: 60_000 }).toEqual([`shell-${r.idB}`]);
    // The runner too, from a runner page of release B.
    await loadClient(page);
    await page.evaluate(() => {
      const w = window as unknown as Browserside;
      w.runner = w.py4kidsRunnerClient.connectRunner(document.body).client;
      return w.runner.ping();
    });
    const runner = runnerFrame(page);
    expect(await runner.evaluate(() => navigator.serviceWorker.controller?.scriptURL ?? '')).toContain(`r=${r.idB}`);
    await expect.poll(async () => (await cacheNames(runner)).filter((n) => n === `shell-${r.idA}` || n === PYODIDE_A), { timeout: 60_000 }).toEqual([]);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test('a hard reload (a page no worker controls) while B waits: with no window left on A, the browser activates B by itself, so no prompt and no handshake is needed', async ({ page, servers }) => {
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'runner');
  try {
    await servers.stop();
    await servers.start(r.A);
    await page.goto('/');
    await page.evaluate(async () => void (await navigator.serviceWorker.ready));
    await page.reload();
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idA}`);
    await servers.stop();
    await servers.start(r.B);
    await page.goto('/about/');
    await expect.poll(() => waitingOf(page), { timeout: 60_000 }).toContain(`r=${r.idB}`);
    const cdp = await page.context().newCDPSession(page);
    await Promise.all([page.waitForEvent('load'), cdp.send('Page.reload', { ignoreCache: true })]);
    expect(await siteController(page)).toBe('');
    const active = () => page.evaluate(async () => (await navigator.serviceWorker.getRegistration('/'))?.active?.scriptURL ?? '');
    await expect.poll(active, { timeout: 30_000 }).toContain(`r=${r.idB}`);
    await page.waitForTimeout(2000);
    await expect(page.locator('[data-pwa-update]')).toBeHidden();
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test("the runner's next release still installing (a slow Pyodide): \"Preparing the update…\", then the handshake completes", async ({ page, servers }) => {
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'runner');
  try {
    await downloadUnderA(page, servers, r);
    // B, with release B's Pyodide runtime 20 s slow: runner B, which must complete it before it
    // can activate (a book is downloaded), is still installing when the update is accepted.
    await servers.stop();
    await servers.start(r.B, (origin, path) => (origin === new URL(RUNNER_URL).origin && path === '/pyodide/0.27.8-b/pyodide.asm.wasm' ? 20_000 : 0));
    await page.goto('/about/');
    const update = page.locator('[data-pwa-update]');
    await expect(update).toBeVisible({ timeout: 60_000 });
    const loaded = page.waitForEvent('load', { timeout: 300_000 });
    await accept(update).click();
    await expect(update).toContainText('Preparing the update…', { timeout: 60_000 });
    await loaded;
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idB}`);
    await page.goto(`/${book}/`);
    await expect(page.locator(STATUS)).toHaveText('Available offline.', { timeout: 180_000 });
    expect(await runnerController(page)).toContain(`r=${r.idB}`);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test('step 6: a site step that keeps failing is given up after 5 attempts: the page simply reloads, still working, and B is offered again', { tag: '@hooks' }, async ({ page, servers }) => {
  test.skip(!HOOKS, 'needs a build with PY4KIDS_TEST_HOOKS=1');
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'runner');
  try {
    await servers.stop();
    await servers.start(r.A);
    await page.goto('/');
    await page.evaluate(async () => void (await navigator.serviceWorker.ready));
    await page.reload();
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idA}`);
    const update = await deployB(page, servers, r, '/about/');
    await setHooks(page, { stepTimeoutMs: 1000, fail: [['site', 1000]] });
    const loaded = page.waitForEvent('load', { timeout: 120_000 });
    await accept(update).click();
    await expect(update).toContainText('Finishing the update…', { timeout: 30_000 });
    await loaded;
    // The plain reload: the site never activated B (every attempt failed), so the page is A's,
    // working, and the update is offered again.
    expect(await siteController(page)).toContain(`r=${r.idA}`);
    expect(await waitingOf(page)).toContain(`r=${r.idB}`);
    await expect(page.locator('[data-pwa-update]')).toBeVisible({ timeout: 60_000 });
    expect(await hookState(page)).toBe('idle');
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test('step 6: a runner step that times out leaves both origins on A ("update failed — try again") and code still checks; a retry completes', { tag: '@hooks' }, async ({ page, context, servers }) => {
  test.skip(!HOOKS, 'needs a build with PY4KIDS_TEST_HOOKS=1');
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'runner');
  const log = new NetLog(context);
  try {
    await downloadUnderA(page, servers, r);
    const found = assertsItem(book);
    const update = await deployB(page, servers, r, found.page);
    await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
    await checkAsserts(page, found); // loads the runner iframe, which registers runner B
    await expect.poll(() => waitingOf(runnerFrame(page)), { timeout: 60_000 }).toContain(`r=${r.idB}`);
    // The runner page ignores the next prepare-activate: the site's real request times out in
    // its RunnerClient (the same timeout path as a runner that never answers).
    await runnerFrame(page).evaluate(() => {
      (window as unknown as { __py4kidsRunnerTest: { swallowPrepareActivate: number } }).__py4kidsRunnerTest.swallowPrepareActivate = 1;
    });
    await setHooks(page, { stepTimeoutMs: 2000 });
    await accept(update).click();
    await expect(update).toContainText('Update failed — try again.', { timeout: 30_000 });
    expect(await hookState(page)).toBe('failed');
    await bothOnA(page, r);
    await aCachesKept(page, r);
    await axe(page, 'the update notice after a failure', '[data-pwa]');
    await checkAsserts(page, found);
    // Try again: it completes.
    await Promise.all([page.waitForEvent('load', { timeout: 60_000 }), accept(update).click()]);
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idB}`);
    await log.settle();
    assertAllowlisted(log, r.roots);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test('step 6: a site step that fails after the runner activated leaves runner B and site A, still checking code; the retry completes', { tag: '@hooks' }, async ({ page, context, servers }) => {
  test.skip(!HOOKS, 'needs a build with PY4KIDS_TEST_HOOKS=1');
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'runner');
  const log = new NetLog(context);
  try {
    await downloadUnderA(page, servers, r);
    const found = assertsItem(book);
    const update = await deployB(page, servers, r, found.page);
    await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
    await setHooks(page, { stepTimeoutMs: 2000, pause: 'after-runner', fail: [['site', 1]] });
    await accept(update).click();
    await expect.poll(() => hookState(page), { timeout: 30_000 }).toBe('paused:after-runner');
    // The mixed state: runner on B, site still on A; the page keeps checking code.
    expect(await runnerController(page)).toContain(`r=${r.idB}`);
    expect(await siteController(page)).toContain(`r=${r.idA}`);
    await checkAsserts(page, found);
    await aCachesKept(page, r);
    const loaded = page.waitForEvent('load', { timeout: 60_000 });
    await resume(page, 'after-runner');
    await expect(update).toContainText('Finishing the update…', { timeout: 30_000 });
    await loaded;
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idB}`);
    await log.settle();
    assertAllowlisted(log, r.roots);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

test("step 7: content B — an interrupted re-download keeps A's book cache and record, and its partial cache is swept on the next worker start; the retry downloads into a new cache and deletes the old one only after confirmation", { tag: '@hooks' }, async ({
  page,
  context,
  servers,
}) => {
  test.skip(!HOOKS, 'needs a build with PY4KIDS_TEST_HOOKS=1');
  test.setTimeout(400_000);
  const book = 'python-projects';
  const r = releases(book, 'content');
  const log = new NetLog(context);
  // Every page of this context slows its downloads, set as its hooks are created (before the
  // book page starts its background re-download), so the test can act mid-download.
  await context.addInitScript(() => {
    let created: { downloadDelayMs: number } | undefined;
    Object.defineProperty(window, '__py4kidsPwaTest', {
      configurable: true,
      get: () => created,
      set: (h: { downloadDelayMs: number }) => {
        h.downloadDelayMs = 250;
        created = h;
      },
    });
  });
  const panel = page.locator('[data-offline-book]');
  const status = panel.locator('[data-offline-status]');
  const progressed = async () => Number((await panel.locator('[data-offline-progress]').getAttribute('value')) ?? 0);
  const bookCaches = async () => (await cacheNames(page)).filter((n) => n.startsWith(`book-${book}-`)).sort();
  try {
    await downloadUnderA(page, servers, r);
    const update = await deployB(page, servers, r, `/${book}/`);
    await Promise.all([page.waitForEvent('load', { timeout: 60_000 }), accept(update).click()]);
    await expect.poll(() => siteController(page), { timeout: 30_000 }).toContain(`r=${r.idB}`);
    // Under B the book reads "Updating…" and downloads again, into book-<book>-<hash B>.
    await expect(status).toHaveText('Updating…', { timeout: 30_000 });
    await expect.poll(progressed, { timeout: 60_000 }).toBeGreaterThan(0);
    await expect.poll(() => cacheNames(page), { timeout: 30_000 }).toContain(`book-${book}-${r.hashB}`);
    // Mid-download: the old cache and record are still there.
    expect(await cacheNames(page)).toContain(`book-${book}-${r.hashA}`);
    expect(await offlineRecords(page)).toEqual([expect.objectContaining({ content_hash: r.hashA, release_id: r.idA })]);

    // Interrupted: both servers stop during the chunks.
    await servers.stop();
    await expect(status).toHaveText(/^The download did not finish/, { timeout: 60_000 });
    expect(await offlineRecords(page)).toEqual([expect.objectContaining({ content_hash: r.hashA, release_id: r.idA })]);
    expect(await bookCaches()).toEqual([`book-${book}-${r.hashA}`, `book-${book}-${r.hashB}`].sort());
    // The next worker start sweeps the partial cache (no record names it); A's book stays and is
    // still readable offline. (The worker is woken on a page outside the book: a book page would
    // try the re-download again at once, and with the servers down leave a new partial cache.)
    await restartServiceWorkers(context, page);
    await page.goto('/about/');
    await expect(page.locator('h1')).toBeVisible();
    await expect.poll(bookCaches, { timeout: 30_000 }).toEqual([`book-${book}-${r.hashA}`]);
    expect(await offlineRecords(page)).toEqual([expect.objectContaining({ content_hash: r.hashA, release_id: r.idA })]);
    await page.goto(`/${book}/`);
    await expect(page.locator('h1')).toBeVisible();
    const lesson = await page.locator('[data-contents] a.contents-title').first().getAttribute('href');
    await page.goto(lesson!);
    await expect(page.locator('main h1')).toBeVisible();

    // Back online: the re-download runs again; the old cache stays until the new one is confirmed.
    await servers.start(r.B);
    await page.goto(`/${book}/`);
    await expect.poll(progressed, { timeout: 60_000 }).toBeGreaterThan(0);
    expect(await bookCaches()).toContain(`book-${book}-${r.hashA}`);
    await expect(status).toHaveText('Available offline.', { timeout: 180_000 });
    await expect.poll(bookCaches, { timeout: 30_000 }).toEqual([`book-${book}-${r.hashB}`]);
    expect(await offlineRecords(page)).toEqual([expect.objectContaining({ content_hash: r.hashB, release_id: r.idB, runner_release_id: r.idB })]);
    expect(await offlineRecords(runnerFrame(page))).toEqual([expect.objectContaining({ content_hash: r.hashB, release_id: r.idB })]);
    await log.settle();
    assertAllowlisted(log, r.roots);
  } finally {
    rmSync(r.work, { recursive: true, force: true });
  }
});

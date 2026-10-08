/**
 * "Export my progress" and "Import progress" on the catalog page (plan 105 Phase C):
 * - export -> clear the browser's storage -> import restores the mastery map and the resume link,
 *   and a second import of the same file changes nothing;
 * - each way of saving: the File System Access picker (saved, cancelled) and the download link;
 * - a malformed, unknown-schema or oversized file is refused with a message and the store is left
 *   as it was;
 * - axe passes on the page with the new UI, in both colour schemes, with a message showing;
 * - no CSP violation, no page error, and nothing leaves the site's origin.
 */
import { readFileSync } from 'node:fs';
import AxeBuilder from '@axe-core/playwright';
import type { Page } from '@playwright/test';
import { watchCsp } from './helpers/csp';
import { assertNoNetwork, expect, test } from './helpers/net';
import { deckOf, stores } from './helpers/site';

const BOOK = 'python-projects';
const SLIDES = `/${BOOK}/unit-03-turtle-art-studio/slides/`;
const WCAG_AA = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];

/** Force the download-link path: no File System Access picker, no Web Share. */
async function downloadOnly(page: Page): Promise<void> {
  await page.addInitScript(() => {
    Object.defineProperty(window, 'showSaveFilePicker', { value: undefined, configurable: true });
    Object.defineProperty(navigator, 'share', { value: undefined, configurable: true });
    Object.defineProperty(navigator, 'canShare', { value: undefined, configurable: true });
  });
}

/** Each concept's percentage on the book page, once the mastery island has filled them. */
async function mastery(page: Page, expectAny: boolean): Promise<string[]> {
  await page.goto(`/${BOOK}/`);
  const pcts = page.locator('[data-mastery] [data-concept] [data-mastery-pct]');
  if (expectAny) await expect(pcts.filter({ hasNotText: /^0%$/ }).first()).toBeAttached();
  else await page.waitForLoadState('networkidle');
  return pcts.allTextContents();
}

/** Puts the first `n` cards of the deck in box 5 (known), as if answered over several weeks. */
async function seedCards(page: Page, n: number): Promise<void> {
  const keys = deckOf(BOOK).slice(0, n).map((c) => c.key);
  await page.evaluate(
    ({ keys, book }) =>
      new Promise<void>((resolve, reject) => {
        const open = indexedDB.open('py4kids');
        open.onerror = () => reject(open.error);
        open.onsuccess = () => {
          const db = open.result;
          const tx = db.transaction('cards', 'readwrite');
          keys.forEach((key, i) =>
            tx.objectStore('cards').put({ key, book, box: 5, due: '2026-12-01T00:00:00.000Z', updated_at: `2026-10-0${1 + (i % 5)}T08:00:00.000Z` }),
          );
          tx.oncomplete = () => {
            db.close();
            resolve();
          };
          tx.onerror = () => reject(tx.error);
        };
      }),
    { keys, book: BOOK },
  );
}

async function clearStorage(page: Page): Promise<void> {
  await page.evaluate(
    () =>
      new Promise<void>((resolve, reject) => {
        const req = indexedDB.deleteDatabase('py4kids');
        req.onsuccess = () => resolve();
        req.onerror = () => reject(req.error);
        req.onblocked = () => reject(new Error('deleteDatabase blocked'));
      }),
  );
}

const status = (page: Page) => page.locator('[data-transfer-status]');

/** The whole store, sorted, as text. */
async function dump(page: Page): Promise<string> {
  const all = await stores(page);
  const out: Record<string, unknown[]> = {};
  for (const name of Object.keys(all).sort()) out[name] = all[name]!.map((r) => JSON.stringify(r)).sort();
  return JSON.stringify(out);
}

test('export, clear storage, import: the mastery map and the resume link come back', async ({ page, context, recorder }) => {
  const csp = await watchCsp(context);
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(`${page.url()}: ${error.message}`));
  await downloadOnly(page);

  // Real progress: the slide player writes slide events and the resume position.
  await page.goto(SLIDES);
  await page.locator('.deck.is-live').waitFor();
  await expect.poll(async () => (await stores(page)).resume?.find((r) => r.book === BOOK)?.href).toBeTruthy();
  await seedCards(page, 12);
  const before = await mastery(page, true);
  expect(before.some((p) => p !== '0%')).toBe(true);

  await page.goto('/');
  const resume = page.locator(`[data-resume-book="${BOOK}"]`);
  await expect(resume).toBeVisible();
  const resumeHref = await resume.locator('a').getAttribute('href');
  const saved = await stores(page);

  // Export by keyboard: the download link (no picker, no share sheet here).
  const button = page.getByRole('button', { name: 'Export my progress' });
  await button.focus();
  const downloading = page.waitForEvent('download');
  await page.keyboard.press('Enter');
  const download = await downloading;
  expect(download.suggestedFilename()).toMatch(/^py4kids-progress-\d{4}-\d{2}-\d{2}\.json$/);
  await expect(status(page)).toHaveText(/^Export finished: your progress was downloaded as py4kids-progress-/);
  const path = await download.path();
  const file = JSON.parse(readFileSync(path, 'utf-8')) as Record<string, unknown[] | string>;
  expect(file.schema).toBe('py4kids/progress-export/1.0.0');
  expect('attempts' in file).toBe(false);
  expect((file.cards as unknown[]).length).toBe(12);
  expect((file.events as unknown[]).length).toBe(saved.events!.length);
  expect((file.resume as unknown[]).length).toBe(saved.resume!.length);

  // Clear the storage: the map is back to 0% and there is no "Continue" link.
  await clearStorage(page);
  await page.reload();
  await expect(resume).toBeHidden();
  const empty = await stores(page);
  expect([empty.events?.length, empty.cards?.length, empty.resume?.length]).toEqual([0, 0, 0]);
  expect((await mastery(page, false)).every((p) => p === '0%')).toBe(true);

  // Import (the file input, by its label): the resume link returns at once.
  await page.goto('/');
  await page.getByLabel('Import progress from a file').setInputFiles(path);
  await expect(status(page)).toHaveText(/^Import finished: brought back \d+ results?, 12 quiz cards and 1 reading place\.$/);
  await expect(status(page)).toHaveAttribute('data-state', 'ok');
  await expect(resume).toBeVisible();
  expect(await resume.locator('a').getAttribute('href')).toBe(resumeHref);
  const restored = await dump(page);
  expect(restored).toBe(JSON.stringify(Object.fromEntries(Object.entries(saved).sort().map(([k, v]) => [k, v.map((r) => JSON.stringify(r)).sort()]))));

  // The same file again changes nothing.
  await page.getByLabel('Import progress from a file').setInputFiles(path);
  await expect(status(page)).toHaveText('Import finished: this device already had everything in that file, so nothing changed.');
  expect(await dump(page)).toBe(restored);

  expect(await mastery(page, true)).toEqual(before);

  expect(errors).toEqual([]);
  expect(csp.violations).toEqual([]);
  expect(csp.console).toEqual([]);
  // The download is a blob: URL of the page itself; everything else is a file in dist/.
  const blobs = recorder.requests.filter((r) => r.url.startsWith('blob:'));
  recorder.requests.splice(0, recorder.requests.length, ...recorder.requests.filter((r) => !r.url.startsWith('blob:')));
  for (const b of blobs) expect(b.method).toBe('GET');
  assertNoNetwork(recorder, []);
});

test('export through the save-file picker, with code attempts only when ticked; cancelling saves nothing', async ({ page }) => {
  await page.addInitScript(() => {
    const w = window as unknown as { __saved: string[]; __cancel: boolean; showSaveFilePicker: unknown };
    w.__saved = [];
    w.__cancel = false;
    w.showSaveFilePicker = async (options: { suggestedName: string }) => {
      if (w.__cancel) throw new DOMException('The user aborted a request.', 'AbortError');
      return {
        createWritable: async () => ({
          write: async (blob: Blob) => {
            w.__saved.push(`${options.suggestedName}\n${await blob.text()}`);
          },
          close: async () => undefined,
        }),
      };
    };
  });
  await page.goto(SLIDES);
  await page.locator('.deck.is-live').waitFor();
  await page.goto('/');
  // An attempt in the store, which only the ticked export carries.
  await page.evaluate(
    () =>
      new Promise<void>((resolve, reject) => {
        const open = indexedDB.open('py4kids');
        open.onsuccess = () => {
          const tx = open.result.transaction('attempts', 'readwrite');
          tx.objectStore('attempts').put({
            attempt_id: '00000000-0000-4000-8000-000000000001',
            book: 'python-projects',
            item_key: 'python-projects/unit-03-turtle-art-studio/exercises/e1',
            kind: 'check',
            code: 'print("my code")',
            result: 'pass',
            timestamp: '2026-10-01T08:00:00.000Z',
          });
          tx.oncomplete = () => {
            open.result.close();
            resolve();
          };
          tx.onerror = () => reject(tx.error);
        };
        open.onerror = () => reject(open.error);
      }),
  );

  const button = page.getByRole('button', { name: 'Export my progress' });
  await button.click();
  await expect(status(page)).toHaveText('Export finished: your progress was saved.');
  let saved = await page.evaluate(() => (window as unknown as { __saved: string[] }).__saved);
  expect(saved).toHaveLength(1);
  expect(saved[0]).toMatch(/^py4kids-progress-\d{4}-\d{2}-\d{2}\.json\n/);
  expect(saved[0]).not.toContain('my code');

  // Tick "Export my code attempts too" by keyboard.
  const tick = page.getByLabel('Export my code attempts too');
  await tick.focus();
  await page.keyboard.press('Space');
  await expect(tick).toBeChecked();
  await button.click();
  await expect(status(page)).toHaveText('Export finished: your progress and code attempts were saved.');
  saved = await page.evaluate(() => (window as unknown as { __saved: string[] }).__saved);
  expect(saved).toHaveLength(2);
  expect(saved[1]).toMatch(/^py4kids-progress-and-code-/);
  const data = JSON.parse(saved[1]!.slice(saved[1]!.indexOf('\n') + 1)) as { attempts: { code: string }[] };
  expect(data.attempts.map((a) => a.code)).toEqual(['print("my code")']);

  await page.evaluate(() => ((window as unknown as { __cancel: boolean }).__cancel = true));
  await button.click();
  await expect(status(page)).toHaveText('Export cancelled: no file was saved.');
  expect(await page.evaluate(() => (window as unknown as { __saved: string[] }).__saved.length)).toBe(2);
});

test('a malformed, unknown-schema or oversized file is refused with a message, and nothing changes', async ({ page }) => {
  await page.goto(SLIDES);
  await page.locator('.deck.is-live').waitFor();
  await expect.poll(async () => (await stores(page)).resume?.length).toBe(1);
  await page.goto('/');
  const before = await dump(page);
  const input = page.getByLabel('Import progress from a file');
  const cases: [string, Buffer, RegExp][] = [
    ['broken.json', Buffer.from('{"schema": "py4kids/progress-export/1.0.0", "events": ['), /^That file is not a py4kids progress file, or it got damaged\./],
    ['other.json', Buffer.from(JSON.stringify({ hello: 'world' })), /^That file is not a py4kids progress file\./],
    [
      'future.json',
      Buffer.from(JSON.stringify({ schema: 'py4kids/progress-export/9.0.0', exported_at: '2030-01-01T00:00:00Z', events: [], cards: [], resume: [] })),
      /^That progress file comes from a different version of py4kids/,
    ],
    [
      'edited.json',
      Buffer.from(
        JSON.stringify({
          schema: 'py4kids/progress-export/1.0.0',
          exported_at: '2026-10-01T00:00:00Z',
          events: [],
          cards: [],
          resume: [{ book: 'acsl', entry: 'x', href: 'javascript:alert(1)', title: 'x', updated_at: '2026-10-01T00:00:00Z' }],
        }),
      ),
      /^That progress file has something wrong inside it/,
    ],
    ['huge.json', Buffer.alloc(20 * 1024 * 1024 + 1, 0x20), /^That file is too big to be a py4kids progress file \(the limit is 20 MB\)\./],
  ];
  for (const [name, buffer, message] of cases) {
    await input.setInputFiles({ name, mimeType: 'application/json', buffer });
    await expect(status(page), name).toHaveText(message);
    await expect(status(page)).toHaveText(/Nothing was changed\.$/);
    await expect(status(page)).toHaveAttribute('data-state', 'error');
    expect(await dump(page), name).toBe(before);
  }
});

for (const scheme of ['light', 'dark'] as const) {
  test(`axe on the catalog with the export and import controls (${scheme})`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: scheme });
    await page.goto('/');
    await page.getByLabel('Import progress from a file').setInputFiles({ name: 'x.json', mimeType: 'application/json', buffer: Buffer.from('nope') });
    await expect(status(page)).toHaveAttribute('data-state', 'error');
    await expect(status(page)).toHaveAttribute('role', 'status');
    const results = await new AxeBuilder({ page }).include('[data-transfer]').withTags([...WCAG_AA, 'best-practice']).analyze();
    const blocking = results.violations.filter((v) => v.tags.some((t) => WCAG_AA.includes(t)));
    expect(blocking.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(' ')).join(' | ')}`)).toEqual([]);
    expect(results.passes.length).toBeGreaterThan(0);
  });
}

/**
 * The practice pager (plan 106, Phase C): one item at a time, Previous / Next, the grouped jump
 * list, its statuses, history, focus, the hidden-item announcements, groups and kickers, resume,
 * search, print, the layouts, no JavaScript, axe and the CSP. Real pages and items are picked from
 * the exported bundles; a check projection is served with the hash of a known output where a test
 * needs a pass (as checks.spec.ts does).
 */
import AxeBuilder from '@axe-core/playwright';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { expect, test, type Page, type Route } from '@playwright/test';
import type { ClientCheck } from '../src/lib/check-model';
import { answerHash, type NormaliseOptions } from '../src/lib/normalise';
import { allItems, CONTENT, type Found } from './helpers/content';
import { watchCsp } from './helpers/csp';
import { RUNNER_URL } from './helpers/env';
import { setCode } from './helpers/practice';
import { search, stores } from './helpers/site';

test.describe.configure({ mode: 'parallel' });

const WCAG_AA = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'];

/** The items of one practice page, in order. */
const itemsOf = (book: string, entry: string): Found[] => allItems().filter((f) => f.book === book && f.entry === entry);

/** python-concepts unit 01: 20 items, the first five expected-output items without files. */
const U01 = itemsOf('python-concepts', 'unit-01-output-and-variables');
const U01_PAGE = U01[0]!.page;
/** python-projects unit 03: 12 items (the "4 of 12" page). */
const U03 = itemsOf('python-projects', 'unit-03-turtle-art-studio');
/** python-concepts unit 10: 37 items (the longest list). */
const U10 = itemsOf('python-concepts', 'unit-10-lists');

const step = (page: Page, anchor: string) => page.locator(`[data-step][data-anchor="${anchor}"]`);
const visibleSteps = (page: Page) => page.locator('[data-step]:visible');
const jump = (page: Page, anchor: string) => page.locator(`a[data-jump="${anchor}"]`);
const status = (page: Page, anchor: string) => jump(page, anchor).locator('[data-jump-status]');
const live = (page: Page) => page.locator('[data-pager-live]');

async function ready(page: Page): Promise<void> {
  await page.locator('[data-practice-layout][data-pager-ready][data-statuses-ready]').waitFor({ state: 'attached' });
  await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
}

/**
 * Load `path` as a new document. (A goto that changes only the hash of the page already open is a
 * same-document navigation, a `hashchange`, not a load: leave the page first.)
 */
async function openPage(page: Page, path: string): Promise<void> {
  if (page.url() !== 'about:blank') await page.goto('about:blank');
  await page.goto(path);
  await ready(page);
}

async function expectShown(page: Page, anchor: string): Promise<void> {
  await expect(visibleSteps(page)).toHaveCount(1);
  await expect(step(page, anchor)).toBeVisible();
}

/**
 * Serve an expected-output item's projection with the hash of `output` (so a program printing it
 * passes), optionally held until `gate` resolves (to keep the check running).
 */
async function passWith(page: Page, found: Found, output: string, gate?: Promise<void>): Promise<void> {
  const format = (found.item.check as { answer_format: NormaliseOptions }).answer_format;
  const hash = await answerHash(found.item.key, output, { case: format.case });
  await page.route(`**${found.page}check/${found.anchor}.json`, async (route: Route) => {
    if (gate) await gate;
    const response = await route.fetch();
    const check = (await response.json()) as ClientCheck;
    await route.fulfill({ response, json: { ...check, hash } });
  });
}

/** A gate a route waits on, and its opener. */
function gate(): { wait: Promise<void>; open: () => void } {
  let open!: () => void;
  const wait = new Promise<void>((resolve) => (open = resolve));
  return { wait, open };
}

/** Press Check on an item without waiting for its verdict. */
const pressCheck = (page: Page, found: Found) => step(page, found.anchor).locator('[data-check-item]').click();

/** Wait until the item's Check button is back (the check ended). */
const checkDone = (page: Page, found: Found, timeout = 90_000) =>
  expect(step(page, found.anchor).locator('[data-check-item]')).toBeEnabled({ timeout });

/** Makes writes to the open IndexedDB `events` store throw once `window.__py4kidsFailEvents` is set. */
async function failEventWrites(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const proto = IDBObjectStore.prototype;
    for (const name of ['put', 'add'] as const) {
      const original = proto[name];
      proto[name] = function (this: IDBObjectStore, ...args: Parameters<IDBObjectStore['put']>) {
        if ((window as unknown as { __py4kidsFailEvents?: boolean }).__py4kidsFailEvents && this.name === 'events') {
          throw new DOMException('the test rejects this write', 'UnknownError');
        }
        return original.apply(this, args);
      } as IDBObjectStore['put'];
    }
  });
}
const startFailing = (page: Page) => page.evaluate(() => ((window as unknown as { __py4kidsFailEvents: boolean }).__py4kidsFailEvents = true));

const NOT_SAVED = 'Your result could not be saved on this device, so it will not count toward your progress.';

// ---------------------------------------------------------------------------------------------
// Showing one item, deep links

test('one item is visible on load (the first); #<anchor> and #<anchor>-h deep links show that item', async ({ page }) => {
  await openPage(page, U01_PAGE);
  await expectShown(page, U01[0]!.anchor);
  await expect(page.locator('[data-pager-nav]')).toBeVisible();
  await expect(page.locator('[data-step]')).toHaveCount(U01.length);
  await expect(jump(page, U01[0]!.anchor)).toHaveAttribute('aria-current', 'step');
  await expect(page.locator('[data-pager-prev]')).toBeDisabled();
  await expect(page.locator('[data-pager-next]')).toHaveText(`Next: ${U01[1]!.item.label}`);

  await openPage(page, `${U01_PAGE}#${U01[6]!.anchor}`);
  await expectShown(page, U01[6]!.anchor);
  await openPage(page, `${U01_PAGE}#${U01[8]!.anchor}-h`);
  await expectShown(page, U01[8]!.anchor);
  await expect(page.locator(`#${U01[8]!.anchor}-h`)).toBeInViewport();
  // An unknown hash at load shows the first item.
  await openPage(page, `${U01_PAGE}#no-such-item`);
  await expectShown(page, U01[0]!.anchor);
  // The last item shows the outro and has no Next.
  await openPage(page, `${U01_PAGE}#${U01.at(-1)!.anchor}`);
  await expect(page.locator('[data-pager-next]')).toBeDisabled();
  await expect(page.locator('[data-pager-prev]')).toHaveText(`Previous: ${U01.at(-2)!.item.label}`);
});

// ---------------------------------------------------------------------------------------------
// History

test('a jump-list choice pushes history (Back, Forward); Previous / Next replace it', async ({ page }) => {
  const [a, b] = [U01[2]!, U01[4]!];
  await openPage(page, U01_PAGE);
  await jump(page, a.anchor).click();
  await expect(page).toHaveURL(new RegExp(`#${a.anchor}$`));
  await expectShown(page, a.anchor);
  await jump(page, b.anchor).click();
  await expectShown(page, b.anchor);
  await page.goBack();
  await expectShown(page, a.anchor);
  await page.goForward();
  await expectShown(page, b.anchor);
  // Next ×3 replaces the entry: one Back returns to the last list choice.
  for (let i = 0; i < 3; i++) await page.locator('[data-pager-next]').click();
  await expectShown(page, U01[7]!.anchor);
  await expect(page).toHaveURL(new RegExp(`#${U01[7]!.anchor}$`));
  await page.goBack();
  await expectShown(page, a.anchor);
});

test('after Next ×3 from a fresh visit, one Back leaves the page', async ({ page }) => {
  await page.goto('/about/');
  await page.goto(U01_PAGE);
  await ready(page);
  for (let i = 0; i < 3; i++) await page.locator('[data-pager-next]').click();
  await expectShown(page, U01[3]!.anchor);
  await page.goBack();
  await expect(page).toHaveURL(/\/about\/$/);
});

// ---------------------------------------------------------------------------------------------
// Focus

test('focus moves to the item heading on a control or a list choice; the heading reads "4 of 12"', async ({ page }) => {
  expect(U03.length).toBe(12);
  await openPage(page, U03[0]!.page);
  await jump(page, U03[2]!.anchor).click();
  await expectShown(page, U03[2]!.anchor);
  await expect(page.locator(`#${U03[2]!.anchor}-h`)).toBeFocused();
  await page.locator('[data-pager-next]').click();
  const heading = page.locator(`#${U03[3]!.anchor}-h`);
  await expect(heading).toBeFocused();
  await expect(heading.locator('.step-pos')).toHaveText('4 of 12');
  await expect(heading).toHaveAccessibleName(new RegExp(`^${U03[3]!.item.label}.* 4 of 12$`));
  await page.locator('[data-pager-prev]').click();
  await expect(page.locator(`#${U03[2]!.anchor}-h`)).toBeFocused();
  // Keyboard: the list link, then Enter.
  await jump(page, U03[6]!.anchor).focus();
  await page.keyboard.press('Enter');
  await expect(page.locator(`#${U03[6]!.anchor}-h`)).toBeFocused();
  // At the first item Previous is disabled, never removed.
  await openPage(page, U03[0]!.page);
  await page.locator('[data-pager-next]').focus();
  await page.keyboard.press('Enter');
  await page.locator('[data-pager-prev]').focus();
  await page.keyboard.press('Enter');
  await expect(page.locator(`#${U03[0]!.anchor}-h`)).toBeFocused();
  await expect(page.locator('[data-pager-prev]')).toBeDisabled();
});

// ---------------------------------------------------------------------------------------------
// Checks, statuses, announcements

test('a Check passed on item 2 survives a jump to item 5 and back; the list shows ✓, kept after a failed re-check', async ({ page }) => {
  const [two, five] = [U01[1]!, U01[4]!];
  await passWith(page, two, 'pager pass\n');
  await openPage(page, `${U01_PAGE}#${two.anchor}`);
  const item = step(page, two.anchor);
  const code = 'print("pager pass")\n';
  await setCode(page, item, code);
  await pressCheck(page, two);
  await checkDone(page, two);
  await expect(item.locator('[data-result] .verdict')).toHaveText('Passed.');
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'passed');
  await expect(status(page, two.anchor)).toContainText('passed');
  await jump(page, five.anchor).click();
  await expectShown(page, five.anchor);
  await jump(page, two.anchor).click();
  await expectShown(page, two.anchor);
  await expect(item.locator('.cm-content')).toHaveText(code.trim());
  await expect(item.locator('[data-result] .verdict')).toHaveText('Passed.');
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'passed');
  // A failed re-check keeps the ✓ (any recorded pass counts).
  await setCode(page, item, 'print("something else")\n');
  await pressCheck(page, two);
  await checkDone(page, two);
  await expect(item.locator('[data-result] .verdict')).toHaveText(/^Not yet/);
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'passed');
  await expect(status(page, two.anchor).locator('[aria-hidden="true"]')).toHaveText('✓');
});

test('a check started on item 2, then a jump to item 5: "checking…" in the list, then the live region announces it', async ({ page }) => {
  const [two, five] = [U01[1]!, U01[4]!];
  const held = gate();
  await passWith(page, two, 'held pass\n', held.wait);
  await openPage(page, `${U01_PAGE}#${two.anchor}`);
  await setCode(page, step(page, two.anchor), 'print("held pass")\n');
  await pressCheck(page, two);
  await jump(page, five.anchor).click();
  await expectShown(page, five.anchor);
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'checking');
  await expect(status(page, two.anchor)).toContainText('checking…');
  held.open();
  await expect(live(page)).toHaveText(`${two.item.label}: Passed`, { timeout: 90_000 });
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'passed');
  // Item 5 is still the one shown; item 2's result is there for when the student returns.
  await expectShown(page, five.anchor);
  await expect(step(page, two.anchor).locator('[data-result] .verdict')).toHaveText('Passed.');
});

test('Stop pressed on item 2 after a jump away and back: "checking…" clears and the outcome is said', async ({ page }) => {
  const [two, five] = [U01[1]!, U01[4]!];
  await page.route(`**${two.page}check/${two.anchor}.json`, async (route) => {
    const response = await route.fetch();
    await route.fulfill({ response, json: { ...((await response.json()) as ClientCheck), budget_ms: 60_000 } });
  });
  await openPage(page, `${U01_PAGE}#${two.anchor}`);
  const item = step(page, two.anchor);
  await setCode(page, item, 'while True:\n    pass\n');
  await pressCheck(page, two);
  // The program is running (the island says "Checking…" just before it starts the run).
  await expect(item.locator('[data-result] .check-status')).toHaveText('Checking…', { timeout: 60_000 });
  await jump(page, five.anchor).click();
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'checking');
  await jump(page, two.anchor).click();
  await expectShown(page, two.anchor);
  await item.locator('[data-stop]').click();
  await checkDone(page, two, 30_000);
  await expect(item.locator('[data-result]')).toHaveText('Stopped before the check finished.');
  await expect(status(page, two.anchor)).not.toHaveAttribute('data-state', 'checking');
  await expect(status(page, two.anchor)).not.toContainText('checking…');
});

test('a runner failure (its origin blocked) on a hidden item: "checking…" clears and "Could not check" is announced', async ({ page }) => {
  test.setTimeout(180_000);
  const [two, five] = [U01[1]!, U01[4]!];
  await page.route(`${RUNNER_URL}/**`, (route) => route.abort('blockedbyclient'));
  await openPage(page, `${U01_PAGE}#${two.anchor}`);
  await pressCheck(page, two);
  await jump(page, five.anchor).click();
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'checking');
  await expect(live(page)).toHaveText(`${two.item.label}: Could not check`, { timeout: 150_000 });
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'none');
  await expect(step(page, two.anchor).locator('.runner-unavailable')).toHaveCount(1);
});

test('the skip link on item 5 (#main) keeps item 5 shown', async ({ page }) => {
  await openPage(page, `${U01_PAGE}#${U01[4]!.anchor}`);
  await page.locator('.skip-link').focus();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/#main$/);
  await expectShown(page, U01[4]!.anchor);
  // Next still works from there.
  await page.locator('[data-pager-next]').click();
  await expectShown(page, U01[5]!.anchor);
});

// ---------------------------------------------------------------------------------------------
// Save failures

test('a passing check whose save fails: no ✓, the not-saved note on the item, and "Passed, but not saved" when hidden', async ({ page }) => {
  const [two, three, five] = [U01[1]!, U01[2]!, U01[4]!];
  await failEventWrites(page);
  await passWith(page, two, 'unsaved pass\n');
  const held = gate();
  await passWith(page, three, 'unsaved pass\n', held.wait);
  await openPage(page, `${U01_PAGE}#${two.anchor}`);
  await startFailing(page);
  // Shown item: the note, no ✓.
  const item = step(page, two.anchor);
  await setCode(page, item, 'print("unsaved pass")\n');
  await pressCheck(page, two);
  await checkDone(page, two);
  await expect(item.locator('[data-result] .verdict')).toHaveText('Passed.');
  await expect(item.locator('[data-result] .not-saved')).toHaveText(NOT_SAVED);
  await expect(status(page, two.anchor)).toHaveAttribute('data-state', 'none');
  // Hidden item: the announcement says it was not saved.
  await jump(page, three.anchor).click();
  await setCode(page, step(page, three.anchor), 'print("unsaved pass")\n');
  await pressCheck(page, three);
  await jump(page, five.anchor).click();
  await expect(status(page, three.anchor)).toHaveAttribute('data-state', 'checking');
  held.open();
  await expect(live(page)).toHaveText(`${three.item.label}: Passed, but not saved`, { timeout: 90_000 });
  await expect(status(page, three.anchor)).toHaveAttribute('data-state', 'none');
  await expect(step(page, three.anchor).locator('[data-result] .not-saved')).toHaveText(NOT_SAVED);
  const events = (await stores(page)).events!.filter((e) => e.item_key === two.item.key || e.item_key === three.item.key);
  expect(events).toEqual([]);
});

test('a correct typed answer whose save fails: "checking…" clears, no ✓, the not-saved note', async ({ page }) => {
  const typedItem = allItems().find((f) => f.item.check.kind === 'answer' && itemsOf(f.book, f.entry).length > 1)!;
  const format = (typedItem.item.check as { answer_format: NormaliseOptions }).answer_format;
  const hash = await answerHash(typedItem.item.key, 'zq9 pager answer', format);
  await failEventWrites(page);
  await page.route(`**${typedItem.page}check/${typedItem.anchor}.json`, async (route) => {
    const response = await route.fetch();
    await route.fulfill({ response, json: { ...((await response.json()) as ClientCheck), hash } });
  });
  await openPage(page, `${typedItem.page}#${typedItem.anchor}`);
  await startFailing(page);
  const item = step(page, typedItem.anchor);
  await item.locator('textarea[data-answer]').fill('zq9 pager answer');
  await item.locator('form[data-answer-form] button[type="submit"]').click();
  await expect(item.locator('[data-result] .verdict')).toHaveText('Correct.');
  await expect(item.locator('[data-result] .not-saved')).toHaveText(NOT_SAVED);
  await expect(status(page, typedItem.anchor)).toHaveAttribute('data-state', 'none');
  await expect(status(page, typedItem.anchor)).not.toContainText('checking…');
});

// ---------------------------------------------------------------------------------------------
// Self-check and also_check statuses

test('a self-check ticked to done shows ✓; an also_check list ticked on a failed automatic item shows •', async ({ page }) => {
  const self = U03.find((f) => f.item.check.kind === 'self-check')!;
  await openPage(page, `${self.page}#${self.anchor}`);
  const boxes = step(page, self.anchor).locator('fieldset[data-self-check] input[type="checkbox"]');
  const count = await boxes.count();
  for (let i = 0; i < count - 1; i++) await boxes.nth(i).check();
  await expect(status(page, self.anchor)).toHaveAttribute('data-state', 'tried');
  await boxes.nth(count - 1).check();
  await expect(status(page, self.anchor)).toHaveAttribute('data-state', 'passed');
  await expect(status(page, self.anchor)).toContainText('passed');

  const also = allItems().find(
    (f) => f.item.also_check !== undefined && f.item.also_check.length > 0 && f.item.check.kind === 'expected-output' && f.item.files.length === 0,
  )!;
  await passWith(page, also, 'the real answer\n');
  await openPage(page, `${also.page}#${also.anchor}`);
  const item = step(page, also.anchor);
  await setCode(page, item, 'print("not it")\n');
  await pressCheck(page, also);
  await checkDone(page, also);
  await expect(item.locator('[data-result] .verdict')).toHaveText(/^Not yet/);
  await expect(status(page, also.anchor)).toHaveAttribute('data-state', 'tried');
  const alsoBoxes = item.locator('fieldset[data-also-check] input[type="checkbox"]');
  for (let i = 0; i < (await alsoBoxes.count()); i++) await alsoBoxes.nth(i).check();
  await expect.poll(async () => (await stores(page)).events!.filter((e) => e.item_key === also.item.key && e.result === 'done').length).toBeGreaterThan(0);
  await expect(status(page, also.anchor)).toHaveAttribute('data-state', 'tried');
  await expect(status(page, also.anchor)).toContainText('tried');
});

// ---------------------------------------------------------------------------------------------
// Groups and kickers

test('a group whose first item has two before blocks: one group, both blocks with the first item, the kicker from the heading', async ({ page }) => {
  const cases = [
    { book: 'python-projects', entry: 'unit-04-quiz-show', label: 'Exercise 11', group: 'Algorithm Extension' },
    { book: 'python-projects', entry: 'unit-05-function-factory', label: 'Challenge 1', group: 'Challenge' },
  ];
  for (const c of cases) {
    const items = itemsOf(c.book, c.entry);
    const i = items.findIndex((f) => f.item.label === c.label);
    const first = items[i]!;
    expect(first.item.before).toHaveLength(2);
    await openPage(page, `${first.page}#${first.anchor}`);
    const s = step(page, first.anchor);
    await expect(s.locator(':scope > .block')).toHaveCount(2);
    await expect(s.locator('.step-kicker')).toHaveText(c.group);
    await expect(page.locator('.jump-group-label').filter({ hasText: new RegExp(`^${c.group}$`) })).toHaveCount(1);
    // The next item is in the same group, with no before blocks of its own.
    const next = items[i + 1];
    if (next) {
      await expect(step(page, next.anchor).locator(':scope > .block')).toHaveCount(0);
      await expect(step(page, next.anchor).locator('.step-kicker')).toHaveText(c.group);
    }
    const group = page.locator('.jump-group').filter({ has: page.locator('.jump-group-label', { hasText: new RegExp(`^${c.group}$`) }) });
    await expect(group.locator(`a[data-jump="${first.anchor}"]`)).toHaveCount(1);
  }
});

test('group kickers: an item in the middle of a group shows its group heading; the list shows the groups', async ({ page }) => {
  const files = itemsOf('python-concepts', 'unit-12-files');
  const e26 = files.find((f) => f.item.label === 'Exercise 26')!;
  await openPage(page, `${e26.page}#${e26.anchor}`);
  await expectShown(page, e26.anchor);
  await expect(step(page, e26.anchor).locator('.step-kicker')).toHaveText('Challenge');
  await expect(step(page, e26.anchor).locator('.step-kicker')).toBeVisible();
  // The kicker says Challenge, so the item's Challenge tag is not repeated; the list still tags it.
  await expect(step(page, e26.anchor).locator('.tag-stretch')).toHaveCount(0);
  await expect(jump(page, e26.anchor).locator('.tag-stretch')).toHaveText('Challenge');
  // The kicker is not a heading (the outline stays h1 → h2).
  expect(await step(page, e26.anchor).locator('.step-kicker').evaluate((el) => el.tagName)).toBe('P');

  const project = itemsOf('python-concepts', 'project-01-algorithm-challenge');
  const p5 = project.find((f) => f.item.label === 'Problem 5')!;
  await openPage(page, `${p5.page}#${p5.anchor}`);
  await expect(step(page, p5.anchor).locator('.step-kicker')).toHaveText('Milestone 2');
  await expect(page.locator('.jump-group-label')).toHaveText(['Milestone 1', 'Milestone 2', 'Milestone 3', 'Milestone 4']);
  const m2 = page.locator('.jump-group').nth(1);
  await expect(m2.locator('a[data-jump]')).toHaveCount(3);
  await expect(m2.locator('a[data-jump]').nth(2)).toHaveAttribute('aria-current', 'step');
});

// ---------------------------------------------------------------------------------------------
// Resume

test('resume: item 3 reached by Next is saved and "Continue" lands on it', async ({ page }) => {
  await openPage(page, U01_PAGE);
  await page.locator('[data-pager-next]').click();
  await page.locator('[data-pager-next]').click();
  await expectShown(page, U01[2]!.anchor);
  const saved = async () => {
    const resume = (await stores(page)).resume ?? [];
    return String(resume.find((r) => r.book === 'python-concepts')?.href ?? '');
  };
  await expect.poll(saved).toMatch(new RegExp(`#${U01[2]!.anchor}$`));
  await page.goto('/python-concepts/');
  const link = page.locator('[data-resume-book="python-concepts"] a');
  await expect(link).toBeVisible();
  await expect(link).toHaveAttribute('href', `${U01_PAGE}#${U01[2]!.anchor}`);
  await link.click();
  await ready(page);
  await expectShown(page, U01[2]!.anchor);
});

// ---------------------------------------------------------------------------------------------
// Search

/**
 * A word of this item's statement whose stem appears nowhere else in the exported content (Pagefind
 * stems words, so the word's first letters, less a possible suffix, must be unique too).
 */
function uniqueWord(found: Found): string | null {
  const corpus = readdirSync(CONTENT)
    .flatMap((book) => readdirSync(join(CONTENT, book, 'entries')).map((f) => readFileSync(join(CONTENT, book, 'entries', f), 'utf-8')))
    .join('\n')
    .toLowerCase();
  const words = [...new Set(found.item.statement_md.toLowerCase().match(/\b[a-z]{8,}\b/g) ?? [])];
  return words.find((w) => corpus.split(w.slice(0, w.length - 3)).length === 2) ?? null;
}

test('a search for words unique to a later exercise links to that exercise and lands on it', async ({ page }) => {
  let target: { found: Found; word: string } | null = null;
  for (const found of allItems()) {
    // A later item: not the first three of its page.
    if (itemsOf(found.book, found.entry).findIndex((f) => f.item.key === found.item.key) < 3) continue;
    const word = uniqueWord(found);
    if (word) {
      target = { found, word };
      break;
    }
  }
  expect(target, 'a later exercise with a word of its own').not.toBeNull();
  const { found, word } = target!;
  await page.goto('/search/');
  await search(page, word);
  const link = page.locator(`[data-search-results] a[href^="${found.page}"]`).first();
  await expect(link).toHaveAttribute('href', `${found.page}#${found.anchor}-h`);
  await link.click();
  await ready(page);
  await expectShown(page, found.anchor);
});

// ---------------------------------------------------------------------------------------------
// Print, layouts, no JavaScript

test('print shows every item and hides the pager chrome', async ({ page }) => {
  await openPage(page, `${U01_PAGE}#${U01[3]!.anchor}`);
  await page.emulateMedia({ media: 'print' });
  await expect(visibleSteps(page)).toHaveCount(U01.length);
  await expect(page.locator('[data-pager-nav]')).toBeHidden();
  await expect(page.locator('[data-pager-controls]')).toBeHidden();
  await page.emulateMedia({ media: 'screen' });
  await expect(visibleSteps(page)).toHaveCount(1);
});

test('phone width: the list is a collapsed <details>, no horizontal scroll', async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 740 });
  await openPage(page, `${U10[0]!.page}#${U10[20]!.anchor}`);
  const list = page.locator('details[data-pager-list]');
  await expect(list).not.toHaveAttribute('open');
  await expect(list.locator('summary')).toHaveText(`All exercises (${U10.length})`);
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(360);
  await list.locator('summary').click();
  await expect(list).toHaveAttribute('open');
  await jump(page, U10[3]!.anchor).click();
  await expectShown(page, U10[3]!.anchor);
  await expect(list).not.toHaveAttribute('open');
  await page.setViewportSize({ width: 320, height: 640 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(320);
});

test('wide width: the side list is open, sticky and scrolls on its own', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 720 });
  await openPage(page, U10[0]!.page);
  const nav = page.locator('[data-pager-nav]');
  await expect(page.locator('details[data-pager-list]')).toHaveAttribute('open');
  const box = await nav.evaluate((el) => ({
    overflow: getComputedStyle(el).overflowY,
    position: getComputedStyle(el).position,
    scrollable: el.scrollHeight > el.clientHeight,
  }));
  expect(box).toEqual({ overflow: 'auto', position: 'sticky', scrollable: true });
  const before = await page.evaluate(() => window.scrollY);
  await nav.evaluate((el) => (el.scrollTop = 300));
  expect(await nav.evaluate((el) => el.scrollTop)).toBeGreaterThan(0);
  expect(await page.evaluate(() => window.scrollY)).toBe(before);
  // The item keeps the reading measure beside the list.
  const [navBox, itemBox] = [await nav.boundingBox(), await step(page, U10[0]!.anchor).boundingBox()];
  expect(itemBox!.x).toBeGreaterThan(navBox!.x + navBox!.width);
});

test.describe('without JavaScript', () => {
  test.use({ javaScriptEnabled: false });
  test('every item is visible and no pager chrome shows', async ({ page }) => {
    await page.goto(U01_PAGE);
    await expect(visibleSteps(page)).toHaveCount(U01.length);
    await expect(page.locator('[data-pager-nav]')).toBeHidden();
    await expect(page.locator('[data-pager-controls]')).toBeHidden();
  });
});

// ---------------------------------------------------------------------------------------------
// axe and the CSP

for (const scheme of ['light', 'dark'] as const) {
  test(`axe on the pager (${scheme}): the list open and closed, wide and phone width`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: scheme });
    const check = async (what: string, phone = false) => {
      // At phone width the code editor is excluded: CodeMirror's scroller (a line wider than the
      // box, as at 360 px) trips scrollable-region-focusable on every practice page, with or without
      // the pager (its contenteditable content is focusable, which axe does not count). It is not
      // part of the pager; reported as a follow-up in plan 106's report.
      let builder = new AxeBuilder({ page }).withTags([...WCAG_AA, 'best-practice']);
      if (phone) builder = builder.exclude('.code-editor');
      const results = await builder.analyze();
      const blocking = results.violations.filter((v) => v.tags.some((t) => WCAG_AA.includes(t)));
      expect(blocking.map((v) => `${what}: ${v.id} ${v.nodes.map((n) => n.target.join(' ')).join(' | ')}`)).toEqual([]);
    };
    const project = itemsOf('python-concepts', 'project-01-algorithm-challenge');
    await page.setViewportSize({ width: 1280, height: 720 });
    await openPage(page, `${project[0]!.page}#${project[2]!.anchor}`);
    await check('wide, open');
    await page.setViewportSize({ width: 360, height: 740 });
    await expect(page.locator('details[data-pager-list]')).not.toHaveAttribute('open');
    await check('phone, closed', true);
    await page.locator('details[data-pager-list] summary').click();
    await expect(page.locator('details[data-pager-list]')).toHaveAttribute('open');
    await check('phone, open', true);
  });
}

test('the pager raises zero CSP violations', async ({ context, page }) => {
  const csp = await watchCsp(context);
  await openPage(page, U01_PAGE);
  await jump(page, U01[5]!.anchor).click();
  await page.locator('[data-pager-next]').click();
  await page.locator('[data-pager-prev]').click();
  await page.goBack();
  await page.emulateMedia({ media: 'print' });
  await page.emulateMedia({ media: 'screen' });
  await page.waitForTimeout(300);
  expect(csp.violations).toEqual([]);
  expect(csp.console).toEqual([]);
});

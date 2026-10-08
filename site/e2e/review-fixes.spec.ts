/**
 * Browser checks for plan 103's content-review round-1 fixes, each in a fresh context:
 * - [sol] 2: every slide of a block split across slides has its own key, in the page and in the
 *   stored `slide` events (acsl unit 12, whose block l-001 spans four slides);
 * - [fable] 2: a code slide whose code overflows its panel shows a scroll cue, removed at the end;
 *   a short code slide shows none;
 * - [fable] 3: the mastery map stays collapsed on a fresh book page and opens once a card has
 *   been reviewed;
 * - [fable] 5: the resume link names the kind of page it returns to.
 */
import { expect, test } from '@playwright/test';
import { settle, stores } from './helpers/site';

test('each slide of a split block has its own key, in the page and in its slide event', async ({ page }) => {
  const base = 'acsl/unit-12-graph-theory/lesson/l-001';
  await page.goto('/acsl/unit-12-graph-theory/slides/');
  await settle(page);
  const keys = await page.locator('li.slide').evaluateAll((lis) => lis.map((li) => (li as HTMLElement).dataset.key ?? ''));
  expect(new Set(keys).size).toBe(keys.length);
  expect(keys.filter((k) => k.startsWith(base))).toEqual([base, `${base}#slide-2`, `${base}#slide-3`, `${base}#slide-4`]);
  for (let n = 2; n <= keys.length; n++) {
    await page.keyboard.press('ArrowRight');
    await expect(page).toHaveURL(new RegExp(`#${n}$`));
  }
  await expect
    .poll(async () => new Set(((await stores(page)).events ?? []).filter((e) => e.kind === 'slide').map((e) => e.item_key)).size)
    .toBe(keys.length);
  const stored = new Set(((await stores(page)).events ?? []).filter((e) => e.kind === 'slide').map((e) => e.item_key as string));
  expect([...stored].sort()).toEqual([...keys].sort());
});

test('a code slide that overflows shows a scroll cue until it is scrolled to the end; a short one shows none', async ({ page }) => {
  const long = 'python-projects/unit-05-function-factory/lesson/9c5221f8#asset:l1_cards.py';
  await page.goto('/python-projects/unit-05-function-factory/slides/');
  await settle(page);
  const n = await page.locator(`li.slide[data-key="${long}"]`).evaluate((li) => Number(li.id.replace('slide-', '')));
  await page.goto(`/python-projects/unit-05-function-factory/slides/#${n}`);
  const panel = page.locator('li.slide:not([hidden]) .slide-code').first();
  await expect(panel).toHaveClass(/\bis-overflowing\b/);
  await expect(page.locator('li.slide:not([hidden]) .slide-scroll-cue')).toBeVisible();
  await panel.locator('pre').evaluate((pre) => pre.scrollTo({ top: pre.scrollHeight }));
  await expect(panel).not.toHaveClass(/\bis-overflowing\b/);

  // A short program: the deck's code slide with the fewest lines (one panel, at most 10 lines).
  const short = await page.locator('li.slide').evaluateAll((lis) => {
    let best = -1;
    let fewest = Infinity;
    lis.forEach((li, i) => {
      const panels = li.querySelectorAll('.slide-code pre');
      if (panels.length !== 1) return;
      const lines = (panels[0]!.textContent ?? '').trim().split('\n').length;
      if (lines < fewest) [best, fewest] = [i, lines];
    });
    return fewest <= 10 ? best : -1;
  });
  expect(short).toBeGreaterThanOrEqual(0);
  await page.goto(`/python-projects/unit-05-function-factory/slides/#${short + 1}`);
  await expect(page.locator('li.slide:not([hidden]) .slide-code').first()).toBeVisible();
  await expect(page.locator('li.slide:not([hidden]) .slide-code.is-overflowing')).toHaveCount(0);
  await expect(page.locator('li.slide:not([hidden]) .slide-scroll-cue:visible')).toHaveCount(0);
});

test('the mastery map is collapsed on a fresh book page and opens once a card is reviewed', async ({ page }) => {
  await page.goto('/python-projects/');
  const details = page.locator('details[data-mastery-details]');
  await expect(details).toHaveCount(1);
  await expect(details.locator('summary')).toBeVisible();
  await expect(details.locator('.mastery-row').first()).toBeHidden();
  await expect(details).not.toHaveAttribute('open');

  await page.goto('/python-projects/cards/');
  await settle(page);
  const card = page.locator('[data-deck-card] article.card');
  if ((await card.locator('.card-typed input').count()) > 0) {
    await card.locator('.card-typed input').fill('0');
    await card.locator('.card-typed button[type="submit"]').click();
  } else if ((await card.locator('.card-option').count()) > 0) {
    await card.locator('.card-option').first().click();
  } else {
    await card.getByRole('button', { name: /Show the (output|meaning)/ }).click();
    await card.getByRole('button', { name: 'Got it' }).click();
  }
  await expect(card.getByRole('button', { name: 'Next card' })).toBeVisible();

  await page.goto('/python-projects/');
  await expect(details).toHaveAttribute('open');
  await expect(details.locator('.mastery-row').first()).toBeVisible();
});

test('the resume link names the kind of page it returns to', async ({ page }) => {
  await page.goto('/python-projects/unit-03-turtle-art-studio/practice/');
  await expect(page.locator('h1')).toBeVisible();
  await page.waitForFunction(async () => {
    const db = await new Promise<IDBDatabase>((resolve, reject) => {
      const open = indexedDB.open('py4kids');
      open.onsuccess = () => resolve(open.result);
      open.onerror = () => reject(open.error);
    });
    const names = [...db.objectStoreNames];
    if (!names.includes('resume')) return (db.close(), false);
    const count = await new Promise<number>((resolve) => {
      const req = db.transaction('resume').objectStore('resume').count();
      req.onsuccess = () => resolve(req.result);
    });
    db.close();
    return count > 0;
  });
  await page.goto('/');
  const resume = page.locator('[data-resume-book="python-projects"]');
  await expect(resume).toBeVisible();
  await expect(resume.locator('a')).toHaveAttribute('href', '/python-projects/unit-03-turtle-art-studio/practice/');
  await expect(resume.locator('[data-resume-title]')).toHaveText(/ \(exercises\)$/);
});

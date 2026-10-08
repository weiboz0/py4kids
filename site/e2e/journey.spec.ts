/**
 * The end-to-end journey, once per book (plan 103 Phase F), in a fresh browser context:
 * catalog -> book page -> read a lesson (blocks, a turtle SVG where the book has one) -> the
 * practice page (tick a self-check box where the book has them) -> step the slides by keyboard
 * -> answer a typed predict card and a choice concept card -> search a glossary term -> reload:
 * the checklist, the card states and the resume link persist -> follow the resume link and leave
 * the slides with Escape.
 *
 * Every request of the context is recorded throughout, and at the end the no-network assertions
 * run over all of it (helpers/net.ts): one origin, body-less GETs for files in dist/, no query
 * strings but Pagefind's own, and none of the typed sentinels or state in any URL or header.
 */
import type { Page } from '@playwright/test';
import { assertNoNetwork, expect, test } from './helpers/net';
import { BOOKS, deckOf, search, stores } from './helpers/site';

interface Counts {
  due: number;
  fresh: number;
  later: number;
}

async function counts(page: Page): Promise<Counts> {
  const text = (await page.locator('[data-deck-counts]').textContent()) ?? '';
  const m = /(\d+) due, (\d+) new, (\d+) not due yet/.exec(text);
  if (!m) throw new Error(`unexpected deck counts: ${text}`);
  return { due: Number(m[1]), fresh: Number(m[2]), later: Number(m[3]) };
}

for (const [book, plan] of Object.entries(BOOKS)) {
  test(`${book}: catalog, lesson, slides, cards, checklist, search, persistence, no network`, async ({ page, recorder }) => {
    const sentinel = `zq9typed${book.replace(/-/g, '')}${Math.random().toString(36).slice(2, 10)}`;
    const secrets = [sentinel];
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(`${page.url()}: ${error.message}`));

    // 1. The catalog, then the book page.
    await page.goto('/');
    await expect(page.locator('h1')).toHaveText('py4kids');
    await page.locator(`.catalog-card h2 a[href="/${book}/"]`).click();
    await expect(page).toHaveURL(`/${book}/`);
    await expect(page.locator('[data-contents] .contents-entry').first()).toBeVisible();

    // 2. Read the lesson: its blocks are there, and its turtle drawings where the book has them.
    await page.locator(`a.contents-title[href="/${book}/${plan.lesson}/"]`).click();
    await expect(page).toHaveURL(`/${book}/${plan.lesson}/`);
    await expect(page.locator('article.lesson .block').first()).toBeVisible();
    expect(await page.locator('article.lesson .block').count()).toBeGreaterThan(5);
    if (plan.turtle) {
      const figure = page.locator('svg.turtle-figure').first();
      await figure.scrollIntoViewIfNeeded();
      await expect(figure).toBeVisible();
      await expect(figure).toHaveAttribute('role', 'img');
      expect(await figure.locator('line, path, polyline, circle').count()).toBeGreaterThan(0);
    } else {
      await expect(page.locator('svg.turtle-figure')).toHaveCount(0);
    }
    if (book === 'acsl') await expect(page.locator('article.lesson math').first()).toBeAttached();

    // 3. The practice page: tick a self-check box where the book has them.
    await page.locator('.entry-actions a', { hasText: 'Exercises' }).click();
    await expect(page).toHaveURL(`/${book}/${plan.lesson}/practice/`);
    const boxes = page.locator('fieldset[data-self-check] input[type="checkbox"][data-item-key][data-requirement]');
    let itemKey = '';
    if (plan.selfCheck) {
      const box = boxes.first();
      itemKey = (await box.getAttribute('data-item-key')) ?? '';
      expect(itemKey).not.toBe('');
      secrets.push(itemKey);
      await box.scrollIntoViewIfNeeded();
      await page.locator(`label[for="${await box.getAttribute('id')}"]`).click();
      await expect(box).toBeChecked();
      // The tick is saved asynchronously; navigating away within milliseconds can abort the
      // IndexedDB write, so wait for the event before leaving (no student is that fast).
      await expect.poll(async () => (await stores(page)).events!.some((e) => e.item_key === itemKey && e.kind === 'self-check')).toBe(true);
    } else {
      await expect(boxes).toHaveCount(0);
    }

    // 4. The slides, by keyboard: arrows, End, Home; the hash and the progress bar follow.
    await page.goto(`/${book}/${plan.lesson}/`);
    await page.locator('.entry-actions a', { hasText: 'Slides' }).click();
    await expect(page).toHaveURL(new RegExp(`/${book}/${plan.lesson}/slides/(#1)?$`));
    const deck = page.locator('.deck[data-deck]');
    await expect(deck).toHaveClass(/is-live/);
    const total = await page.locator('li.slide').count();
    expect(total).toBeGreaterThan(3);
    const visible = page.locator('li.slide:not([hidden])');
    const progress = page.locator('progress[data-deck-progress]');
    const at = async (n: number) => {
      await expect(page).toHaveURL(new RegExp(`#${n}$`));
      await expect(visible).toHaveCount(1);
      await expect(progress).toHaveJSProperty('value', n);
    };
    await at(1);
    await expect(page.locator('[data-deck-prev]')).toBeDisabled();
    await page.keyboard.press('ArrowRight');
    await at(2);
    await page.keyboard.press('ArrowRight');
    await at(3);
    await page.keyboard.press('ArrowLeft');
    await at(2);
    await page.keyboard.press('End');
    await at(total);
    await expect(page.locator('[data-deck-next]')).toBeDisabled();
    await page.keyboard.press('Home');
    await at(1);
    await page.locator('[data-deck-next]').click();
    await page.keyboard.press('ArrowRight');
    await at(3);
    // The resume position is written after the slide event settles; leave only once it is stored.
    await expect
      .poll(async () => (await stores(page)).resume?.find((r) => r.book === book)?.href)
      .toBe(`/${book}/${plan.lesson}/slides/#3`);

    // 5. The cards: a typed predict card (answered with the sentinel) and a choice concept card.
    await page.goto(`/${book}/`);
    await page.locator('.book-tools a', { hasText: 'Quiz cards' }).click();
    await expect(page).toHaveURL(`/${book}/cards/`);
    await expect(page.locator('[data-deck-bar]')).toBeVisible();
    const cards = deckOf(book);
    const units = [...new Set(cards.map((c) => c.unit))]
      .filter((u) => cards.some((c) => c.unit === u && c.kind === 'predict' && c.mode === 'typed') && cards.some((c) => c.unit === u && c.kind === 'concept' && c.mode === 'choice'))
      .sort((a, b) => cards.filter((c) => c.unit === a).length - cards.filter((c) => c.unit === b).length);
    const unit = units[0];
    expect(unit, 'a unit with both a typed predict card and a choice concept card').toBeDefined();
    await page.locator('[data-deck-unit]').selectOption(unit!);
    const before = await counts(page);
    expect(before).toEqual({ due: 0, fresh: cards.filter((c) => c.unit === unit).length, later: 0 });
    let typed = false;
    let choice = false;
    let answered = 0;
    while (!(typed && choice)) {
      expect(answered, 'cards answered before both kinds came up').toBeLessThan(before.fresh);
      const card = page.locator('[data-deck-card] article.card');
      await expect(card).toBeVisible();
      if ((await card.locator('.card-typed input').count()) > 0) {
        await card.locator('.card-typed input').fill(sentinel);
        await card.locator('.card-typed button[type="submit"]').click();
        await expect(card.locator('.card-feedback')).toHaveText(/Not quite/);
        typed = true;
      } else if ((await card.locator('.card-option').count()) > 0) {
        await card.locator('.card-option').first().click();
        await expect(card.locator('.card-feedback')).toHaveText(/Correct!|Not quite/);
        await expect(card.locator('.card-option.is-correct')).toHaveCount(1);
        choice = true;
      } else {
        await card.getByRole('button', { name: /Show the (output|meaning)/ }).click();
        await card.getByRole('button', { name: 'Not yet' }).click();
      }
      answered += 1;
      await card.getByRole('button', { name: 'Next card' }).click();
    }

    // 6. Search for a glossary term of this book.
    await page.goto(`/${book}/glossary/`);
    const term = ((await page.locator('dl.glossary dt').first().textContent()) ?? '').trim();
    expect(term).not.toBe('');
    const bookTitle = ((await page.locator('.crumbs a').first().textContent()) ?? '').trim();
    await page.goto('/');
    await page.locator('.site-search-link').click();
    await expect(page).toHaveURL('/search/');
    await search(page, term, bookTitle);
    await expect(page.locator('[data-search-status]')).toHaveText(/\d+ pages? match/);
    // Every result, ten at a time ("Show more results"), waiting for each page to render.
    const found = Number(/(\d+) pages? match/.exec((await page.locator('[data-search-status]').textContent()) ?? '')![1]);
    const items = page.locator('[data-search-results] .search-result');
    for (let shown = Math.min(10, found); ; shown = Math.min(shown + 10, found)) {
      await expect(items).toHaveCount(shown);
      if (shown === found) break;
      await page.locator('[data-search-more]').click();
    }
    await expect(page.locator('[data-search-more]')).toBeHidden();
    const hrefs = await page.locator('[data-search-results] .search-result a').evaluateAll((as) => as.map((a) => a.getAttribute('href') ?? ''));
    expect(hrefs.length).toBeGreaterThan(0);
    expect(hrefs.every((h) => h.startsWith(`/${book}/`)), `results outside ${book}: ${hrefs.join(', ')}`).toBe(true);
    expect(hrefs.some((h) => h.startsWith(`/${book}/glossary/`)), `no glossary result for "${term}"`).toBe(true);
    // The search ran in Pagefind's worker; its index, fragment and WebAssembly loads are recorded.
    const pagefind = recorder.requests.filter((r) => r.url.includes('/pagefind/')).map((r) => new URL(r.url).pathname);
    expect(pagefind.some((p) => p.endsWith('.pagefind') && p.includes('wasm')), 'Pagefind WebAssembly load recorded').toBe(true);
    // (Plan 105: Pagefind sits in a content-hashed folder, /pagefind/<hash>/.)
    expect(pagefind.some((p) => /^\/pagefind\/(?:[0-9a-f]{10}\/)?index\//.test(p)), 'Pagefind index load recorded').toBe(true);
    expect(pagefind.some((p) => /^\/pagefind\/(?:[0-9a-f]{10}\/)?fragment\//.test(p)), 'Pagefind fragment load recorded').toBe(true);

    // 7. Reload: the checklist, the card states and the resume link persist.
    // The resume link (catalog, after a reload): the last entry page visited was the slides, at
    // slide 3. Following it returns there; Escape then leaves the slides for the reading view.
    await page.goto('/');
    await page.reload();
    const resume = page.locator(`[data-resume-book="${book}"]`);
    await expect(resume).toBeVisible();
    await expect(resume.locator('a')).toHaveAttribute('href', `/${book}/${plan.lesson}/slides/#3`);
    await expect(resume.locator('[data-resume-title]')).toHaveText(/ \(slides\)$/); // the page kind is named
    await resume.locator('a').click();
    await expect(page.locator('li.slide:not([hidden])')).toHaveCount(1);
    await expect(page.locator('progress[data-deck-progress]')).toHaveJSProperty('value', 3);
    await page.keyboard.press('Escape');
    await expect(page).toHaveURL(`/${book}/${plan.lesson}/`);

    if (plan.selfCheck) {
      await page.goto(`/${book}/${plan.lesson}/practice/`);
      await page.reload();
      const box = boxes.first();
      await expect(box).toBeChecked(); // the progress island restores it from IndexedDB
      await expect(boxes.nth(1)).not.toBeChecked();
    }
    await page.goto(`/${book}/cards/`);
    await page.reload();
    await expect(page.locator('[data-deck-bar]')).toBeVisible();
    await page.locator('[data-deck-unit]').selectOption(unit!);
    const after = await counts(page);
    expect(after.fresh).toBe(before.fresh - answered);
    expect(after.due + after.later).toBe(answered);

    const saved = await stores(page);
    const events = saved.events ?? [];
    expect(events.filter((e) => e.kind === 'card' && e.book === book)).toHaveLength(answered);
    expect(events.filter((e) => e.kind === 'slide' && e.book === book).length).toBeGreaterThanOrEqual(3);
    expect((saved.cards ?? []).filter((c) => c.book === book)).toHaveLength(answered);
    if (plan.selfCheck) {
      const checks = events.filter((e) => e.kind === 'self-check' && e.item_key === itemKey);
      expect(checks.length).toBeGreaterThan(0);
      expect((checks.at(-1)!.detail as { checklist: boolean[] }).checklist[0]).toBe(true);
    }
    // Results only: the typed answer is stored nowhere.
    expect(JSON.stringify(saved).includes(sentinel)).toBe(false);

    expect(errors, 'uncaught page errors').toEqual([]);
    expect(await page.locator('.progress-notice').count(), 'the unsaved notice (IndexedDB works here)').toBe(0);
    assertNoNetwork(recorder, secrets);
  });
}

/**
 * Offline end to end, once per book (plan 105 Phase E, "Offline end-to-end, per book"; design 012
 * §3 "an offline test that runs code and checks an exercise", the D10 test):
 *   1. online, open the book, press "Download this book" and wait for "Available offline" (every
 *      request of the download, the service workers' own included, is on the allowlist);
 *   2. STOP both servers (offline emulation alone is not trusted: a service worker's fetches escape
 *      it), then reload, recording at context level: the only requests that may reach the network
 *      are the update checks, at most one failed `GET /release.json` per document load on each
 *      origin; zero others, and no console error (helpers.ts `assertOfflineContract`);
 *   3. read a lesson and run one of its cells; check one exercise of each check kind the book has
 *      (a fixtures item where the book has them: every case boots a fresh Python worker from the
 *      cached Pyodide); answer a quiz card;
 *   4. rerun the hang test offline: `interrupts: "sab"`, the end-to-end proof that the isolation
 *      headers survived the cache;
 *   5. reload offline again: the progress persists.
 * The books are separate tests (one fresh browser context each).
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Page } from '@playwright/test';
import { CONTENT, cpython, fixturePairs, lookupProgram, allItems, type Found } from '../e2e/helpers/content';
import { loadClient, type Browserside } from '../e2e/helpers/runner';
import { BOOKS, stores } from '../e2e/helpers/site';
import { check, open, setCode } from '../e2e/helpers/practice';
import { RUNNER_URL } from '../e2e/helpers/env';
import { assertAllowlisted, assertOfflineContract, downloadBook, NetLog, RUNNER_ORIGIN, SITE_ORIGIN } from './helpers';
import { expect, test } from './servers';

interface Block {
  key: string;
  type: string;
  code?: string;
  output?: string;
  probe: string | null;
  files: string[];
}

/** A lesson cell of `book` that runs on its own and prints a known output (the plan's lesson first). */
function lessonBlock(book: string): { entry: string; block: Block } {
  const files = readdirSync(join(CONTENT, book, 'entries')).sort();
  const preferred = `${BOOKS[book]!.lesson}.json`;
  for (const file of [preferred, ...files.filter((f) => f !== preferred)]) {
    const entry = JSON.parse(readFileSync(join(CONTENT, book, 'entries', file), 'utf-8')) as { entry: { id: string }; lesson: { blocks: Block[] } | null };
    const block = entry.lesson?.blocks.find(
      (b) => b.type === 'code' && b.probe === 'standalone' && b.files.length === 0 && (b.output ?? '').trim() !== '' && !/input\(|random|turtle|time\./.test(b.code ?? ''),
    );
    if (block) return { entry: entry.entry.id, block };
  }
  throw new Error(`${book}: no standalone lesson cell with a known output`);
}

/** One item per check kind the book has (a small fixtures item, so a fresh worker per case stays quick). */
function itemsByKind(book: string): Map<string, Found> {
  const out = new Map<string, Found>();
  const items = allItems().filter((f) => f.book === book);
  const size = (f: Found) => fixturePairs(f).reduce((n, c) => n + c.input.length + c.output.length, 0);
  for (const f of items) {
    const kind = f.item.check.kind;
    if (out.has(kind)) continue;
    if (kind === 'fixtures' && (f.item.check.cases.length < 2 || size(f) > 20_000)) continue;
    if (kind === 'expected-output' && ((f.item.check as { turtle?: boolean }).turtle || f.item.files.length > 0)) continue;
    if (kind === 'predict' && /input\(|random|turtle/.test((f.item.check as { program: string }).program)) continue;
    out.set(kind, f);
  }
  const kinds = new Set(items.map((f) => f.item.check.kind));
  expect([...out.keys()].sort(), `${book}: an item of every check kind`).toEqual([...kinds].sort());
  return out;
}

/** Check one item offline, by its kind; returns what the page said. */
async function checkOffline(page: Page, kind: string, found: Found): Promise<string> {
  const item = await open(page, found);
  switch (kind) {
    case 'fixtures': {
      const pairs = fixturePairs(found);
      await setCode(page, item, lookupProgram(Object.fromEntries(pairs.map((c) => [c.input, c.output]))));
      const verdict = await check(item);
      expect(verdict, `${found.item.key}: every case passes, each in a fresh worker`).toMatch(/^Passed/);
      await expect(item.locator('[data-result] .case-list > li')).toHaveCount(pairs.length);
      return verdict;
    }
    case 'asserts': {
      await setCode(page, item, 'pass\n');
      const verdict = await check(item);
      expect(verdict).toMatch(/^Not yet/);
      expect(await item.locator('[data-result] .case-list > li').count()).toBeGreaterThan(0);
      return verdict;
    }
    case 'expected-output': {
      await setCode(page, item, 'print("offline and running")\n');
      const verdict = await check(item);
      expect(verdict).toMatch(/^Not yet/);
      await expect(item.locator('[data-result] .io-output code')).toHaveText('offline and running');
      return verdict;
    }
    case 'self-check': {
      await setCode(page, item, 'print("made offline")\n');
      await item.locator('[data-run-item]').click();
      await expect(item.locator('[data-result] .io-output code')).toHaveText('made offline', { timeout: 90_000 });
      return 'ran';
    }
    case 'predict':
    case 'answer': {
      const typed = kind === 'predict' ? cpython((found.item.check as { program: string }).program) : 'zq9 not the answer';
      await item.locator('textarea[data-answer]').fill(typed);
      await item.locator('form[data-answer-form] button[type="submit"]').click();
      const verdict = item.locator('[data-result] .verdict');
      await expect(verdict).toHaveText(kind === 'predict' ? 'Correct.' : /^Not yet/);
      return (await verdict.textContent()) ?? '';
    }
    default:
      throw new Error(`no offline check for kind ${kind}`);
  }
}

/** Answer the first card of the deck, whatever its mode. */
async function answerCard(page: Page, book: string): Promise<void> {
  await page.goto(`/${book}/cards/`);
  const card = page.locator('[data-deck-card] article.card');
  await expect(card).toBeVisible({ timeout: 30_000 });
  if ((await card.locator('.card-typed input').count()) > 0) {
    await card.locator('.card-typed input').fill('zq9 offline guess');
    await card.locator('.card-typed button[type="submit"]').click();
  } else if ((await card.locator('.card-option').count()) > 0) {
    await card.locator('.card-option').first().click();
  } else {
    await card.getByRole('button', { name: /Show the (output|meaning)/ }).click();
    await card.getByRole('button', { name: 'Not yet' }).click();
  }
  await expect.poll(async () => ((await stores(page)).events ?? []).filter((e) => e.kind === 'card' && e.book === book).length).toBe(1);
}

for (const book of Object.keys(BOOKS)) {
  test(`offline end to end, ${book}: download, servers stopped, lesson run, a check of every kind, a card, the hang, persistence`, async ({ page, context, servers }) => {
    test.setTimeout(600_000);
    const log = new NetLog(context);
    const lesson = lessonBlock(book);
    const kinds = itemsByKind(book);

    // 1. Online: the download, every request on the allowlist (the service workers' own included).
    await downloadBook(page, book);
    await log.settle();
    assertAllowlisted(log);
    expect(log.errors, 'console errors online').toEqual([]);

    // 2. Both servers stopped; reload, recording from here.
    await servers.stop();
    await expect(page.request.get('/release.json')).rejects.toThrow();
    await expect(page.request.get(`${RUNNER_URL}/release.json`)).rejects.toThrow();
    log.reset();
    await page.reload();
    await expect(page.locator('[data-offline-book] [data-offline-status]')).toHaveText('Available offline.', { timeout: 30_000 });
    expect(await page.evaluate(() => crossOriginIsolated)).toBe(true);

    // 3. Read a lesson and run one of its cells.
    await page.locator(`a.contents-title[href="/${book}/${lesson.entry}/"]`).click();
    await expect(page).toHaveURL(`/${book}/${lesson.entry}/`);
    await expect(page.locator('article.lesson .block').first()).toBeVisible();
    const holder = page.locator(`[data-run][data-key="${lesson.block.key}"]`);
    await holder.scrollIntoViewIfNeeded();
    await holder.locator('[data-lesson-run]').click();
    await expect(holder.locator('[data-run-output] .io-output code')).toHaveText(lesson.block.output!.replace(/\n$/, ''), { timeout: 90_000 });

    // ... one exercise of each check kind the book has ...
    const verdicts: string[] = [];
    for (const [kind, found] of kinds) verdicts.push(`${kind} (${found.item.key}): ${await checkOffline(page, kind, found)}`);
    test.info().annotations.push({ type: 'offline checks', description: verdicts.join('; ') });

    // ... and a quiz card.
    await answerCard(page, book);

    // 4. The hang test, offline: the SharedArrayBuffer interrupt stops it (isolation survived the cache).
    await loadClient(page);
    const ready = await page.evaluate(() => {
      const w = window as unknown as Browserside;
      w.runner = w.py4kidsRunnerClient.connectRunner(document.body).client;
      return w.runner.ping();
    });
    expect(ready.isolated, 'the runner page and its worker are cross-origin isolated offline').toBe(true);
    const hang = await page.evaluate(() =>
      (window as unknown as Browserside).runner.run({ session: 'offline-hang', code: 'while True:\n    pass\n', budget_ms: 1000 }).result,
    );
    expect(hang.status).toBe('timeout');
    expect(hang.interrupts).toBe('sab');

    // 5. Reload offline: the progress persists.
    const before = await stores(page);
    const mine = (s: typeof before) => ({
      events: (s.events ?? []).filter((e) => e.book === book).map((e) => `${e.kind} ${e.item_key ?? ''} ${e.result ?? ''}`).sort(),
      cards: (s.cards ?? []).filter((c) => c.book === book).length,
    });
    const kept = mine(before);
    expect(kept.events.some((e) => e.startsWith('lesson-run '))).toBe(true);
    expect(kept.events.filter((e) => e.startsWith('card ')).length).toBe(1);
    expect(kept.cards).toBe(1);
    await page.goto(`/${book}/`);
    await page.reload();
    await expect(page.locator('[data-offline-book] [data-offline-status]')).toHaveText('Available offline.', { timeout: 30_000 });
    expect(mine(await stores(page))).toEqual(kept);
    // The book page reads the stored progress back (the resume link names the last page visited).
    await expect(page.locator(`[data-resume-book="${book}"]`)).toBeVisible();

    await log.settle();
    const checks = assertOfflineContract(log);
    // The runner iframe was loaded offline, so its update checks were seen too.
    expect(log.loads[RUNNER_ORIGIN] ?? 0).toBeGreaterThan(0);
    test.info().annotations.push({
      type: 'offline requests',
      description: `${log.entries.length} recorded; update checks ${JSON.stringify(checks)}; document loads ${JSON.stringify(log.loads)}; site ${SITE_ORIGIN}`,
    });
  });
}

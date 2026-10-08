/**
 * The practice checks and the runnable reading view in a real browser (plan 104 Phase B; the
 * grading-UI rows of Phase D). Real items are picked from the exported bundles at test time
 * (e2e/helpers/content.ts); programs whose output is known are built from the fixtures there.
 * Where the bundle has no item of a kind yet (no answer or predict item ships `whitespace: exact`, so
 * no typed box is an exact one), the item's projection is simulated by intercepting its check JSON
 * and its one `data-exact` attribute; the island code under test is the same.
 */
import { expect, test } from '@playwright/test';
import { answerHash, type NormaliseOptions } from '../src/lib/normalise';
import type { ClientCheck } from '../src/lib/check-model';
import { watchCsp } from './helpers/csp';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { CONTENT, cpython, findItem, fixturePairs, judgeMatch, lookupProgram, type Found } from './helpers/content';
import { stores } from './helpers/site';
import { caseRows, check, open, patchCheck, section, setCode, turtleItem } from './helpers/practice';

test.describe.configure({ mode: 'parallel' });

const small = (f: Found) => fixturePairs(f).reduce((n, c) => n + c.input.length + c.output.length, 0) < 150_000;

// ---------------------------------------------------------------------------------------------
// Fixtures

test('fixtures, line-exact (acsl): one token per line is rejected where a line holds several, as tools/judge.py rules', async ({ page }) => {
  const found = findItem(
    (f) =>
      f.book === 'acsl' &&
      f.item.check.kind === 'fixtures' &&
      f.item.check.match === 'line' &&
      f.item.check.cases.length >= 3 &&
      small(f) &&
      fixturePairs(f).some((c) => c.output.split('\n').some((line) => line.trim().split(/\s+/).length > 1)),
    'an acsl line-matched fixtures item with a multi-token line',
    (f) => (f.item.check as { cases: unknown[] }).cases.length,
  );
  const pairs = fixturePairs(found);
  const item = await open(page, found);

  // Each expected token on its own line (`15 10 4` printed as `15\n10\n4`).
  const split = (out: string) => `${out.split(/\s+/).filter(Boolean).join('\n')}\n`;
  await setCode(page, item, lookupProgram(Object.fromEntries(pairs.map((c) => [c.input, split(c.output)]))));
  await check(item);
  const rows = await caseRows(item);
  const ordered = [...pairs.filter((c) => c.sample), ...pairs.filter((c) => !c.sample)];
  expect(rows).toHaveLength(ordered.length);
  ordered.forEach((c, i) => {
    const pass = judgeMatch(split(c.output), c.output, true);
    expect(rows[i], `case ${c.n}`).toMatch(pass ? /: passed$/ : /: wrong output$/);
  });
  expect(ordered.some((c) => !judgeMatch(split(c.output), c.output, true))).toBe(true);

  // The exact output passes every case.
  await setCode(page, item, lookupProgram(Object.fromEntries(pairs.map((c) => [c.input, c.output]))));
  expect(await check(item)).toMatch(/^Passed/);
  for (const c of ordered) expect(judgeMatch(c.output, c.output, true)).toBe(true);
});

test('fixtures, token-based (usaco): the same reflowed output is accepted, as tools/judge.py rules', async ({ page }) => {
  const found = findItem(
    (f) =>
      f.book === 'usaco-bronze' &&
      f.item.check.kind === 'fixtures' &&
      f.item.check.match === 'token' &&
      f.item.check.cases.length >= 3 &&
      small(f) &&
      fixturePairs(f).some((c) => c.output.trim().split(/\s+/).length > 1),
    'a usaco token-matched fixtures item with several tokens',
    (f) => (f.item.check as { cases: unknown[] }).cases.length,
  );
  const pairs = fixturePairs(found);
  const item = await open(page, found);
  const split = (out: string) => `${out.split(/\s+/).filter(Boolean).join('\n')}\n`;
  await setCode(page, item, lookupProgram(Object.fromEntries(pairs.map((c) => [c.input, split(c.output)]))));
  expect(await check(item)).toMatch(/^Passed/);
  for (const c of pairs) expect(judgeMatch(split(c.output), c.output, false), `case ${c.n}`).toBe(true);
  // A wrong answer fails, case by case.
  await setCode(page, item, 'print("nope")\n');
  expect(await check(item)).toMatch(/^Not yet: 0 of/);
});

test('the sample runs first with its input and expected output shown; no hidden case\'s output reaches the DOM', async ({ page }) => {
  const found = findItem(
    (f) => f.book === 'usaco-bronze' && f.item.check.kind === 'fixtures' && f.item.check.cases.filter((c) => !c.sample).length >= 2 && small(f),
    'a usaco item with hidden cases',
  );
  const pairs = fixturePairs(found);
  const sample = pairs.find((c) => c.sample)!;
  const item = await open(page, found);
  const hidden = pairs.filter((c) => !c.sample).map((c) => c.output.trim()).filter((t) => t.length >= 4);
  const before = await page.content();
  const absent = hidden.filter((t) => !before.includes(t));
  expect(absent.length).toBeGreaterThan(0);

  await setCode(page, item, lookupProgram(Object.fromEntries(pairs.map((c) => [c.input, c.output]))));
  await item.locator('[data-check-item]').click();
  // The sample's verdict shows while the hidden cases are still running.
  await expect(item.locator('.case-list > li').first()).toHaveText(/^Sample case \d+: passed/, { timeout: 60_000 });
  await expect(item.locator('[data-check-item]')).toBeEnabled({ timeout: 90_000 });
  const reveal = item.locator('.sample-reveal');
  await expect(reveal).toHaveCount(1);
  await expect(reveal.locator('.io-input code')).toHaveText(sample.input.replace(/\n$/, ''));
  await expect(reveal.locator('.io-expected code')).toHaveText(sample.output.replace(/\n$/, ''));
  const after = await page.content();
  for (const text of absent) expect(after.includes(text), 'a hidden case output is in the DOM').toBe(false);
  expect(await caseRows(item)).toEqual(
    expect.arrayContaining([expect.stringMatching(/^Hidden case 1: passed$/), expect.stringMatching(/^Hidden case 2: passed$/)]),
  );
});

test('a case over budget is listed as skipped, never run, and left out of the event\'s cases', async ({ page }) => {
  const found = findItem((f) => f.book === 'usaco-bronze' && f.item.check.kind === 'fixtures' && f.item.check.cases.length >= 3 && small(f), 'a usaco item');
  const pairs = fixturePairs(found);
  const hiddenN = pairs.find((c) => !c.sample)!.n;
  await patchCheck(page, found, (c) => {
    if (c.kind !== 'fixtures') throw new Error('not fixtures');
    return { ...c, cases: c.cases.map((x) => (x.n === hiddenN ? { ...x, skipped: true } : x)) };
  });
  const item = await open(page, found);
  await setCode(page, item, lookupProgram(Object.fromEntries(pairs.map((c) => [c.input, c.output]))));
  await check(item);
  const rows = await caseRows(item);
  expect(rows.filter((r) => /: skipped \(too slow/.test(r))).toHaveLength(1);
  await expect(item.locator('[data-result] .check-status')).toHaveText(/ 1 skipped\.$/);
  const events = (await stores(page)).events!.filter((e) => e.item_key === found.item.key);
  expect(events).toHaveLength(1);
  const cases = (events[0]!.detail as { cases: { n: number }[] }).cases;
  expect(cases.map((c) => c.n)).not.toContain(hiddenN);
  expect(cases).toHaveLength(pairs.length - 1);
});

test('Stop ends a long fixture check: the running case stops and the rest are listed as not run', async ({ page }) => {
  const found = findItem((f) => f.book === 'usaco-bronze' && f.item.check.kind === 'fixtures' && f.item.check.cases.length >= 3 && small(f), 'a usaco item');
  await patchCheck(page, found, (c) => ({ ...c, budget_ms: 30_000 }) as ClientCheck);
  const item = await open(page, found);
  await setCode(page, item, 'while True:\n    pass\n');
  await item.locator('[data-check-item]').click();
  await expect(item.locator('.case-list > li').first()).toHaveText(/: running…$/, { timeout: 60_000 });
  const stop = item.locator('[data-stop]');
  await expect(stop).toBeVisible();
  await stop.click();
  await expect(item.locator('[data-check-item]')).toBeEnabled({ timeout: 15_000 });
  const rows = await caseRows(item);
  expect(rows[0]).toMatch(/: stopped$/);
  expect(rows.slice(1).every((r) => /: not run \(stopped\)$/.test(r))).toBe(true);
  await expect(stop).toBeHidden();
});

test('a 10-case fixture check (timing)', async ({ page }) => {
  const found = findItem((f) => f.item.check.kind === 'fixtures' && f.item.check.cases.length >= 10 && small(f), 'a 10-case item');
  const pairs = fixturePairs(found);
  const item = await open(page, found);
  await setCode(page, item, lookupProgram(Object.fromEntries(pairs.map((c) => [c.input, c.output]))));
  // Boot Python first (a Run), so the timing is the check's own.
  await item.locator('[data-run-item]').click();
  await expect(item.locator('[data-run-item]')).toBeEnabled({ timeout: 60_000 });
  const start = Date.now();
  expect(await check(item, 110_000)).toMatch(/^Passed/);
  const ms = Date.now() - start;
  test.info().annotations.push({ type: 'timing', description: `${pairs.length}-case fixture check (${found.item.key}): ${ms} ms` });
  console.log(`fixture check: ${pairs.length} cases in ${ms} ms (${found.item.key})`);
});

// ---------------------------------------------------------------------------------------------
// Hash checks

test('expected-output: the program runs and its stdout is compared by hash (pass and fail)', async ({ page }) => {
  const found = findItem((f) => f.item.check.kind === 'expected-output' && !f.item.check.turtle && f.item.files.length === 0, 'an expected-output item');
  const format = (found.item.check as { answer_format: NormaliseOptions }).answer_format;
  // The real expected output is only a hash; the test serves the hash of a known output.
  const hash = await answerHash(found.item.key, 'Hello, checker!\n', { case: format.case });
  await patchCheck(page, found, (c) => ({ ...c, hash }) as ClientCheck);
  const item = await open(page, found);
  await setCode(page, item, 'print("Hello, checker!")\n');
  expect(await check(item)).toBe('Passed.');
  await expect(item.locator('[data-result] .io-output code')).toHaveText('Hello, checker!');
  await setCode(page, item, 'print("Hello, world")\n');
  expect(await check(item)).toMatch(/^Not yet/);
  await expect(item.locator('[data-result] .case-list')).toContainText('Output: does not match the expected output');
});

test('predict: the real program\'s output, typed, passes; a wrong prediction fails', async ({ page }) => {
  const found = findItem(
    (f) => f.item.check.kind === 'predict' && !/input\(|random|turtle/.test((f.item.check as { program: string }).program),
    'a predict item with a deterministic program',
  );
  const output = cpython((found.item.check as { program: string }).program);
  const item = await open(page, found);
  const box = item.locator('textarea[data-answer]');
  await box.fill(output);
  await item.locator('form[data-answer-form] button[type="submit"]').click();
  await expect(item.locator('[data-result] .verdict')).toHaveText('Correct.');
  await box.fill(`${output.trim()}!!`);
  await item.locator('form[data-answer-form] button[type="submit"]').click();
  await expect(item.locator('[data-result] .verdict')).toHaveText(/^Not yet/);
  // The typed answers stay in the attempt store; the events carry results only.
  const db = await stores(page);
  const events = db.events!.filter((e) => e.item_key === found.item.key);
  expect(events.map((e) => e.result).sort()).toEqual(['fail', 'pass']);
  expect(JSON.stringify(events)).not.toContain(output.trim());
  // The attempt is stored after the verdict shows: wait for the second one.
  await expect
    .poll(async () => ((await stores(page)).attempts ?? []).filter((a) => a.item_key === found.item.key).map((a) => a.answer as string).sort())
    .toEqual([output, `${output.trim()}!!`].sort());
});

test('answer with aliases (acsl unit 4 e-024): `^` typed for `↑` is accepted', async ({ page }) => {
  const found = findItem(
    (f) => f.item.key === 'acsl/unit-04-prefix-infix-postfix/exercises/e-024',
    'acsl unit 4 e-024, an answer item with aliases',
  );
  expect((found.item.check as { answer_format: NormaliseOptions }).answer_format.aliases).toEqual({ '^': '↑' });
  const item = await open(page, found);
  const box = item.locator('textarea[data-answer]');
  for (const [typed, verdict] of [
    ['- * + A B ^ C 2 / D - E F', 'Correct.'],
    ['- * + A B ↑ C 2 / D - E F', 'Correct.'],
    ['- * + A B ^ C 2 / D - F E', /^Not yet/],
  ] as const) {
    await box.fill(typed);
    await item.locator('form[data-answer-form] button[type="submit"]').click();
    await expect(item.locator('[data-result] .verdict')).toHaveText(verdict);
  }
});

test('expected-output with whitespace: exact (python-concepts u01e14a): printing a real tab passes; a literal backslash-t or spaces fail', async ({ page }) => {
  const found = findItem(
    (f) => f.item.key === 'python-concepts/unit-01-output-and-variables/exercises/u01e14a',
    'python-concepts u01e14a, an exact-whitespace expected-output item',
  );
  expect((found.item.check as { answer_format: NormaliseOptions }).answer_format.whitespace).toBe('exact');
  const item = await open(page, found);
  await setCode(page, item, '# Print the poem.\npoem = "Sun comes up\\nBirds sing\\n\\tThe end"\nprint(poem)\n');
  expect(await check(item)).toBe('Passed.');
  // The program's output is graded, so printing the two characters `\` and `t` is not a tab.
  await setCode(page, item, '# Print the poem.\npoem = "Sun comes up\\nBirds sing\\n\\\\tThe end"\nprint(poem)\n');
  expect(await check(item)).toMatch(/^Not yet/);
  await setCode(page, item, '# Print the poem.\npoem = "Sun comes up\\nBirds sing\\n    The end"\nprint(poem)\n');
  expect(await check(item)).toMatch(/^Not yet/);
  await setCode(page, item, '# Print the poem.\npoem = "Sun comes up\\nBirds  sing\\n\\tThe end"\nprint(poem)\n');
  expect(await check(item)).toMatch(/^Not yet/);
});

test('answer with whitespace: exact — Tab types a tab, spacing counts, Escape then Tab leaves the box', async ({ page }) => {
  const found = findItem((f) => f.item.check.kind === 'answer', 'an answer item');
  const format: NormaliseOptions = { case: 'sensitive', whitespace: 'exact' };
  const hash = await answerHash(found.item.key, 'a\tb\n  c', format);
  await patchCheck(page, found, (c) => ({ ...c, hash, format: { ...(c as { format: object }).format, ...format } }) as ClientCheck);
  // No answer or predict item ships `whitespace: exact`, so mark this item's box as one.
  await page.route(`**${found.page}`, async (route) => {
    const response = await route.fetch();
    const html = (await response.text()).replace(
      new RegExp(`(data-item-key="${found.item.key}"[\\s\\S]*?<textarea[^>]*?data-answer)`),
      '$1 data-exact',
    );
    await route.fulfill({ response, body: html });
  });
  const item = await open(page, found);
  const box = item.locator('textarea[data-answer]');
  await expect(box).toHaveAttribute('data-exact', '');
  await box.click();
  await page.keyboard.type('a');
  await page.keyboard.press('Tab');
  await page.keyboard.type('b');
  await page.keyboard.press('Enter');
  await page.keyboard.type('  c');
  await expect(box).toHaveValue('a\tb\n  c');
  await expect(box).toBeFocused();
  // Escape, then Tab, leaves the box for the Check button.
  await page.keyboard.press('Escape');
  await page.keyboard.press('Tab');
  await expect(item.locator('form[data-answer-form] button[type="submit"]')).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(item.locator('[data-result] .verdict')).toHaveText('Correct.');
  await box.fill('a b\nc');
  await item.locator('form[data-answer-form] button[type="submit"]').click();
  await expect(item.locator('[data-result] .verdict')).toHaveText(/^Not yet/);
});

// ---------------------------------------------------------------------------------------------
// Asserts, self-check, also_check, the turtle rule

test('asserts: a verdict per test, never the source', async ({ page }) => {
  const found = findItem((f) => f.item.check.kind === 'asserts' && (f.item.check as { source: string }).source.split('\n').length >= 2, 'an asserts item');
  const source = (found.item.check as { source: string }).source;
  const item = await open(page, found);
  await setCode(page, item, 'pass\n');
  expect(await check(item)).toMatch(/^Not yet/);
  const rows = await caseRows(item);
  expect(rows.length).toBeGreaterThanOrEqual(2);
  for (const row of rows) expect(row).toMatch(/^Test \d+: |^Your code: /);
  const html = await page.content();
  for (const line of source.split('\n').filter((l) => l.trim().length > 12)) expect(html.includes(line.trim())).toBe(false);
  const events = (await stores(page)).events!.filter((e) => e.item_key === found.item.key);
  expect(events).toHaveLength(1);
  expect(events[0]).toMatchObject({ kind: found.item.kind === 'checkpoint' ? 'checkpoint' : found.item.kind === 'project' ? 'project' : 'exercise', result: 'fail' });
  expect((events[0]!.detail as { cases: unknown[] }).cases.length).toBe(rows.length);
});

test('self-check: a checklist with no automatic verdict, and the "cannot check this" notice', async ({ page }) => {
  const found = findItem((f) => f.item.check.kind === 'self-check' && f.item.kind === 'unit', 'a self-check item');
  const item = await open(page, found);
  await expect(item.locator('[data-cannot-check]')).toHaveText(/The site cannot check this one\./);
  await expect(item.locator('fieldset[data-self-check] input[type="checkbox"]')).toHaveCount((found.item.check as { requirements: string[] }).requirements.length);
  await expect(item.locator('[data-check-item]')).toHaveCount(0);
  await expect(item.locator('[data-run-item]')).toHaveCount(1);
  await setCode(page, item, 'print("made by me")\n');
  await item.locator('[data-run-item]').click();
  await expect(item.locator('[data-result] .io-output code')).toHaveText('made by me', { timeout: 60_000 });
  await expect(item.locator('[data-result] .verdict')).toHaveCount(0);
});

test('also_check: the requirements the check cannot see are listed beside the automatic check', async ({ page }) => {
  const found = findItem((f) => (f.item.also_check?.length ?? 0) > 0 && f.item.check.kind !== 'self-check', 'an item with also_check');
  const item = await open(page, found);
  await expect(item.locator('[data-check-item], form[data-answer-form]')).toHaveCount(1);
  const list = item.locator('fieldset[data-also-check]');
  await expect(list.locator('legend')).toHaveText('Also check yourself');
  await expect(list.locator('input[type="checkbox"]')).toHaveCount(found.item.also_check!.length);
});

test('the turtle rule: three verdicts and the drawing; an open path fails "closed path"', async ({ page }) => {
  const found = await turtleItem(page);
  const item = await open(page, found);
  await setCode(page, item, 'import turtle\nt = turtle.Turtle()\nfor _ in range(4):\n    t.forward(50)\n    t.left(90)\n');
  await check(item);
  const rows = await caseRows(item);
  expect(rows.filter((r) => r.startsWith('Turtle: '))).toEqual(['Turtle: draws: passed', 'Turtle: moves: passed', 'Turtle: closed path: passed']);
  await expect(item.locator('[data-result] svg.turtle-figure line')).toHaveCount(4);
  await setCode(page, item, 'import turtle\nt = turtle.Turtle()\nt.forward(50)\nt.left(90)\nt.forward(50)\n');
  await check(item);
  expect((await caseRows(item)).find((r) => r.startsWith('Turtle: closed path'))).toMatch(/^Turtle: closed path: (?!passed)/);
});

// ---------------------------------------------------------------------------------------------
// Answer gating

test('an odd exercise\'s answer: absent before an attempt and after opening the editor, shown after a FAILED Check', async ({ page }) => {
  const found = findItem((f) => f.item.answer_visibility === 'after-attempt' && f.item.check.kind === 'asserts' && f.item.kind === 'unit', 'an odd asserts exercise');
  const answers: string[] = [];
  page.on('request', (r) => {
    if (r.url().includes('/practice/answer/')) answers.push(r.url());
  });
  const item = await open(page, found);
  const slot = item.locator('[data-answer-slot]');
  await expect(slot).toBeHidden();
  await expect(slot).toBeEmpty();
  // Open the editor and type: still no answer.
  await setCode(page, item, 'x = 1\n');
  await page.waitForTimeout(300);
  await expect(slot).toBeEmpty();
  expect(answers).toEqual([]);
  const answerUrl = (await item.getAttribute('data-answer-href'))!;
  const projection = (await (await page.request.get(answerUrl)).json()) as { html: string };
  const text = projection.html.replace(/<[^>]+>/g, '').trim().slice(0, 40);
  expect((await page.content()).includes(text)).toBe(false);

  expect(await check(item)).toMatch(/^Not yet/);
  await expect(slot).toBeVisible();
  await expect(slot.locator('h3')).toHaveText('Answer');
  expect(answers).toHaveLength(1);
  await expect(slot.locator('.answer-body')).toContainText(text.slice(0, 20));

  // It stays unlocked on this device after a reload (the attempt is stored).
  await page.reload();
  await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
  await expect(section(page, found).locator('[data-answer-slot]')).toBeVisible();
});

test('an even exercise never shows an answer, even after a Check', async ({ page }) => {
  const found = findItem((f) => f.item.answer_visibility === 'none' && f.item.kind === 'unit' && f.item.check.kind === 'asserts', 'an even asserts exercise');
  const answers: string[] = [];
  page.on('request', (r) => {
    if (r.url().includes('/practice/answer/')) answers.push(r.url());
  });
  const item = await open(page, found);
  await expect(item.locator('[data-answer-slot]')).toHaveCount(0);
  expect(await item.getAttribute('data-answer-href')).toBeNull();
  await setCode(page, item, 'pass\n');
  await check(item);
  await expect(item.locator('[data-answer-slot]')).toHaveCount(0);
  expect(answers).toEqual([]);
});

test('an odd self-check exercise\'s answer shows after a Run plus the checklist marked done, not before', async ({ page }) => {
  const found = findItem(
    (f) => f.item.answer_visibility === 'after-attempt' && f.item.check.kind === 'self-check' && (f.item.check as { requirements: string[] }).requirements.length >= 2,
    'an odd self-check exercise',
  );
  const item = await open(page, found);
  const slot = item.locator('[data-answer-slot]');
  const boxes = item.locator('fieldset[data-self-check] input[type="checkbox"]');
  // The checklist alone is not an attempt.
  const count = await boxes.count();
  for (let i = 0; i < count; i++) await boxes.nth(i).check();
  await page.waitForTimeout(300);
  await expect(slot).toBeEmpty();
  await boxes.nth(0).uncheck();
  // A Run alone is not either.
  await setCode(page, item, 'print("draft")\n');
  await item.locator('[data-run-item]').click();
  await expect(item.locator('[data-result] .io-output code')).toHaveText('draft', { timeout: 60_000 });
  await page.waitForTimeout(300);
  await expect(slot).toBeEmpty();
  // Both: the answer appears.
  await boxes.nth(0).check();
  await expect(slot).toBeVisible();
  await expect(slot.locator('h3')).toHaveText('Answer');
});

// ---------------------------------------------------------------------------------------------
// The editor under the CSP, progress, and the reading view

test('the code editor raises zero CSP violations while it is opened, typed in, scrolled and highlighted', async ({ context, page }) => {
  const csp = await watchCsp(context);
  const found = findItem((f) => f.item.check.kind === 'asserts' && f.item.starter.trim() !== '', 'an asserts item with a starter');
  const item = await open(page, found);
  await item.locator('[data-work][data-editor-ready]').waitFor();
  const content = item.locator('.cm-content');
  await expect(content).toHaveAttribute('contenteditable', 'true');
  await content.click();
  await page.keyboard.press('ControlOrMeta+End');
  await page.keyboard.type('\ndef shout(word):\n# typed\nreturn word.upper() + "!"\n');
  for (let i = 0; i < 40; i++) await page.keyboard.press('Enter');
  await page.keyboard.type('print(shout("hi"), 42, True)');
  await item.locator('.cm-scroller').evaluate((el) => el.scrollTo(0, el.scrollHeight));
  await item.locator('.cm-scroller').evaluate((el) => el.scrollTo(0, 0));
  await page.mouse.wheel(0, 400);
  // Highlighted: keyword, string and number tokens carry highlight classes.
  const highlighted = await item.locator('.cm-line span[class]').count();
  expect(highlighted).toBeGreaterThan(3);
  // The editor's styles are constructable stylesheets in its shadow root, never a <style> element.
  const sheets = await item.locator('.code-editor').evaluate((host) => ({
    adopted: host.shadowRoot!.adoptedStyleSheets.length,
    styleTags: host.shadowRoot!.querySelectorAll('style').length + document.querySelectorAll('style').length,
  }));
  expect(sheets.adopted).toBeGreaterThan(0);
  expect(sheets.styleTags).toBe(0);
  await page.waitForTimeout(300);
  expect(csp.violations).toEqual([]);
  expect(csp.console).toEqual([]);
});

test('a Check writes an event with its cases and keeps the code only in the attempt store', async ({ page }) => {
  const found = findItem((f) => f.item.check.kind === 'asserts' && f.item.kind === 'checkpoint', 'a checkpoint asserts item');
  const item = await open(page, found);
  const code = 'secret_marker_value = 4242\n';
  await setCode(page, item, code);
  await check(item);
  const db = await stores(page);
  const events = db.events!.filter((e) => e.item_key === found.item.key);
  expect(events).toHaveLength(1);
  expect(events[0]).toMatchObject({ kind: 'checkpoint', schema: 'py4kids/progress-event/1.0.0' });
  expect(Array.isArray((events[0]!.detail as { cases: unknown }).cases)).toBe(true);
  expect(JSON.stringify(db.events)).not.toContain('secret_marker_value');
  const attempts = db.attempts!.filter((a) => a.item_key === found.item.key);
  expect(attempts).toHaveLength(1);
  expect(attempts[0]).toMatchObject({ kind: 'check', code });
  // The editor reopens with the last code.
  await page.reload();
  await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
  await expect(section(page, found).locator('textarea[data-code]')).toHaveValue(code);
});

test('the reading view: Run shows output, a prelude block replays its prelude, Reset clears, input() reads the box', async ({ page }) => {
  // A block that needs earlier cells: running it first replays them and gives the stored output.
  type B = { key: string; type: string; code?: string; output?: string; probe: string | null; prelude: string[]; stdin?: boolean; files: string[] };
  let target: { book: string; entry: string; block: B } | null = null;
  for (const book of ['python-projects', 'python-concepts']) {
    for (const file of readdirSync(join(CONTENT, book, 'entries')).sort()) {
      const entry = JSON.parse(readFileSync(join(CONTENT, book, 'entries', file), 'utf-8')) as { entry: { id: string }; lesson: { blocks: B[] } | null };
      const block = entry.lesson?.blocks.find(
        (b) => b.probe === 'prelude' && b.prelude.length > 0 && b.files.length === 0 && (b.output ?? '').trim() !== '' && !/input\(|random|turtle/.test(b.code ?? ''),
      );
      if (block) {
        target = { book, entry: entry.entry.id, block };
        break;
      }
    }
    if (target) break;
  }
  expect(target).not.toBeNull();
  const { book, entry, block } = target!;
  await page.goto(`/${book}/${entry}/`);
  const holder = page.locator(`[data-run][data-key="${block.key}"]`);
  await holder.scrollIntoViewIfNeeded();
  await holder.locator('[data-lesson-run]').click();
  const out = holder.locator('[data-run-output]');
  await expect(out.locator('.io-output code')).toHaveText(block.output!.replace(/\n$/, ''), { timeout: 60_000 });
  await expect(out).toContainText('the earlier code this example needs was run for you');
  const events = (await stores(page)).events!.filter((e) => e.kind === 'lesson-run');
  expect(events.map((e) => e.item_key)).toContain(block.key);
  // Reset clears the session; running again replays the prelude again.
  await holder.locator('[data-lesson-reset]').click();
  await expect(out).toContainText('Reset: Python starts fresh', { timeout: 60_000 });
  await holder.locator('[data-lesson-run]').click();
  await expect(out.locator('.io-output code')).toHaveText(block.output!.replace(/\n$/, ''), { timeout: 60_000 });

  // input(): the box feeds stdin.
  await page.goto('/usaco-bronze/unit-01-reading-the-input/');
  const tryit = page.locator('[data-run][data-stdin]').first();
  await tryit.scrollIntoViewIfNeeded();
  const box = tryit.locator('textarea.stdin-input');
  await expect(box).toBeVisible();
  await box.fill('3 4\n5 6\n7 8\n');
  await tryit.locator('[data-lesson-run]').click();
  await expect(tryit.locator('[data-run-output] .io-output, [data-run-output] .io-error').first()).toBeVisible({ timeout: 60_000 });
});

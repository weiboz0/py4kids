/**
 * Runner acceptance through the site's own UI (plan 104 Phase D; design 012 §3 "Runner
 * acceptance"): one named test per §3 row that is about what a student does on a page. (The
 * rows about the runner itself, stdin and EOF, the hang and restart paths, and CPython parity of
 * recursion and floats, are in runner.spec.ts, driving the real client.)
 *
 * Real items and lesson blocks are picked from the exported bundles at test time. Where a row
 * needs a program or an item the books do not have (the pinned hash vectors' own item keys, a set
 * of asserts with a known mix of verdicts, a lesson block that reads its mounted file, a block
 * that swallows the interrupt), the projection the page fetches is changed in flight
 * (`page.route`), and the island code under test is the site's own.
 */
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { expect, test, type Page } from '@playwright/test';
import type { ClientCheck, LessonRun } from '../src/lib/check-model';
import { CONTENT, findItem, fixturePairs, REPO, type Found } from './helpers/content';
import { caseRows, check, open, patchCheck, setCode } from './helpers/practice';
import { stores } from './helpers/site';

test.describe.configure({ mode: 'parallel' });

const small = (f: Found) => fixturePairs(f).reduce((n, c) => n + c.input.length + c.output.length, 0) < 150_000;

interface Vector {
  input: string;
  case: 'sensitive' | 'insensitive';
  normalised: string;
  item_key: string;
  hash: string;
}

test('§3 short-answer hashing and normalisation: every hash_vectors.json vector, typed and checked through the UI', async ({ page }) => {
  const vectors = JSON.parse(readFileSync(join(REPO, 'tools', 'export', 'hash_vectors.json'), 'utf-8')) as Vector[];
  expect(vectors.length).toBeGreaterThan(20);
  const found = findItem((f) => f.item.check.kind === 'answer', 'an answer item');
  let current: Vector = vectors[0]!;
  // The page carries the vector's own item key (the hash's salt), and its check projection the
  // vector's pinned hash and case rule, so the pinned hash itself is what the page must reproduce.
  await page.route(`**${found.page}`, async (route) => {
    const response = await route.fetch();
    const html = (await response.text()).replaceAll(`data-item-key="${found.item.key}"`, `data-item-key="${current.item_key}"`);
    await route.fulfill({ response, body: html });
  });
  await page.route(`**${found.page}check/*.json`, async (route) => {
    const response = await route.fetch();
    const c = (await response.json()) as ClientCheck;
    if (c.key !== found.item.key) return route.fulfill({ response });
    await route.fulfill({ response, json: { ...c, key: current.item_key, hash: current.hash, format: { case: current.case, hint: '' } } });
  });
  for (const vector of vectors) {
    current = vector;
    await page.goto(found.page);
    await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
    const item = page.locator(`section.practice-item[data-item-key="${vector.item_key}"]`);
    await item.scrollIntoViewIfNeeded();
    const box = item.locator('textarea[data-answer]');
    const submit = item.locator('form[data-answer-form] button[type="submit"]');
    const what = `vector ${vector.item_key} ${JSON.stringify(vector.input)}`;
    if (vector.normalised === '') {
      // A blank answer is never checked: the page asks for one (and records nothing).
      await box.fill(vector.input);
      await submit.click();
      await expect(item.locator('[data-result]'), what).toContainText('Type your answer first.');
      await expect(item.locator('[data-result] .verdict'), what).toHaveCount(0);
      continue;
    }
    await box.fill(vector.input);
    await submit.click();
    await expect(item.locator('[data-result] .verdict'), what).toHaveText('Correct.');
    // The normalised form is accepted too, and a different answer is not.
    await box.fill(vector.normalised);
    await submit.click();
    await expect(item.locator('[data-result] .verdict'), what).toHaveText('Correct.');
    await box.fill(`${vector.normalised}?`);
    await submit.click();
    await expect(item.locator('[data-result] .verdict'), what).toHaveText(/^Not yet/);
  }
});

test('§3 function-assert isolation: one failing assert does not stop the others, and no assert source reaches the DOM', async ({ page }) => {
  const found = findItem((f) => f.item.check.kind === 'asserts' && !f.item.check.turtle && f.item.files.length === 0, 'an asserts item');
  const asserts = [
    'assert double(2) == 5  # SECRET-ASSERT-1',
    'assert double(2) == 4  # SECRET-ASSERT-2',
    'assert undefined_helper(3)  # SECRET-ASSERT-3',
    'assert double(-1) == -2  # SECRET-ASSERT-4',
    'assert 1 / 0  # SECRET-ASSERT-5',
    'assert double(0) == 0  # SECRET-ASSERT-6',
  ];
  await patchCheck(page, found, (c) => ({ ...c, kind: 'asserts', asserts }) as ClientCheck);
  const item = await open(page, found);
  await setCode(page, item, 'def double(x):\n    return x * 2\n');
  expect(await check(item)).toMatch(/^Not yet/);
  const rows = (await caseRows(item)).filter((r) => r.startsWith('Test '));
  expect(rows).toEqual([
    'Test 1: assertion failed',
    'Test 2: passed',
    "Test 3: NameError: name 'undefined_helper' is not defined",
    'Test 4: passed',
    'Test 5: ZeroDivisionError: division by zero',
    'Test 6: passed',
  ]);
  const html = await page.content();
  expect(html).not.toContain('SECRET-ASSERT');
  expect(html).not.toContain('undefined_helper(3)');
  expect(JSON.stringify(await stores(page))).not.toContain('SECRET-ASSERT');
});

test('§3 turtle directives: a closed path passes; open-path allows an open one; no pen-down move and too many moves fail', async ({ page }) => {
  const found = findItem((f) => f.item.check.turtle && (f.item.check.kind === 'expected-output' || f.item.check.kind === 'asserts'), 'a turtle item');
  const item = await open(page, found);
  const turtleRows = async (code: string) => {
    await setCode(page, item, code);
    await check(item, 120_000);
    return Object.fromEntries((await caseRows(item)).filter((r) => r.startsWith('Turtle: ')).map((r) => [r.replace(/^Turtle: ([^:]+): .*$/, '$1'), r.replace(/^Turtle: [^:]+: /, '')]));
  };
  const head = 'import turtle\nt = turtle.Turtle()\n';
  expect(await turtleRows(`${head}for _ in range(3):\n    t.forward(60)\n    t.left(120)\n`)).toEqual({ draws: 'passed', moves: 'passed', 'closed path': 'passed' });
  // An open path fails the closed-path part, unless the directive comment allows it.
  const openPath = `${head}t.forward(60)\nt.left(90)\nt.forward(30)\n`;
  expect((await turtleRows(openPath))['closed path']).toMatch(/^path does not close/);
  expect(await turtleRows(`# turtle-check: open-path\n${openPath}`)).toEqual({ draws: 'passed', moves: 'passed', 'closed path': 'passed' });
  // Moves with the pen up draw nothing.
  expect((await turtleRows(`${head}t.penup()\nfor _ in range(4):\n    t.forward(40)\n    t.left(90)\n`)).draws).toBe('no pen-down move');
  // 10,000 moves or more is too many (a closed square traced 2,500 times).
  const many = await turtleRows(`${head}for _ in range(2500):\n    for _ in range(4):\n        t.forward(1)\n        t.left(90)\n`);
  expect(many.moves).toMatch(/^\d+ moves \(must be fewer than 10000\)$/);
  expect(many.draws).toBe('passed');
});

/** A lesson block with mounted files (an asset program the lesson shows), and the lesson. */
function assetBlock(): { book: string; entry: string; key: string; path: string; bundle: string } {
  for (const book of ['python-projects', 'python-concepts']) {
    for (const file of readdirSync(join(CONTENT, book, 'entries')).sort()) {
      const entry = JSON.parse(readFileSync(join(CONTENT, book, 'entries', file), 'utf-8')) as {
        entry: { id: string };
        lesson: { blocks: { key: string; type: string; files: string[]; code?: string }[] } | null;
      };
      const block = entry.lesson?.blocks.find((b) => b.files.length === 1 && b.files[0]!.endsWith('.py') && /import turtle/.test(b.code ?? ''));
      if (block) {
        const bundle = block.files[0]!;
        return { book, entry: entry.entry.id, key: block.key, path: bundle.replace(/^files\/[^/]+\//, ''), bundle };
      }
    }
  }
  throw new Error('no lesson block with a mounted file');
}

async function lessonOut(page: Page, key: string) {
  const holder = page.locator(`[data-run][data-key="${key}"]`);
  await holder.scrollIntoViewIfNeeded();
  return { holder, run: holder.locator('[data-lesson-run]'), out: holder.locator('[data-run-output]') };
}

test('§3 mounted asset files: a lesson block runs with its file mounted, and a cell reads the mounted file', async ({ page }) => {
  const asset = assetBlock();
  const text = readFileSync(join(CONTENT, asset.book, asset.bundle), 'utf-8');
  // 1. The real block: the asset program runs and draws.
  await page.goto(`/${asset.book}/${asset.entry}/`);
  let block = await lessonOut(page, asset.key);
  await block.run.click();
  await expect(block.out.locator('svg.turtle-figure')).toBeVisible({ timeout: 60_000 });
  await expect(block.out.locator('.io-error')).toHaveCount(0);
  // 2. The same block, its code a cell that reads the mounted file (projection changed in flight).
  const reader = [
    'import os',
    `with open(${JSON.stringify(asset.path)}, encoding="utf-8") as f:`,
    '    text = f.read()',
    'print(text.splitlines()[0])',
    'print(len(text), text.count("\\n"))',
  ].join('\n');
  await page.route(`**/${asset.book}/${asset.entry}/run.json`, async (route) => {
    const response = await route.fetch();
    const data = (await response.json()) as LessonRun;
    data.blocks[asset.key] = { ...data.blocks[asset.key]!, code: reader };
    await route.fulfill({ response, json: data });
  });
  await page.goto(`/${asset.book}/${asset.entry}/`);
  block = await lessonOut(page, asset.key);
  await block.run.click();
  const expected = `${text.split('\n')[0]}\n${[...text].length} ${text.split('\n').length - 1}`;
  await expect(block.out.locator('.io-output code')).toHaveText(expected, { timeout: 60_000 });
});

interface LessonBlock {
  key: string;
  type: string;
  code?: string;
  output?: string;
  probe: string | null;
  prelude: string[];
  files: string[];
}

test('§3 cumulative lesson state: a prelude block replays its prelude, and again after a forced worker restart', async ({ page }) => {
  let target: { book: string; entry: string; block: LessonBlock; other: LessonBlock } | null = null;
  for (const book of ['python-projects', 'python-concepts']) {
    for (const file of readdirSync(join(CONTENT, book, 'entries')).sort()) {
      const entry = JSON.parse(readFileSync(join(CONTENT, book, 'entries', file), 'utf-8')) as { entry: { id: string }; lesson: { blocks: LessonBlock[] } | null };
      const blocks = entry.lesson?.blocks ?? [];
      const block = blocks.find(
        (b) => b.probe === 'prelude' && b.prelude.length > 0 && b.files.length === 0 && (b.output ?? '').trim() !== '' && !/input\(|random|turtle/.test(b.code ?? ''),
      );
      const other = block && blocks.find((b) => b.type === 'code' && b.key !== block.key && !block.prelude.includes(b.key) && (b.code ?? '').trim() !== '');
      if (block && other) {
        target = { book, entry: entry.entry.id, block, other };
        break;
      }
    }
    if (target) break;
  }
  expect(target).not.toBeNull();
  const { book, entry, block, other } = target!;
  // The other block becomes one that swallows the interrupt, so the runner must restart Python.
  const swallow = 'while True:\n    try:\n        while True:\n            pass\n    except KeyboardInterrupt:\n        pass\n';
  await page.route(`**/${book}/${entry}/run.json`, async (route) => {
    const response = await route.fetch();
    const data = (await response.json()) as LessonRun;
    data.budget_ms = 1000;
    data.blocks[other.key] = { code: swallow, prelude: [], stdin: false, sample_input: '', files: [] };
    await route.fulfill({ response, json: data });
  });
  await page.goto(`/${book}/${entry}/`);
  const stored = block.output!.replace(/\n$/, '');
  const t = await lessonOut(page, block.key);
  // 1. Cumulative state: the block's earlier cells run first (silently), then the block.
  await t.run.click();
  await expect(t.out.locator('.io-output code')).toHaveText(stored, { timeout: 60_000 });
  await expect(t.out).toContainText('the earlier code this example needs was run for you');
  // 2. Run again: the state is kept, so nothing is replayed.
  await t.run.click();
  await expect(t.out.locator('.io-output code')).toHaveText(stored, { timeout: 60_000 });
  await expect(t.out).not.toContainText('earlier code');
  // 3. Force a worker restart from another block of the same lesson.
  const o = await lessonOut(page, other.key);
  await o.run.click();
  await expect(o.out).toContainText('Python had to restart to stop your program', { timeout: 30_000 });
  await expect(o.out).toContainText('Everything this lesson ran before was cleared.');
  // 4. The block replays its prelude in the new Python and gives the stored output again.
  await t.run.click();
  await expect(t.out.locator('.io-output code')).toHaveText(stored, { timeout: 60_000 });
  await expect(t.out).toContainText('the earlier code this example needs was run for you');
});

test('§3 process state: fixture case 1 mutates modules and seeds random; case 2 of the same item sees none of it', async ({ page }) => {
  const found = findItem(
    (f) => f.book === 'usaco-bronze' && f.item.check.kind === 'fixtures' && f.item.check.cases.length >= 3 && small(f),
    'a usaco item with three cases',
    (f) => (f.item.check as { cases: unknown[] }).cases.length,
  );
  const pairs = fixturePairs(found);
  const ordered = [...pairs.filter((c) => c.sample), ...pairs.filter((c) => !c.sample)];
  const table = Object.fromEntries(pairs.map((c) => [c.input, c.output]));
  const code = [
    'import builtins, json, math, random, sys',
    `T = json.loads(${JSON.stringify(JSON.stringify(table))})`,
    `FIRST = json.loads(${JSON.stringify(JSON.stringify(ordered[0]!.input))})`,
    'data = sys.stdin.read()',
    'if data == FIRST:',
    '    math.pi = 3',
    '    sys.path.append("x")',
    '    random.seed(1)',
    '    sys.stdout.write(T[data])',
    '    builtins.print = None',
    'else:',
    '    clean = (math.pi == 3.141592653589793 and callable(builtins.print)',
    '             and "x" not in sys.path and random.random() != 0.13436424411240122)',
    '    sys.stdout.write(T[data] if clean else "contaminated\\n")',
    '',
  ].join('\n');
  const item = await open(page, found);
  await setCode(page, item, code);
  expect(await check(item)).toMatch(/^Passed/);
  const rows = await caseRows(item);
  expect(rows).toHaveLength(ordered.length);
  for (const row of rows) expect(row).toMatch(/: passed$/);
});

/**
 * The practice checks' projections and rules (plan 104 Phase B): what a check island may fetch
 * (src/lib/checks.ts) and the pure rules it applies (src/lib/check-model.ts): budgets, case order,
 * outcomes, event kinds and the odd-answer gate.
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBook, loadBooks, repoRoot } from '../src/lib/bundle';
import {
  answerUnlocked,
  caseBudget,
  eventKindOf,
  NO_ATTEMPT,
  orderCases,
  outcomeOf,
  verdictText,
  type ClientCheck,
} from '../src/lib/check-model';
import {
  answerProjection,
  bundleFiles,
  checkProjection,
  clientFile,
  itemAnchors,
  itemRoutes,
  lessonRunProjection,
  shipsAnswer,
  splitAsserts,
} from '../src/lib/checks';
import { practiceView, readingView, renderBlock } from '../src/lib/entry';
import type { Block, Item } from '../src/lib/types';

const FIXTURE = join(import.meta.dirname, 'fixtures', 'bundles', 'demo');
const CONTENT = join(repoRoot(), 'site', 'content');
const books = existsSync(CONTENT) ? loadBooks({ contentDir: CONTENT }) : [];

const item = (over: Partial<Item>): Item => ({
  key: 'demo/unit-01-demo/exercises/e9',
  kind: 'unit',
  number: 9,
  label: 'Exercise 9',
  title: '',
  division: [],
  stretch: false,
  concepts: [],
  statement_md: 'Do it.',
  starter: '',
  files: [],
  check: { kind: 'self-check', requirements: ['It works.'], turtle: false, confirmed: true },
  answer_visibility: 'none',
  before: [],
  ...over,
});

describe('splitAsserts', () => {
  it('splits one assert per line', () => {
    expect(splitAsserts('assert f(1) == 2\nassert f(2) == 4\n')).toEqual(['assert f(1) == 2', 'assert f(2) == 4']);
  });

  it('keeps bracketed, indented, continued and triple-quoted statements whole', () => {
    const source = [
      'assert f([',
      '    1, 2,',
      ']) == 3',
      '',
      '# a comment',
      'assert g("a)b") == \\',
      '    1',
      'xs = """',
      'assert inside',
      '"""',
      'assert len(xs) > 0',
    ].join('\n');
    expect(splitAsserts(source)).toEqual([
      'assert f([\n    1, 2,\n]) == 3',
      'assert g("a)b") == \\\n    1',
      'xs = """\nassert inside\n"""',
      'assert len(xs) > 0',
    ]);
  });

  it.skipIf(books.length === 0)('splits every real asserts check into at least one statement, losing no line', () => {
    for (const r of itemRoutes(books)) {
      const check = r.item.check;
      if (check.kind !== 'asserts') continue;
      const parts = splitAsserts(check.source);
      expect(parts.length, r.item.key).toBeGreaterThan(0);
      const kept = (text: string) => text.split('\n').map((l) => l.trim()).filter((l) => l !== '' && !l.startsWith('#'));
      expect(parts.flatMap(kept), r.item.key).toEqual(kept(check.source));
    }
  });
});

describe('budgets and verdicts', () => {
  it('budgets a case at max(1 s, 10x cpu_ms), capped at 10 s; 5 s without a measurement', () => {
    expect(caseBudget(undefined)).toBe(5000);
    expect(caseBudget(20)).toBe(1000);
    expect(caseBudget(300)).toBe(3000);
    expect(caseBudget(5000)).toBe(10_000);
    expect(caseBudget(-1)).toBe(5000);
  });

  it('runs sample cases first, keeping bundle order', () => {
    const cases = [
      { n: 1, sample: false },
      { n: 2, sample: true },
      { n: 3, sample: false },
    ];
    expect(orderCases(cases).map((c) => c.n)).toEqual([2, 1, 3]);
  });

  it('summarises cases as pass, fail, partial, or error when none ran', () => {
    expect(outcomeOf([{ pass: true }, { pass: true }])).toBe('pass');
    expect(outcomeOf([{ pass: false }])).toBe('fail');
    expect(outcomeOf([{ pass: true }, { pass: false }])).toBe('partial');
    expect(outcomeOf([])).toBe('error');
    expect(verdictText(true, '')).toBe('passed');
    expect(verdictText(false, '')).toBe('wrong output');
    expect(verdictText(false, 'time limit')).toBe('time limit');
  });

  it('writes exercise, checkpoint and project events by item kind', () => {
    expect(eventKindOf('unit')).toBe('exercise');
    expect(eventKindOf('challenge')).toBe('exercise');
    expect(eventKindOf('checkpoint')).toBe('checkpoint');
    expect(eventKindOf('project')).toBe('project');
  });
});

describe('the odd-answer gate', () => {
  const coded = { gated: true, kind: 'fixtures' as const };
  const selfCheck = { gated: true, kind: 'self-check' as const };

  it('stays shut before an attempt, and for an item that ships no answer', () => {
    expect(answerUnlocked(coded, NO_ATTEMPT)).toBe(false);
    expect(answerUnlocked({ gated: false, kind: 'answer' }, { ...NO_ATTEMPT, checks: 3, answers: 2 })).toBe(false);
  });

  it('opens after one Check run (any verdict) or one submitted answer', () => {
    expect(answerUnlocked(coded, { ...NO_ATTEMPT, checks: 1 })).toBe(true);
    expect(answerUnlocked({ gated: true, kind: 'answer' }, { ...NO_ATTEMPT, answers: 1 })).toBe(true);
    // A Run alone is not a check.
    expect(answerUnlocked(coded, { ...NO_ATTEMPT, runs: 4 })).toBe(false);
  });

  it('opens a self-check item only after a Run plus the checklist marked done', () => {
    expect(answerUnlocked(selfCheck, { ...NO_ATTEMPT, runs: 1 })).toBe(false);
    expect(answerUnlocked(selfCheck, { ...NO_ATTEMPT, checklistDone: true })).toBe(false);
    expect(answerUnlocked(selfCheck, { ...NO_ATTEMPT, runs: 1, checklistDone: true })).toBe(true);
  });
});

describe('check projections', () => {
  it('carries a typed item\'s hash and format, never its answer or program', () => {
    const typed = item({
      check: {
        kind: 'predict',
        hash: `sha256:${'a'.repeat(64)}`,
        answer_format: { case: 'sensitive', hint: 'one line', aliases: { '^': '↑' }, whitespace: 'exact' },
        program: 'print(1)',
        turtle: false,
        confirmed: true,
      },
      answer_visibility: 'after-attempt',
      answer_md: 'It prints 1.',
    });
    const projection = checkProjection('demo', typed);
    expect(projection).toEqual({
      key: typed.key,
      turtle: false,
      kind: 'predict',
      hash: `sha256:${'a'.repeat(64)}`,
      format: { case: 'sensitive', hint: 'one line', aliases: { '^': '↑' }, whitespace: 'exact' },
    });
    expect(JSON.stringify(projection)).not.toMatch(/answer_md|program|It prints/);
  });

  it('lists fixture cases sample first, by file URL, with skipped (over-budget) cases marked', () => {
    const fixtures = item({
      check: {
        kind: 'fixtures',
        cases: [
          { n: 1, in_file: 'files/unit-01-demo/fixtures/q1/1.in', out_file: 'files/unit-01-demo/fixtures/q1/1.out', sample: false },
          { n: 2, in_file: 'files/unit-01-demo/fixtures/q1/2.in', out_file: 'files/unit-01-demo/fixtures/q1/2.out', sample: true },
        ],
        match: 'line',
        over_budget: [1],
        cpu_ms: 250,
        turtle: false,
        confirmed: true,
      },
    });
    const projection = checkProjection('demo', fixtures) as Extract<ClientCheck, { kind: 'fixtures' }>;
    expect(projection.cases).toEqual([
      { n: 2, sample: true, input: '/demo/files/unit-01-demo/fixtures/q1/2.in', expected: '/demo/files/unit-01-demo/fixtures/q1/2.out', skipped: false },
      { n: 1, sample: false, input: '/demo/files/unit-01-demo/fixtures/q1/1.in', expected: '/demo/files/unit-01-demo/fixtures/q1/1.out', skipped: true },
    ]);
    expect(projection.budget_ms).toBe(2500);
    expect(projection.match).toBe('line');
  });

  it('splits asserts for the runner and mounts item files at their path in the entry', () => {
    const asserts = item({
      files: ['files/unit-01-demo/assets/data.txt'],
      check: { kind: 'asserts', source: 'assert f(1) == 1\nassert f(2) == 2', functions: ['f'], turtle: true, confirmed: true },
    });
    expect(checkProjection('demo', asserts)).toMatchObject({
      kind: 'asserts',
      asserts: ['assert f(1) == 1', 'assert f(2) == 2'],
      turtle: true,
      files: [{ path: 'assets/data.txt', url: '/demo/files/unit-01-demo/assets/data.txt' }],
    });
    expect(() => clientFile('demo', 'assets/x')).toThrow();
  });

  it('answers only for odd unit exercises, rendered without raw LaTeX, with turtle drawings', () => {
    const odd = item({
      answer_visibility: 'after-attempt',
      answer_md: 'Use `print`.\n\n```{=latex}\n\\begin{tikzpicture}\\end{tikzpicture}\n```\n',
      answer_figures: [[{ x1: 0, y1: 0, x2: 10, y2: 0, color: 'red', width: 2 }]],
    });
    expect(shipsAnswer(odd)).toBe(true);
    const answer = answerProjection(odd)!;
    expect(answer.html).toContain('<code>print</code>');
    expect(answer.html).not.toMatch(/tikz|=latex/);
    expect(answer.figures).toHaveLength(1);
    expect(answer.figures[0]).toMatch(/^<svg class="turtle-figure"[^>]* aria-label="Answer drawing for Exercise 9"/);
    expect(answerProjection(item({ answer_visibility: 'none' }))).toBeNull();
    expect(answerProjection(item({ ...odd, kind: 'checkpoint' }))).toBeNull();
    expect(answerProjection(item({ ...odd, kind: 'project' }))).toBeNull();
    // No answer_figures (before plan 104 Phase C): the answer renders without drawings.
    expect(answerProjection(item({ ...odd, answer_figures: undefined }))!.figures).toEqual([]);
  });

  it.skipIf(books.length === 0)('on the real bundles: an answer projection exactly for after-attempt unit items, none leaking into checks', () => {
    let answers = 0;
    for (const r of itemRoutes(books)) {
      const projection = checkProjection(r.book, r.item);
      const text = JSON.stringify(projection);
      expect(text).not.toMatch(/"(?:answer_md|source|program|out_file)"/);
      if (r.item.answer_md && r.item.answer_md.trim().length > 20) expect(text.includes(r.item.answer_md), r.item.key).toBe(false);
      const answer = answerProjection(r.item);
      expect(answer !== null, r.item.key).toBe(r.item.kind === 'unit' && r.item.answer_visibility === 'after-attempt');
      if (answer) {
        answers++;
        expect(answer.html).not.toContain('{=latex}');
      }
      if (projection.kind === 'fixtures') {
        const firstHidden = projection.cases.findIndex((c) => !c.sample);
        expect(projection.cases.slice(firstHidden < 0 ? projection.cases.length : firstHidden).every((c) => !c.sample)).toBe(true);
      }
    }
    expect(answers).toBeGreaterThan(0);
  });

  it.skipIf(books.length === 0)('serves every file a projection names', () => {
    for (const book of books) {
      const served = new Set(bundleFiles(book).map((p) => `/${book.id}/${p}`));
      for (const r of itemRoutes([book])) {
        const p = checkProjection(r.book, r.item);
        const urls = [...('files' in p ? p.files.map((f) => f.url) : []), ...(p.kind === 'fixtures' ? p.cases.flatMap((c) => [c.input, c.expected]) : [])];
        for (const url of urls) expect(served.has(url), url).toBe(true);
      }
    }
  });
});

describe('lesson runs', () => {
  const demo = loadBook(FIXTURE);
  const block = (over: Partial<Block>): Block => ({
    key: 'demo/unit-01-demo/lesson/x',
    type: 'code',
    code: 'print(1)\n',
    needs_prelude: false,
    prelude: [],
    files: [],
    concepts: [],
    probe: 'standalone',
    tags: [],
    ...over,
  });

  it('marks runnable lesson blocks, with an input box for input()', () => {
    expect(renderBlock(block({}), 'H', { runnable: true })).toContain('data-run>');
    expect(renderBlock(block({ type: 'tryit', stdin: true }), 'H', { runnable: true })).toContain('data-run data-stdin>');
    expect(renderBlock(block({}), 'H')).not.toContain('data-run');
    expect(renderBlock(block({ type: 'prose', code: undefined, md: 'Hi' }), 'H', { runnable: true })).not.toContain('data-run');
    expect(readingView(demo, 'unit-01-demo').runHref).toBe('/demo/unit-01-demo/run.json');
    expect(readingView(demo, 'unit-01-demo').blocks.join('')).toContain('data-run');
  });

  it('labels a mismatch block\'s stored output "may differ when you run it"', () => {
    expect(renderBlock(block({ probe: 'mismatch', output: '0.42\n' }), 'H')).toContain('Output (may differ when you run it)');
    expect(renderBlock(block({ output: '1\n' }), 'H')).not.toContain('may differ');
  });

  it('projects the runnable blocks with their prelude and files', () => {
    const run = lessonRunProjection(demo, demo.entries[0]!)!;
    expect(run.session).toBe('unit-01-demo');
    expect(Object.keys(run.blocks)).toEqual(['demo/unit-01-demo/lesson/c2', 'demo/unit-01-demo/lesson/c3']);
    expect(run.blocks['demo/unit-01-demo/lesson/c2']).toEqual({ code: "print('hi')\n", prelude: [], stdin: false, sample_input: '', files: [] });
  });

  it.skipIf(books.length === 0)('replays only prelude blocks that exist in the same lesson', () => {
    for (const book of books) {
      for (const entry of book.entries) {
        const run = lessonRunProjection(book, entry);
        if (!run) continue;
        for (const b of Object.values(run.blocks)) for (const key of b.prelude) expect(run.blocks[key], key).toBeDefined();
      }
    }
  });
});

describe('the practice view', () => {
  it('gives every item a check URL by anchor and an answer URL only when it ships one', () => {
    const demo = loadBook(FIXTURE);
    for (const entry of demo.entries) {
      const anchors = itemAnchors(entry.data.items);
      const view = practiceView(demo, entry.record.id);
      view.items.forEach((it, i) => {
        expect(it.checkHref).toBe(`/demo/${entry.record.id}/practice/check/${anchors[i]}.json`);
        expect(it.answerHref).toBe(shipsAnswer(entry.data.items[i]!) ? `/demo/${entry.record.id}/practice/answer/${anchors[i]}.json` : null);
      });
    }
  });

  it('lists also_check requirements beside an automatic check (plan 102 data)', () => {
    const demo = loadBook(FIXTURE);
    const entry = demo.entries.find((e) => e.record.id === 'checkpoint-01-demo')!;
    const source = entry.data.items[0]!;
    expect(source.check.kind).not.toBe('self-check');
    source.also_check = ['It prints a **friendly** greeting.', 'It uses a loop.'];
    const [view] = practiceView(demo, 'checkpoint-01-demo').items;
    expect(view!.alsoCheck).toEqual([
      { id: `${view!.anchor}-also-0`, index: 0, html: 'It prints a <strong>friendly</strong> greeting.' },
      { id: `${view!.anchor}-also-1`, index: 1, html: 'It uses a loop.' },
    ]);
    expect(view!.selfCheck).toBeNull();
  });

  it.skipIf(books.length === 0)('shows also_check beside an automatic check, and never on a self-check item', () => {
    for (const book of books) {
      for (const entry of book.entries.filter((e) => e.data.items.length > 0)) {
        const view = practiceView(book, entry.record.id);
        view.items.forEach((it, i) => {
          const source = entry.data.items[i]!;
          expect(it.alsoCheck?.length ?? 0).toBe(source.check.kind === 'self-check' ? 0 : (source.also_check?.length ?? 0));
          expect(it.editor).toBe(['fixtures', 'asserts', 'expected-output', 'self-check'].includes(source.check.kind));
          expect(it.typed).toBe(['answer', 'predict'].includes(source.check.kind));
        });
      }
    }
  });
});

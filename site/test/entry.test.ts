/** The reading view and practice page view models (plan 103 Phase B). */
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBook } from '../src/lib/bundle';
import {
  BLOCK_LABELS,
  checkLine,
  entryPaths,
  lastHeading,
  practicePaths,
  practiceView,
  readingView,
  renderBlock,
  renderBlocks,
  reportHref,
} from '../src/lib/entry';
import type { Block, Check } from '../src/lib/types';

const book = loadBook(join(import.meta.dirname, 'fixtures', 'bundles', 'demo'));

const block = (type: Block['type'], extra: Partial<Block> = {}): Block => ({
  key: `demo/u/lesson/${type}`,
  type,
  needs_prelude: false,
  prelude: [],
  files: [],
  concepts: [],
  probe: null,
  tags: [],
  ...extra,
});

describe('blocks', () => {
  it('labels try-it, error-demo and hang-demo blocks as the PDFs do', () => {
    expect(renderBlock(block('tryit', { code: 'x = input()' }), 'H')).toContain('<p class="panel-label">Try it yourself</p>');
    expect(renderBlock(block('error-demo', { code: '1/0' }), 'H')).toContain('<p class="panel-label">Read the error</p>');
    expect(renderBlock(block('hang-demo', { code: 'while True: pass' }), 'H')).toContain(
      '<p class="panel-label">Watch out: this never stops</p>',
    );
  });

  it('styles opener, goals, recap and notice blocks as panels', () => {
    for (const type of ['opener', 'goals', 'recap', 'notice'] as const) {
      const html = renderBlock(block(type, { md: 'Text.' }), 'H');
      expect(html).toContain(`class="block block-${type} panel panel-${type}"`);
      const label = BLOCK_LABELS[type];
      if (label) expect(html).toContain(`<p class="panel-label">${label}</p>`);
    }
  });

  it('shows a code block with its stored output under "Output"', () => {
    const html = renderBlock(block('code', { code: "print('hi')\n", output: 'hi\n' }), 'H');
    expect(html).toContain('class="shiki');
    expect(html).toContain('<p class="io-label">Output</p><pre class="output-text"><code>hi</code></pre>');
    expect(renderBlock(block('code', { code: 'x = 1' }), 'H')).not.toContain('Output');
  });

  it('escapes output and sample input', () => {
    const html = renderBlock(block('tryit', { code: 'print(input())', sample_input: '<b>', output: '<i>' }), 'H');
    expect(html).toContain('<p class="io-label">Sample input</p><pre class="output-text"><code>&lt;b&gt;</code></pre>');
    expect(html).toContain('&lt;i&gt;');
  });

  it('draws a turtle figure named for the nearest heading above it', () => {
    const blocks = [
      block('prose', { md: '## Lesson 1\n\n```python\n# Not a heading\n```\n\n### Your first `turtle` program' }),
      block('turtle-figure', { code: 'forward(10)', figure: [{ x1: 0, y1: 0, x2: 10, y2: 0, color: 'red', width: 1 }] }),
    ];
    const html = renderBlocks(blocks, 'Entry title')[1]!;
    expect(html).toContain('role="img" aria-label="Drawing for Your first turtle program"');
    expect(renderBlocks(blocks.slice(1), 'Entry title')[0]).toContain('aria-label="Drawing for Entry title"');
  });

  it('finds the last heading outside code fences', () => {
    expect(lastHeading('## A\n\n```python\n# comment\n```\n')).toBe('A');
    expect(lastHeading('No heading.')).toBeUndefined();
  });
});

describe('reading view', () => {
  it('renders a unit lesson with slides, practice and prev/next links', () => {
    const view = readingView(book, 'unit-01-demo');
    expect(view.blocks).toHaveLength(3);
    expect(view.slidesHref).toBe('/demo/unit-01-demo/slides/');
    expect(view.practiceHref).toBe('/demo/unit-01-demo/practice/');
    expect(view.prev).toBeNull();
    expect(view.next).toEqual({ href: '/demo/checkpoint-01-demo/', title: 'Checkpoint 1 — Demo' });
  });

  it('shows a lesson-less checkpoint\'s intro, without slides', () => {
    const view = readingView(book, 'checkpoint-01-demo');
    expect(view.hasLesson).toBe(false);
    expect(view.slidesHref).toBeNull();
    expect(view.blocks.join('')).toContain('Answer every question.');
    expect(view.prev?.href).toBe('/demo/unit-01-demo/');
  });

  it('lists every entry page and every practice page', () => {
    expect(entryPaths([book])).toEqual([
      { book: 'demo', entry: 'unit-01-demo' },
      { book: 'demo', entry: 'checkpoint-01-demo' },
    ]);
    expect(practicePaths([book])).toHaveLength(2);
  });
});

describe('practice page', () => {
  it('renders a self-check item as a checklist keyed by item', () => {
    const [item] = practiceView(book, 'unit-01-demo').items;
    expect(item!.anchor).toBe('exercise-1');
    expect(item!.selfCheck).toEqual([{ id: 'exercise-1-req-0', index: 0, html: 'It prints your name.' }]);
    // A code item opens its starter in the editor (plan 104), not as read-only code.
    expect(item!.editor).toBe(true);
    expect(item!.starter).toBeNull();
    expect(item!.starterCode).not.toBe('');
    expect(item!.checkKind).toBe('self-check');
    expect(item!.typed).toBe(false);
    expect(item!.checkHref).toBe('/demo/unit-01-demo/practice/check/exercise-1.json');
    expect(item!.statement).toBe('<p>Print your name.</p>\n');
  });

  it('gives a typed item an answer box with its format hint', () => {
    const view = practiceView(book, 'checkpoint-01-demo');
    expect(view.heading).toBe('Questions');
    const [item] = view.items;
    expect(item!.selfCheck).toBeNull();
    expect(item!.typed).toBe(true);
    expect(item!.editor).toBe(false);
    expect(item!.exact).toBe(false);
    expect(item!.eventKind).toBe('checkpoint');
    expect(item!.answerHref).toBeNull();
    expect(item!.formatHint).toBe('Type a number.');
    expect(item!.starter).toBeNull();
    expect(item!.checkLine).toContain('comparing your answer');
  });

  it('describes each check kind without reading a hidden field', () => {
    const base = { turtle: false, confirmed: true };
    const fmt = { case: 'insensitive' as const, hint: '' };
    const lines = ([
      { ...base, kind: 'fixtures', match: 'line', over_budget: [], cpu_ms: 100, cases: [
        { n: 1, in_file: 'a', out_file: 'b', sample: true },
        { n: 2, in_file: 'c', out_file: 'd', sample: false },
      ] },
      { ...base, kind: 'answer', hash: 'sha256:x', answer_format: fmt },
      { ...base, kind: 'expected-output', hash: 'sha256:x', answer_format: fmt },
      { ...base, kind: 'predict', hash: 'sha256:x', answer_format: fmt, program: 'SECRET' },
      { ...base, kind: 'asserts', source: 'SECRET', functions: ['area'] },
      { ...base, turtle: true, kind: 'self-check', requirements: [] },
    ] as Check[]).map(checkLine);
    expect(lines[0]).toBe('Checked by running your program on 2 test inputs (1 sample, 1 hidden) and comparing its output line by line.');
    expect(lines[1]).toContain('ignoring capital letters');
    expect(lines[4]).toBe('Checked by tests that run your function `area`.');
    expect(lines[5]).toContain('turtle drawing');
    expect(lines.join(' ')).not.toMatch(/SECRET|sha256/);
  });
});

describe('report a problem', () => {
  it('carries only the item key and the content hash', () => {
    const href = reportHref('demo/u/exercises/e1', 'sha256:abc');
    const url = new URL(href);
    expect(url.origin + url.pathname).toBe('https://github.com/weiboz0/py4kids/issues/new');
    expect([...url.searchParams.keys()]).toEqual(['title', 'body']);
    expect(url.searchParams.get('title')).toBe('Problem report: demo/u/exercises/e1');
    expect(url.searchParams.get('body')).toBe('Item: demo/u/exercises/e1\nContent: sha256:abc\n\nWhat is wrong:\n');
  });

  it('is on every reading view and practice item', () => {
    expect(readingView(book, 'unit-01-demo').reportHref).toContain('Content%3A%20sha256%3A0000');
    for (const item of practiceView(book, 'unit-01-demo').items) expect(item.reportHref).toContain(encodeURIComponent(item.key));
  });
});

/**
 * The slide rules and the slide audit (plan 103 D6, Phase C).
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBooks, repoRoot, type LoadedBook } from '../src/lib/bundle';
import { auditLoadedBook } from '../src/lib/slide-config';
import { renderSlideMarkdown, slideDecks } from '../src/lib/slide-view';
import {
  auditBook,
  auditPasses,
  buildSlides,
  countWords,
  DEFAULT_LIMITS,
  formatAudit,
  splitUnits,
  type SlideConfig,
} from '../src/lib/slides';
import type { Block, BlockType } from '../src/lib/types';

let n = 0;
function block(type: BlockType, body: string, extra: Partial<Block> = {}): Block {
  n += 1;
  const isProse = ['prose', 'opener', 'notice', 'goals', 'recap'].includes(type);
  return {
    key: `demo/unit-01-demo/lesson/c${n}`,
    type,
    ...(isProse ? { md: body } : { code: body }),
    needs_prelude: false,
    prelude: [],
    files: [],
    concepts: [],
    probe: null,
    tags: [],
    ...extra,
  };
}
const words = (k: number, word = 'word') => Array.from({ length: k }, () => word).join(' ');
const config = (extra: Partial<SlideConfig> = {}): SlideConfig => ({ ...DEFAULT_LIMITS, allow: [], ...extra });

/** usaco-bronze unit 1's recap, verbatim from the bundle: 110 words, 5 bullets and a closing line. */
const USACO_U1_RECAP =
  '- A contest program reads ALL of its input from stdin as one string, then parses it and prints the answer.\n' +
  '- `.split()` breaks text on any spaces or newlines, and each token stays a string until you call `int()`.\n' +
  '- A moving `position` counter walks through the tokens: first `N` (or `R C`), then the values or grid rows.\n' +
  '- `grid[r][c]` reads one cell of a list-of-lists grid built with nested loops.\n' +
  '- Judges compare output exactly, so test the edges: one value, one row or column, and the last position.\n\n' +
  'You can now write a program that reads a contest input, parses it and prints the exact answer.';

describe('splitUnits', () => {
  it('cuts at paragraphs and top-level list items', () => {
    const units = splitUnits('First para\nstill first.\n\nSecond para.\n\n- one\n- two\n1. three');
    expect(units.map((u) => [u.kind, u.md])).toEqual([
      ['paragraph', 'First para\nstill first.'],
      ['paragraph', 'Second para.'],
      ['item', '- one'],
      ['item', '- two'],
      ['item', '1. three'],
    ]);
  });

  it('keeps continuation lines and nested lists with their item', () => {
    const md = '- parent item\n  continues here\n  - nested a\n  - nested b\n\n  a continuation paragraph\n- next item\n\nAfter.';
    const units = splitUnits(md);
    expect(units.map((u) => u.kind)).toEqual(['item', 'item', 'paragraph']);
    expect(units[0]!.md).toBe('- parent item\n  continues here\n  - nested a\n  - nested b\n\n  a continuation paragraph');
  });

  it('never cuts a fenced code block', () => {
    const md = 'Look:\n```python\nx = 1\n\n\ny = 2\n- not an item\n# not a heading\n```\n\nDone.';
    const units = splitUnits(md);
    expect(units.map((u) => u.kind)).toEqual(['paragraph', 'paragraph']);
    expect(units[0]!.md).toContain('# not a heading\n```');
    expect(units[0]!.words).toBe(countWords('Look:\nx = 1\ny = 2\n- not an item\n# not a heading'));
  });

  it('makes a pipe table one atomic unit measured by body rows, with no words', () => {
    const rows = Array.from({ length: 13 }, (_, i) => `| r${i} | many words in this cell ${i} |`).join('\n');
    const units = splitUnits(`Intro line.\n\n| a | b |\n|---|---|\n${rows}\n\nAfter the table.`);
    expect(units.map((u) => u.kind)).toEqual(['paragraph', 'table', 'paragraph']);
    expect(units[1]).toMatchObject({ kind: 'table', rows: 13, words: 0 });
  });

  it('separates a heading and drops HTML comment lines', () => {
    const units = splitUnits('## Title\nBody under it.\n<!-- pattern: x -->\nMore.');
    expect(units.map((u) => [u.kind, u.md])).toEqual([
      ['heading', '## Title'],
      ['paragraph', 'Body under it.'],
      ['paragraph', 'More.'],
    ]);
    expect(splitUnits('<!-- pattern: count-by-condition -->')).toEqual([]);
  });

  it('counts whitespace-separated tokens as words', () => {
    expect(countWords('- `print()` shows text — always.')).toBe(6);
  });

  it('splits usaco-bronze unit 1 recap (110 words) into its 5 bullets and closing line', () => {
    const units = splitUnits(USACO_U1_RECAP);
    expect(units.map((u) => u.kind)).toEqual(['item', 'item', 'item', 'item', 'item', 'paragraph']);
    expect(units.reduce((s, u) => s + u.words, 0)).toBe(110);
    const slides = buildSlides([block('recap', USACO_U1_RECAP)]);
    expect(slides.map((s) => s.words)).toEqual([73, 37]);
    expect(slides.every((s) => s.words <= DEFAULT_LIMITS.maxWords)).toBe(true);
    expect(slides.map((s) => s.parts.length)).toEqual([1, 1]);
  });
});

describe('buildSlides', () => {
  it('starts slides at opener, goals, recap and code; packs consecutive prose', () => {
    const slides = buildSlides([
      block('opener', 'Hook.'),
      block('goals', '- a\n- b'),
      block('prose', '## Lesson 1\n\nIntro.'),
      block('prose', 'More intro.'),
      block('code', 'print(1)', { output: '1\n' }),
      block('prose', 'After code.'),
      block('tryit', 'input()'),
      block('error-demo', 'print(x'),
      block('turtle-figure', 'forward(1)'),
      block('recap', '- done'),
    ]);
    expect(slides.map((s) => s.kind)).toEqual(['prose', 'prose', 'prose', 'code', 'prose', 'tryit', 'demo', 'figure', 'prose']);
    expect(slides[2]!.parts).toHaveLength(2);
  });

  it('packs up to max_words; a heading starts a slide and is not counted', () => {
    const slides = buildSlides([
      block('prose', `${words(50)}\n\n${words(30)}\n\n${words(20)}`),
      block('prose', `## Heading here\n\n${words(86)}\n\n${words(5)}`),
    ]);
    expect(slides.map((s) => s.words)).toEqual([80, 20, 86, 5]);
  });

  it('keeps a run of headings on one slide', () => {
    const slides = buildSlides([block('prose', `## Lesson 1\n\n### First part\n\n${words(10)}`)]);
    expect(slides).toHaveLength(1);
  });

  it('puts a unit over max_words on its own slide', () => {
    const slides = buildSlides([block('prose', `${words(10)}\n\n${words(120)}\n\n${words(10)}`)]);
    expect(slides.map((s) => s.words)).toEqual([10, 120, 10]);
  });

  it('holds at most one table per slide', () => {
    const t = '| a |\n|---|\n| 1 |';
    const slides = buildSlides([block('prose', `${t}\n\nText.\n\n${t}`)]);
    expect(slides).toHaveLength(2);
  });

  it('attaches a notice to the code slide before it, else after it, within budget', () => {
    const slides = buildSlides([
      block('code', 'print(1)', { output: '1\n' }),
      block('notice', 'Short notice after.'),
      block('prose', 'Prose.'),
      block('notice', 'Short notice before.'),
      block('code', 'print(2)'),
      block('code', words(80, 'x')),
      block('notice', words(20)),
    ]);
    expect(slides.map((s) => [s.kind, s.parts.map((p) => p.kind)])).toEqual([
      ['code', ['block', 'md']],
      ['prose', ['md']],
      ['code', ['md', 'block']],
      ['code', ['block']],
      ['notice', ['md']],
    ]);
  });

  it('honours slide-break (once per cell) and slide-skip', () => {
    const one = block('prose', 'One.');
    const two = block('prose', 'Two.', { tags: ['slide-break'] });
    const twoPart2 = { ...block('prose', 'Two, part 2.', { tags: ['slide-break'] }), key: `${two.key}#2` };
    const slides = buildSlides([
      one,
      two,
      twoPart2,
      block('prose', 'Hidden.', { tags: ['slide-skip'] }),
      block('code', 'print(3)', { tags: ['slide-skip'] }),
    ]);
    expect(slides).toHaveLength(2);
    expect(slides[1]!.parts.map((p) => (p.kind === 'md' ? p.md : ''))).toEqual(['Two.', 'Two, part 2.']);
  });
});

describe('auditBook', () => {
  const rows = (k: number) => `| h |\n|---|\n${Array.from({ length: k }, (_, i) => `| ${i} |`).join('\n')}`;
  const lesson = [
    block('prose', words(151)),
    block('prose', rows(13)),
    block('code', Array.from({ length: 41 }, (_, i) => `x = ${i}`).join('\n')),
    block('prose', words(120)),
    block('prose', words(90)),
    block('notice', words(10)),
  ];
  const entries = [{ id: 'unit-01-demo', blocks: lesson }];

  it('fails over the failure limits and only reports the 90–150 band', () => {
    const audit = auditBook('demo', entries, config());
    expect(audit.findings.map((f) => [f.kind, f.size])).toEqual([
      ['unit-words', 151],
      ['table-rows', 13],
      ['code-lines', 41],
    ]);
    expect(audit.band.map((b) => b.words)).toEqual([120]);
    expect(audit.noticeSlides).toBe(1);
    expect(auditPasses(audit)).toBe(false);
  });

  it('passes on the limits and with every finding allow-listed', () => {
    expect(auditPasses(auditBook('demo', [{ id: 'u', blocks: [block('prose', words(150)), block('prose', rows(12))] }], config()))).toBe(true);
    const allow = lesson.slice(0, 3).map((b) => ({ key: b.key, reason: 'reviewed' }));
    const audit = auditBook('demo', entries, config({ allow }));
    expect(audit.findings.every((f) => f.allowed === 'reviewed')).toBe(true);
    expect(auditPasses(audit)).toBe(true);
    expect(formatAudit(audit, config({ allow }))[0]).toContain('0 failing, 3 allow-listed; 1 unit(s) between 90 and 150 words');
  });

  it('fails on a stale allow entry', () => {
    const audit = auditBook('demo', [{ id: 'u', blocks: [block('prose', 'Fine.')] }], config({ allow: [{ key: 'demo/x/lesson/y', reason: 'gone' }] }));
    expect(audit.staleAllow).toEqual(['demo/x/lesson/y']);
    expect(auditPasses(audit)).toBe(false);
  });

  it('reads limits from the config', () => {
    const audit = auditBook('demo', [{ id: 'u', blocks: [block('prose', words(60))] }], config({ maxWords: 50, maxUnitWords: 55 }));
    expect(audit.findings.map((f) => f.kind)).toEqual(['unit-words']);
  });
});

describe('renderSlideMarkdown', () => {
  it('renders through the shared Markdown pipeline: raw HTML escaped, lists, tables, code', () => {
    const html = renderSlideMarkdown(splitUnits('Use `<name>` and <b>raw</b>.\n\n- **one**\n- two\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\n```\nx < 1\n```'));
    expect(html).toContain('<code>&lt;name&gt;</code> and &lt;b&gt;raw&lt;/b&gt;.');
    expect(html).toMatch(/<ul>\s*<li>\s*<p><strong>one<\/strong><\/p>\s*<\/li>\s*<li>\s*<p>two<\/p>\s*<\/li>\s*<\/ul>/);
    expect(html).toContain('<th scope="col">a</th>');
    // Fenced code goes through the shared highlighter: classes, never inline styles.
    expect(html).toMatch(/<pre class="shiki[^"]*"[^>]*><code>/);
    expect(html).toContain('&lt;');
    expect(html).not.toMatch(/\sstyle="/);
  });
});

// --- the real books --------------------------------------------------------------------------

const CONTENT = join(repoRoot(), 'site', 'content');
function realBooks(): LoadedBook[] | null {
  if (!existsSync(CONTENT)) return null;
  try {
    return loadBooks({ contentDir: CONTENT });
  } catch {
    return null;
  }
}
const books = realBooks();

/**
 * The measured counts after the Phase C tag pass (plan 103: "Phase C asserts these counts").
 * band: units between 90 and 150 words; tables: tables over 12 rows; code: code slides over
 * 40 lines. Every table and code finding is allow-listed in the book's site.yaml.
 */
const EXPECTED: Record<string, { band: number; unitWords: number; tables: number; code: number }> = {
  'python-projects': { band: 0, unitWords: 0, tables: 0, code: 2 },
  'python-concepts': { band: 0, unitWords: 0, tables: 0, code: 0 },
  'usaco-bronze': { band: 1, unitWords: 0, tables: 0, code: 4 },
  acsl: { band: 12, unitWords: 0, tables: 1, code: 7 },
};

describe.skipIf(books === null)('the real books', () => {
  it('match the measured slide-audit counts and pass the audit', () => {
    const got: Record<string, unknown> = {};
    for (const book of books!) {
      const { audit } = auditLoadedBook(repoRoot(), book);
      const count = (kind: string) => audit.findings.filter((f) => f.kind === kind).length;
      got[book.id] = { band: audit.band.length, unitWords: count('unit-words'), tables: count('table-rows'), code: count('code-lines') };
      expect(auditPasses(audit), formatAudit(audit, { ...DEFAULT_LIMITS, allow: [] }).join('\n')).toBe(true);
    }
    expect(got).toEqual(Object.fromEntries(books!.map((b) => [b.id, EXPECTED[b.id]])));
  });

  it('build a deck for every lesson, with no empty slide', () => {
    for (const book of books!) {
      const decks = slideDecks(book);
      expect(decks.length).toBe(book.entries.filter((e) => (e.data.lesson?.blocks.length ?? 0) > 0).length);
      for (const deck of decks) for (const slide of deck.slides) expect(slide.parts.length).toBeGreaterThan(0);
    }
  });
});

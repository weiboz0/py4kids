/**
 * The card deck (plan 103 Phase D): the build-time projection carries no hidden material, the
 * choice order is stable, prelude cards carry their prelude, and the client-side grading rules.
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBook, loadBooks, repoRoot, type LoadedBook } from '../src/lib/bundle';
import { deckProjection, deckSummary, inlineMarkdown, stableShuffle } from '../src/lib/cards';
import { deckQueue, gradeChoice, gradeTyped, reportHref } from '../src/lib/deck';
import type { CardState } from '../src/lib/leitner';
import { masteryProjection } from '../src/lib/mastery';
import { pageContext, pageDataAttributes } from '../src/lib/page-context';
import { validateEvent, makeEvent } from '../src/lib/progress';
import { block, conceptCard, fakeBook, predict } from './helpers/fake-book';

const FIXTURE = join(import.meta.dirname, 'fixtures', 'bundles', 'demo');
const CONTENT = join(repoRoot(), 'site', 'content');
const hasReal = existsSync(CONTENT);
const FORBIDDEN = new Set(['answer_md', 'source', 'hash', 'check', 'program', 'requirements', 'statement_md']);

/** Every object key anywhere in a JSON value. */
function keysOf(value: unknown, out = new Set<string>()): Set<string> {
  if (Array.isArray(value)) for (const v of value) keysOf(v, out);
  else if (value && typeof value === 'object') {
    for (const [k, v] of Object.entries(value)) {
      out.add(k);
      keysOf(v, out);
    }
  }
  return out;
}

function forbiddenKeys(value: unknown): string[] {
  return [...keysOf(JSON.parse(JSON.stringify(value)))].filter((k) => FORBIDDEN.has(k));
}

describe('stableShuffle', () => {
  it('is stable per seed and a permutation', () => {
    const items = ['term', 'a', 'b', 'c'];
    const once = stableShuffle(items, 'book/back-matter/glossary/x');
    expect(stableShuffle(items, 'book/back-matter/glossary/x')).toEqual(once);
    expect([...once].sort()).toEqual([...items].sort());
    expect(items).toEqual(['term', 'a', 'b', 'c']); // not mutated
    const orders = new Set(Array.from({ length: 40 }, (_, i) => stableShuffle(items, `seed-${i}`).join()));
    expect(orders.size).toBeGreaterThan(5);
    const firsts = new Set(Array.from({ length: 40 }, (_, i) => stableShuffle(items, `seed-${i}`)[0]));
    expect(firsts.size).toBe(4); // the term is not always first
  });
});

describe('inlineMarkdown', () => {
  it('escapes everything and renders code spans', () => {
    expect(inlineMarkdown('Use `x < y` & <b>bold</b>')).toBe('Use <code>x &lt; y</code> &amp; &lt;b&gt;bold&lt;/b&gt;');
  });
});

describe('deckProjection', () => {
  const B = 'pc';
  const pre1 = block(`${B}/unit-01/lesson/p1`, ['variables'], 'x = 3');
  const pre2 = block(`${B}/unit-01/lesson/p2`, [], 'y = x + 1');
  const main = block(`${B}/unit-01/lesson/m`, ['print', 'variables'], 'print(x, y)', '3 4\n');
  const book = fakeBook(B, [], [
    { id: 'unit-01', blocks: [pre1, pre2, main], cards: [predict(main.key, 'flip', [pre1.key, pre2.key]), conceptCard(B, 'print', 'print', ['input', 'len'])] },
    { id: 'unit-02' },
  ]);
  const deck = deckProjection(book);

  it('shows the prelude code above a prelude card, in order', () => {
    expect(deck.cards[0]).toEqual({
      key: `${main.key}#predict`,
      kind: 'predict',
      mode: 'flip',
      unit: 'unit-01',
      concepts: ['print', 'variables'],
      code: 'print(x, y)',
      prelude: ['x = 3', 'y = x + 1'],
      output: '3 4\n',
    });
  });

  it('gives a choice card its term among the distractors, seeded by the card key', () => {
    const card = deck.cards[1]!;
    expect(card.kind).toBe('concept');
    if (card.kind !== 'concept') return;
    expect([...card.options].sort()).toEqual(['input', 'len', 'print']);
    expect(card.options).toEqual(stableShuffle(['print', 'input', 'len'], card.key));
    expect(card.definition_html).toBe('The <code>print</code> thing &amp; &lt;more&gt;.');
  });

  it('lists only units that have cards', () => {
    expect(deck.units).toEqual([{ id: 'unit-01', title: 'Unit 1' }]);
    expect(deckSummary(book)).toEqual({ units: [{ id: 'unit-01', title: 'Unit 1', count: 2 }], total: 2 });
  });

  it('carries no hidden material on the fixture bundle (which has a hashed checkpoint)', () => {
    const demo = loadBook(FIXTURE);
    expect(forbiddenKeys(deckProjection(demo))).toEqual([]);
    expect(forbiddenKeys(masteryProjection(demo))).toEqual([]);
    expect(JSON.stringify(deckProjection(demo))).not.toContain('sha256:');
  });
});

describe('grading and order', () => {
  it('compares a typed line with the output through normalise, case-sensitive', () => {
    expect(gradeTyped('  3   4 ', '3 4\n')).toBe(true);
    expect(gradeTyped('3 4', '3 4')).toBe(true);
    expect(gradeTyped('true', 'True\n')).toBe(false);
    expect(gradeTyped('34', '3 4')).toBe(false);
    expect(gradeChoice('print', 'print')).toBe(true);
    expect(gradeChoice('len', 'print')).toBe(false);
  });

  it('queues due cards first, then new, then later, filtered by unit', () => {
    const cards = ['u1', 'u1', 'u2', 'u1'].map((unit, i) => ({
      key: `b/${unit}/lesson/c${i}#predict`,
      kind: 'predict' as const,
      mode: 'typed' as const,
      unit,
      concepts: [],
      code: '',
      prelude: [],
      output: '',
    }));
    const now = new Date('2026-10-07T00:00:00.000Z');
    const s = (key: string, due: string): [string, CardState] => [key, { key, book: 'b', box: 2, due, updated_at: due }];
    const states = new Map([s(cards[0]!.key, '2026-10-09T00:00:00.000Z'), s(cards[3]!.key, '2026-10-06T00:00:00.000Z')]);
    const all = deckQueue(cards, states, '', now);
    expect(all.cards.map((c) => c.key)).toEqual([cards[3]!.key, cards[1]!.key, cards[2]!.key, cards[0]!.key]);
    expect([all.due, all.fresh, all.later]).toEqual([1, 2, 1]);
    expect(deckQueue(cards, states, 'u2', now).cards.map((c) => c.key)).toEqual([cards[2]!.key]);
  });

  it('builds a report link carrying only the key and the content hash', () => {
    const href = reportHref('acsl/unit-01-x/lesson/c1#predict', `sha256:${'c'.repeat(64)}`);
    expect(href.startsWith('https://github.com/weiboz0/py4kids/issues/new?title=')).toBe(true);
    const url = new URL(href);
    expect(url.searchParams.get('title')).toBe('Problem with acsl/unit-01-x/lesson/c1#predict');
    expect(url.searchParams.get('body')).toContain(`Content: sha256:${'c'.repeat(64)}`);
  });
});

describe('pageContext', () => {
  const demo = loadBook(FIXTURE);
  it('finds the entry on its reading, slides and practice pages only', () => {
    expect(pageContext(demo, '/demo/unit-01-demo/')).toMatchObject({ book: 'demo', entry: 'unit-01-demo', entryTitle: 'Unit 1 — Demo' });
    expect(pageContext(demo, '/demo/unit-01-demo/slides/').entry).toBe('unit-01-demo');
    expect(pageContext(demo, '/demo/unit-01-demo/practice/').entry).toBe('unit-01-demo');
    expect(pageContext(demo, '/demo/').entry).toBeUndefined();
    expect(pageContext(demo, '/demo/cards/').entry).toBeUndefined();
    expect(pageDataAttributes(pageContext(demo, '/demo/'))).toEqual({
      'data-book': 'demo',
      'data-content-hash': `sha256:${'0'.repeat(64)}`,
    });
    expect(pageDataAttributes(undefined)).toEqual({});
  });
});

describe.skipIf(!hasReal)('real bundles', () => {
  const books: LoadedBook[] = hasReal ? loadBooks({ contentDir: CONTENT }) : [];

  it('project every card with no hidden material', () => {
    for (const book of books) {
      const deck = deckProjection(book);
      const total = book.entries.reduce((n, e) => n + e.data.cards.length, 0);
      expect(deck.cards.length, book.id).toBe(total);
      expect(forbiddenKeys(deck), book.id).toEqual([]);
      expect(forbiddenKeys(masteryProjection(book)), book.id).toEqual([]);
      // No item answer hash text appears in the projection.
      const json = JSON.stringify(deck);
      for (const { data } of book.entries) {
        for (const item of data.items) {
          if ('hash' in item.check) expect(json.includes(item.check.hash.slice(7)), item.key).toBe(false);
        }
      }
    }
  });

  it('have card keys that make valid card events', () => {
    for (const book of books) {
      for (const card of deckProjection(book).cards) {
        const event = makeEvent({ item_key: card.key, kind: 'card', result: 'pass', detail: { box: 2 }, content_hash: book.book.release.content_hash });
        expect(validateEvent(event), card.key).toEqual([]);
        expect(event.book).toBe(book.id);
      }
    }
  });

  it('give every choice card its term among 2-4 options, and prelude cards their code', () => {
    for (const book of books) {
      for (const card of deckProjection(book).cards) {
        if (card.kind === 'concept' && card.mode === 'choice') {
          expect(card.options, card.key).toContain(card.term);
          expect(card.options.length).toBeGreaterThanOrEqual(2);
          expect(card.options.length).toBeLessThanOrEqual(4);
        }
        if (card.kind === 'predict') {
          expect(card.code.length, card.key).toBeGreaterThan(0);
          for (const code of card.prelude) expect(code.length, card.key).toBeGreaterThan(0);
        }
      }
    }
  });
});

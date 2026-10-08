/**
 * The mastery map (plan 103 "Mastery map and cards (D8)"): attribution, 1/k weighting on
 * python-concepts-like multi-concept cards, the N = 3 threshold and "practice in exercises".
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBooks, repoRoot } from '../src/lib/bundle';
import type { CardState } from '../src/lib/leitner';
import { attribution, conceptMastery, masteryMap, masteryProjection, MIN_ATTRIBUTED } from '../src/lib/mastery';
import type { Concept } from '../src/lib/types';
import { block, conceptCard, fakeBook, item, predict } from './helpers/fake-book';

const ids = Array.from({ length: 17 }, (_, i) => `c${i + 1}`);
const concepts: Concept[] = [
  ...ids.map((id, i) => ({ id, name: `Concept ${id}`, category: i < 10 ? 'basics' : 'loops' })),
  { id: 'glossed', name: 'Glossed', category: 'words' },
];
const B = 'pc';
const big = block(`${B}/unit-01/lesson/big`, ids); // one block carrying 17 concept ids
const soloA = block(`${B}/unit-01/lesson/solo-a`, ['c1']);
const soloB = block(`${B}/unit-01/lesson/solo-b`, ['c1', 'c1']); // duplicates count once
const book = fakeBook(B, concepts, [
  {
    id: 'unit-01',
    blocks: [big, soloA, soloB],
    cards: [predict(big.key), predict(soloA.key), predict(soloB.key, 'flip'), conceptCard(B, 'glossed', 'Glossed')],
    items: [
      item(`${B}/unit-01/exercises/e1`, ['c2', 'c4', 'c5', 'c6', 'c3']),
      item(`${B}/unit-01/exercises/e2`, ['c2', 'c4', 'c5', 'c6']),
      item(`${B}/unit-01/exercises/e3`, ['c5', 'glossed', 'glossed']),
    ],
  },
]);
const at = '2026-10-07T00:00:00.000Z';
const known = (...keys: string[]) => new Map<string, CardState>(keys.map((key) => [key, { key, book: B, box: 3, due: at, updated_at: at }]));
const P17 = `${big.key}#predict`;
const P1a = `${soloA.key}#predict`;
const P1b = `${soloB.key}#predict`;

describe('attribution', () => {
  it('takes a predict card from its block, a concept card from its concept, items from their concepts', () => {
    const { cards, items } = attribution(book);
    expect(cards.get(P17)).toEqual(ids);
    expect(cards.get(P1b)).toEqual(['c1']);
    expect(cards.get(`${B}/back-matter/glossary/glossed`)).toEqual(['glossed']);
    expect(items.get('c5')).toBe(3);
    expect(items.get('glossed')).toBe(1);
  });
});

describe('the N = 3 threshold', () => {
  const shown = () => new Map(masteryMap(book).groups.flatMap((g) => g.concepts.map((c) => [c.id, c] as const)));

  it('is 3', () => {
    expect(MIN_ATTRIBUTED).toBe(3);
  });

  it('shows a concept with exactly 3 attributed cards or items, and hides one with 2', () => {
    const map = shown();
    expect(map.get('c1')?.cards).toBe(3); // 3 cards
    expect(map.get('c2')).toMatchObject({ cards: 1, items: 2, mode: 'percent' }); // 1 card + 2 items
    expect(map.get('c4')).toMatchObject({ cards: 1, items: 2 });
    expect(map.has('c3')).toBe(false); // 1 card + 1 item
    expect(map.has('c7')).toBe(false); // 1 card only
    expect(map.has('glossed')).toBe(false); // 1 card + 1 item (the duplicate counts once)
  });

  it('shows "practice in exercises" for a concept that reaches N with items only', () => {
    expect(shown().get('c5')).toMatchObject({ cards: 1, items: 3, mode: 'percent' });
    const itemsOnly = fakeBook(B, concepts, [
      { id: 'unit-01', items: [1, 2, 3].map((n) => item(`${B}/unit-01/exercises/e${n}`, ['c9'])) },
    ]);
    expect(masteryMap(itemsOnly).groups).toEqual([
      { category: 'basics', concepts: [{ id: 'c9', name: 'Concept c9', cards: 0, items: 3, mode: 'practice' }] },
    ]);
    expect(masteryProjection(itemsOnly).concepts).toEqual([]);
  });

  it('groups by registry category, in registry order', () => {
    const big2 = block(`${B}/unit-01/lesson/x`, ['c11']);
    const withLoops = fakeBook(B, concepts, [
      { id: 'unit-01', blocks: [big2], cards: [predict(big2.key)], items: [1, 2].map((n) => item(`${B}/unit-01/exercises/e${n}`, ['c11', 'c1'])) },
      { id: 'unit-02', items: [item(`${B}/unit-02/exercises/e1`, ['c1'])] },
    ]);
    expect(masteryMap(withLoops).groups.map((g) => [g.category, g.concepts.map((c) => c.id)])).toEqual([
      ['basics', ['c1']],
      ['loops', ['c11']],
    ]);
  });
});

describe('1/k weighting', () => {
  const projection = masteryProjection(book);

  it('projects every card attributed to a shown concept', () => {
    expect(Object.keys(projection.cards).sort()).toEqual([P17, P1a, P1b].sort());
    expect(projection.concepts).toContain('c1');
    expect(projection.concepts).not.toContain('c3');
  });

  it('lets a 17-concept card add only 1/17 to each concept', () => {
    // c1: P17 (weight 1/17), P1a (1), P1b (1). Only the 17-concept card known:
    const m = conceptMastery(projection, known(P17));
    expect(m.get('c1')).toBeCloseTo(1 / 17 / (2 + 1 / 17), 10);
    expect(m.get('c1')).toBeLessThan(0.03);
    // An unweighted count would have said 1/3.
  });

  it('counts a single-concept card at full weight', () => {
    expect(conceptMastery(projection, known(P1a)).get('c1')).toBeCloseTo(1 / (2 + 1 / 17), 10);
    expect(conceptMastery(projection, known(P1a, P1b, P17)).get('c1')).toBe(1);
  });

  it('gives a concept whose only card is the 17-concept card that card’s full share', () => {
    expect(conceptMastery(projection, known(P17)).get('c2')).toBe(1);
    expect(conceptMastery(projection, known()).get('c2')).toBe(0);
  });

  it('counts a card as known only from box 3', () => {
    const box2 = new Map<string, CardState>([[P1a, { key: P1a, book: B, box: 2, due: at, updated_at: at }]]);
    expect(conceptMastery(projection, box2).get('c1')).toBe(0);
  });
});

const CONTENT = join(repoRoot(), 'site', 'content');
describe.skipIf(!existsSync(CONTENT))('real bundles', () => {
  it('builds a map and projection for every book', () => {
    for (const real of loadBooks({ contentDir: CONTENT })) {
      const map = masteryMap(real);
      const proj = masteryProjection(real);
      expect(map.groups.length, real.id).toBeGreaterThan(0);
      for (const g of map.groups) for (const c of g.concepts) expect(c.cards + c.items).toBeGreaterThanOrEqual(MIN_ATTRIBUTED);
      const registry = new Set(real.book.concepts.map((c) => c.id));
      for (const id of proj.concepts) expect(registry.has(id)).toBe(true);
    }
  });
});

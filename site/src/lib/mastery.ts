/**
 * The concept mastery map (design 012 D8; plan 103 "Mastery map and cards").
 *
 * - Attribution: a predict card counts toward its lesson block's `concepts`, a concept card
 *   toward its `concept`, an item toward its `concepts`.
 * - Weighting: a card attributed to k distinct concepts adds 1/k to each, so one card carrying
 *   17 concept ids cannot move 17 concepts at full weight. A concept's mastery is the weighted
 *   share of its cards in Leitner box >= 3.
 * - A concept appears only with at least `MIN_ATTRIBUTED` (N = 3) attributed cards or items
 *   (a plain count). One that reaches N without any card shows "practice in exercises"
 *   (part C adds item results).
 * - Concepts are grouped by registry `category`, in registry order.
 *
 * The attribution is static, so the map's layout is rendered at build time; the island computes
 * the percentages from the on-device card boxes and the `MasteryProjection`.
 */

import type { LoadedBook } from './bundle';
import { blocksByKey } from './lesson-blocks';
import { boxOf, KNOWN_BOX, type CardState } from './leitner';
import type { ConceptId } from './types';

export const MIN_ATTRIBUTED = 3;

export interface MapConcept {
  id: ConceptId;
  name: string;
  cards: number;
  items: number;
  /** `percent`: has cards, so a percentage; `practice`: reaches N only through items. */
  mode: 'percent' | 'practice';
}

export interface MasteryMap {
  groups: { category: string; concepts: MapConcept[] }[];
}

/** The island's projection (`/<book>/mastery.json`): each card's concepts, for shown concepts. */
export interface MasteryProjection {
  book: string;
  /** card key -> every distinct concept the card is attributed to (k = its length). */
  cards: Record<string, ConceptId[]>;
  /** The concepts shown with a percentage. */
  concepts: ConceptId[];
}

const distinct = <T>(values: readonly T[]): T[] => [...new Set(values)];

/** Each card's concepts and each concept's item count, from the bundle. */
export function attribution(book: LoadedBook): { cards: Map<string, ConceptId[]>; items: Map<ConceptId, number> } {
  const blocks = blocksByKey(book);
  const cards = new Map<string, ConceptId[]>();
  const items = new Map<ConceptId, number>();
  for (const { data } of book.entries) {
    for (const card of data.cards) {
      const concepts = card.kind === 'predict' ? (blocks.get(card.block)?.concepts ?? []) : [card.concept];
      cards.set(card.key, distinct(concepts));
    }
    for (const item of data.items) for (const id of distinct(item.concepts)) items.set(id, (items.get(id) ?? 0) + 1);
  }
  return { cards, items };
}

function counts(cards: Map<string, ConceptId[]>): Map<ConceptId, number> {
  const out = new Map<ConceptId, number>();
  for (const concepts of cards.values()) for (const id of concepts) out.set(id, (out.get(id) ?? 0) + 1);
  return out;
}

/** The book page's mastery map layout (build time). */
export function masteryMap(book: LoadedBook): MasteryMap {
  const { cards, items } = attribution(book);
  const cardCounts = counts(cards);
  const groups: MasteryMap['groups'] = [];
  for (const concept of book.book.concepts) {
    const nCards = cardCounts.get(concept.id) ?? 0;
    const nItems = items.get(concept.id) ?? 0;
    if (nCards + nItems < MIN_ATTRIBUTED) continue;
    let group = groups.find((g) => g.category === concept.category);
    if (!group) {
      group = { category: concept.category, concepts: [] };
      groups.push(group);
    }
    group.concepts.push({ id: concept.id, name: concept.name, cards: nCards, items: nItems, mode: nCards > 0 ? 'percent' : 'practice' });
  }
  return { groups };
}

/** The mastery island's projection (build time). */
export function masteryProjection(book: LoadedBook): MasteryProjection {
  const shown = masteryMap(book).groups.flatMap((g) => g.concepts.filter((c) => c.mode === 'percent').map((c) => c.id));
  const wanted = new Set(shown);
  const cards: Record<string, ConceptId[]> = {};
  for (const [key, concepts] of attribution(book).cards) {
    if (concepts.some((id) => wanted.has(id))) cards[key] = concepts;
  }
  return { book: book.id, cards, concepts: shown };
}

/**
 * Each shown concept's mastery in [0, 1]: the 1/k-weighted share of its cards in box >= 3.
 * A card never reviewed counts as box 1.
 */
export function conceptMastery(projection: MasteryProjection, states: Map<string, CardState>): Map<ConceptId, number> {
  const known = new Map<ConceptId, number>();
  const total = new Map<ConceptId, number>();
  for (const [key, concepts] of Object.entries(projection.cards)) {
    if (concepts.length === 0) continue;
    const weight = 1 / concepts.length;
    const isKnown = boxOf(states.get(key)) >= KNOWN_BOX;
    for (const id of concepts) {
      total.set(id, (total.get(id) ?? 0) + weight);
      if (isKnown) known.set(id, (known.get(id) ?? 0) + weight);
    }
  }
  const out = new Map<ConceptId, number>();
  for (const id of projection.concepts) {
    const t = total.get(id) ?? 0;
    out.set(id, t > 0 ? (known.get(id) ?? 0) / t : 0);
  }
  return out;
}

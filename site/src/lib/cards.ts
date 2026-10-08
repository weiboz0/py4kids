/**
 * The card deck's build-time projection (plan 103 Architecture, "No bundle JSON reaches the
 * client"; "Mastery map and cards (D8)"). The deck island receives only this: card keys,
 * prompts (code, prelude code, terms, definitions), stored outputs, modes, units and concept
 * ids. Never `answer_md`, `check.*` or a hash: a predict card's output is the lesson block's
 * stored output, which the reading view shows anyway.
 */

import type { LoadedBook } from './bundle';
import { blocksByKey } from './lesson-blocks';
import { renderInline } from './markdown';
import type { ConceptId } from './types';

export { blocksByKey };

interface DeckCardBase {
  key: string;
  /** The entry whose deck lists the card (the deck page's unit filter). */
  unit: string;
  /** The concepts the card is attributed to (mastery map, D8). */
  concepts: ConceptId[];
}

export interface DeckPredictCard extends DeckCardBase {
  kind: 'predict';
  mode: 'typed' | 'flip';
  code: string;
  /** The probe's prelude code, in order, shown above the card's code. */
  prelude: string[];
  output: string;
}

export interface DeckConceptCard extends DeckCardBase {
  kind: 'concept';
  mode: 'choice' | 'flip';
  term: string;
  /** The definition, rendered at build time by the site's Markdown pipeline (`renderInline`). */
  definition_html: string;
  /** `choice` only: the term and its distractors in a stable order seeded by the card key. */
  options: string[];
}

export type DeckCard = DeckPredictCard | DeckConceptCard;

export interface DeckProjection {
  book: string;
  /** Entries that list at least one card, in syllabus order. */
  units: { id: string; title: string }[];
  cards: DeckCard[];
}

/** 32-bit FNV-1a of a string's UTF-16 code units. */
export function seedOf(text: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) {
    h ^= text.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h;
}

/** A Fisher–Yates shuffle driven by mulberry32 seeded with `seed`: the same seed, the same order. */
export function stableShuffle<T>(items: readonly T[], seed: string): T[] {
  let a = seedOf(seed);
  const random = () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const out = [...items];
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [out[i], out[j]] = [out[j]!, out[i]!];
  }
  return out;
}

const distinct = <T>(values: readonly T[]): T[] => [...new Set(values)];

/** The deck page's projection (`/<book>/cards/deck.json`). */
export function deckProjection(book: LoadedBook): DeckProjection {
  const blocks = blocksByKey(book);
  const units: DeckProjection['units'] = [];
  const cards: DeckCard[] = [];
  for (const { record, data } of book.entries) {
    if (data.cards.length === 0) continue;
    units.push({ id: record.id, title: record.title });
    for (const card of data.cards) {
      if (card.kind === 'predict') {
        const block = blocks.get(card.block);
        if (!block) throw new Error(`${card.key}: block ${card.block} is not a lesson block of ${book.id}`);
        cards.push({
          key: card.key,
          kind: 'predict',
          mode: card.mode,
          unit: record.id,
          concepts: distinct(block.concepts),
          code: block.code ?? '',
          prelude: card.prelude.map((key) => {
            const pre = blocks.get(key);
            if (!pre) throw new Error(`${card.key}: prelude ${key} is not a lesson block of ${book.id}`);
            return pre.code ?? '';
          }),
          output: block.output ?? '',
        });
      } else {
        cards.push({
          key: card.key,
          kind: 'concept',
          mode: card.mode,
          unit: record.id,
          concepts: [card.concept],
          term: card.term,
          definition_html: renderInline(card.definition_md.trim()),
          options: card.mode === 'choice' ? stableShuffle([card.term, ...card.distractors], card.key) : [],
        });
      }
    }
  }
  return { book: book.id, units, cards };
}

/** The deck page's server-rendered summary (the unit filter and the counts without script). */
export function deckSummary(book: LoadedBook): { units: { id: string; title: string; count: number }[]; total: number } {
  const units = book.entries
    .filter((e) => e.data.cards.length > 0)
    .map((e) => ({ id: e.record.id, title: e.record.title, count: e.data.cards.length }));
  return { units, total: units.reduce((n, u) => n + u.count, 0) };
}

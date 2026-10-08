/**
 * The card deck's client-side rules (plan 103 "Mastery map and cards (D8)"), kept free of the DOM
 * so they are unit-tested.
 */

import type { DeckCard } from './cards';
import { orderDeck, type CardState } from './leitner';
import { normalise } from './normalise';

/** A typed predict card: the student's line against the stored output, case-sensitive (D5). */
export const gradeTyped = (typed: string, output: string): boolean =>
  normalise(typed, { case: 'sensitive' }) === normalise(output, { case: 'sensitive' });

/** A choice concept card: the picked option against the term. */
export const gradeChoice = (picked: string, term: string): boolean => picked === term;

export interface Queue {
  cards: DeckCard[];
  due: number;
  fresh: number;
  later: number;
}

/** The session's card order for a unit filter (`''` = every unit): due, then new, then later. */
export function deckQueue(cards: DeckCard[], states: Map<string, CardState>, unit: string, now: Date = new Date()): Queue {
  const order = orderDeck(unit ? cards.filter((c) => c.unit === unit) : cards, states, now);
  return {
    cards: [...order.due, ...order.fresh, ...order.later],
    due: order.due.length,
    fresh: order.fresh.length,
    later: order.later.length,
  };
}

export const ISSUES_URL = 'https://github.com/weiboz0/py4kids/issues/new';

/**
 * The "report a problem" link (plan 103 Pages): a prefilled GitHub new-issue URL carrying only
 * the item key and the bundle content hash.
 */
export function reportHref(key: string, contentHash: string): string {
  const title = `Problem with ${key}`;
  const body = `Item: ${key}\nContent: ${contentHash}\n\nWhat is wrong:\n`;
  return `${ISSUES_URL}?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
}

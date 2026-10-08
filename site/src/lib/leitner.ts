/**
 * Leitner spaced repetition for the card deck (design 012 D8; plan 103 "Mastery map and cards").
 * Five boxes. A card never reviewed is in box 1 and due now. A correct answer moves a card up
 * one box (at most 5) and schedules it `INTERVAL_DAYS[box]` days later; a miss sends it back to
 * box 1, due again at once. Mastery counts a card as known from box `KNOWN_BOX` (3) up.
 */

export const BOXES = 5;
export const KNOWN_BOX = 3;
/** Days until a card in each box is due again (index = box; box 0 is unused). */
export const INTERVAL_DAYS = [0, 0, 1, 3, 7, 14] as const;
const DAY_MS = 24 * 60 * 60 * 1000;

export interface CardState {
  /** The card's global key. */
  key: string;
  book: string;
  /** 1..5. */
  box: number;
  /** When the card is next due: UTC ISO 8601. */
  due: string;
  /** UTC ISO 8601. */
  updated_at: string;
}

/** A card's box, treating a card never reviewed as box 1. */
export const boxOf = (state: CardState | undefined): number => state?.box ?? 1;

/** The card's state after one review. */
export function review(
  previous: CardState | undefined,
  card: { key: string; book: string },
  correct: boolean,
  now: Date = new Date(),
): CardState {
  const box = correct ? Math.min(boxOf(previous) + 1, BOXES) : 1;
  const due = new Date(now.getTime() + INTERVAL_DAYS[box as 1 | 2 | 3 | 4 | 5] * DAY_MS);
  return { key: card.key, book: card.book, box, due: due.toISOString(), updated_at: now.toISOString() };
}

export const isDue = (state: CardState | undefined, now: Date = new Date()): boolean =>
  state === undefined || Date.parse(state.due) <= now.getTime();

export interface DeckOrder<T> {
  /** Reviewed before and due now, the longest overdue first. */
  due: T[];
  /** Never reviewed, in deck (syllabus) order. */
  fresh: T[];
  /** Not due yet, the soonest first. */
  later: T[];
}

/** Splits a deck into due, new and not-yet-due cards; the deck page shows them in that order. */
export function orderDeck<T extends { key: string }>(
  cards: T[],
  states: Map<string, CardState>,
  now: Date = new Date(),
): DeckOrder<T> {
  const due: T[] = [];
  const fresh: T[] = [];
  const later: T[] = [];
  for (const card of cards) {
    const state = states.get(card.key);
    if (!state) fresh.push(card);
    else if (isDue(state, now)) due.push(card);
    else later.push(card);
  }
  const at = (card: T) => Date.parse(states.get(card.key)!.due);
  due.sort((a, b) => at(a) - at(b));
  later.sort((a, b) => at(a) - at(b));
  return { due, fresh, later };
}

/** Leitner transitions and deck order (plan 103 Phase D). */
import { describe, expect, it } from 'vitest';
import { BOXES, boxOf, INTERVAL_DAYS, isDue, orderDeck, review, type CardState } from '../src/lib/leitner';

const card = { key: 'b/u/lesson/c1#predict', book: 'b' };
const now = new Date('2026-10-07T12:00:00.000Z');
const DAY = 86_400_000;
const later = (days: number) => new Date(now.getTime() + days * DAY);

describe('review', () => {
  it('treats a new card as box 1', () => {
    expect(boxOf(undefined)).toBe(1);
    expect(isDue(undefined, now)).toBe(true);
  });

  it('moves a correct card up one box and schedules it by the box interval', () => {
    let state: CardState | undefined;
    const boxes: number[] = [];
    for (let i = 0; i < 6; i++) {
      state = review(state, card, true, now);
      boxes.push(state.box);
      expect(Date.parse(state.due) - now.getTime()).toBe(INTERVAL_DAYS[state.box as 1]! * DAY);
    }
    expect(boxes).toEqual([2, 3, 4, 5, 5, 5]);
    expect(BOXES).toBe(5);
  });

  it('sends a missed card back to box 1, due at once', () => {
    let state = review(undefined, card, true, now);
    state = review(state, card, true, now);
    state = review(state, card, true, now);
    expect(state.box).toBe(4);
    state = review(state, card, false, now);
    expect(state.box).toBe(1);
    expect(state.due).toBe(now.toISOString());
    expect(isDue(state, now)).toBe(true);
    expect(review(undefined, card, false, now).box).toBe(1);
  });

  it('records UTC timestamps and the card identity', () => {
    const state = review(undefined, card, true, now);
    expect(state).toEqual({ key: card.key, book: 'b', box: 2, due: later(1).toISOString(), updated_at: now.toISOString() });
    expect(state.due.endsWith('Z')).toBe(true);
  });

  it('is due exactly when its due time has come', () => {
    const state = review(undefined, card, true, now); // due in 1 day
    expect(isDue(state, later(0.5))).toBe(false);
    expect(isDue(state, later(1))).toBe(true);
  });
});

describe('orderDeck', () => {
  const cards = ['a', 'b', 'c', 'd', 'e'].map((key) => ({ key }));
  const state = (key: string, dueInDays: number, box = 2): CardState => ({
    key,
    book: 'b',
    box,
    due: later(dueInDays).toISOString(),
    updated_at: now.toISOString(),
  });

  it('puts due cards first (most overdue first), then new cards in deck order, then later ones (soonest first)', () => {
    const states = new Map([
      ['b', state('b', -1)],
      ['d', state('d', -3)],
      ['a', state('a', 5)],
      ['e', state('e', 2)],
    ]);
    const order = orderDeck(cards, states, now);
    expect(order.due.map((c) => c.key)).toEqual(['d', 'b']);
    expect(order.fresh.map((c) => c.key)).toEqual(['c']);
    expect(order.later.map((c) => c.key)).toEqual(['e', 'a']);
  });
});

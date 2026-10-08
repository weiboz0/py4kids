/** Leitner transitions and deck order (plan 103 Phase D). */
import { describe, expect, it } from 'vitest';
import { BOXES, boxOf, INTERVAL_DAYS, isDue, KNOWN_BOX, orderDeck, review, type CardState } from '../src/lib/leitner';
import { conceptMastery, type MasteryProjection } from '../src/lib/mastery';

const card = { key: 'b/u/lesson/c1#predict', book: 'b' };
const now = new Date('2026-10-07T12:00:00.000Z');
const DAY = 86_400_000;
const later = (days: number) => new Date(now.getTime() + days * DAY);

describe('review', () => {
  it('treats a new card as box 1', () => {
    expect(boxOf(undefined)).toBe(1);
    expect(isDue(undefined, now)).toBe(true);
  });

  it('moves a correct card that is due up one box and schedules it by the box interval', () => {
    let state: CardState | undefined;
    let t = now;
    const boxes: number[] = [];
    for (let i = 0; i < 6; i++) {
      state = review(state, card, true, t);
      boxes.push(state.box);
      expect(Date.parse(state.due) - t.getTime()).toBe(INTERVAL_DAYS[state.box as 1]! * DAY);
      t = new Date(state.due); // review it again exactly when it is due
    }
    expect(boxes).toEqual([2, 3, 4, 5, 5, 5]);
    expect(BOXES).toBe(5);
  });

  it('sends a missed card back to box 1, due at once', () => {
    let state = review(undefined, card, true, now);
    state = review(state, card, true, new Date(state.due));
    state = review(state, card, true, new Date(state.due));
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

describe('early review (a card that is not due yet)', () => {
  const box2 = review(undefined, card, true, now); // box 2, due in 1 day
  const early = later(0.5);

  it('does not promote a correct answer: the box and due date stay the same', () => {
    const again = review(box2, card, true, early);
    expect(again.box).toBe(2);
    expect(again.due).toBe(box2.due);
    expect(again.updated_at).toBe(early.toISOString());
  });

  it('promotes the same card once it is due', () => {
    expect(review(box2, card, true, later(1)).box).toBe(3);
  });

  it('still sends a miss back to box 1 (a miss is honest evidence at any time)', () => {
    const missed = review(box2, card, false, early);
    expect(missed.box).toBe(1);
    expect(isDue(missed, early)).toBe(true);
  });

  it('cannot reach the known box by going round the deck again and again ("Start again")', () => {
    let state: CardState | undefined;
    for (let round = 0; round < 10; round++) state = review(state, card, true, later(round / 100));
    expect(state!.box).toBe(2);
    expect(state!.box).toBeLessThan(KNOWN_BOX);
  });

  it('leaves mastery unchanged', () => {
    const projection: MasteryProjection = { book: 'b', cards: { [card.key]: ['c1'] }, concepts: ['c1'] };
    const before = conceptMastery(projection, new Map([[card.key, box2]]));
    let state = box2;
    for (let i = 0; i < 5; i++) state = review(state, card, true, later(0.1 * (i + 1)));
    expect(conceptMastery(projection, new Map([[card.key, state]]))).toEqual(before);
    expect(before.get('c1')).toBe(0);
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

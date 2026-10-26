/** The practice pager's pure rules (plan 106, src/lib/pager.ts) and its groups in the view. */
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBook } from '../src/lib/bundle';
import { jumpEntries, lastHeading, practiceView } from '../src/lib/entry';
import {
  announcement,
  groupLabels,
  hashId,
  neighbours,
  positionText,
  saysChallenge,
  stepForHash,
  stepStatus,
  type StatusEvent,
} from '../src/lib/pager';

/** A page of four steps; ids map to the step containing them, as `closest('[data-step]')` does. */
const steps = ['s1', 's2', 's3', 's4'] as const;
const ids: Record<string, (typeof steps)[number]> = {
  'exercise-1': 's1',
  'exercise-1-h': 's1',
  'exercise-2': 's2',
  'exercise-2-h': 's2',
  // An id inside a step's `before` block (a heading above the item, inside its step container).
  'milestone-2': 's3',
  'exercise-3': 's3',
  'exercise-4': 's4',
};
const stepOf = (id: string) => ids[id] ?? null;
const atLoad = { atLoad: true, current: 0 };
const later = (current: number) => ({ atLoad: false, current });

describe('hash resolution', () => {
  it('resolves an item anchor, its heading id, and an id inside a before block to the step', () => {
    expect(stepForHash('#exercise-2', steps, stepOf, atLoad)).toBe(1);
    expect(stepForHash('#exercise-2-h', steps, stepOf, atLoad)).toBe(1);
    expect(stepForHash('#milestone-2', steps, stepOf, later(0))).toBe(2);
    expect(stepForHash('#exercise-4', steps, stepOf, later(1))).toBe(3);
  });

  it('shows the first item at load for an empty or unknown hash', () => {
    expect(stepForHash('', steps, stepOf, atLoad)).toBe(0);
    expect(stepForHash('#', steps, stepOf, atLoad)).toBe(0);
    expect(stepForHash('#no-such-id', steps, stepOf, atLoad)).toBe(0);
    expect(stepForHash('#main', steps, stepOf, atLoad)).toBe(0);
  });

  it('leaves the current step unchanged for an unresolvable hash after load (the skip link)', () => {
    expect(stepForHash('#main', steps, stepOf, later(3))).toBe(3);
    expect(stepForHash('#no-such-id', steps, stepOf, later(2))).toBe(2);
    expect(stepForHash('', steps, stepOf, later(1))).toBe(1);
  });

  it('decodes a percent-encoded hash and tolerates a malformed one', () => {
    expect(hashId('#a%20b')).toBe('a b');
    expect(hashId('#%E0%A4%A')).toBe('%E0%A4%A');
    expect(hashId('')).toBe('');
  });
});

describe('Previous / Next', () => {
  it('has no Previous on the first step and no Next on the last', () => {
    expect(neighbours(0, 4)).toEqual({ prev: null, next: 1 });
    expect(neighbours(3, 4)).toEqual({ prev: 2, next: null });
    expect(neighbours(1, 4)).toEqual({ prev: 0, next: 2 });
  });

  it('writes the position as "4 of 12"', () => {
    expect(positionText(3, 12)).toBe('4 of 12');
  });
});

describe('status', () => {
  const ev = (kind: string, result: string): StatusEvent => ({ kind, result });

  it('is passed after any recorded pass, even after a later failed check', () => {
    expect(stepStatus([ev('exercise', 'pass'), ev('exercise', 'fail')], false)).toBe('passed');
    expect(stepStatus([ev('checkpoint', 'fail'), ev('checkpoint', 'pass'), ev('checkpoint', 'partial')], false)).toBe('passed');
    expect(stepStatus([ev('project', 'pass')], false)).toBe('passed');
  });

  it('is passed for a self-check item whose latest checklist is done', () => {
    expect(stepStatus([ev('self-check', 'partial'), ev('self-check', 'done')], true)).toBe('passed');
    expect(stepStatus([ev('self-check', 'done'), ev('self-check', 'partial')], true)).toBe('tried');
  });

  it('is only tried for an automatic item whose also_check list is done but whose check failed', () => {
    expect(stepStatus([ev('exercise', 'fail'), ev('self-check', 'done')], false)).toBe('tried');
    expect(stepStatus([ev('self-check', 'done')], false)).toBe('tried');
    expect(stepStatus([ev('exercise', 'error')], false)).toBe('tried');
  });

  it('is nothing without events', () => {
    expect(stepStatus([], false)).toBe('none');
    expect(stepStatus([], true)).toBe('none');
  });
});

describe('announcements', () => {
  it('names the item and the outcome, and says when it was not saved', () => {
    expect(announcement('Exercise 2', 'pass', true)).toBe('Exercise 2: Passed');
    expect(announcement('Exercise 2', 'fail', true)).toBe('Exercise 2: Not yet');
    expect(announcement('Exercise 2', 'partial', true)).toBe('Exercise 2: Not yet');
    expect(announcement('Exercise 2', 'error', true)).toBe('Exercise 2: Could not check');
    expect(announcement('Exercise 2', 'stopped', true)).toBe('Exercise 2: Stopped');
    expect(announcement('Exercise 2', 'pass', false)).toBe('Exercise 2: Passed, but not saved');
  });
});

describe('groups from before blocks', () => {
  it('starts a group only at a before block with a heading; it lasts until the next', () => {
    const befores = [
      [],
      ['### Milestone 1\n\nNumber algorithms'],
      [],
      ['<!-- pattern: running-total -->'],
      ['### Milestone 2', 'Lists and searching'],
      [],
    ];
    expect(groupLabels(befores, lastHeading)).toEqual([
      { label: null, start: false },
      { label: 'Milestone 1', start: true },
      { label: 'Milestone 1', start: false },
      // A marker comment starts no group: the item stays in the group above.
      { label: 'Milestone 1', start: false },
      { label: 'Milestone 2', start: true },
      { label: 'Milestone 2', start: false },
    ]);
  });

  it('takes the label from the heading only (a heading plus a marker comment, or a paragraph)', () => {
    const quiz = ['### Algorithm Extension\n\n*Extra loop practice — optional enrichment*', '<!-- pattern: running-total -->'];
    const factory = ['### Challenge', 'Try these after the earlier exercises.'];
    expect(groupLabels([quiz, factory], lastHeading)).toEqual([
      { label: 'Algorithm Extension', start: true },
      { label: 'Challenge', start: true },
    ]);
  });

  it('ignores a heading inside a code fence and blocks without Markdown', () => {
    expect(groupLabels([['```\n# not a heading\n```'], [undefined]], lastHeading)).toEqual([
      { label: null, start: false },
      { label: null, start: false },
    ]);
  });

  it('builds the grouped jump list in item order', () => {
    const items = [
      { group: null, groupStart: false },
      { group: 'Milestone 1', groupStart: true },
      { group: 'Milestone 1', groupStart: false },
      { group: 'Milestone 2', groupStart: true },
    ];
    expect(jumpEntries(items)).toEqual([
      { kind: 'item', index: 0 },
      { kind: 'group', label: 'Milestone 1', indexes: [1, 2] },
      { kind: 'group', label: 'Milestone 2', indexes: [3] },
    ]);
  });

  it('does not repeat the Challenge tag under a kicker that says Challenge', () => {
    expect(saysChallenge('Challenge — Exercises 25–28 combine file skills')).toBe(true);
    expect(saysChallenge('Milestone 2')).toBe(false);
    expect(saysChallenge(null)).toBe(false);
  });

  it('gives every practice item of the demo book a group field and a jump entry', () => {
    const book = loadBook(join(import.meta.dirname, 'fixtures', 'bundles', 'demo'));
    const view = practiceView(book, 'unit-01-demo');
    const listed = view.jump.flatMap((e) => (e.kind === 'item' ? [e.index] : e.indexes));
    expect(listed).toEqual(view.items.map((_, i) => i));
    for (const item of view.items) {
      expect(item).toHaveProperty('group');
      expect(item.stretchTag).toBe(item.stretch && !saysChallenge(item.group));
    }
  });
});

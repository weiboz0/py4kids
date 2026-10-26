/**
 * The practice-page pager's pure rules (plan 106): which step a URL hash shows, the Previous /
 * Next targets, an item's status in the jump list, the hidden-item announcement, and the groups
 * the `before` blocks open. The island (src/scripts/practice-pager.ts) does the DOM work; the
 * practice view (src/lib/entry.ts) computes the groups at build time. No DOM, no store here.
 */

// ---------------------------------------------------------------------------------------------
// Addressing

/** A URL hash's element id: `#a%20b` → `a b`; empty for no hash. */
export function hashId(hash: string): string {
  const raw = hash.startsWith('#') ? hash.slice(1) : hash;
  try {
    return decodeURIComponent(raw);
  } catch {
    return raw;
  }
}

/**
 * The step a hash shows. `stepOf(id)` is the step that contains the element with that id
 * (`document.getElementById(id)?.closest('[data-step]')` in the page), or null.
 * At load, an empty or unresolvable hash shows the first step; on a later `hashchange`, it leaves
 * the current step shown (the skip link `#main`, any link outside a step).
 */
export function stepForHash<T>(
  hash: string,
  steps: readonly T[],
  stepOf: (id: string) => T | null | undefined,
  options: { atLoad: boolean; current: number },
): number {
  const id = hashId(hash);
  const step = id === '' ? null : stepOf(id);
  const index = step ? steps.indexOf(step) : -1;
  if (index >= 0) return index;
  return options.atLoad ? 0 : options.current;
}

/** The Previous and Next targets of step `index` of `count` (null at an end). */
export function neighbours(index: number, count: number): { prev: number | null; next: number | null } {
  return { prev: index > 0 ? index - 1 : null, next: index < count - 1 ? index + 1 : null };
}

/** The visually hidden position in a step's heading: "4 of 12". */
export const positionText = (index: number, count: number) => `${index + 1} of ${count}`;

// ---------------------------------------------------------------------------------------------
// Status

export type StepStatus = 'passed' | 'tried' | 'none';

/** The fields of a progress event the status reads. */
export interface StatusEvent {
  kind: string;
  result: string;
}

/** The kinds a Check writes (the automatic check). */
const CHECK_KINDS = new Set(['exercise', 'checkpoint', 'project']);

/**
 * An item's status from its recorded events (oldest first):
 * - passed: an automatic-check item with **any** recorded check `pass` (a later failed experiment
 *   does not take it away); a self-check item whose latest self-check event is `done`;
 * - tried: any other event, including an `also_check` checklist (which is not the automatic check);
 * - none: no event.
 */
export function stepStatus(events: readonly StatusEvent[], selfCheck: boolean): StepStatus {
  if (events.length === 0) return 'none';
  if (selfCheck) {
    const last = events.filter((e) => e.kind === 'self-check').at(-1);
    return last?.result === 'done' ? 'passed' : 'tried';
  }
  return events.some((e) => CHECK_KINDS.has(e.kind) && e.result === 'pass') ? 'passed' : 'tried';
}

/** A status's glyph and its visually hidden text equivalent (none: nothing). */
export const STATUS_TEXT: Record<StepStatus | 'checking', { glyph: string; text: string } | null> = {
  passed: { glyph: '✓', text: 'passed' },
  tried: { glyph: '•', text: 'tried' },
  checking: { glyph: '…', text: 'checking…' },
  none: null,
};

// ---------------------------------------------------------------------------------------------
// Announcements

/** How a check ended (`py4kids:check`): the outcomes, plus `error` and `stopped`. */
export type CheckEnd = 'pass' | 'fail' | 'partial' | 'error' | 'stopped';

const END_TEXT: Record<CheckEnd, string> = {
  pass: 'Passed',
  fail: 'Not yet',
  partial: 'Not yet',
  error: 'Could not check',
  stopped: 'Stopped',
};

/** What the page live region says when a check ends on a hidden item: "Exercise 2: Passed". */
export function announcement(label: string, result: CheckEnd, saved: boolean): string {
  return `${label}: ${END_TEXT[result] ?? 'Could not check'}${saved ? '' : ', but not saved'}`;
}

// ---------------------------------------------------------------------------------------------
// Groups

/**
 * Each item's group label, from its `before` blocks' Markdown: an item whose `before` blocks hold a
 * heading starts a group (its label is the heading: `headingOf` is entry.ts's `lastHeading`, of the
 * last block that has one), which lasts until the next such item. A `before` block without a
 * heading starts nothing. Items before the first group have no group (null).
 */
export function groupLabels(
  befores: readonly (readonly (string | undefined)[])[],
  headingOf: (md: string) => string | undefined,
): { label: string | null; start: boolean }[] {
  let current: string | null = null;
  return befores.map((mds) => {
    let heading: string | undefined;
    for (const md of mds) if (md !== undefined) heading = headingOf(md) ?? heading;
    if (heading !== undefined && heading !== '') {
      current = heading;
      return { label: current, start: true };
    }
    return { label: current, start: false };
  });
}

/** True when a group label already says "Challenge" (the item's Challenge tag is not repeated). */
export const saysChallenge = (label: string | null) => label !== null && /\bchallenge\b/i.test(label);

/**
 * The DOM contract between the page islands (plan 103 Phase D).
 *
 * - `py4kids:slide`: the slide player (Phase C) dispatches it each time a slide is shown, on
 *   `document` or `window` (or on an element with `bubbles: true`). `detail.key` is the global
 *   key of the slide's first block; `detail.index` is the slide number (optional). The progress
 *   island writes a `slide` event and moves the book's resume position to the slide.
 * - Practice-page checklists (Phase B): each requirement of a self-check item is an
 *   `<input type="checkbox" data-item-key="<item key>">`; an item's boxes, in document order,
 *   are its `detail.checklist`. The progress island restores their state and writes a
 *   `self-check` event on every change.
 * - `[data-resume-book="<book>"]`: a hidden element holding an `<a>` (and optionally a
 *   `[data-resume-title]` span); the progress island points the link at the book's last
 *   position and unhides it.
 */

export const SLIDE_EVENT = 'py4kids:slide';

export interface SlideEventDetail {
  key: string;
  index?: number;
  total?: number;
}

/** The slide's block key from an event detail; tolerant of `blockKey`/`block` spellings. */
export function slideKey(detail: unknown): string | undefined {
  if (typeof detail !== 'object' || detail === null) return undefined;
  const d = detail as Record<string, unknown>;
  for (const name of ['key', 'blockKey', 'block', 'item_key']) {
    const value = d[name];
    if (typeof value === 'string' && value) return value;
  }
  return undefined;
}

/** The checklist of one item: its boxes' checked states, in document order. */
export function checklistOf(root: ParentNode, itemKey: string): boolean[] {
  return [...root.querySelectorAll<HTMLInputElement>('input[type="checkbox"][data-item-key]')]
    .filter((box) => box.dataset.itemKey === itemKey)
    .map((box) => box.checked);
}

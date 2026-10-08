/**
 * The DOM contract between the page islands (plan 103 Phase D).
 *
 * - `py4kids:slide`: the slide player (Phase C) dispatches it on `document` each time a slide is
 *   shown, with `{book, entry, index, key, count}`. `detail.key` is the slide's identifier (its
 *   first block's global key, `#slide-<k>` on the k-th slide of a split block; `slideKeys`); `detail.index` is 0-based. The progress island (a capturing `window` listener)
 *   writes a `slide` event and moves the book's resume position to the slide.
 * - Practice-page checklists (Phase B): each requirement of a self-check item is an
 *   `<input type="checkbox" data-item-key="<item key>" data-requirement="<i>">`; an item's boxes,
 *   in document order,
 *   are its `detail.checklist`. The progress island restores their state and writes a
 *   `self-check` event on every change.
 * - `[data-resume-book="<book>"]`: a hidden element holding an `<a>` (and optionally a
 *   `[data-resume-title]` span); the progress island points the link at the book's last
 *   position and unhides it.
 * - `py4kids:progress-imported` (plan 105 Phase C): the export/import island dispatches it on
 *   `document` after an import wrote to the store; the progress island fills the "Continue" links
 *   again.
 */

export const SLIDE_EVENT = 'py4kids:slide';
export const PROGRESS_IMPORTED_EVENT = 'py4kids:progress-imported';

/** What the slide player (src/scripts/slides.ts) sends; only `key` is required here. */
export interface SlideEventDetail {
  key: string;
  book?: string;
  entry?: string;
  /** 0-based slide index. */
  index?: number;
  count?: number;
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

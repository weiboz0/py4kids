/**
 * What the progress island needs to know about a page (plan 103 Phase D), rendered by the layout
 * as `data-*` attributes on `<body>`: the book, its release content hash (every progress event
 * carries it), and, on an entry's pages (`/<book>/<entry>/`, `.../slides/`, `.../practice/`),
 * the entry, so the page can record the reader's position in the `resume` store, labelled with
 * the kind of page it is (`resumeTitle`, e.g. "Unit 3 — Story Machine (exercises)"), so the
 * "Continue" link never implies reading when it leads to practice or slides.
 */

import type { LoadedBook } from './bundle';
import type { EntryKind } from './types';

/** The practice page's heading for an entry kind (the page and the resume label share it). */
export const practiceHeading = (kind: EntryKind): string =>
  kind === 'unit' ? 'Exercises' : kind === 'checkpoint' ? 'Questions' : 'Problems';

/** The kind of entry page at `page` (the path segment after the entry), lower case. */
function pageLabel(kind: EntryKind, page: string | undefined): string {
  if (page === 'slides') return 'slides';
  if (page === 'practice') return practiceHeading(kind).toLowerCase();
  return kind === 'unit' ? 'lesson' : 'reading';
}

export interface PageContext {
  book: string;
  contentHash: string;
  entry?: string;
  entryTitle?: string;
  /** The resume link's label: the entry title and the page kind. */
  resumeTitle?: string;
}

export function pageContext(book: LoadedBook, pathname: string): PageContext {
  const ctx: PageContext = { book: book.id, contentHash: book.book.release.content_hash };
  const parts = pathname.split('/').filter(Boolean);
  if (parts[0] === book.id && parts[1]) {
    const record = book.book.entries.find((e) => e.id === parts[1]);
    if (record) {
      ctx.entry = record.id;
      ctx.entryTitle = record.title;
      ctx.resumeTitle = `${record.title} (${pageLabel(record.kind, parts[2])})`;
    }
  }
  return ctx;
}

/** The `data-*` attributes for `<body>`. */
export function pageDataAttributes(ctx: PageContext | undefined): Record<string, string> {
  if (!ctx) return {};
  const out: Record<string, string> = { 'data-book': ctx.book, 'data-content-hash': ctx.contentHash };
  if (ctx.entry) out['data-entry'] = ctx.entry;
  if (ctx.entryTitle) out['data-entry-title'] = ctx.entryTitle;
  if (ctx.resumeTitle) out['data-resume-title'] = ctx.resumeTitle;
  return out;
}

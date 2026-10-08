/**
 * What the progress island needs to know about a page (plan 103 Phase D), rendered by the layout
 * as `data-*` attributes on `<body>`: the book, its release content hash (every progress event
 * carries it), and, on an entry's pages (`/<book>/<entry>/`, `.../slides/`, `.../practice/`),
 * the entry, so the page can record the reader's position in the `resume` store.
 */

import type { LoadedBook } from './bundle';

export interface PageContext {
  book: string;
  contentHash: string;
  entry?: string;
  entryTitle?: string;
}

export function pageContext(book: LoadedBook, pathname: string): PageContext {
  const ctx: PageContext = { book: book.id, contentHash: book.book.release.content_hash };
  const parts = pathname.split('/').filter(Boolean);
  if (parts[0] === book.id && parts[1]) {
    const record = book.book.entries.find((e) => e.id === parts[1]);
    if (record) {
      ctx.entry = record.id;
      ctx.entryTitle = record.title;
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
  return out;
}

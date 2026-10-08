/**
 * View models for the layout shell and the catalog (plan 103 Phase A). Pages read bundle data
 * only through functions like these, so the schema-key test can run them over a recording proxy.
 */

import type { LoadedBook } from './bundle';

export interface BookLink {
  id: string;
  title: string;
  href: string;
}

export interface CatalogCard extends BookLink {
  subtitle: string;
  unitCount: number;
}

export const bookHref = (id: string): string => `/${id}/`;

/** The header's book switcher. */
export function bookLinks(books: LoadedBook[]): BookLink[] {
  return books.map((b) => ({ id: b.id, title: b.book.book.title, href: bookHref(b.id) }));
}

/** The catalog page `/`: each book's title, subtitle and unit count. */
export function catalogCards(books: LoadedBook[]): CatalogCard[] {
  return books.map((b) => ({
    id: b.id,
    title: b.book.book.title,
    subtitle: b.book.book.subtitle,
    href: bookHref(b.id),
    unitCount: b.book.entries.filter((e) => e.kind === 'unit').length,
  }));
}

/**
 * The footer's release line: the given book's release tag, or, on a page that belongs to no
 * book, the tag every book shares (books exported together share one), else nothing.
 */
export function releaseTag(books: LoadedBook[], book?: LoadedBook): string | undefined {
  if (book) return book.book.release.tag;
  const tags = new Set(books.map((b) => b.book.release.tag));
  return tags.size === 1 ? [...tags][0] : undefined;
}

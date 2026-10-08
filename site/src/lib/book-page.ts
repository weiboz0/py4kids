/**
 * View models for a book's own pages (plan 103 Phase E): the contents page `/<book>/`, the
 * glossary `/<book>/glossary/` and the quick reference `/<book>/reference/`. Pages read bundle
 * data only through these functions (they are in the schema-key test's CONSUMERS).
 */

import type { LoadedBook } from './bundle';
import { bookHref } from './catalog';
import { renderMarkdown } from './markdown';
import { buildSlides } from './slides';
import type { EntryKind, PdfEdition } from './types';

export const glossaryHref = (book: string) => `${bookHref(book)}glossary/`;
export const referenceHref = (book: string) => `${bookHref(book)}reference/`;
export const cardsHref = (book: string) => `${bookHref(book)}cards/`;

export const KIND_LABELS: Record<EntryKind, string> = {
  unit: 'Unit',
  checkpoint: 'Checkpoint',
  project: 'Project',
};

const PRACTICE_LABELS: Record<EntryKind, string> = {
  unit: 'Exercises',
  checkpoint: 'Questions',
  project: 'Problems',
};

/** The release PDFs, as the book page lists them (student editions first). */
export const PDF_EDITIONS: { edition: PdfEdition; label: string; audience: 'student' | 'adult' }[] = [
  { edition: 'student', label: 'Student Book (screen)', audience: 'student' },
  { edition: 'student-print', label: 'Student Book (print)', audience: 'student' },
  { edition: 'answer-key', label: 'Answer Key', audience: 'adult' },
  { edition: 'teacher', label: "Teacher's Edition", audience: 'adult' },
];

export interface ContentsEntry {
  id: string;
  kind: EntryKind;
  /** "Unit 3", "Checkpoint 1" (or "Unit" for an unnumbered entry). */
  kindLabel: string;
  /** The entry's full title. */
  title: string;
  /** The title without a leading "Checkpoint 1 — " that the kind label already shows. */
  name: string;
  /** The reading view. */
  href: string;
  /** The practice page, when the entry has items. */
  practice: { href: string; label: string; count: number } | null;
  /** The slide deck, when the lesson has slides (the slide route set). */
  slidesHref: string | null;
}

export interface PdfLink {
  edition: PdfEdition;
  label: string;
  audience: 'student' | 'adult';
  href: string;
}

export interface BookPage {
  id: string;
  title: string;
  subtitle: string;
  release: string;
  /** Every entry, in syllabus order. */
  entries: ContentsEntry[];
  counts: Record<EntryKind, number>;
  glossaryHref: string | null;
  referenceHref: string | null;
  /** The release PDFs; null when the bundle is unreleased (no PDF section). */
  pdfs: PdfLink[] | null;
}

export function bookPage(book: LoadedBook): BookPage {
  const counts: Record<EntryKind, number> = { unit: 0, checkpoint: 0, project: 0 };
  const entries = book.entries.map(({ record, data }): ContentsEntry => {
    counts[record.kind]++;
    const href = `${bookHref(book.id)}${record.id}/`;
    const items = data.items.length;
    const lesson = data.lesson;
    const kind = KIND_LABELS[record.kind];
    const kindLabel = record.number === null ? kind : `${kind} ${record.number}`;
    const prefix = new RegExp(`^${kindLabel}\\s*[—:–-]\\s*`);
    return {
      id: record.id,
      kind: record.kind,
      kindLabel,
      title: record.title,
      name: record.title.replace(prefix, '') || record.title,
      href,
      practice: items > 0 ? { href: `${href}practice/`, label: PRACTICE_LABELS[record.kind], count: items } : null,
      slidesHref: lesson !== null && buildSlides(lesson.blocks).length > 0 ? `${href}slides/` : null,
    };
  });
  const pdfs = book.book.pdfs;
  return {
    id: book.id,
    title: book.book.book.title,
    subtitle: book.book.book.subtitle,
    release: book.book.release.tag,
    entries,
    counts,
    glossaryHref: hasGlossary(book) ? glossaryHref(book.id) : null,
    referenceHref: hasReference(book) ? referenceHref(book.id) : null,
    pdfs: pdfs === null ? null : PDF_EDITIONS.map((e) => ({ ...e, href: pdfs[e.edition] })),
  };
}

export const hasGlossary = (book: LoadedBook) => book.book.glossary.length > 0;
export const hasReference = (book: LoadedBook) => book.book.reference_md.trim() !== '';

// ---------------------------------------------------------------------------------------------
// The glossary

export interface GlossaryRow {
  term: string;
  anchor: string;
  /** The definition, rendered. */
  html: string;
  /** "First taught in Unit N", linked to that unit's reading view when the book has it. */
  firstTaught: { label: string; href: string | null } | null;
}

export interface GlossaryView {
  bookId: string;
  bookTitle: string;
  bookHref: string;
  terms: GlossaryRow[];
}

const slug = (text: string) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'term';

export function glossaryView(book: LoadedBook): GlossaryView {
  // Unit numbers to reading views (unit numbers are unique within a book).
  const units = new Map<number, string>();
  for (const { record } of book.entries) {
    if (record.kind === 'unit' && record.number !== null) units.set(record.number, `${bookHref(book.id)}${record.id}/`);
  }
  const used = new Set<string>();
  const terms = book.book.glossary.map((t): GlossaryRow => {
    let anchor = `term-${slug(t.term)}`;
    for (let n = 2; used.has(anchor); n++) anchor = `term-${slug(t.term)}-${n}`;
    used.add(anchor);
    const first = t.units.length > 0 ? Math.min(...t.units) : null;
    return {
      term: t.term,
      anchor,
      html: renderMarkdown(t.definition_md),
      firstTaught: first === null ? null : { label: `Unit ${first}`, href: units.get(first) ?? null },
    };
  });
  return { bookId: book.id, bookTitle: book.book.book.title, bookHref: bookHref(book.id), terms };
}

// ---------------------------------------------------------------------------------------------
// The quick reference

export interface ReferenceView {
  bookId: string;
  bookTitle: string;
  bookHref: string;
  html: string;
  /** True when the reference opens with its own level-1 heading (the page then adds none). */
  ownHeading: boolean;
}

export function referenceView(book: LoadedBook): ReferenceView {
  const md = book.book.reference_md;
  return {
    bookId: book.id,
    bookTitle: book.book.book.title,
    bookHref: bookHref(book.id),
    html: renderMarkdown(md),
    ownHeading: /^\s*#[ \t]/.test(md),
  };
}

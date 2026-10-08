/**
 * View models for an entry's reading view (`/<book>/<entry>/`) and practice page
 * (`/<book>/<entry>/practice/`) (plan 103 Phase B). Pages read bundle data only through these
 * functions (the schema-key test runs them over a recording proxy).
 *
 * Hidden answers stay hidden: nothing here reads `answer_md`, `check.source`, `check.hash`,
 * `check.program` or a fixture's `out_file`. The poisoned-bundle leak test proves the built site
 * carries none of them.
 */

import type { LoadedBook, LoadedEntry } from './bundle';
import { bookHref } from './catalog';
import { escapeHtml, highlightCode, renderInline, renderMarkdown, renderOutput } from './markdown';
import { turtleSvg } from './turtle';
import type { Block, Check, EntryKind, Item } from './types';

export const ISSUES_URL = 'https://github.com/weiboz0/py4kids/issues/new';
export const REPORT_LABEL = 'For parents and teachers: report a problem';

/**
 * A prefilled GitHub new-issue link carrying only the item key and the bundle content hash
 * (plan 103, "Report a problem"). A plain link: no script, nothing sent until the adult submits.
 */
export function reportHref(key: string, contentHash: string): string {
  const title = `Problem report: ${key}`;
  const body = `Item: ${key}\nContent: ${contentHash}\n\nWhat is wrong:\n`;
  return `${ISSUES_URL}?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
}

export const entryHref = (book: string, entry: string) => `${bookHref(book)}${entry}/`;
export const practiceHref = (book: string, entry: string) => `${entryHref(book, entry)}practice/`;
export const slidesHref = (book: string, entry: string) => `${entryHref(book, entry)}slides/`;

// ---------------------------------------------------------------------------------------------
// Blocks

/** Panel labels, as the PDFs label each block type (null: no label). */
export const BLOCK_LABELS: Record<Block['type'], string | null> = {
  prose: null,
  opener: null,
  goals: 'You will learn',
  recap: 'Recap',
  notice: 'Notice',
  code: null,
  tryit: 'Try it yourself',
  'error-demo': 'Read the error',
  'hang-demo': 'Watch out: this never stops',
  'turtle-figure': null,
  program: 'Program',
  starter: 'Starter',
};

const PANEL_TYPES = new Set<Block['type']>(['opener', 'goals', 'recap', 'notice', 'tryit', 'error-demo', 'hang-demo', 'program', 'starter']);

/** The last heading in a block's Markdown, outside code fences, as plain text. */
export function lastHeading(md: string): string | undefined {
  const outside = md.replace(/^(```|~~~)[^\n]*\n[\s\S]*?^\1[^\n]*$/gm, '');
  const headings = [...outside.matchAll(/^#{1,6}[ \t]+(.+?)[ \t#]*$/gm)].map((m) =>
    m[1]!.replace(/[`*_]/g, '').trim(),
  );
  return headings.at(-1);
}

/** One block as HTML. `heading` names the nearest heading above it (for a figure's label). */
export function renderBlock(block: Block, heading: string): string {
  const type = block.type;
  const label = BLOCK_LABELS[type];
  const parts: string[] = [];
  if (label) parts.push(`<p class="panel-label">${escapeHtml(label)}</p>`);
  if (block.md !== undefined) parts.push(renderMarkdown(block.md));
  if (block.code !== undefined) parts.push(highlightCode(block.code, 'python'));
  if (block.sample_input !== undefined && block.sample_input !== '') {
    parts.push(`<div class="io"><p class="io-label">Sample input</p>${renderOutput(block.sample_input)}</div>`);
  }
  if (block.output !== undefined && block.output !== '') {
    parts.push(`<div class="io io-output"><p class="io-label">Output</p>${renderOutput(block.output)}</div>`);
  }
  if (type === 'turtle-figure' && block.figure && block.figure.length > 0) {
    parts.push(`<figure class="turtle">${turtleSvg(block.figure, `Drawing for ${heading}`)}</figure>`);
  }
  const classes = ['block', `block-${type}`];
  if (PANEL_TYPES.has(type)) classes.push('panel', `panel-${type}`);
  return `<div class="${classes.join(' ')}" data-key="${escapeHtml(block.key)}">\n${parts.join('\n')}\n</div>`;
}

/** Blocks in order, each labelled for its figure by the nearest heading above it. */
export function renderBlocks(blocks: Block[], fallbackHeading: string): string[] {
  let heading = fallbackHeading;
  return blocks.map((block) => {
    const html = renderBlock(block, heading);
    if (block.md !== undefined) heading = lastHeading(block.md) ?? heading;
    return html;
  });
}

// ---------------------------------------------------------------------------------------------
// Navigation

export interface NavLink {
  href: string;
  title: string;
}

function neighbours(book: LoadedBook, entryId: string): { prev: NavLink | null; next: NavLink | null } {
  const records = book.book.entries;
  const i = records.findIndex((r) => r.id === entryId);
  const link = (j: number): NavLink | null => {
    const r = j >= 0 ? records[j] : undefined;
    return r ? { href: entryHref(book.id, r.id), title: r.title } : null;
  };
  return { prev: link(i - 1), next: link(i + 1) };
}

function findEntry(book: LoadedBook, entryId: string): LoadedEntry {
  const entry = book.entries.find((e) => e.record.id === entryId);
  if (!entry) throw new Error(`no entry ${entryId} in ${book.id}`);
  return entry;
}

/** Every entry page's route parameters, in book then syllabus order. */
export function entryPaths(books: LoadedBook[]): { book: string; entry: string }[] {
  return books.flatMap((b) => b.book.entries.map((r) => ({ book: b.id, entry: r.id })));
}

/** The practice pages: every entry that has items. */
export function practicePaths(books: LoadedBook[]): { book: string; entry: string }[] {
  return books.flatMap((b) =>
    b.entries.filter((e) => e.data.items.length > 0).map((e) => ({ book: b.id, entry: e.record.id })),
  );
}

// ---------------------------------------------------------------------------------------------
// The reading view

export interface ReadingView {
  bookId: string;
  bookTitle: string;
  bookHref: string;
  entryId: string;
  kind: EntryKind;
  title: string;
  /** A lesson's blocks, or (for a checkpoint or project, which has none) its intro. */
  blocks: string[];
  hasLesson: boolean;
  /** `/<book>/<entry>/slides/` when the entry has a lesson (the slide player's route). */
  slidesHref: string | null;
  practiceHref: string | null;
  practiceCount: number;
  prev: NavLink | null;
  next: NavLink | null;
  reportHref: string;
}

export function readingView(book: LoadedBook, entryId: string): ReadingView {
  const entry = findEntry(book, entryId);
  const data = entry.data;
  const title = entry.record.title;
  const lesson = data.lesson;
  const itemCount = data.items.length;
  return {
    bookId: book.id,
    bookTitle: book.book.book.title,
    bookHref: bookHref(book.id),
    entryId,
    kind: entry.record.kind,
    title,
    blocks: renderBlocks(lesson ? lesson.blocks : data.intro, title),
    hasLesson: lesson !== null,
    slidesHref: lesson !== null && lesson.blocks.length > 0 ? slidesHref(book.id, entryId) : null,
    practiceHref: itemCount > 0 ? practiceHref(book.id, entryId) : null,
    practiceCount: itemCount,
    ...neighbours(book, entryId),
    reportHref: reportHref(`${book.id}/${entryId}`, book.book.release.content_hash),
  };
}

// ---------------------------------------------------------------------------------------------
// The practice page

export interface Requirement {
  id: string;
  index: number;
  html: string;
}

export interface PracticeItem {
  key: string;
  anchor: string;
  label: string;
  title: string;
  stretch: boolean;
  divisions: string[];
  before: string[];
  statement: string;
  /** Read-only starter code, highlighted; null when the item has none. */
  starter: string | null;
  /** "How this is checked". */
  checkLine: string;
  /** The answer format hint ("one line"), for typed answers. */
  formatHint: string | null;
  /** A self-check item's requirements, as a checklist; null for every other kind. */
  selfCheck: Requirement[] | null;
  /** Every kind but self-check: checking arrives in part C. */
  checkingSoon: boolean;
  reportHref: string;
}

export interface PracticeView {
  bookId: string;
  bookTitle: string;
  bookHref: string;
  entryId: string;
  kind: EntryKind;
  title: string;
  heading: string;
  readingHref: string;
  intro: string[];
  items: PracticeItem[];
  outro: string[];
}

const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? '' : 's'}`;

/** The "How this is checked" line for a check kind. Reads no hidden field. */
export function checkLine(check: Check): string {
  const turtle = check.turtle ? ' The turtle drawing is checked from the moves your program makes.' : '';
  switch (check.kind) {
    case 'fixtures': {
      const samples = check.cases.filter((c) => c.sample).length;
      const hidden = check.cases.length - samples;
      const how = check.match === 'line' ? 'line by line' : 'word by word';
      return `Checked by running your program on ${plural(check.cases.length, 'test input')} (${samples} sample, ${hidden} hidden) and comparing its output ${how}.${turtle}`;
    }
    case 'answer':
      return `Checked by comparing your answer with the expected answer${check.answer_format.case === 'insensitive' ? ', ignoring capital letters' : ''}.${turtle}`;
    case 'expected-output':
      return `Checked by comparing what your program prints with the expected output${check.answer_format.case === 'insensitive' ? ', ignoring capital letters' : ''}.${turtle}`;
    case 'predict':
      return `Checked by comparing your prediction with what the program really prints.${turtle}`;
    case 'asserts': {
      const fns = check.functions.map((f) => `\`${f}\``);
      const what = fns.length === 0 ? 'your code' : `your ${fns.length === 1 ? 'function' : 'functions'} ${fns.join(', ')}`;
      return `Checked by tests that run ${what}.${turtle}`;
    }
    case 'self-check':
      return `You check this one yourself, against the list below.${turtle}`;
  }
}

const slug = (text: string) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'item';

const divisionName = (id: string) => id.charAt(0).toUpperCase() + id.slice(1);

function practiceItem(item: Item, anchor: string, contentHash: string): PracticeItem {
  const check = item.check;
  const selfCheck =
    check.kind === 'self-check'
      ? check.requirements.map((text, index) => ({ id: `${anchor}-req-${index}`, index, html: renderInline(text) }))
      : null;
  // Narrow by kind, never with `in`: the schema-key test records every probe.
  const hint =
    check.kind === 'answer' || check.kind === 'expected-output' || check.kind === 'predict'
      ? check.answer_format.hint
      : null;
  return {
    key: item.key,
    anchor,
    label: item.label,
    title: item.title,
    stretch: item.stretch,
    divisions: item.division.map(divisionName),
    before: renderBlocks(item.before, item.label),
    statement: renderMarkdown(item.statement_md),
    starter: item.starter.trim() === '' ? null : highlightCode(item.starter, 'python'),
    checkLine: renderInline(checkLine(check)),
    formatHint: hint || null,
    selfCheck,
    checkingSoon: check.kind !== 'self-check',
    reportHref: reportHref(item.key, contentHash),
  };
}

export function practiceView(book: LoadedBook, entryId: string): PracticeView {
  const entry = findEntry(book, entryId);
  const data = entry.data;
  const kind = entry.record.kind;
  const contentHash = book.book.release.content_hash;
  const used = new Set<string>();
  const items = data.items.map((item, i) => {
    let anchor = slug(item.label || `item ${i + 1}`);
    if (used.has(anchor)) anchor = `${anchor}-${i + 1}`;
    used.add(anchor);
    return practiceItem(item, anchor, contentHash);
  });
  return {
    bookId: book.id,
    bookTitle: book.book.book.title,
    bookHref: bookHref(book.id),
    entryId,
    kind,
    title: entry.record.title,
    heading: kind === 'unit' ? 'Exercises' : kind === 'checkpoint' ? 'Questions' : 'Problems',
    readingHref: entryHref(book.id, entryId),
    intro: renderBlocks(data.intro, entry.record.title),
    items,
    outro: renderBlocks(data.outro, entry.record.title),
  };
}

// ---------------------------------------------------------------------------------------------
// The code stylesheet

/**
 * Render every Markdown and code string any page shows, so the highlighter's class registry is
 * complete before `/code.css` is written (pages and the stylesheet may build in any order).
 * Covers the reading and practice pages, the glossary, the reference and the concept cards;
 * never `answer_md` (part B renders none).
 */
export function warmPipeline(books: LoadedBook[]): void {
  for (const path of entryPaths(books)) readingView(bookOf(books, path.book), path.entry);
  for (const path of practicePaths(books)) practiceView(bookOf(books, path.book), path.entry);
  for (const book of books) {
    for (const term of book.book.glossary) renderMarkdown(term.definition_md);
    renderMarkdown(book.book.reference_md);
    for (const entry of book.entries) {
      for (const card of entry.data.cards) if (card.kind === 'concept') renderMarkdown(card.definition_md);
    }
  }
}

function bookOf(books: LoadedBook[], id: string): LoadedBook {
  const book = books.find((b) => b.id === id);
  if (!book) throw new Error(`no book ${id}`);
  return book;
}

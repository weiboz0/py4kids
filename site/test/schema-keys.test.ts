/**
 * Every key the site's code reads is declared in the bundle schema (plan 103, Architecture).
 * Add each new bundle-reading view model (Phases B–E) to CONSUMERS.
 */
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBook, loadBooks, repoRoot, type LoadedBook } from '../src/lib/bundle';
import { bookLinks, catalogCards, releaseTag } from '../src/lib/catalog';
import { bookPage, glossaryView, referenceView } from '../src/lib/book-page';
import { slideDecks } from '../src/lib/slide-view';
import { deckProjection, deckSummary } from '../src/lib/cards';
import { attribution, masteryMap, masteryProjection } from '../src/lib/mastery';
import { pageContext } from '../src/lib/page-context';
import { entryPaths, practicePaths, practiceView, readingView, warmPipeline } from '../src/lib/entry';
import { answerProjection, bundleFiles, checkProjection, itemRoutes, lessonRunProjection } from '../src/lib/checks';
import { distinctReads, makeDeclared, Recorder, undeclaredReads } from './helpers/schema-keys';

const FIXTURE = join(import.meta.dirname, 'fixtures', 'bundles', 'demo');
const CONTENT = join(repoRoot(), 'site', 'content');
const hasRealBundles = existsSync(CONTENT) && loadable();

function loadable(): boolean {
  try {
    loadBooks({ contentDir: CONTENT });
    return true;
  } catch {
    return false;
  }
}

/** Every function that reads bundle data for a page. */
const CONSUMERS: ((books: LoadedBook[]) => unknown)[] = [
  bookLinks,
  catalogCards,
  (books) => releaseTag(books),
  (books) => books.map((b) => releaseTag(books, b)),
  // Phase E: the book page, the glossary and the quick reference.
  (books) => books.map(bookPage),
  (books) => books.map(glossaryView),
  (books) => books.map(referenceView),
  (books) => books.map(slideDecks),
  // Phase D: the card deck, the mastery map and the progress island's page context.
  (books) => books.map(deckProjection),
  (books) => books.map(deckSummary),
  (books) => books.map((b) => [...attribution(b).cards, ...attribution(b).items]),
  (books) => books.map(masteryMap),
  (books) => books.map(masteryProjection),
  (books) => books.map((b) => b.book.entries.map((e) => pageContext(b, `/${b.id}/${e.id}/`))),
  // Phase B: the reading view, the practice page and the code stylesheet's warm-up.
  (books) => entryPaths(books),
  (books) => practicePaths(books),
  (books) => books.flatMap((b) => b.book.entries.map((e) => readingView(b, e.id))),
  (books) => practicePaths(books).map((p) => practiceView(books.find((b) => b.id === p.book)!, p.entry)),
  (books) => warmPipeline(books),
  // Plan 104 Phase B: the check, answer and lesson-run projections and the served files.
  (books) => itemRoutes(books).map((r) => checkProjection(r.book, r.item)),
  (books) => itemRoutes(books).map((r) => answerProjection(r.item)),
  (books) => books.flatMap((b) => b.entries.map((e) => lessonRunProjection(b, e))),
  (books) => books.map(bundleFiles),
];

/**
 * Keys the site reads that a branch not yet merged here declares: plan 102 (`also_check`,
 * `answer_format.aliases` and `.whitespace`) and plan 104 Phase C (`check.cpu_ms`,
 * `answer_figures`). The site reads each as optional. Each must still be undeclared: once the
 * schema declares it, the 'pending keys' test fails until it is removed from this list.
 */
const PENDING_KEYS = new Set(['also_check', 'aliases', 'whitespace', 'cpu_ms', 'answer_figures']);
const SCHEMA_TEXT = readFileSync(join(repoRoot(), 'tools', 'export', 'schema', 'bundle.schema.json'), 'utf-8');
const notPending = (reads: string[]) => reads.filter((read) => !PENDING_KEYS.has(read.split(' ').at(-1)!));

function run(books: LoadedBook[]): void {
  for (const consume of CONSUMERS) JSON.stringify(consume(books));
}

describe('declared', () => {
  const declared = makeDeclared();
  const raw = (file: string) => loadBook(FIXTURE).entries.find((e) => e.record.file === file)!.data;

  it('follows oneOf branches, items and if/then', () => {
    const unit = raw('entries/unit-01-demo.json');
    const checkpoint = raw('entries/checkpoint-01-demo.json');
    expect(declared('entry_file', checkpoint, ['items', 0, 'check'], 'hash')).toBe(true);
    expect(declared('entry_file', unit, ['items', 0, 'check'], 'hash')).toBe(false); // a self-check
    expect(declared('entry_file', unit, ['items', 0], 'solution')).toBe(false);
    expect(declared('entry_file', unit, ['lesson', 'blocks', 0], 'md')).toBe(true);
    expect(declared('entry_file', unit, ['lesson', 'blocks', 0], 'output')).toBe(true); // optional, absent
    expect(declared('entry_file', unit, ['cards', 1], 'distractors')).toBe(true);
    expect(declared('entry_file', unit, ['cards', 0], 'distractors')).toBe(false); // a predict card
  });
});

describe('the site reads only declared keys', () => {
  it('catches an undeclared read', () => {
    const recorder = new Recorder();
    const book = loadBook(FIXTURE, { wrap: recorder.wrap });
    void (book.book.book as unknown as Record<string, unknown>).cover;
    void (book.entries[0]!.data.items[0] as unknown as Record<string, unknown>).solution;
    expect(undeclaredReads(recorder)).toEqual([
      'book.json /book cover',
      'entries/unit-01-demo.json /items/0 solution',
    ]);
  });

  it('pending keys are still undeclared (drop each from PENDING_KEYS once its schema change lands)', () => {
    for (const key of PENDING_KEYS) expect(SCHEMA_TEXT.includes(`"${key}":`), key).toBe(false);
  });

  it('on the fixture bundle', () => {
    const recorder = new Recorder();
    run([loadBook(FIXTURE, { wrap: recorder.wrap })]);
    expect(notPending(undeclaredReads(recorder))).toEqual([]);
    expect(distinctReads(recorder)).toBeGreaterThan(10);
  });

  it.skipIf(!hasRealBundles)('on every real bundle under site/content', () => {
    const recorder = new Recorder();
    const books = loadBooks({ contentDir: CONTENT, wrap: recorder.wrap });
    run(books);
    expect(notPending(undeclaredReads(recorder))).toEqual([]);
    expect(distinctReads(recorder)).toBeGreaterThan(10 * books.length);
  });
});

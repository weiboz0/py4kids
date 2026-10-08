/**
 * Every key the site's code reads is declared in the bundle schema (plan 103, Architecture).
 * Add each new bundle-reading view model (Phases B–E) to CONSUMERS.
 */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBook, loadBooks, repoRoot, type LoadedBook } from '../src/lib/bundle';
import { bookLinks, catalogCards, contents, releaseTag } from '../src/lib/catalog';
import { slideDecks } from '../src/lib/slide-view';
import { deckProjection, deckSummary } from '../src/lib/cards';
import { attribution, masteryMap, masteryProjection } from '../src/lib/mastery';
import { pageContext } from '../src/lib/page-context';
import { entryPaths, practicePaths, practiceView, readingView, warmPipeline } from '../src/lib/entry';
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
  (books) => books.map(contents),
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
];

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

  it('on the fixture bundle', () => {
    const recorder = new Recorder();
    run([loadBook(FIXTURE, { wrap: recorder.wrap })]);
    expect(undeclaredReads(recorder)).toEqual([]);
    expect(distinctReads(recorder)).toBeGreaterThan(10);
  });

  it.skipIf(!hasRealBundles)('on every real bundle under site/content', () => {
    const recorder = new Recorder();
    const books = loadBooks({ contentDir: CONTENT, wrap: recorder.wrap });
    run(books);
    expect(undeclaredReads(recorder)).toEqual([]);
    expect(distinctReads(recorder)).toBeGreaterThan(10 * books.length);
  });
});

/**
 * The book page, glossary and quick reference view models (plan 103 Phase E), on the demo
 * fixture bundle and on a released copy of it (`pdfs` set), plus the real bundles when present.
 */
import { cpSync, existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterAll, describe, expect, it } from 'vitest';
import { bookPage, glossaryView, PDF_EDITIONS, referenceView } from '../src/lib/book-page';
import { loadBook, loadBooks, repoRoot } from '../src/lib/bundle';
import { codeCss } from '../src/lib/markdown';
import { warmPipeline } from '../src/lib/entry';

const FIXTURE = join(import.meta.dirname, 'fixtures', 'bundles', 'demo');
const CONTENT = join(repoRoot(), 'site', 'content');
const realBooks = (() => {
  try {
    return existsSync(CONTENT) ? loadBooks({ contentDir: CONTENT }) : [];
  } catch {
    return [];
  }
})();

const RELEASE = 'pdfs-2026-09-30';
const work = mkdtempSync(join(tmpdir(), 'py4kids-book-page-'));
afterAll(() => rmSync(work, { recursive: true, force: true }));

/** The demo bundle as a release would export it: a release tag and its four PDF links. */
function releasedDemo() {
  const dir = join(work, 'demo');
  cpSync(FIXTURE, dir, { recursive: true });
  const path = join(dir, 'book.json');
  const book = JSON.parse(readFileSync(path, 'utf-8')) as Record<string, unknown>;
  book.release = { ...(book.release as object), tag: RELEASE };
  book.pdfs = Object.fromEntries(
    PDF_EDITIONS.map((e) => [e.edition, `https://github.com/weiboz0/py4kids/releases/download/${RELEASE}/demo-${e.edition}.pdf`]),
  );
  writeFileSync(path, JSON.stringify(book));
  return loadBook(dir);
}

describe('bookPage', () => {
  const demo = loadBook(FIXTURE);

  it('lists every entry in syllabus order with its reading, practice and slide links', () => {
    const page = bookPage(demo);
    expect(page.entries.map((e) => e.id)).toEqual(demo.book.entries.map((e) => e.id));
    const [unit, checkpoint] = page.entries;
    expect(unit).toMatchObject({
      kind: 'unit',
      kindLabel: 'Unit 1',
      name: 'Demo',
      href: '/demo/unit-01-demo/',
      practice: { href: '/demo/unit-01-demo/practice/', label: 'Exercises', count: 1 },
      slidesHref: '/demo/unit-01-demo/slides/',
    });
    // A checkpoint has no lesson, so no slides; its title keeps no repeated "Checkpoint 1".
    expect(checkpoint).toMatchObject({
      kind: 'checkpoint',
      kindLabel: 'Checkpoint 1',
      name: 'Demo',
      title: 'Checkpoint 1 — Demo',
      practice: { href: '/demo/checkpoint-01-demo/practice/', label: 'Questions', count: 1 },
      slidesHref: null,
    });
    expect(page.counts).toEqual({ unit: 1, checkpoint: 1, project: 0 });
    expect(page.glossaryHref).toBe('/demo/glossary/');
    expect(page.referenceHref).toBe('/demo/reference/');
  });

  it('has no PDF section while unreleased', () => {
    expect(demo.book.pdfs).toBeNull();
    expect(bookPage(demo).pdfs).toBeNull();
  });

  it('lists the four release PDFs when the bundle has a release, student editions first', () => {
    const page = bookPage(releasedDemo());
    expect(page.release).toBe(RELEASE);
    expect(page.pdfs?.map((p) => [p.label, p.audience])).toEqual([
      ['Student Book (screen)', 'student'],
      ['Student Book (print)', 'student'],
      ['Answer Key', 'adult'],
      ["Teacher's Edition", 'adult'],
    ]);
    for (const pdf of page.pdfs!) {
      expect(pdf.href).toBe(`https://github.com/weiboz0/py4kids/releases/download/${RELEASE}/demo-${pdf.edition}.pdf`);
    }
  });

  it.skipIf(realBooks.length === 0)('lists every entry of every real book, in order, with links that route', () => {
    for (const book of realBooks) {
      const page = bookPage(book);
      expect(page.entries.map((e) => e.id)).toEqual(book.book.entries.map((e) => e.id));
      for (const e of page.entries) {
        expect(e.href).toBe(`/${book.id}/${e.id}/`);
        expect(e.name.length, e.id).toBeGreaterThan(0);
        expect(e.name.startsWith(e.kindLabel), e.id).toBe(false);
      }
      expect(page.pdfs === null).toBe(book.book.pdfs === null);
    }
  });
});

describe('glossaryView', () => {
  it('renders each definition and links the unit that first teaches the term', () => {
    const view = glossaryView(loadBook(FIXTURE));
    expect(view.terms.map((t) => t.term)).toEqual(['print', 'variable']);
    expect(view.terms[0]).toEqual({
      term: 'print',
      anchor: 'term-print',
      html: '<p>Shows a value on the screen.</p>\n',
      firstTaught: { label: 'Unit 1', href: '/demo/unit-01-demo/' },
    });
  });

  it.skipIf(realBooks.length === 0)('links every real term to an existing unit', () => {
    for (const book of realBooks) {
      const units = new Set(book.book.entries.filter((e) => e.kind === 'unit').map((e) => `/${book.id}/${e.id}/`));
      const view = glossaryView(book);
      expect(view.terms.length).toBe(book.book.glossary.length);
      expect(new Set(view.terms.map((t) => t.anchor)).size).toBe(view.terms.length);
      for (const t of view.terms) {
        expect(t.html, t.term).toMatch(/^<p>/);
        expect(t.firstTaught?.href, `${book.id}: ${t.term}`).toSatisfy((h: string | null | undefined) => !!h && units.has(h));
      }
    }
  });
});

describe('referenceView', () => {
  it('renders the reference Markdown, keeping its own heading', () => {
    const view = referenceView(loadBook(FIXTURE));
    expect(view.ownHeading).toBe(true);
    expect(view.html).toContain('<h1>Quick reference</h1>');
    expect(view.html).toContain('<code>print(x)</code>');
  });

  it.skipIf(realBooks.length === 0)('is warmed by warmPipeline: every highlighted class it uses is in code.css', () => {
    warmPipeline(realBooks);
    const css = codeCss();
    for (const book of realBooks) {
      const html = referenceView(book).html + glossaryView(book).terms.map((t) => t.html).join('');
      const used = [...html.matchAll(/class="([^"]*)"/g)].flatMap((m) => m[1]!.split(/\s+/)).filter((c) => c.startsWith('sh-'));
      expect(used.length, book.id).toBeGreaterThan(0);
      for (const name of new Set(used)) expect(css, `${book.id}: ${name}`).toContain(`.${name}{`);
    }
  });
});

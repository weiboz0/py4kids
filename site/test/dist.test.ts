/**
 * Checks on the built site (plan 103 Global constraints), run after `astro build`; skipped when
 * site/dist does not exist (ci-local always builds first). Phase F's CSP and network tests go
 * further; these keep the skeleton honest from the start.
 */
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { describe, expect, it } from 'vitest';
import { loadBooks, repoRoot } from '../src/lib/bundle';

const DIST = join(import.meta.dirname, '..', 'dist');
const built = existsSync(join(DIST, 'index.html'));
const CONTENT = join(repoRoot(), 'site', 'content');

function files(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? files(join(dir, d.name)) : [join(dir, d.name)],
  );
}

describe.skipIf(!built)('site/dist', () => {
  const all = built ? files(DIST) : [];
  const html = all.filter((f) => f.endsWith('.html'));
  const read = (f: string) => readFileSync(f, 'utf-8');
  const rel = (f: string) => relative(DIST, f);

  it('has no inline script, inline style or style attribute', () => {
    for (const file of html) {
      const text = read(file);
      expect(text.match(/<script(?![^>]*\ssrc=)[^>]*>/g), `${rel(file)}: inline <script>`).toBeNull();
      expect(text.match(/<style[\s>]/g), `${rel(file)}: <style>`).toBeNull();
      expect(text.match(/<[^>]+\sstyle=/g), `${rel(file)}: style attribute`).toBeNull();
    }
  });

  it('has no data: URL and loads nothing from another origin', () => {
    for (const file of all.filter((f) => /\.(html|css|js)$/.test(f))) {
      const text = read(file);
      // In HTML, a data: URL can only load from an attribute or a CSS url(); lesson text may
      // say "data:" in prose ("Variation axis — data: …"). CSS and JS carry no prose.
      const dataUrl = file.endsWith('.html')
        ? /=\s*["']?\s*data:|url\(\s*["']?\s*data:/i.test(text)
        : text.includes('data:');
      expect(dataUrl, `${rel(file)}: data: URL`).toBe(false);
      expect(text.match(/<(?:script|link|img|iframe)[^>]+(?:src|href)="(?:https?:)?\/\//g), `${rel(file)}: remote load`).toBeNull();
    }
  });

  it('ships no bundle JSON', () => {
    expect(all.filter((f) => f.endsWith('book.json') || /[\\/]entries[\\/][^\\/]+\.json$/.test(f)).map(rel)).toEqual([]);
  });

  it('builds a wired slide deck for every lesson of every book', () => {
    // The built books: every book directory in dist/ that has a page per bundle entry.
    const books = readdirSync(DIST, { withFileTypes: true })
      .filter((d) => d.isDirectory() && existsSync(join(DIST, '..', 'content', d.name, 'book.json')))
      .map((d) => d.name);
    expect(books.length).toBeGreaterThan(0);
    const decks = html.filter((f) => /[\\/]slides[\\/]index\.html$/.test(f));
    for (const book of books) {
      expect(decks.some((f) => rel(f).startsWith(`${book}/`)), `${book}: no slides page`).toBe(true);
    }
    for (const file of decks) {
      const text = read(file);
      const [book, entry] = rel(file).split(/[\\/]/);
      const count = Number(/data-count="(\d+)"/.exec(text)?.[1]);
      expect(count, rel(file)).toBeGreaterThan(0);
      expect(text.match(/<li class="slide slide-/g)?.length, rel(file)).toBe(count);
      expect(text, rel(file)).toContain(`data-reading="/${book}/${entry}/"`);
      expect(text, rel(file)).toContain(`<a class="deck-exit" href="/${book}/${entry}/">`);
      expect(text, rel(file)).toMatch(new RegExp(`<progress[^>]*max="${count}"`));
      expect(text, rel(file)).toMatch(/<script type="module" src="\/_astro\/[^"]+\.js"><\/script>/);
    }
  });

  it('ships no JSON carrying an answer_md, source or hash key (plan 103 leak rule)', () => {
    const keys = (value: unknown, out: string[] = []): string[] => {
      if (Array.isArray(value)) value.forEach((v) => keys(v, out));
      else if (value && typeof value === 'object') {
        for (const [k, v] of Object.entries(value)) {
          out.push(k);
          keys(v, out);
        }
      }
      return out;
    };
    for (const file of all.filter((f) => f.endsWith('.json'))) {
      const found = keys(JSON.parse(read(file))).filter((k) => ['answer_md', 'source', 'hash', 'check'].includes(k));
      expect(found, rel(file)).toEqual([]);
    }
  });

  it('has a card deck page, its deck.json and a mastery.json for every book (plan 103 Phase D)', () => {
    const bookPages = html.filter((f) => /^[a-z0-9-]+[\\/]index\.html$/.test(rel(f)) && read(f).includes('data-content-hash='));
    expect(bookPages.length).toBeGreaterThan(0);
    for (const page of bookPages) {
      const book = rel(page).split(/[\\/]/)[0]!;
      const cards = join(DIST, book, 'cards', 'index.html');
      expect(existsSync(cards), `${book}/cards/`).toBe(true);
      const text = read(cards);
      expect(text).toContain(`data-deck data-book="${book}"`);
      expect(text).toMatch(/<script type="module" src="\/_astro\/[^"]+\.js"><\/script>/);
      const deck = JSON.parse(read(join(DIST, book, 'cards', 'deck.json'))) as { book: string; cards: { key: string; kind: string }[] };
      expect(deck.book).toBe(book);
      expect(deck.cards.length, book).toBeGreaterThan(0);
      for (const card of deck.cards) expect(card.key.startsWith(`${book}/`), card.key).toBe(true);
      const mastery = JSON.parse(read(join(DIST, book, 'mastery.json'))) as { book: string; concepts: string[] };
      expect(mastery.book).toBe(book);
      // The book page carries the resume link and the mastery map.
      expect(read(page)).toContain(`data-resume-book="${book}"`);
      expect(read(page)).toContain('data-mastery');
    }
  });

  it('puts a resume link for every book on the catalog', () => {
    const catalog = read(join(DIST, 'index.html'));
    expect(catalog.match(/data-resume-book="/g)?.length ?? 0).toBeGreaterThan(0);
  });

  // Phase B: the reading view and the practice pages.
  const books = built && existsSync(CONTENT) ? loadBooks({ contentDir: CONTENT }) : [];
  const page = (...parts: string[]) => join(DIST, ...parts, 'index.html');

  it.skipIf(books.length === 0)('has a reading page for every entry and a practice page for every entry with items', () => {
    for (const book of books) {
      for (const entry of book.entries) {
        expect(existsSync(page(book.id, entry.record.id)), `${book.id}/${entry.record.id}/`).toBe(true);
        const practice = page(book.id, entry.record.id, 'practice');
        expect(existsSync(practice), `${book.id}/${entry.record.id}/practice/`).toBe(entry.data.items.length > 0);
      }
    }
  });

  it.skipIf(books.length === 0)('draws every turtle figure as an inline SVG image with a name', () => {
    const expected = books.flatMap((b) =>
      b.entries.flatMap((e) => (e.data.lesson?.blocks ?? []).filter((x) => x.type === 'turtle-figure' && x.figure?.length)),
    ).length;
    const isSlides = (f: string) => /[\\/]slides[\\/]index\.html$/.test(f);
    // The reading views draw each figure once; the slide decks draw them again with turtle.ts.
    const svgs = html.filter((f) => !isSlides(f)).flatMap((f) => read(f).match(/<svg class="turtle-figure"[^>]*>/g) ?? []);
    expect(svgs).toHaveLength(expected);
    const slideSvgs = html.filter(isSlides).flatMap((f) => read(f).match(/<svg[^>]*>/g) ?? []);
    expect(slideSvgs.length).toBeGreaterThan(0);
    for (const svg of [...svgs, ...slideSvgs]) {
      expect(svg).toMatch(/^<svg class="turtle-figure"/);
      expect(svg).toMatch(/ role="img" aria-label="Drawing for [^"]+"/);
    }
  });

  it.skipIf(books.length === 0)('links "Slides" from exactly the reading pages that have a slide deck', () => {
    for (const book of books) {
      for (const entry of book.entries) {
        const id = entry.record.id;
        const linked = read(page(book.id, id)).includes(`href="/${book.id}/${id}/slides/"`);
        expect(linked, `${book.id}/${id}: Slides link vs slides route`).toBe(existsSync(page(book.id, id, 'slides')));
      }
    }
  });

  it('keeps the build-time pipeline (Shiki, KaTeX, markdown-it) out of every client script', () => {
    for (const file of all.filter((f) => f.endsWith('.js') && rel(f).startsWith('_astro'))) {
      expect(statSync(file).size, rel(file)).toBeLessThan(64 * 1024);
    }
  });

  it('defines every highlighted-code class in /code.css, linked from every page', () => {
    const css = read(join(DIST, 'code.css'));
    const defined = new Set([...css.matchAll(/\.(sh-[a-z0-9]+)\{/g)].map((m) => m[1]));
    for (const file of html) {
      const text = read(file);
      expect(text, rel(file)).toContain('<link rel="stylesheet" href="/code.css">');
      const used = [...text.matchAll(/class="([^"]*)"/g)].flatMap((m) => m[1]!.split(/\s+/)).filter((c) => c.startsWith('sh-'));
      for (const name of new Set(used)) expect(defined.has(name), `${rel(file)}: ${name}`).toBe(true);
    }
  });

  it('shows no Markdown source as text: no HTML comment, no fenced-div marker, no raw latex', () => {
    for (const file of html) {
      const prose = read(file).replace(/<pre[\s\S]*?<\/pre>|<code[\s\S]*?<\/code>/g, '');
      expect(prose.match(/&lt;!--|<p>:::|\{=latex\}/g), rel(file)).toBeNull();
    }
  });

  it('gives every table header cell a scope', () => {
    for (const file of html) expect(read(file).match(/<th(?![^>]*scope="col")[\s>]/g), rel(file)).toBeNull();
  });

  it.skipIf(books.length === 0)('links "report a problem" with only a key and the content hash', () => {
    // The reading and practice pages (cards render their links in the island; slides have none).
    const routes = new Set(
      books.flatMap((b) =>
        b.entries.flatMap((e) => [
          join(b.id, e.record.id, 'index.html'),
          ...(e.data.items.length > 0 ? [join(b.id, e.record.id, 'practice', 'index.html')] : []),
        ]),
      ),
    );
    const pages = html.filter((f) => routes.has(rel(f)));
    expect(pages.length).toBe(routes.size);
    expect(pages.length).toBeGreaterThan(0);
    for (const file of pages) {
      const links = [...read(file).matchAll(/<a href="([^"]+)">For parents and teachers: report a problem<\/a>/g)];
      expect(links.length, rel(file)).toBeGreaterThan(0);
      for (const [, href] of links) {
        const url = new URL(href!.replace(/&amp;/g, '&'));
        expect(`${url.origin}${url.pathname}`).toBe('https://github.com/weiboz0/py4kids/issues/new');
        expect(url.searchParams.get('body')).toMatch(/^Item: \S+\nContent: sha256:[0-9a-f]{64}\n\nWhat is wrong:\n$/);
      }
    }
  });

  it('links the license deed and the site pages from every page', () => {
    expect(html.length).toBeGreaterThan(1);
    for (const file of html) {
      const text = read(file);
      expect(text, rel(file)).toContain('<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" rel="license">');
      for (const page of ['/about/', '/privacy/', '/terms/']) expect(text, rel(file)).toContain(`href="${page}"`);
      expect(text, rel(file)).toContain('<script src="/scripts/theme.js"></script>');
    }
  });
});

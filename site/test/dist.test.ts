/**
 * Checks on the built site (plan 103 Global constraints), run after `astro build`; skipped when
 * site/dist does not exist (ci-local always builds first). Phase F's CSP and network tests go
 * further; these keep the skeleton honest from the start.
 */
import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { describe, expect, it } from 'vitest';

const DIST = join(import.meta.dirname, '..', 'dist');
const built = existsSync(join(DIST, 'index.html'));

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
      expect(text.includes('data:'), `${rel(file)}: data: URL`).toBe(false);
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

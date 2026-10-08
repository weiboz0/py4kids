/**
 * Checks on the built site (plan 103 Global constraints), run after `astro build`; skipped when
 * site/dist does not exist (ci-local always builds first). Phase F's CSP and network tests go
 * further; these keep the skeleton honest from the start.
 */
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { describe, expect, it } from 'vitest';
import { gunzipSync } from 'node:zlib';
import { loadBooks, repoRoot } from '../src/lib/bundle';
import { itemRoutes, shipsAnswer, splitAsserts } from '../src/lib/checks';
import { CSP, parseHeaders } from './helpers/headers';
import { pagefindDir } from '../scripts/offline-manifest';

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
  // Plan 105: the root assets and Pagefind have content-hashed names (scripts/fingerprint.ts).
  const rootAsset = (re: RegExp) => readdirSync(DIST).find((f) => re.test(f)) ?? '(missing)';
  const PAGEFIND = built ? pagefindDir(DIST)! : 'pagefind';

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
      // CodeMirror's base theme (plan 104's editor, loaded lazily) styles `.cm-highlightTab` with a
      // data: SVG background. Nothing here enables highlightWhitespace, so no element ever matches
      // it and the image is never requested (img-src 'self' would block it anyway; the editor's
      // zero-violation test proves no request happens). That one declaration is exempt.
      const text = read(file).replace(".cm-highlightTab\":{backgroundImage:`url('data:image/svg+xml,", '');
      // In HTML, a data: URL can only load from an attribute or a CSS url(); lesson text may
      // say "data:" in prose ("Variation axis — data: …"). In CSS and JS a data: URL has a media
      // type or an empty one ("data:image/png;…", "data:,…"); a `data:` object key is not one.
      const dataUrl = file.endsWith('.html')
        ? /=\s*["']?\s*data:|url\(\s*["']?\s*data:/i.test(text)
        : /\bdata:(?:[a-z]+\/[\w.+-]+)?[;,]/i.test(text);
      expect(dataUrl, `${rel(file)}: data: URL`).toBe(false);
      expect(text.match(/<(?:script|link|img|iframe)[^>]+(?:src|href)="(?:https?:)?\/\//g), `${rel(file)}: remote load`).toBeNull();
    }
  });

  it.skipIf(process.env.PY4KIDS_TEST_HOOKS === '1')('ships no test hooks (plan 105: they exist only in a PY4KIDS_TEST_HOOKS=1 build)', () => {
    for (const file of all.filter((f) => f.endsWith('.js'))) expect(read(file).includes('__py4kidsPwaTest'), rel(file)).toBe(false);
  });

  it.skipIf(!existsSync(join(DIST, 'release.json')))('ships the service worker, release.json and a download manifest per book (plan 105)', () => {
    expect(existsSync(join(DIST, 'sw.js'))).toBe(true);
    const release = JSON.parse(read(join(DIST, 'release.json'))) as { release_id: string; books: Record<string, { manifest: string; content_hash: string }> };
    expect(release.release_id).toMatch(/^[0-9a-f]{64}$/);
    expect(Object.keys(release.books).length).toBeGreaterThan(0);
    for (const [book, summary] of Object.entries(release.books)) {
      const manifest = JSON.parse(read(join(DIST, summary.manifest))) as { book: string; content_hash: string; files: { url: string }[] };
      expect(manifest.book).toBe(book);
      expect(manifest.content_hash).toBe(summary.content_hash);
      expect(manifest.files.some((f) => f.url === `/${book}/`)).toBe(true);
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

  it('ships no JSON carrying an answer_md, source or hash key (plan 103 leak rule; plan 104: hashes only in check projections)', () => {
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
    // Pagefind's manifest names each language index by its own "hash" (a file-name tag); the
    // leak test pins its keys and scans its content.
    // A check projection (`<book>/<entry>/practice/check/<anchor>.json`) carries its item's salted
    // hash; nothing else carries a hash, and nothing carries answer_md, source or program.
    const isCheck = (f: string) => /^[a-z0-9-]+\/[^/]+\/practice\/check\/[a-z0-9-]+\.json$/.test(rel(f).split(sep).join('/'));
    for (const file of all.filter((f) => f.endsWith('.json') && rel(f) !== join(PAGEFIND, 'pagefind-entry.json'))) {
      const forbidden = isCheck(file) ? ['answer_md', 'source', 'program', 'check'] : ['answer_md', 'source', 'hash', 'check', 'program'];
      const found = keys(JSON.parse(read(file))).filter((k) => forbidden.includes(k));
      expect(found, rel(file)).toEqual([]);
    }
  });

  // Plan 104 Phase B: the check, answer and lesson-run projections.
  const loaded = built && existsSync(CONTENT) ? loadBooks({ contentDir: CONTENT }) : [];
  const routes = itemRoutes(loaded);
  const releaseHash = new Map(loaded.map((b) => [b.id, b.book.release.content_hash]));

  it.skipIf(routes.length === 0)('writes a check projection for every item, and an answer projection for exactly the odd unit exercises', () => {
    const answers = new Set(
      all.filter((f) => /[\\/]practice[\\/]answer[\\/][^\\/]+\.json$/.test(f)).map((f) => rel(f).split(sep).join('/')),
    );
    const expected = new Set<string>();
    for (const r of routes) {
      const check = JSON.parse(read(join(DIST, r.book, r.entry, 'practice', 'check', `${r.anchor}.json`))) as { key: string; kind: string };
      expect(check.key).toBe(r.item.key);
      expect(check.kind).toBe(r.item.check.kind);
      if (shipsAnswer(r.item)) {
        expect(r.item.kind).toBe('unit');
        expect(r.item.answer_visibility).toBe('after-attempt');
        expected.add(`${r.book}/${r.entry}/practice/answer/${r.anchor}.json`);
      }
    }
    expect(expected.size).toBeGreaterThan(0);
    expect([...answers].sort()).toEqual([...expected].sort());
  });

  it.skipIf(routes.length === 0)('renders no hash, no assert source and no answer in a practice page', () => {
    const byPage = new Map<string, typeof routes>();
    for (const r of routes) byPage.set(join(r.book, r.entry), [...(byPage.get(join(r.book, r.entry)) ?? []), r]);
    for (const [dir, items] of byPage) {
      const html = read(join(DIST, dir, 'practice', 'index.html'));
      // The release content hash (on <body>, and in report links) is public; no item hash may be here.
      expect(html.replaceAll(releaseHash.get(items[0]!.book)!, ''), dir).not.toMatch(/sha256:[0-9a-f]{64}/);
      for (const r of items) {
        const check = r.item.check;
        if (check.kind === 'asserts') for (const statement of splitAsserts(check.source)) expect(html.includes(statement), `${r.item.key} assert`).toBe(false);
        if (r.item.answer_md && r.item.answer_md.trim().length > 40) expect(html.includes(r.item.answer_md.trim()), `${r.item.key} answer`).toBe(false);
      }
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
    const scripts = all.filter((f) => f.endsWith('.js') && rel(f).startsWith('_astro'));
    for (const file of scripts) expect(read(file), rel(file)).not.toMatch(/katex|shiki|markdown-it|markdownit/i);
    // Every script a page loads up front (its module scripts and their static imports) stays small;
    // the code editor (CodeMirror, plan 104) is loaded with a dynamic import, only where it is used.
    const eager = new Set<string>();
    const visit = (file: string) => {
      if (eager.has(file)) return;
      eager.add(file);
      for (const m of read(file).matchAll(/import\s*(?:[\w$*{}\s,]+from\s*)?["']\.\/([^"']+\.js)["']/g)) visit(join(DIST, '_astro', m[1]!));
    };
    for (const page of html) {
      for (const m of read(page).matchAll(/<script type="module" src="\/(_astro\/[^"]+\.js)"/g)) visit(join(DIST, m[1]!));
    }
    expect(eager.size).toBeGreaterThan(0);
    for (const file of eager) expect(statSync(file).size, rel(file)).toBeLessThan(64 * 1024);
    const lazy = scripts.filter((f) => !eager.has(f));
    expect(lazy.reduce((n, f) => n + statSync(f).size, 0)).toBeLessThan(640 * 1024);
  });

  it('defines every highlighted-code class in /code.css, linked from every page', () => {
    const codeCss = rootAsset(/^code\.[0-9a-f]{10}\.css$/);
    const css = read(join(DIST, codeCss));
    const defined = new Set([...css.matchAll(/\.(sh-[a-z0-9]+)\{/g)].map((m) => m[1]));
    for (const file of html) {
      const text = read(file);
      expect(text, rel(file)).toContain(`<link rel="stylesheet" href="/${codeCss}">`);
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
      expect(text, rel(file)).toMatch(/<script src="\/scripts\/theme\.[0-9a-f]{10}\.js"><\/script>/);
    }
  });
  // Phase E: the book pages, glossary, reference, search, the site pages, headers and favicon.
  const fragments = (): { url: string; meta: Record<string, string> }[] => {
    const dir = join(DIST, PAGEFIND, 'fragment');
    return readdirSync(dir).map((name) => {
      const text = gunzipSync(readFileSync(join(dir, name))).toString('utf-8');
      expect(text.startsWith('pagefind_dcd'), name).toBe(true);
      return JSON.parse(text.slice('pagefind_dcd'.length)) as { url: string; meta: Record<string, string> };
    });
  };

  it.skipIf(books.length === 0)('lists every entry on the book page, in syllabus order, with links that exist', () => {
    for (const book of books) {
      const text = read(page(book.id));
      const listed = [...text.matchAll(/<li class="contents-entry contents-(\w+)" data-entry="([^"]+)">([\s\S]*?)<\/li>/g)];
      expect(listed.map((m) => m[2]), book.id).toEqual(book.entries.map((e) => e.record.id));
      for (const [, kind, id, body] of listed) {
        const entry = book.entries.find((e) => e.record.id === id)!;
        expect(kind).toBe(entry.record.kind);
        const hrefs = [...body!.matchAll(/href="([^"]+)"/g)].map((m) => m[1]!);
        expect(hrefs[0], id).toBe(`/${book.id}/${id}/`);
        expect(hrefs.includes(`/${book.id}/${id}/practice/`), `${id} practice`).toBe(entry.data.items.length > 0);
        for (const href of hrefs) expect(existsSync(join(DIST, href, 'index.html')), href).toBe(true);
      }
      expect(text, book.id).toContain(`data-resume-book="${book.id}"`);
    }
  });

  it.skipIf(books.length === 0)('shows the PDF section exactly when the bundle has a release', () => {
    for (const book of books) {
      const text = read(page(book.id));
      expect(text.includes('data-pdfs'), book.id).toBe(book.book.pdfs !== null);
      if (book.book.pdfs) for (const href of Object.values(book.book.pdfs)) expect(text).toContain(`href="${href}"`);
    }
  });

  it.skipIf(books.length === 0)('links the tools from the book page and builds a glossary and reference page per book', () => {
    for (const book of books) {
      const text = read(page(book.id));
      for (const [tool, has] of [
        ['glossary', book.book.glossary.length > 0],
        ['reference', book.book.reference_md.trim() !== ''],
      ] as const) {
        expect(existsSync(page(book.id, tool)), `${book.id}/${tool}/`).toBe(has);
        expect(text.includes(`href="/${book.id}/${tool}/"`), `${book.id}: ${tool} link`).toBe(has);
        if (has) expect(read(page(book.id, tool))).toContain('data-pagefind-body');
      }
      const glossary = read(page(book.id, 'glossary'));
      expect(glossary.match(/<dt>/g)?.length).toBe(book.book.glossary.length);
      for (const [, href] of glossary.matchAll(/First taught in <a href="([^"]+)">/g)) {
        expect(existsSync(join(DIST, href!, 'index.html')), href).toBe(true);
      }
    }
  });

  it('indexes the lessons, items, glossaries and references, and never the site pages', () => {
    const urls = new Set(fragments().map((f) => f.url));
    for (const book of books) {
      expect(urls.has(`/${book.id}/glossary/`), book.id).toBe(true);
      expect(urls.has(`/${book.id}/reference/`), book.id).toBe(true);
      expect(urls.has(`/${book.id}/${book.entries[0]!.record.id}/`), book.id).toBe(true);
    }
    for (const unindexed of ['/', '/about/', '/privacy/', '/terms/', '/search/']) expect(urls.has(unindexed), unindexed).toBe(false);
    for (const url of urls) expect(url, url).not.toMatch(/\/(?:cards|slides)\/$|^\/[a-z0-9-]+\/$/);
    for (const name of ['about', 'privacy', 'terms']) expect(read(page(name))).not.toContain('data-pagefind-body');
  });

  it('labels each search result with its page title and book', () => {
    const titles = new Set(books.map((b) => b.book.book.title));
    for (const f of fragments()) {
      expect(f.meta.title, f.url).toBeTruthy();
      expect(titles.has(f.meta.book ?? ''), `${f.url}: ${f.meta.book}`).toBe(true);
    }
  });

  it('serves search from the site itself: only same-origin scripts, styles and index files', () => {
    const text = read(page('search'));
    const loads = [...text.matchAll(/<(?:script|link)\b[^>]*\s(?:src|href)="([^"]+)"/g)].map((m) => m[1]!);
    expect(loads.length).toBeGreaterThan(0);
    for (const url of loads) {
      expect(url, url).toMatch(/^\/(?!\/)/);
      expect(existsSync(join(DIST, url)), url).toBe(true);
    }
    const scripts = loads.filter((u) => u.endsWith('.js')).map((u) => read(join(DIST, u)));
    expect(scripts.some((js) => js.includes('`/pagefind/pagefind.js`') || js.includes('"/pagefind/pagefind.js"'))).toBe(true);
    for (const needed of ['pagefind.js', 'pagefind-worker.js', 'pagefind-entry.json']) {
      expect(existsSync(join(DIST, PAGEFIND, needed)), needed).toBe(true);
    }
    // Pagefind's own prebuilt UI is never loaded, so it is not shipped.
    expect(readdirSync(join(DIST, PAGEFIND)).filter((f) => /ui\.(?:js|css)$|highlight/.test(f))).toEqual([]);
    // The search page names the content-hashed Pagefind loader (plan 105).
    expect(text).toContain(`data-pagefind="/${PAGEFIND}/pagefind.js"`);
    for (const file of files(join(DIST, PAGEFIND)).filter((f) => f.endsWith('.js'))) {
      expect(read(file), rel(file)).not.toMatch(/\bimport\s*\(\s*["'`]https?:|fetch\(\s*["'`]https?:/);
    }
  });

  it('ships the _headers file with the strict CSP, and the favicons', () => {
    const rules = parseHeaders(read(join(DIST, '_headers')));
    expect(rules.get('/*')?.get('content-security-policy')).toBe(CSP);
    const svg = rootAsset(/^favicon\.[0-9a-f]{10}\.svg$/);
    expect(existsSync(join(DIST, svg))).toBe(true);
    expect(rootAsset(/^favicon\.[0-9a-f]{10}\.ico$/)).not.toBe('(missing)');
    for (const file of html) expect(read(file), rel(file)).toContain(`<link rel="icon" href="/${svg}" type="image/svg+xml">`);
  });

  it('shows the release tag in the footer of every page', () => {
    const tags = new Set(books.map((b) => b.book.release.tag));
    expect(tags.size).toBe(1);
    const [tag] = [...tags];
    for (const file of html) expect(read(file), rel(file)).toContain(`<p>Release: ${tag}</p>`);
  });

  it('writes the about, privacy and terms pages with their required statements', () => {
    const about = read(page('about'));
    expect(about).toContain('This is a study aid, not security.');
    expect(about).toContain('<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" rel="license">CC BY-NC-SA 4.0</a>');
    for (const book of books) expect(about).toContain(`href="/${book.id}/"`);
    const privacy = read(page('privacy'));
    for (const phrase of ['no analytics', 'no cookies', 'no accounts', 'no third-party services', 'IndexedDB', 'py4kids-theme', 'An adult should use it']) {
      expect(privacy, phrase).toContain(phrase);
    }
    const terms = read(page('terms'));
    expect(terms).toContain('<a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" rel="license">CC BY-NC-SA 4.0</a>');
    expect(terms).toContain('without any warranty');
    expect(terms).toContain('"py4kids"');
    for (const text of [about, privacy, terms]) expect(text).toContain('href="https://github.com/weiboz0/py4kids/issues"');
  });
});

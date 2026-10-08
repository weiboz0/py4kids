/**
 * The build-time "download this book" manifests (plan 105 "Size and count"; Phase A). One per
 * book, written to `dist/_offline/<book>.<content hash>.json`:
 *
 *   { book, content_hash, bytes, count, files: [{ url, bytes }] }
 *
 * - **files:** every file of the book's folder (its pages as their `/<book>/x/` URLs, and its data:
 *   check and answer projections, run.json, deck.json, mastery.json, fixture and asset files);
 *   every same-origin asset its pages load (scripts, stylesheets, icons, the web manifest),
 *   following `_astro` imports transitively (including the lazily imported editor); and Pagefind
 *   for the book: its loader, worker, WebAssembly, metadata, every index and filter chunk, and the
 *   fragments of the book's own pages (so search works offline).
 * - **content_hash:** sha256 over the sorted `(url, sha256(bytes))` list of those files. It covers
 *   the rendered pages, so any change to what the book shows (content or site code) gives a new
 *   hash and a new `book-<book>-<content_hash>` cache; an unchanged hash means byte-identical files.
 *   (Pagefind's index is shared by every book, so a content change in one book changes every
 *   book's hash: correct, at the cost of a re-download.)
 * - Caching copies only files already in dist/ (hidden answers stay hidden): every URL maps to a
 *   dist file, which the builder checks.
 */
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { join, posix, relative, sep } from 'node:path';
import { gunzipSync } from 'node:zlib';

export interface ManifestFile {
  url: string;
  bytes: number;
}
export interface BookManifest {
  book: string;
  content_hash: string;
  bytes: number;
  count: number;
  files: ManifestFile[];
}

export const MANIFEST_DIR = '_offline';

const sha = (data: string | Uint8Array) => createHash('sha256').update(data).digest('hex');

function walk(dir: string, base: string = dir): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? walk(join(dir, d.name), base) : [relative(base, join(dir, d.name)).split(sep).join('/')],
  );
}

/** The URL a dist file is served at (`a/index.html` is `/a/`). */
export function urlOf(path: string): string {
  if (path === 'index.html') return '/';
  if (path.endsWith('/index.html')) return `/${path.slice(0, -'index.html'.length)}`;
  return `/${path}`;
}

/** The dist file a same-origin URL path is served from (`/a/` is `a/index.html`). */
export function fileOf(url: string): string {
  const path = decodeURIComponent(url.split(/[?#]/)[0]!);
  return path.endsWith('/') ? `${path.slice(1)}index.html` : path.slice(1);
}

/** The books in a built site: top-level folders whose index page carries `data-content-hash`. */
export function bookDirs(dist: string): string[] {
  return readdirSync(dist, { withFileTypes: true })
    .filter((d) => d.isDirectory() && existsSync(join(dist, d.name, 'index.html')))
    .filter((d) => /<body[^>]*\sdata-content-hash="/.test(readFileSync(join(dist, d.name, 'index.html'), 'utf-8')))
    .map((d) => d.name)
    .sort();
}

/** Same-origin URLs an HTML page loads (script src, link href, img src), not its <a> links. */
export function htmlLoads(html: string): string[] {
  const out: string[] = [];
  for (const tag of html.match(/<(?:script|link|img|source)\b[^>]*>/g) ?? []) {
    if (/^<link\b/.test(tag) && !/\srel="(?:stylesheet|icon|apple-touch-icon|manifest|modulepreload|preload)"/.test(tag)) continue;
    for (const m of tag.matchAll(/\s(?:src|href)="(\/(?!\/)[^"#?]*)"/g)) out.push(m[1]!);
  }
  return out;
}

/** `_astro` files a script or stylesheet imports (static, dynamic, Vite's preload lists, CSS url()). */
export function assetImports(text: string, fromUrl: string): string[] {
  const out: string[] = [];
  const base = posix.dirname(fromUrl);
  for (const m of text.matchAll(/["'`(]((?:\.\.?\/|\/_astro\/|_astro\/)[\w.@-]+\.(?:js|mjs|css|woff2?|ttf|svg|png|wasm))["'`)]/g)) {
    const ref = m[1]!;
    if (ref.startsWith('/')) out.push(ref);
    else if (ref.startsWith('_astro/')) out.push(`/${ref}`);
    else out.push(posix.normalize(posix.join(base, ref)));
  }
  return out;
}

/** Pagefind's folder in a fingerprinted build (`pagefind/<hash>`), or null when not indexed. */
export function pagefindDir(dist: string): string | null {
  if (!existsSync(join(dist, 'pagefind'))) return null;
  const dirs = readdirSync(join(dist, 'pagefind')).filter((d) => existsSync(join(dist, 'pagefind', d, 'pagefind.js')));
  if (existsSync(join(dist, 'pagefind', 'pagefind.js'))) return 'pagefind';
  if (dirs.length !== 1) throw new Error(`offline-manifest: expected one Pagefind folder, found ${dirs.length}`);
  return `pagefind/${dirs[0]}`;
}

/** Pagefind's files for `book`: everything but the fragments of other books' pages. */
export function pagefindFiles(dist: string, dir: string, book: string): string[] {
  return walk(join(dist, dir))
    .map((p) => `${dir}/${p}`)
    .filter((p) => {
      if (!p.startsWith(`${dir}/fragment/`)) return true;
      const text = gunzipSync(readFileSync(join(dist, p))).toString('utf-8');
      if (!text.startsWith('pagefind_dcd')) throw new Error(`offline-manifest: not a Pagefind fragment: ${p}`);
      const { url } = JSON.parse(text.slice('pagefind_dcd'.length)) as { url: string };
      return url.startsWith(`/${book}/`);
    });
}

/** The download manifest of one book. */
export function buildBookManifest(dist: string, book: string): BookManifest {
  const files = new Set<string>(walk(join(dist, book)).map((p) => `${book}/${p}`));
  // Every asset the book's pages load, and what those assets import, transitively.
  const queue: string[] = [];
  const add = (url: string, from: string) => {
    const path = fileOf(url);
    if (path.startsWith(`${book}/`)) return;
    if (!existsSync(join(dist, path)) || !statSync(join(dist, path)).isFile()) {
      throw new Error(`offline-manifest: ${from} loads ${url}, which is not a file in dist/`);
    }
    if (!files.has(path)) {
      files.add(path);
      queue.push(path);
    }
  };
  for (const page of [...files].filter((p) => p.endsWith('.html'))) {
    for (const url of htmlLoads(readFileSync(join(dist, page), 'utf-8'))) add(url, page);
  }
  while (queue.length > 0) {
    const path = queue.shift()!;
    if (/\.(?:js|mjs|css)$/.test(path)) {
      for (const url of assetImports(readFileSync(join(dist, path), 'utf-8'), `/${path}`)) add(url, path);
    } else if (path.endsWith('.webmanifest')) {
      const manifest = JSON.parse(readFileSync(join(dist, path), 'utf-8')) as { icons?: { src: string }[] };
      for (const icon of manifest.icons ?? []) add(icon.src, path);
    }
  }
  const pf = pagefindDir(dist);
  if (pf) for (const p of pagefindFiles(dist, pf, book)) files.add(p);

  const sorted = [...files].sort();
  const entries = sorted.map((path) => {
    const bytes = readFileSync(join(dist, path));
    return { url: urlOf(path), bytes: bytes.length, sha256: sha(bytes) };
  });
  entries.sort((a, b) => (a.url < b.url ? -1 : a.url > b.url ? 1 : 0));
  const content_hash = sha(entries.map((e) => `${e.url}\0${e.sha256}\n`).join(''));
  return {
    book,
    content_hash,
    bytes: entries.reduce((n, e) => n + e.bytes, 0),
    count: entries.length,
    files: entries.map(({ url, bytes }) => ({ url, bytes })),
  };
}

/** Write every book's manifest to `dist/_offline/` (replacing earlier ones); returns them. */
export function writeBookManifests(dist: string): BookManifest[] {
  rmSync(join(dist, MANIFEST_DIR), { recursive: true, force: true });
  mkdirSync(join(dist, MANIFEST_DIR), { recursive: true });
  const out = bookDirs(dist).map((book) => buildBookManifest(dist, book));
  for (const m of out) writeFileSync(join(dist, MANIFEST_DIR, `${m.book}.${m.content_hash.slice(0, 16)}.json`), `${JSON.stringify(m)}\n`);
  return out;
}

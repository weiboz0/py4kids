/**
 * Release-specific asset URLs (plan 105 "Every asset URL is release-specific"): after the build,
 * the site's few stable-named assets get content-hashed names, so an exact URL identifies exactly
 * one file across releases and a service worker can serve it from any retained cache.
 *
 * - The root assets (`favicon.svg`, `favicon.ico`, `scripts/theme.js`, `code.css`, the generated
 *   icons) become `<name>.<hash>.<ext>`; the web app manifest, which names the icons, is renamed
 *   after its icon URLs are rewritten.
 * - Pagefind moves into `pagefind/<hash>/` (a hash over all its files): `pagefind.js` finds its
 *   index relative to its own URL, and the search page names it in `data-pagefind`.
 * - Every reference in the HTML pages (and the manifest's icon list) is rewritten. `_astro/*` is
 *   already hashed by Astro. Only the HTML pages, `release.json`, `sw.js` and the books' data
 *   files keep stable names (`assertReleaseSpecific` enforces it); a book's files are cached and
 *   served as one unit under the book's content hash.
 */
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readdirSync, readFileSync, renameSync, rmdirSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, sep } from 'node:path';

export const ROOT_ASSETS = ['favicon.svg', 'favicon.ico', 'scripts/theme.js', 'code.css'];
export const WEB_MANIFEST = 'manifest.webmanifest';
export const PAGEFIND_ENTRY = '/pagefind/pagefind.js';

const hex = (data: string | Uint8Array, n = 10) => createHash('sha256').update(data).digest('hex').slice(0, n);

function walk(dir: string, base: string = dir): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? walk(join(dir, d.name), base) : [relative(base, join(dir, d.name)).split(sep).join('/')],
  );
}
const below = (root: string, sub: string) => walk(join(root, sub)).map((p) => `${sub}/${p}`);

/** `a/b.css` with content hash `h` is `a/b.h.css`. */
export function hashedName(path: string, bytes: Uint8Array): string {
  const slash = path.lastIndexOf('/');
  const dot = path.lastIndexOf('.');
  const h = hex(bytes);
  return dot > slash ? `${path.slice(0, dot)}.${h}${path.slice(dot)}` : `${path}.${h}`;
}

/** Replace each `"<old>"` (a quoted URL) by `"<new>"` in `text`. */
function rewrite(text: string, urls: Map<string, string>): string {
  let out = text;
  for (const [from, to] of urls) out = out.replaceAll(`"${from}"`, `"${to}"`);
  return out;
}

function rewriteHtml(dist: string, urls: Map<string, string>): void {
  for (const path of walk(dist).filter((p) => p.endsWith('.html'))) {
    const full = join(dist, path);
    const text = readFileSync(full, 'utf-8');
    const next = rewrite(text, urls);
    if (next !== text) writeFileSync(full, next);
  }
}

function renameHashed(dist: string, path: string, urls: Map<string, string>): void {
  const bytes = readFileSync(join(dist, path));
  const next = hashedName(path, bytes);
  renameSync(join(dist, path), join(dist, next));
  urls.set(`/${path}`, `/${next}`);
}

/** Fingerprint `dist` in place; returns every renamed URL (old -> new). */
export function fingerprint(dist: string, extra: string[] = []): Map<string, string> {
  const urls = new Map<string, string>();
  for (const path of [...ROOT_ASSETS, ...extra]) {
    if (!existsSync(join(dist, path))) throw new Error(`fingerprint: ${path} is missing from dist/`);
    renameHashed(dist, path, urls);
  }
  if (existsSync(join(dist, WEB_MANIFEST))) {
    const full = join(dist, WEB_MANIFEST);
    writeFileSync(full, rewrite(readFileSync(full, 'utf-8'), urls));
    renameHashed(dist, WEB_MANIFEST, urls);
  }
  if (existsSync(join(dist, 'pagefind', 'pagefind.js'))) {
    const files = below(dist, 'pagefind').sort();
    const digest = hex(files.map((p) => `${p}\0${hex(readFileSync(join(dist, p)), 64)}\n`).join(''));
    for (const path of files) {
      const to = join(dist, 'pagefind', digest, path.slice('pagefind/'.length));
      mkdirSync(dirname(to), { recursive: true });
      renameSync(join(dist, path), to);
    }
    for (const d of readdirSync(join(dist, 'pagefind'))) {
      if (d !== digest && statSync(join(dist, 'pagefind', d)).isDirectory() && walk(join(dist, 'pagefind', d)).length === 0) {
        rmEmpty(join(dist, 'pagefind', d)); // Pagefind's emptied subfolders (fragment/, index/, filter/)
      }
    }
    urls.set(PAGEFIND_ENTRY, `/pagefind/${digest}/pagefind.js`);
  }
  rewriteHtml(dist, urls);
  return urls;
}

/** Remove `dir` and its subdirectories; they hold no file (rmdirSync refuses a non-empty one). */
function rmEmpty(dir: string): void {
  for (const d of readdirSync(dir)) rmEmpty(join(dir, d));
  rmdirSync(dir);
}

/** Content-hashed file names: Astro's `name.<hash>.ext`, ours `name.<10 hex>.ext`, or a hashed directory. */
const HASHED = /^_astro\/[^/]+\.[A-Za-z0-9_-]{8,}\.[a-z0-9]+$|^(?:[^/]+\/)*[^/]+\.[0-9a-f]{10}\.[a-z0-9]+$|^pagefind\/[0-9a-f]{10}\/|^pyodide\/[^/]+\/|^_offline\/[^/]+\.[0-9a-f]{16}\.json$/;
/** Stable names allowed outside the books: the entry pages and the files no worker caches. */
const STABLE = /(?:^|\/)index\.html$|^_headers$|^release\.json$|^sw\.js$/;

/**
 * Every file in `dist` outside `books` must have a release-specific (content-hashed or
 * versioned) name, unless it is an HTML entry page or a never-cached file. Returns the offenders.
 */
export function releaseSpecificViolations(dist: string, books: string[]): string[] {
  const bookSet = new Set(books);
  return walk(dist).filter((p) => !bookSet.has(p.split('/')[0]!) && !STABLE.test(p) && !HASHED.test(p));
}

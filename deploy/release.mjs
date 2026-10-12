/**
 * Release identity and the deploy checks (plan 105 Global constraints "Release identity", Phase D).
 *
 * - **`release_id`** is a sha256 over the sorted `(path, sha256(bytes))` list of every file in
 *   `site/dist/` and `runner/dist/` (paths prefixed `site/` and `runner/`; the Pyodide runtime
 *   included), **except the one file that carries the id**: `release.json` at the root of each
 *   dist. No other file embeds the id, so there is no circularity: each page registers its
 *   service worker as `/sw.js?r=<release_id>`, read from `/release.json`.
 *   The list is serialised one line per file, `<path>\0<hex sha256>\n`, sorted by path (code
 *   units), and the id is the hex sha256 of that text.
 * - **`release.json`** (written into both dists, never cached: the service workers fetch it
 *   network-only) carries the id and what each origin's service worker needs to know about the
 *   release: the app shell's files (URL and size), and for the site the books' download summaries
 *   and the runner's total size, for the runner the versioned Pyodide runtime.
 * - **Size check:** Cloudflare Pages refuses any file over 25 MiB; the build fails first.
 */
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

export const RELEASE_FILE = 'release.json';
/** Cloudflare Pages' per-file limit. */
export const MAX_FILE_BYTES = 25 * 1024 * 1024;
/** Files a dist ships that no service worker caches. */
const NEVER_CACHED = new Set(['_headers', RELEASE_FILE, 'sw.js']);

const sha256 = (data) => createHash('sha256').update(data).digest('hex');

/** Every file under `dir`, as sorted `/`-separated relative paths. */
export function listFiles(dir) {
  const out = [];
  const walk = (d) => {
    for (const entry of readdirSync(d, { withFileTypes: true })) {
      const full = join(d, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.isFile()) out.push(relative(dir, full).split(sep).join('/'));
      else throw new Error(`release: not a regular file: ${full}`);
    }
  };
  walk(dir);
  return out.sort();
}

/**
 * The `(path, sha256)` list of `dists` (`[{ name, dir }]`), every file but each dist's own
 * root `release.json`, sorted by path.
 */
export function fileDigests(dists) {
  const out = [];
  for (const { name, dir } of dists) {
    for (const path of listFiles(dir)) {
      if (path === RELEASE_FILE) continue;
      out.push({ path: `${name}/${path}`, sha256: sha256(readFileSync(join(dir, path))) });
    }
  }
  return out.sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
}

/** The release id of a digest list (see the module comment for the serialisation). */
export function releaseIdOf(digests) {
  return sha256(digests.map((d) => `${d.path}\0${d.sha256}\n`).join(''));
}

/** The release id of the two dists. */
export function computeReleaseId({ site, runner }) {
  return releaseIdOf(fileDigests([{ name: 'site', dir: site }, { name: 'runner', dir: runner }]));
}

/** Files over Cloudflare Pages' 25 MiB limit, as `[{ path, bytes }]`. */
export function oversized(dists, limit = MAX_FILE_BYTES) {
  const out = [];
  for (const { name, dir } of dists) {
    for (const path of listFiles(dir)) {
      const bytes = statSync(join(dir, path)).size;
      if (bytes > limit) out.push({ path: `${name}/${path}`, bytes });
    }
  }
  return out;
}

/** The URL a dist file is served at: `a/index.html` is `/a/`, anything else `/path`. */
export function urlOf(path) {
  if (path === 'index.html') return '/';
  if (path.endsWith('/index.html')) return `/${path.slice(0, -'index.html'.length)}`;
  return `/${path}`;
}

/** `{ files: [{ url, bytes }], bytes }` for dist-relative `paths`. */
function urlSet(dir, paths) {
  const files = paths.map((p) => ({ url: urlOf(p), bytes: statSync(join(dir, p)).size }));
  return { files, bytes: files.reduce((n, f) => n + f.bytes, 0) };
}

/**
 * The site's release description: the app shell (every file outside the books, Pagefind and the
 * download manifests: the site pages, `_astro/*`, the fingerprinted root assets, icons and web
 * manifest) and each book's download summary, read from its manifest in `_offline/`.
 */
export function describeSite(dir) {
  const files = listFiles(dir);
  const manifests = files.filter((p) => /^_offline\/[^/]+\.json$/.test(p));
  const books = {};
  for (const path of manifests) {
    const m = JSON.parse(readFileSync(join(dir, path), 'utf-8'));
    books[m.book] = { content_hash: m.content_hash, bytes: m.bytes, count: m.count, manifest: urlOf(path) };
  }
  const bookDirs = new Set(Object.keys(books));
  const shell = files.filter((p) => {
    const top = p.split('/')[0];
    return !NEVER_CACHED.has(p) && !bookDirs.has(top) && top !== 'pagefind' && top !== '_offline';
  });
  return { app: 'site', shell: urlSet(dir, shell), books };
}

/**
 * The runner's release description: the shell (the page and its content-hashed assets) and the
 * Pyodide runtime under its versioned directory `pyodide/<dir>/`, cached as `pyodide-<dir>`.
 */
export function describeRunner(dir) {
  const files = listFiles(dir);
  const pyodide = files.filter((p) => p.startsWith('pyodide/'));
  const dirs = new Set(pyodide.map((p) => p.split('/')[1]));
  if (dirs.size !== 1) throw new Error(`release: runner/dist/pyodide/ must hold exactly one versioned directory, found ${[...dirs].join(', ') || 'none'}`);
  const [version] = [...dirs];
  const shell = files.filter((p) => !NEVER_CACHED.has(p) && !p.startsWith('pyodide/'));
  return {
    app: 'runner',
    shell: urlSet(dir, shell),
    pyodide: { dir: version, cache: `pyodide-${version}`, ...urlSet(dir, pyodide) },
  };
}

/**
 * Check both dists, compute the release id and write `release.json` into each. Returns the id.
 * Throws (and writes nothing) if any file exceeds the 25 MiB limit.
 */
export function writeRelease({ site, runner }) {
  const dists = [{ name: 'site', dir: site }, { name: 'runner', dir: runner }];
  const big = oversized(dists);
  if (big.length > 0) {
    throw new Error(`release: over Cloudflare Pages' 25 MiB per-file limit: ${big.map((f) => `${f.path} (${f.bytes} bytes)`).join(', ')}`);
  }
  const siteInfo = describeSite(site);
  const runnerInfo = describeRunner(runner);
  const releaseId = computeReleaseId({ site, runner });
  // The site's download UI shows the runner's share (its shell and Pyodide) up front too.
  const runnerBytes = { bytes: runnerInfo.shell.bytes + runnerInfo.pyodide.bytes };
  writeFileSync(join(site, RELEASE_FILE), `${JSON.stringify({ release_id: releaseId, ...siteInfo, runner: runnerBytes })}\n`);
  writeFileSync(join(runner, RELEASE_FILE), `${JSON.stringify({ release_id: releaseId, ...runnerInfo })}\n`);
  return releaseId;
}

/** The largest file of the dists (the build log names it next to the limit). */
export function largest(dists) {
  let best = { path: '', bytes: 0 };
  for (const { name, dir } of dists) {
    for (const path of listFiles(dir)) {
      const bytes = statSync(join(dir, path)).size;
      if (bytes > best.bytes) best = { path: `${name}/${path}`, bytes };
    }
  }
  return best;
}

// CLI: node deploy/release.mjs <site dist> <runner dist>
if (process.argv[1] && import.meta.filename === process.argv[1]) {
  const [site, runner] = process.argv.slice(2);
  if (!site || !runner) {
    console.error('usage: node deploy/release.mjs <site/dist> <runner/dist>');
    process.exit(2);
  }
  try {
    const id = writeRelease({ site, runner });
    const top = largest([{ name: 'site', dir: site }, { name: 'runner', dir: runner }]);
    console.log(`release: release_id ${id}; largest file ${top.path} (${(top.bytes / 1048576).toFixed(1)} MiB, limit 25 MiB)`);
  } catch (error) {
    console.error(`FAIL: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

/**
 * Builds the search index (plan 103 Architecture, "Search"): `pnpm -C site search-index [dir]`.
 *
 * Runs Pagefind over the built site (default `dist/`). Pagefind indexes only the pages that carry
 * `data-pagefind-body` (the reading views, the practice pages, the glossaries and the quick
 * references), so the About, privacy, terms, search, catalog, book, card and slide pages are
 * never indexed. The index is written to `<dir>/pagefind/` and served by the site itself.
 *
 * The site's search page uses Pagefind's JS API with its own UI, so Pagefind's prebuilt UI
 * bundles (which the site never loads) are removed: nothing unused ships.
 */
import { spawnSync } from 'node:child_process';
import { existsSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';

const SITE = resolve(import.meta.dirname, '..');
const dir = resolve(process.argv[2] ?? join(SITE, 'dist'));
if (!existsSync(join(dir, 'index.html'))) {
  console.error(`search-index: no built site at ${dir} (run astro build first)`);
  process.exit(1);
}

const bin = join(SITE, 'node_modules', '.bin', process.platform === 'win32' ? 'pagefind.cmd' : 'pagefind');
const run = spawnSync(bin, ['--site', dir, '--quiet'], { stdio: 'inherit' });
if (run.status !== 0) {
  console.error('search-index: pagefind failed');
  process.exit(run.status ?? 1);
}

/** Pagefind's own UI bundles: unused by the site (src/scripts/search.ts is its UI). */
const UNUSED = [
  'pagefind-ui.js',
  'pagefind-ui.css',
  'pagefind-component-ui.js',
  'pagefind-component-ui.css',
  'pagefind-modular-ui.js',
  'pagefind-modular-ui.css',
  'pagefind-highlight.js',
];
for (const name of UNUSED) rmSync(join(dir, 'pagefind', name), { force: true });
for (const needed of ['pagefind.js', 'pagefind-worker.js', 'pagefind-entry.json']) {
  if (!existsSync(join(dir, 'pagefind', needed))) {
    console.error(`search-index: pagefind did not write pagefind/${needed}`);
    process.exit(1);
  }
}
console.log(`search-index: indexed ${dir}`);

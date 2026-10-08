/**
 * The site's post-build steps for the installable, offline site (plan 105 Phases A and D), run by
 * scripts/build-site.sh after Pagefind: `pnpm -C site pwa-build [dist]`.
 *
 *   1. the web app manifest's PNG icons, rasterised from favicon.svg (scripts/pwa-icons.ts)
 *   2. release-specific asset URLs: content-hashed root assets and Pagefind folder
 *      (scripts/fingerprint.ts)
 *   3. one "download this book" manifest per book in `_offline/` (scripts/offline-manifest.ts)
 *   4. the check that only HTML pages, `release.json`, `sw.js` and the books' files keep
 *      stable names
 */
import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fingerprint, releaseSpecificViolations } from './fingerprint.ts';
import { bookDirs, writeBookManifests } from './offline-manifest.ts';
import { encodePng, ICONS, parseIconSvg, renderIcon } from './pwa-icons.ts';

const SITE = resolve(import.meta.dirname, '..');

export async function pwaBuild(dist: string): Promise<void> {
  const design = parseIconSvg(readFileSync(join(dist, 'favicon.svg'), 'utf-8'));
  for (const icon of ICONS) {
    mkdirSync(dirname(join(dist, icon.path)), { recursive: true });
    writeFileSync(join(dist, icon.path), encodePng(renderIcon(design, icon.size, { maskable: icon.maskable }), icon.size, icon.size));
  }
  fingerprint(dist, ICONS.map((i) => i.path));
  const manifests = writeBookManifests(dist);
  const stable = releaseSpecificViolations(dist, bookDirs(dist));
  if (stable.length > 0) throw new Error(`pwa-build: stable-named assets outside the books: ${stable.join(', ')}`);
  for (const m of manifests) console.log(`pwa-build: ${m.book}: ${m.count} files, ${(m.bytes / 1e6).toFixed(1)} MB`);
}

if (process.argv[1] && import.meta.filename === resolve(process.argv[1])) {
  const dist = resolve(process.argv[2] ?? join(SITE, 'dist'));
  try {
    await pwaBuild(dist);
  } catch (error) {
    console.error(`FAIL: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

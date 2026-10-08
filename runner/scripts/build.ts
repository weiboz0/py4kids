#!/usr/bin/env node
/**
 * Build the runner (plan 104 Phase A) to runner/dist/:
 *   - assets/worker-<hash>.js: src/worker.ts with the harness (py/*.py) bundled in as text
 *   - assets/main-<hash>.js: src/main.ts (the runner page's module), told the worker's URL and
 *     the site origin
 *   - index.html: the page, pointing at main-<hash>.js
 *   - pyodide/<version>/: the self-hosted Pyodide runtime from the pinned npm package (versioned
 *     path, so its URLs are release-specific; nothing loads from a CDN, and no package is
 *     installed at runtime)
 *   - _headers: public/_headers with the site origin filled in
 * Origins come from deploy/origins.json through deploy/origins.mjs (PY4KIDS_TARGET, or the
 * PY4KIDS_SITE_ORIGIN / PY4KIDS_RUNNER_ORIGIN overrides; plan 105 Phase D).
 */
import { createHash } from 'node:crypto';
import { copyFileSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { build } from 'esbuild';
import { resolveOrigins, type ResolvedOrigins } from '../../deploy/origins.mjs';

const ROOT = join(import.meta.dirname, '..');
/** The output folder: dist/, or PY4KIDS_RUNNER_OUT (the release-id reproducibility test). */
const DIST = process.env.PY4KIDS_RUNNER_OUT ?? join(ROOT, 'dist');
/**
 * Test-only hooks (plan 105 Phase E): built in only with PY4KIDS_TEST_HOOKS=1, never in a release
 * (scripts/build-release.sh refuses it). They let the update-path test move Pyodide to another
 * versioned folder (PY4KIDS_TEST_PYODIDE_DIR) so release B's Pyodide URLs differ from A's.
 */
const TEST_HOOKS = process.env.PY4KIDS_TEST_HOOKS === '1';
const PYODIDE_PKG = join(ROOT, 'node_modules', 'pyodide');
const PYODIDE_FILES = ['pyodide.js', 'pyodide.asm.js', 'pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json'];

export function origins(): ResolvedOrigins {
  return resolveOrigins();
}

const hash = (text: string | Uint8Array) => createHash('sha256').update(text).digest('hex').slice(0, 12);

async function bundle(entry: string, format: 'iife' | 'esm', define: Record<string, unknown>): Promise<string> {
  const out = await build({
    entryPoints: [join(ROOT, entry)],
    bundle: true,
    format,
    target: 'es2023',
    minify: true,
    legalComments: 'none',
    write: false,
    loader: { '.py': 'text' },
    define: Object.fromEntries(Object.entries(define).map(([k, v]) => [k, JSON.stringify(v)])),
  });
  const file = out.outputFiles[0];
  if (!file) throw new Error(`esbuild produced nothing for ${entry}`);
  return file.text;
}

async function main(): Promise<void> {
  const { primary, pairs } = origins();
  const site = primary.site;
  const pairList = pairs.map(({ site, runner }) => ({ site, runner }));
  const pin = (JSON.parse(readFileSync(join(ROOT, 'package.json'), 'utf-8')) as { devDependencies: Record<string, string> }).devDependencies.pyodide;
  const installed = (JSON.parse(readFileSync(join(PYODIDE_PKG, 'package.json'), 'utf-8')) as { version: string }).version;
  if (!pin || pin !== installed) throw new Error(`pyodide ${installed} installed, ${pin} pinned (run pnpm install --frozen-lockfile)`);
  // Pyodide lives under a versioned path (plan 105: every asset URL is release-specific).
  const pyodideDir = (TEST_HOOKS && process.env.PY4KIDS_TEST_PYODIDE_DIR) || pin;
  if (!/^[0-9A-Za-z._-]+$/.test(pyodideDir) || !pyodideDir.startsWith(pin)) throw new Error(`not a versioned Pyodide folder: ${pyodideDir}`);
  const pyodideIndex = `/pyodide/${pyodideDir}/`;

  rmSync(DIST, { recursive: true, force: true });
  mkdirSync(join(DIST, 'assets'), { recursive: true });

  const worker = await bundle('src/worker.ts', 'iife', { PYODIDE_INDEX: pyodideIndex, PYODIDE_VERSION: pin });
  const workerName = `assets/worker-${hash(worker)}.js`;
  writeFileSync(join(DIST, workerName), worker);

  const page = await bundle('src/main.ts', 'esm', { ORIGIN_PAIRS: pairList, WORKER_URL: `/${workerName}` });
  const pageName = `assets/main-${hash(page)}.js`;
  writeFileSync(join(DIST, pageName), page);

  const html = readFileSync(join(ROOT, 'index.html'), 'utf-8')
    .replace('./src/main.ts', `/${pageName}`)
    .replaceAll('%PYODIDE_VERSION%', pin);
  if (html.includes('src/main.ts')) throw new Error('index.html: the module script was not rewritten');
  writeFileSync(join(DIST, 'index.html'), html);

  mkdirSync(join(DIST, 'pyodide', pyodideDir), { recursive: true });
  for (const file of PYODIDE_FILES) copyFileSync(join(PYODIDE_PKG, file), join(DIST, 'pyodide', pyodideDir, file));

  const headers = readFileSync(join(ROOT, 'public', '_headers'), 'utf-8').replaceAll('{{SITE_ORIGINS}}', pairList.map((p) => p.site).join(' '));
  if (/\{\{/.test(headers)) throw new Error('_headers: an unfilled placeholder');
  writeFileSync(join(DIST, '_headers'), headers);

  console.log(`runner: built ${DIST} (Pyodide ${pin} under /pyodide/${pyodideDir}/; site origin ${site}${TEST_HOOKS ? '; TEST HOOKS' : ''})`);
}

if (process.argv[1] && import.meta.filename === process.argv[1]) await main();

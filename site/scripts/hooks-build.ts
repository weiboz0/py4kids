/**
 * The test-hooks build (plan 105 Phase E): the same site and runner as scripts/build-site.sh
 * steps 2-7, built with PY4KIDS_TEST_HOOKS=1 into a separate folder, never into `site/dist/` or
 * `runner/dist/` (the production dists every other test checks stay untouched):
 *
 *   build/site-hooks/site/     astro build --outDir, Pagefind, pwa-build
 *   build/site-hooks/runner/   the runner (PY4KIDS_RUNNER_OUT)
 *   then deploy/release.mjs writes release.json into both.
 *
 * It reuses the exported bundles in site/content/ (run scripts/build-site.sh first) and the
 * origins of the environment (PY4KIDS_SITE_ORIGIN / PY4KIDS_RUNNER_ORIGIN, else deploy/origins.json).
 * `pnpm -C site e2e` runs it before the hook-tagged PWA tests (`pnpm -C site e2e:pwa-hooks`),
 * which find it through PY4KIDS_TEST_SITE_DIST / PY4KIDS_TEST_RUNNER_DIST (e2e/helpers/env.ts).
 * Usage: node scripts/hooks-build.ts [outDir]
 */
import { spawnSync } from 'node:child_process';
import { existsSync, rmSync } from 'node:fs';
import { join, resolve } from 'node:path';

const SITE = resolve(import.meta.dirname, '..');
export const HOOKS_OUT = join(SITE, '..', 'build', 'site-hooks');

function run(what: string, command: string, args: string[], cwd: string, env: Record<string, string>): void {
  const started = Date.now();
  const result = spawnSync(command, args, { cwd, env: { ...process.env, ...env }, stdio: 'inherit' });
  if (result.status !== 0) {
    console.error(`FAIL: hooks-build: ${what} exited ${result.status}`);
    process.exit(result.status ?? 1);
  }
  console.log(`hooks-build: ${what} (${((Date.now() - started) / 1000).toFixed(1)} s)`);
}

const out = resolve(process.argv[2] ?? HOOKS_OUT);
const site = join(out, 'site');
const runner = join(out, 'runner');
if (!existsSync(join(SITE, 'content'))) {
  console.error('FAIL: hooks-build: no exported bundles in site/content/ (run scripts/build-site.sh first)');
  process.exit(1);
}
rmSync(out, { recursive: true, force: true });
const env = { PY4KIDS_TEST_HOOKS: '1', ASTRO_TELEMETRY_DISABLED: '1' };
const node = process.execPath;
run('astro build', node, [join(SITE, 'node_modules', 'astro', 'bin', 'astro.mjs'), 'build', '--silent', '--outDir', site], SITE, env);
run('search index', node, [join(SITE, 'scripts', 'search-index.ts'), site], SITE, env);
run('pwa-build', node, [join(SITE, 'scripts', 'pwa-build.ts'), site], SITE, env);
run('runner', node, [join(SITE, '..', 'runner', 'scripts', 'build.ts')], join(SITE, '..', 'runner'), { ...env, PY4KIDS_RUNNER_OUT: runner });
run('release', node, [join(SITE, '..', 'deploy', 'release.mjs'), site, runner], SITE, env);
console.log(`hooks-build: built ${site} and ${runner} with PY4KIDS_TEST_HOOKS=1`);

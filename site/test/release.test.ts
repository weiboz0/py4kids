/**
 * Release identity (plan 105 Global constraints "Release identity", Phase D): `release_id` is a
 * sha256 over the sorted (path, sha256) list of every file of both dists except each
 * `release.json`, so it is reproducible, recomputable from the emitted files, and changes with any
 * one file; the 25 MiB per-file check; the release descriptions.
 */
import { spawnSync } from 'node:child_process';
import { appendFileSync, cpSync, existsSync, mkdirSync, mkdtempSync, openSync, closeSync, ftruncateSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { afterAll, describe, expect, it } from 'vitest';
import {
  computeReleaseId,
  describeRunner,
  describeSite,
  fileDigests,
  MAX_FILE_BYTES,
  oversized,
  RELEASE_FILE,
  writeRelease,
} from '../../deploy/release.mjs';

const SITE = join(import.meta.dirname, '..');
const RUNNER = join(SITE, '..', 'runner');
const scratch = join(SITE, 'node_modules', '.cache');
mkdirSync(scratch, { recursive: true });
const work = mkdtempSync(join(scratch, 'py4kids-release-'));
afterAll(() => rmSync(work, { recursive: true, force: true }));

function fakeDists(name: string): { site: string; runner: string } {
  const site = join(work, name, 'site');
  const runner = join(work, name, 'runner');
  const put = (path: string, text: string) => {
    mkdirSync(join(path, '..'), { recursive: true });
    writeFileSync(path, text);
  };
  put(join(site, 'index.html'), '<!doctype html><title>py4kids</title>');
  put(join(site, 'about', 'index.html'), '<p>about</p>');
  put(join(site, '_astro', 'a.B1c2D3e4.js'), 'console.log(1)');
  put(join(site, '_headers'), '/*\n  X: y\n');
  put(join(site, 'sw.js'), '// sw');
  put(join(site, 'demo', 'index.html'), '<body data-content-hash="sha256:x">');
  put(join(site, '_offline', 'demo.0123456789abcdef.json'), JSON.stringify({ book: 'demo', content_hash: 'ab', bytes: 3, count: 1, files: [] }));
  put(join(runner, 'index.html'), '<p>runner</p>');
  put(join(runner, 'assets', 'worker-0123456789ab.js'), 'onmessage=()=>{}');
  put(join(runner, 'pyodide', '0.27.8', 'pyodide.asm.wasm'), 'wasm');
  put(join(runner, 'sw.js'), '// runner sw');
  return { site, runner };
}

describe('release_id', () => {
  it('is the same for the same inputs, wherever they are and whenever they were written', () => {
    const a = fakeDists('a');
    const b = fakeDists('b');
    expect(computeReleaseId(a)).toBe(computeReleaseId(b));
    expect(computeReleaseId(a)).toMatch(/^[0-9a-f]{64}$/);
  });

  it('leaves out release.json, the one file that carries it (no circularity)', () => {
    const a = fakeDists('c');
    const before = computeReleaseId(a);
    const id = writeRelease(a);
    expect(id).toBe(before);
    expect(computeReleaseId(a)).toBe(before);
    expect(fileDigests([{ name: 'site', dir: a.site }]).map((d) => d.path)).not.toContain(`site/${RELEASE_FILE}`);
    // ...but a release.json anywhere else is an ordinary file.
    writeFileSync(join(a.site, 'about', RELEASE_FILE), '{}');
    expect(computeReleaseId(a)).not.toBe(before);
  });

  it('is recomputed from the emitted files to the id in both release.json files', () => {
    const a = fakeDists('d');
    const id = writeRelease(a);
    for (const dir of [a.site, a.runner]) expect(JSON.parse(readFileSync(join(dir, RELEASE_FILE), 'utf-8')).release_id).toBe(id);
    expect(computeReleaseId(a)).toBe(id);
  });

  it('changes when one runner file changes, is renamed, is added, or moves between the dists', () => {
    const a = fakeDists('e');
    const base = computeReleaseId(a);
    appendFileSync(join(a.runner, 'assets', 'worker-0123456789ab.js'), ';');
    const changed = computeReleaseId(a);
    expect(changed).not.toBe(base);
    const b = fakeDists('f');
    writeFileSync(join(b.runner, 'extra.txt'), '');
    expect(computeReleaseId(b)).not.toBe(base);
    const c = fakeDists('g');
    // The same bytes under the other dist's name are a different file list.
    cpSync(join(c.runner, 'index.html'), join(c.site, 'runner-copy.html'));
    expect(computeReleaseId(c)).not.toBe(base);
  });
});

describe('the 25 MiB check', () => {
  it('names a file over the limit, and writeRelease refuses the build', () => {
    const a = fakeDists('h');
    const big = join(a.runner, 'pyodide', '0.27.8', 'huge.bin');
    const fd = openSync(big, 'w');
    ftruncateSync(fd, MAX_FILE_BYTES + 1); // sparse: no 25 MiB written
    closeSync(fd);
    expect(oversized([{ name: 'runner', dir: a.runner }])).toEqual([{ path: 'runner/pyodide/0.27.8/huge.bin', bytes: MAX_FILE_BYTES + 1 }]);
    expect(() => writeRelease(a)).toThrow(/25 MiB.*huge\.bin/);
    expect(existsSync(join(a.site, RELEASE_FILE))).toBe(false);
    expect(MAX_FILE_BYTES).toBe(25 * 1024 * 1024);
  });
});

describe('the release descriptions', () => {
  it('describes the site shell (no book, Pagefind, manifest, sw.js or _headers) and the books', () => {
    const a = fakeDists('i');
    const site = describeSite(a.site);
    expect(site.shell.urls.sort()).toEqual(['/', '/_astro/a.B1c2D3e4.js', '/about/']);
    expect(site.books.demo).toEqual({ content_hash: 'ab', bytes: 3, count: 1, manifest: '/_offline/demo.0123456789abcdef.json' });
  });
  it('describes the runner shell and its versioned Pyodide', () => {
    const a = fakeDists('j');
    const runner = describeRunner(a.runner);
    expect(runner.shell.urls.sort()).toEqual(['/', '/assets/worker-0123456789ab.js']);
    expect(runner.pyodide).toMatchObject({ dir: '0.27.8', cache: 'pyodide-0.27.8', urls: ['/pyodide/0.27.8/pyodide.asm.wasm'] });
  });
});

// The real build: the runner rebuilt twice from unchanged inputs gives the same id with the built
// site; one changed runner file gives another. Needs the runner's dependencies and a built site.
const realSite = join(SITE, 'dist');
const canBuildRunner = existsSync(join(RUNNER, 'node_modules', 'pyodide')) && existsSync(join(realSite, 'index.html'));

describe.skipIf(!canBuildRunner)('the real release (rebuilt runner)', () => {
  const build = (out: string) => {
    const run = spawnSync(process.execPath, [join(RUNNER, 'scripts', 'build.ts')], {
      cwd: RUNNER,
      env: { ...process.env, PY4KIDS_RUNNER_OUT: out },
      encoding: 'utf-8',
    });
    if (run.status !== 0) throw new Error(`runner build failed:\n${run.stdout}\n${run.stderr}`);
  };

  it('rebuilds to the same id, and one changed runner file changes it', () => {
    const one = join(work, 'runner-1');
    const two = join(work, 'runner-2');
    build(one);
    build(two);
    const id1 = computeReleaseId({ site: realSite, runner: one });
    expect(computeReleaseId({ site: realSite, runner: two })).toBe(id1);
    const worker = readdirSync(join(two, 'assets')).find((f) => f.startsWith('worker-'))!;
    appendFileSync(join(two, 'assets', worker), '\n');
    expect(computeReleaseId({ site: realSite, runner: two })).not.toBe(id1);
  }, 120_000);

  it.skipIf(!existsSync(join(realSite, RELEASE_FILE)) || !existsSync(join(RUNNER, 'dist', RELEASE_FILE)))(
    'recomputes the built release_id from site/dist and runner/dist',
    () => {
      const id = computeReleaseId({ site: realSite, runner: join(RUNNER, 'dist') });
      expect(JSON.parse(readFileSync(join(realSite, RELEASE_FILE), 'utf-8')).release_id).toBe(id);
      expect(JSON.parse(readFileSync(join(RUNNER, 'dist', RELEASE_FILE), 'utf-8')).release_id).toBe(id);
    },
  );
});

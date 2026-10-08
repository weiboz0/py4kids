/**
 * The structural leak test (plan 103 Phase B, "the poisoned bundle"). The site must never render
 * a field that may hold hidden material. This copies every real bundle, writes a unique sentinel
 * into every forbidden field —
 *   - `answer_md`
 *   - `check.source` (asserts)
 *   - `check.hash` (as `sha256:` + the sentinel's own SHA-256, so the schema still accepts it;
 *     the scan looks for that hex)
 *   - `check.program` of a hidden item (`answer_visibility: none`)
 *   - every non-sample fixture `.out` file
 * — builds the site from the poisoned copies (`PY4KIDS_SITE_CONTENT`), and searches all of the
 * output (HTML, JS, CSS, JSON, and Pagefind's index and fragments, decompressed, when Pagefind
 * runs) for any sentinel. Zero hits is required.
 *
 * The build also injects one page that deliberately renders an `answer_md`
 * (test/leak/regression.astro): its sentinel must be found there, which proves the scan catches
 * a leak, and nowhere else.
 */
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { gunzipSync } from 'node:zlib';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { CONTENT_ENV, loadBooks, repoRoot } from '../src/lib/bundle';
import type { EntryFile } from '../src/lib/types';

const SITE = join(import.meta.dirname, '..');
const CONTENT = join(repoRoot(), 'site', 'content');
const hasRealBundles = existsSync(CONTENT) && loadable();
const REGRESSION = `leak-regression${sep}index.html`;

function loadable(): boolean {
  try {
    loadBooks({ contentDir: CONTENT });
    return true;
  } catch {
    return false;
  }
}

function files(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? files(join(dir, d.name)) : [join(dir, d.name)],
  );
}

const sha256 = (text: string) => createHash('sha256').update(text).digest('hex');

interface Poisoned {
  /** Every needle to search for, with the field it was written to. */
  needles: Map<string, string>;
  counts: Record<string, number>;
  /** The first answer_md sentinel (the one the regression page renders). */
  firstAnswer: string;
}

/** Write a sentinel into every forbidden field of every bundle under `contentDir`. */
function poison(contentDir: string): Poisoned {
  const needles = new Map<string, string>();
  const counts: Record<string, number> = { answer_md: 0, source: 0, hash: 0, program: 0, fixture: 0 };
  let firstAnswer = '';
  let n = 0;
  // Lower-case letters and digits only: one token to Pagefind's indexer, and never a substring
  // of real text.
  const sentinel = (field: string) => `zqleak${field.replace(/[^a-z]/g, '')}${++n}zq`;

  for (const book of readdirSync(contentDir).sort()) {
    const bundle = join(contentDir, book);
    const bookJson = JSON.parse(readFileSync(join(bundle, 'book.json'), 'utf-8')) as { entries: { file: string }[] };
    for (const record of bookJson.entries) {
      const path = join(bundle, record.file);
      const entry = JSON.parse(readFileSync(path, 'utf-8')) as EntryFile;
      for (const item of entry.items) {
        if (item.answer_md !== undefined) {
          const s = sentinel('answer');
          item.answer_md = `The answer is ${s}.`;
          needles.set(s, `${item.key} answer_md`);
          counts.answer_md!++;
          firstAnswer ||= s;
        }
        const check = item.check;
        if (check.kind === 'asserts') {
          const s = sentinel('source');
          check.source = `assert solve() == "${s}"`;
          needles.set(s, `${item.key} check.source`);
          counts.source!++;
        }
        if (check.kind === 'answer' || check.kind === 'expected-output' || check.kind === 'predict') {
          const hex = sha256(sentinel('hash'));
          check.hash = `sha256:${hex}`;
          needles.set(hex, `${item.key} check.hash`);
          counts.hash!++;
        }
        if (check.kind === 'predict' && item.answer_visibility === 'none') {
          const s = sentinel('program');
          check.program = `print("${s}")`;
          needles.set(s, `${item.key} check.program`);
          counts.program!++;
        }
        if (check.kind === 'fixtures') {
          for (const c of check.cases) {
            if (c.sample) continue;
            const s = sentinel('fixture');
            writeFileSync(join(bundle, c.out_file), `${s}\n`);
            needles.set(s, `${item.key} ${c.out_file}`);
            counts.fixture!++;
          }
        }
      }
      writeFileSync(path, JSON.stringify(entry));
    }
  }
  return { needles, counts, firstAnswer };
}

/** A built file's searchable text: Pagefind's gzip-compressed index files are decompressed. */
function searchable(file: string): string {
  const bytes = readFileSync(file);
  if (bytes[0] === 0x1f && bytes[1] === 0x8b) {
    try {
      return gunzipSync(bytes).toString('latin1');
    } catch {
      // not gzip after all
    }
  }
  return bytes.toString('latin1');
}

/** Every (file, needle) hit under `dir`. */
function scan(dir: string, needles: Iterable<string>): { file: string; needle: string }[] {
  const list = [...needles];
  const hits: { file: string; needle: string }[] = [];
  for (const file of files(dir)) {
    const text = searchable(file).toLowerCase();
    for (const needle of list) if (text.includes(needle)) hits.push({ file: relative(dir, file), needle });
  }
  return hits;
}

describe.skipIf(!hasRealBundles)('the poisoned-bundle leak test', () => {
  let work = '';
  let out = '';
  let poisoned: Poisoned;
  let hits: { file: string; needle: string }[] = [];

  beforeAll(() => {
    // Under node_modules (never committed, and on the site's filesystem: Astro renames its
    // output into outDir, which fails across devices).
    const scratch = join(SITE, 'node_modules', '.cache');
    mkdirSync(scratch, { recursive: true });
    work = mkdtempSync(join(scratch, 'py4kids-leak-'));
    const content = join(work, 'content');
    out = join(work, 'dist');
    cpSync(CONTENT, content, { recursive: true });
    poisoned = poison(content);

    const astro = join(SITE, 'node_modules', '.bin', 'astro');
    const build = spawnSync(astro, ['build', '--config', 'test/leak/astro.config.mjs', '--outDir', out], {
      cwd: SITE,
      env: {
        ...process.env,
        [CONTENT_ENV]: content,
        PY4KIDS_LEAK_CACHE: join(work, 'cache'),
        ASTRO_TELEMETRY_DISABLED: '1',
      },
      encoding: 'utf-8',
    });
    if (build.status !== 0) throw new Error(`poisoned build failed:\n${build.stdout}\n${build.stderr}`);

    // Pagefind (plan 103 Phase E) indexes the poisoned build too, when it is installed.
    const pagefind = join(SITE, 'node_modules', '.bin', 'pagefind');
    if (existsSync(pagefind)) {
      const index = spawnSync(pagefind, ['--site', out], { cwd: SITE, encoding: 'utf-8' });
      if (index.status !== 0) throw new Error(`pagefind failed:\n${index.stdout}\n${index.stderr}`);
    }
    hits = scan(out, poisoned.needles.keys());
  }, 600_000);

  afterAll(() => {
    if (work) rmSync(work, { recursive: true, force: true });
  });

  it('poisons every kind of forbidden field', () => {
    for (const [field, count] of Object.entries(poisoned.counts)) {
      expect(count, `${field} sentinels`).toBeGreaterThan(0);
    }
    expect(poisoned.firstAnswer).not.toBe('');
  });

  it('built the real pages from the poisoned bundles', () => {
    const html = files(out).filter((f) => f.endsWith('.html'));
    expect(html.some((f) => f.includes(`${sep}practice${sep}`))).toBe(true);
    expect(html.length).toBeGreaterThan(100);
    // The scan covers every output: the slide decks, the card decks and the mastery maps too.
    const all = files(out).map((f) => relative(out, f));
    const books = loadBooks({ contentDir: CONTENT }).map((b) => b.id);
    for (const book of books) {
      expect(all, `${book} deck.json`).toContain(join(book, 'cards', 'deck.json'));
      expect(all, `${book} mastery.json`).toContain(join(book, 'mastery.json'));
      expect(all, `${book} cards page`).toContain(join(book, 'cards', 'index.html'));
      expect(all.some((f) => f.startsWith(`${book}${sep}`) && f.endsWith(`${sep}slides${sep}index.html`)), `${book} slides`).toBe(true);
    }
  });

  it('renders no sentinel anywhere in the site', () => {
    const leaks = hits
      .filter((h) => h.file !== REGRESSION)
      .map((h) => `${h.file}: ${poisoned.needles.get(h.needle)}`);
    expect(leaks).toEqual([]);
  });

  it('catches the deliberate leak (the regression page renders one answer_md)', () => {
    const caught = hits.filter((h) => h.file === REGRESSION).map((h) => poisoned.needles.get(h.needle));
    expect(caught).toHaveLength(1);
    expect(caught[0]).toMatch(/ answer_md$/);
  });

  it('ships no JSON carrying answer_md, source or hash keys', () => {
    for (const file of files(out).filter((f) => f.endsWith('.json'))) {
      const text = readFileSync(file, 'utf-8');
      expect(text, relative(out, file)).not.toMatch(/"(?:answer_md|source|hash)"\s*:/);
    }
  });
});

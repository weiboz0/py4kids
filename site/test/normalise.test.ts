/**
 * normalise.ts against every pinned vector in tools/export/hash_vectors.json (plan 103 Phase D),
 * including the Python-vs-JavaScript `\s` cases, plus plan 102 rule 3's `whitespace` and
 * `aliases` and an exhaustive casefold comparison with Python when one is available.
 */
import { spawnSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { repoRoot } from '../src/lib/bundle';
import { answerHash, casefold, normalise, type NormaliseOptions } from '../src/lib/normalise';

interface Vector {
  input: string;
  case: 'sensitive' | 'insensitive';
  whitespace?: 'collapse' | 'exact';
  aliases?: Record<string, string>;
  normalised: string;
  item_key: string;
  hash: string;
}

const vectors = JSON.parse(readFileSync(join(repoRoot(), 'tools', 'export', 'hash_vectors.json'), 'utf-8')) as Vector[];
const opts = (v: Vector): NormaliseOptions => ({
  case: v.case,
  ...(v.whitespace ? { whitespace: v.whitespace } : {}),
  ...(v.aliases ? { aliases: v.aliases } : {}),
});

describe('hash_vectors.json', () => {
  it('has the vectors', () => {
    expect(vectors.length).toBeGreaterThanOrEqual(28);
  });

  it.each(vectors.map((v) => [JSON.stringify(v.input), v] as const))('normalises %s', (_, v) => {
    expect(normalise(v.input, opts(v))).toBe(v.normalised);
  });

  it.each(vectors.map((v) => [v.item_key, v] as const))('hashes %s', async (_, v) => {
    expect(await answerHash(v.item_key, v.input, opts(v))).toBe(v.hash);
  });

  it('covers the characters where Python and JavaScript \\s differ', () => {
    const inputs = vectors.map((v) => v.input).join('');
    for (const ch of ['\x1f', '\x85', '\u2028', '\ufeff', '\xa0', '\u3000']) expect(inputs).toContain(ch);
  });
});

/**
 * Normalisation parity with the Python producer (plan 103 content review, [sol] 4): every vector
 * in hash_vectors.json, with every field it carries (`case`, and `whitespace` and `aliases` when
 * present), must normalise and hash exactly as Python pinned it. A vector field this test does not
 * know fails it, so a new rule can never be silently ignored. Plan 102 brings the full set of 41
 * vectors (with `whitespace: exact` and `aliases`); once it merges into this branch, this test
 * covers them all with no change.
 */
describe('parity with Python: every hash_vectors.json vector, all fields', () => {
  const KNOWN = new Set(['input', 'case', 'whitespace', 'aliases', 'normalised', 'item_key', 'hash']);

  it('uses only fields the TypeScript normaliser understands', () => {
    for (const v of vectors) expect(Object.keys(v).filter((k) => !KNOWN.has(k)), v.item_key).toEqual([]);
  });

  it('reproduces every vector\'s normalised text and hash', async () => {
    const failures: string[] = [];
    for (const v of vectors) {
      const got = normalise(v.input, opts(v));
      if (got !== v.normalised) failures.push(`${v.item_key}: normalised ${JSON.stringify(got)} != ${JSON.stringify(v.normalised)}`);
      const hash = await answerHash(v.item_key, v.input, opts(v));
      if (hash !== v.hash) failures.push(`${v.item_key}: hash ${hash} != ${v.hash}`);
    }
    expect(failures).toEqual([]);
    console.log(`hash_vectors.json parity: ${vectors.length} vectors, ${vectors.filter((v) => v.whitespace).length} with whitespace, ${vectors.filter((v) => v.aliases).length} with aliases`);
  });
});

describe('Python \\s, not JavaScript \\s', () => {
  it('collapses U+001C..U+001F and U+0085 (JavaScript \\s does not)', () => {
    for (const ch of ['\x1c', '\x1d', '\x1e', '\x1f', '\x85']) expect(normalise(`a${ch}b`, { case: 'sensitive' })).toBe('a b');
  });

  it('keeps U+FEFF (JavaScript \\s would strip it)', () => {
    expect(normalise('\ufeffa\ufeff', { case: 'sensitive' })).toBe('\ufeffa\ufeff');
  });

  it('splits lines only on \\n and \\r, as Python split("\\n") after folding CR', () => {
    expect(normalise('a\u2028b\u2029c\vd\fe', { case: 'sensitive' })).toBe('a b c d e');
  });
});

describe('whitespace: exact (plan 102 rule 3)', () => {
  const exact = { case: 'sensitive', whitespace: 'exact' } as const;

  it('keeps tabs, indentation and inner runs', () => {
    expect(normalise('a\tb', exact)).toBe('a\tb');
    expect(normalise('  x  =  1', exact)).toBe('  x  =  1');
  });

  it('folds CRLF, strips trailing whitespace per line, drops leading and trailing blank lines', () => {
    expect(normalise('\r\n  \r\n\tif x:  \r\n\t\tpass\t\r\n\r\n', exact)).toBe('\tif x:\n\t\tpass');
  });

  it('hashes a\\tb and a b differently under exact, the same under collapse', async () => {
    const key = 'book/unit-01-x/exercises/tab';
    expect(await answerHash(key, 'a\tb', exact)).not.toBe(await answerHash(key, 'a b', exact));
    expect(await answerHash(key, 'a\tb', { case: 'sensitive' })).toBe(await answerHash(key, 'a b', { case: 'sensitive' }));
  });
});

describe('aliases (plan 102 rule 3)', () => {
  const aliases = { '^': '↑' };

  it('maps the typed form to the canonical one', () => {
    expect(normalise('^ + A B', { case: 'sensitive', aliases })).toBe('↑ + A B');
  });

  it('applies after case folding', () => {
    expect(normalise('X', { case: 'insensitive', aliases: { x: 'y' } })).toBe('y');
    expect(normalise('X', { case: 'insensitive', aliases: { X: 'y' } })).toBe('x');
  });

  it('applies after whitespace collapsing', () => {
    expect(normalise('a  b', { case: 'sensitive', aliases: { 'a b': 'c' } })).toBe('c');
  });

  it('prefers the longest key and maps in one pass', () => {
    expect(normalise('<= <', { case: 'sensitive', aliases: { '<': '≺', '<=': '≤' } })).toBe('≤ ≺');
    expect(normalise('ab', { case: 'sensitive', aliases: { a: 'b', b: 'a' } })).toBe('ba');
  });

  it('makes ^ and ↑ hash the same, and differ without the alias', async () => {
    const key = 'acsl/unit-04-prefix/exercises/e-024';
    const s = { case: 'sensitive' } as const;
    expect(await answerHash(key, '^ A B', { ...s, aliases })).toBe(await answerHash(key, '↑ A B', { ...s, aliases }));
    expect(await answerHash(key, '^ A B', s)).not.toBe(await answerHash(key, '↑ A B', s));
  });
});

describe('casefold', () => {
  it('folds like Python on the known special cases', () => {
    expect(casefold('Straße ẞ ﬁ ΣΑΣ ı İ ŉ')).toBe('strasse ss fi σασ ı i̇ ʼn');
    expect(casefold('Ꭰ ꭰ ᏸ')).toBe('Ꭰ Ꭰ Ᏸ');
  });

  const python = spawnSync('uv', ['run', '--no-project', 'python', '-c', 'import sys; print(sys.version_info >= (3, 12))'], {
    cwd: repoRoot(),
    encoding: 'utf-8',
  });
  const hasPython = python.status === 0 && python.stdout.trim() === 'True';

  it.skipIf(!hasPython)('agrees with Python str.casefold() on every code point Python assigns', () => {
    const script = [
      'import json, sys, unicodedata',
      'out = {}',
      'for c in range(0x110000):',
      '    if 0xD800 <= c < 0xE000 or unicodedata.category(chr(c)) == "Cn": continue',
      '    f = chr(c).casefold()',
      '    if f != chr(c): out[c] = f',
      'out["assigned"] = [c for c in range(0x110000) if not (0xD800 <= c < 0xE000) and unicodedata.category(chr(c)) != "Cn"]',
      'sys.stdout.write(json.dumps(out))',
    ].join('\n');
    const run = spawnSync('uv', ['run', '--no-project', 'python', '-c', script], {
      cwd: repoRoot(),
      encoding: 'utf-8',
      maxBuffer: 64 * 1024 * 1024,
    });
    expect(run.status).toBe(0);
    const table = JSON.parse(run.stdout) as Record<string, string | number[]>;
    const assigned = table.assigned as number[];
    const wrong: string[] = [];
    for (const cp of assigned) {
      const ch = String.fromCodePoint(cp);
      const want = (table[String(cp)] as string | undefined) ?? ch;
      if (casefold(ch) !== want) wrong.push(cp.toString(16));
    }
    expect(wrong).toEqual([]);
  });
});

/**
 * The exported bundles, read by the browser tests at test time (plan 104 Phase B) to pick real
 * items and to build programs whose correct output is known: the test is the only reader of a
 * hidden fixture's `.out` here, never the page.
 */
import { spawnSync } from 'node:child_process';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { SITE } from './env';
import type { EntryFile, Item } from '../../src/lib/types';

export const CONTENT = join(SITE, 'content');
export const REPO = join(SITE, '..');

export interface Found {
  book: string;
  entry: string;
  item: Item;
  /** `/<book>/<entry>/practice/`. */
  page: string;
}

/** Every item of every exported book. */
export function allItems(): Found[] {
  const out: Found[] = [];
  for (const book of readdirSync(CONTENT).sort()) {
    const dir = join(CONTENT, book, 'entries');
    for (const file of readdirSync(dir).sort()) {
      const entry = JSON.parse(readFileSync(join(dir, file), 'utf-8')) as EntryFile;
      for (const item of entry.items) out.push({ book, entry: entry.entry.id, item, page: `/${book}/${entry.entry.id}/practice/` });
    }
  }
  return out;
}

/** The first matching item, or with `rank`, the matching item that ranks lowest. */
export function findItem(pred: (f: Found) => boolean, what: string, rank?: (f: Found) => number): Found {
  const matches = allItems().filter(pred);
  const found = rank ? matches.sort((a, b) => rank(a) - rank(b))[0] : matches[0];
  if (!found) throw new Error(`no item: ${what}`);
  return found;
}

/** A bundle file's text (`files/<entry>/...` under the book's bundle). */
export const bundleText = (book: string, path: string) => readFileSync(join(CONTENT, book, path), 'utf-8');

/** The fixture pairs of a fixtures item, in bundle order. */
export function fixturePairs(found: Found): { n: number; sample: boolean; input: string; output: string }[] {
  const check = found.item.check;
  if (check.kind !== 'fixtures') throw new Error(`${found.item.key} is not a fixtures item`);
  return check.cases.map((c) => ({ n: c.n, sample: c.sample, input: bundleText(found.book, c.in_file), output: bundleText(found.book, c.out_file) }));
}

/**
 * A Python program that answers each of the item's inputs with `answer(expected)` (a lookup
 * table from each case's input to a function of its expected output). The JSON text is passed as
 * a JSON string literal, which is also a valid Python string literal.
 */
export function lookupProgram(table: Record<string, string>): string {
  return ['import json, sys', `T = json.loads(${JSON.stringify(JSON.stringify(table))})`, 'sys.stdout.write(T.get(sys.stdin.read(), ""))', ''].join('\n');
}

/** `tools/judge.py`'s own `outputs_match` verdict (CPython), for parity. */
export function judgeMatch(actual: string, expected: string, lineExact: boolean): boolean {
  const script = 'import json, sys\nfrom tools.judge import outputs_match\na = json.load(sys.stdin)\nprint(outputs_match(a[0], a[1], line_exact=a[2]))';
  const result = spawnSync('uv', ['run', '--quiet', 'python', '-c', script], {
    cwd: REPO,
    input: JSON.stringify([actual, expected, lineExact]),
    encoding: 'utf-8',
  });
  if (result.status !== 0) throw new Error(`judge parity failed: ${result.stderr}`);
  return result.stdout.trim() === 'True';
}

/** Run a Python program under CPython (a predict item's program, read from the bundle). */
export function cpython(code: string): string {
  const result = spawnSync('uv', ['run', '--quiet', 'python', '-c', code], { cwd: REPO, encoding: 'utf-8' });
  if (result.status !== 0) throw new Error(`python failed: ${result.stderr}`);
  return result.stdout;
}

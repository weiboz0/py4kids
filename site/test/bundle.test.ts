import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { afterEach, describe, expect, it } from 'vitest';
import { BundleError, loadBook, loadBooks } from '../src/lib/bundle';

const FIXTURES = join(import.meta.dirname, 'fixtures', 'bundles');
const temps: string[] = [];

/** A writable copy of the fixture content directory. */
function copyFixtures(): string {
  const dir = mkdtempSync(join(tmpdir(), 'py4kids-bundle-'));
  temps.push(dir);
  cpSync(FIXTURES, dir, { recursive: true });
  return dir;
}

function edit(path: string, change: (data: any) => void): void {
  const data = JSON.parse(readFileSync(path, 'utf-8'));
  change(data);
  writeFileSync(path, JSON.stringify(data));
}

afterEach(() => {
  for (const dir of temps.splice(0)) rmSync(dir, { recursive: true, force: true });
});

describe('loadBook', () => {
  it('loads a valid bundle with its entries in syllabus order', () => {
    const book = loadBook(join(FIXTURES, 'demo'));
    expect(book.id).toBe('demo');
    expect(book.book.book.title).toBe('Demo Book');
    expect(book.entries.map((e) => e.record.id)).toEqual(['unit-01-demo', 'checkpoint-01-demo']);
    expect(book.entries[0]?.data.lesson?.blocks).toHaveLength(3);
    expect(book.entries[1]?.data.lesson).toBeNull();
  });

  it('fails on an invalid field in book.json, naming the file and the field', () => {
    const dir = copyFixtures();
    edit(join(dir, 'demo', 'book.json'), (d) => { d.entries[0].kind = 'lesson'; });
    expect(() => loadBook(join(dir, 'demo'))).toThrow(BundleError);
    expect(() => loadBook(join(dir, 'demo'))).toThrow(/invalid site bundle .*demo\/book\.json[\s\S]*\/entries\/0\/kind/);
  });

  it('fails on an invalid field in an entry file', () => {
    const dir = copyFixtures();
    edit(join(dir, 'demo', 'entries', 'unit-01-demo.json'), (d) => { d.items[0].check.requirements = []; });
    expect(() => loadBook(join(dir, 'demo'))).toThrow(/invalid site bundle .*unit-01-demo\.json/);
  });

  it('fails on a key the schema does not declare', () => {
    const dir = copyFixtures();
    edit(join(dir, 'demo', 'entries', 'unit-01-demo.json'), (d) => { d.items[0].solution = 'print(1)'; });
    expect(() => loadBook(join(dir, 'demo'))).toThrow(/must NOT have additional properties \(solution\)/);
  });

  it('fails when an entry file is missing or disagrees with book.json', () => {
    const dir = copyFixtures();
    rmSync(join(dir, 'demo', 'entries', 'checkpoint-01-demo.json'));
    expect(() => loadBook(join(dir, 'demo'))).toThrow(/cannot read .*checkpoint-01-demo\.json/);
    const other = copyFixtures();
    edit(join(other, 'demo', 'entries', 'checkpoint-01-demo.json'), (d) => { d.entry.kind = 'project'; });
    expect(() => loadBook(join(other, 'demo'))).toThrow(/but book\.json lists checkpoint/);
  });

  it('fails when book.id is not the bundle directory name', () => {
    const dir = copyFixtures();
    cpSync(join(dir, 'demo'), join(dir, 'other'), { recursive: true });
    expect(() => loadBook(join(dir, 'other'))).toThrow(/bundle directory is "other"/);
  });

  it('fails on malformed JSON', () => {
    const dir = copyFixtures();
    writeFileSync(join(dir, 'demo', 'book.json'), '{');
    expect(() => loadBook(join(dir, 'demo'))).toThrow(/not valid JSON/);
  });
});

describe('loadBooks', () => {
  it('discovers every */book.json in books.yaml order', () => {
    const dir = copyFixtures();
    cpSync(join(dir, 'demo'), join(dir, 'zeta'), { recursive: true });
    edit(join(dir, 'zeta', 'book.json'), (d) => { d.book.id = 'zeta'; });
    const yaml = join(dir, 'books.yaml');
    writeFileSync(yaml, 'books:\n- id: zeta\n- id: demo\n');
    expect(loadBooks({ contentDir: dir, booksYaml: yaml }).map((b) => b.id)).toEqual(['zeta', 'demo']);
    writeFileSync(yaml, 'books: []\n');
    expect(loadBooks({ contentDir: dir, booksYaml: yaml }).map((b) => b.id)).toEqual(['demo', 'zeta']);
  });

  it('fails clearly when there is no bundle', () => {
    const dir = mkdtempSync(join(tmpdir(), 'py4kids-empty-'));
    temps.push(dir);
    expect(() => loadBooks({ contentDir: dir })).toThrow(/no site bundle .* run scripts\/build-site\.sh/);
  });
});

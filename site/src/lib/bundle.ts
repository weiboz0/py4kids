/**
 * The bundle loader (plan 103, Architecture): discovers `site/content/<book>/book.json`, reads
 * every entry file it lists, and validates each document against
 * `tools/export/schema/bundle.schema.json` with Ajv (JSON Schema 2020-12). The schema is read
 * from the repository, never copied. An invalid bundle throws `BundleError`, which fails the
 * Astro build.
 *
 * The site keys on `book.json`, never on a book id: adding a book needs no site code.
 * Books are ordered as `books.yaml` lists them; a book it does not list sorts last, by id.
 */

import { existsSync, readdirSync, readFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { Ajv2020, type ErrorObject, type ValidateFunction } from 'ajv/dist/2020.js';
import { parse as parseYaml } from 'yaml';
import type { BookFile, EntryFile, EntryRecord } from './types';

export const SCHEMA_RELPATH = 'tools/export/schema/bundle.schema.json';
export const SCHEMA_ID = 'py4kids/bundle/1.0.0';
/** Points the loader at another content directory (tests, the poisoned-bundle build). */
export const CONTENT_ENV = 'PY4KIDS_SITE_CONTENT';

export class BundleError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'BundleError';
  }
}

export interface LoadedEntry {
  record: EntryRecord;
  data: EntryFile;
}

export interface LoadedBook {
  /** The book id; equal to its bundle directory name and to `book.book.id`. */
  id: string;
  /** Absolute path of the bundle directory (`site/content/<id>`). */
  dir: string;
  book: BookFile;
  /** In syllabus order, as `book.entries` lists them. */
  entries: LoadedEntry[];
}

/** Hands each validated document to a wrapper before use (the schema-key test records reads). */
export type Wrap = <T extends object>(data: T, file: string) => T;

export interface LoadOptions {
  /** Defaults to `$PY4KIDS_SITE_CONTENT`, else `<repo>/site/content`. */
  contentDir?: string;
  /** Defaults to `<repo>/tools/export/schema/bundle.schema.json`. */
  schemaPath?: string;
  /** Defaults to `<repo>/books.yaml`; only its order is used. */
  booksYaml?: string;
  wrap?: Wrap;
}

/** The repository root: the nearest ancestor of `start` holding the bundle schema. */
export function repoRoot(start: string = process.cwd()): string {
  let dir = resolve(start);
  for (;;) {
    if (existsSync(join(dir, SCHEMA_RELPATH))) return dir;
    const parent = dirname(dir);
    if (parent === dir) {
      throw new BundleError(`cannot find ${SCHEMA_RELPATH} above ${start}`);
    }
    dir = parent;
  }
}

export function defaultContentDir(): string {
  const override = process.env[CONTENT_ENV];
  return override ? resolve(override) : join(repoRoot(), 'site', 'content');
}

export interface BundleValidator {
  ajv: Ajv2020;
  book: ValidateFunction<BookFile>;
  entry: ValidateFunction<EntryFile>;
}

const validators = new Map<string, BundleValidator>();

/** Ajv validators for `book.json` and entry files, compiled once per schema path. */
export function bundleValidator(schemaPath: string = join(repoRoot(), SCHEMA_RELPATH)): BundleValidator {
  const cached = validators.get(schemaPath);
  if (cached) return cached;
  const schema: unknown = JSON.parse(readFileSync(schemaPath, 'utf-8'));
  // strictTypes is off: the schema's side_block narrows `type` in an allOf branch without
  // repeating `"type": "object"`, which is valid 2020-12 but trips that lint.
  const ajv = new Ajv2020({ allErrors: true, strict: true, strictRequired: false, strictTypes: false });
  ajv.addSchema(schema as object);
  const get = <T>(name: string): ValidateFunction<T> => {
    const fn = ajv.getSchema<T>(`${SCHEMA_ID}#/$defs/${name}`);
    if (!fn) throw new BundleError(`${schemaPath} has no $defs/${name}`);
    return fn;
  };
  const made = { ajv, book: get<BookFile>('book_file'), entry: get<EntryFile>('entry_file') };
  validators.set(schemaPath, made);
  return made;
}

const MAX_ERRORS = 8;

function describe(errors: ErrorObject[] | null | undefined): string {
  const lines = (errors ?? []).map((e) => {
    const extra = e.keyword === 'additionalProperties'
      ? ` (${String((e.params as { additionalProperty?: string }).additionalProperty)})`
      : e.keyword === 'enum'
        ? ` (${JSON.stringify((e.params as { allowedValues?: unknown }).allowedValues)})`
        : '';
    return `  ${e.instancePath || '/'}: ${e.message ?? e.keyword}${extra}`;
  });
  const unique = [...new Set(lines)];
  const shown = unique.slice(0, MAX_ERRORS);
  if (unique.length > MAX_ERRORS) shown.push(`  ... and ${unique.length - MAX_ERRORS} more`);
  return shown.join('\n');
}

function readJson(path: string, label: string): unknown {
  let text: string;
  try {
    text = readFileSync(path, 'utf-8');
  } catch (error) {
    throw new BundleError(`cannot read ${label}: ${(error as Error).message}`);
  }
  try {
    return JSON.parse(text);
  } catch (error) {
    throw new BundleError(`${label} is not valid JSON: ${(error as Error).message}`);
  }
}

function invalid(label: string, detail: string): BundleError {
  return new BundleError(
    `invalid site bundle ${label} (against ${SCHEMA_RELPATH}):\n${detail}\n` +
      'Regenerate it with scripts/build-site.sh (py4kids-tools export); never hand-edit a bundle.',
  );
}

const identity: Wrap = (data) => data;

/** Load and validate one bundle directory. */
export function loadBook(dir: string, options: LoadOptions = {}): LoadedBook {
  const abs = resolve(dir);
  const id = abs.split(/[\\/]/).pop() ?? abs;
  const validator = bundleValidator(options.schemaPath);
  const wrap = options.wrap ?? identity;
  const label = (path: string) => relative(process.cwd(), path) || path;

  const bookPath = join(abs, 'book.json');
  const rawBook = readJson(bookPath, label(bookPath));
  if (!validator.book(rawBook)) throw invalid(label(bookPath), describe(validator.book.errors));
  if (rawBook.book.id !== id) {
    throw invalid(label(bookPath), `  /book/id: is ${JSON.stringify(rawBook.book.id)}, but the bundle directory is ${JSON.stringify(id)}`);
  }
  const seen = new Set<string>();
  for (const record of rawBook.entries) {
    if (seen.has(record.id)) throw invalid(label(bookPath), `  /entries: duplicate entry id ${record.id}`);
    seen.add(record.id);
  }
  const book = wrap(rawBook, 'book.json');

  const entries: LoadedEntry[] = book.entries.map((record) => {
    const path = join(abs, record.file);
    const raw = readJson(path, label(path));
    if (!validator.entry(raw)) throw invalid(label(path), describe(validator.entry.errors));
    if (raw.entry.id !== record.id || raw.entry.kind !== record.kind) {
      throw invalid(label(path), `  /entry: is ${raw.entry.kind} ${raw.entry.id}, but book.json lists ${record.kind} ${record.id}`);
    }
    return { record, data: wrap(raw, record.file) };
  });
  return { id, dir: abs, book, entries };
}

function bookOrder(booksYaml: string): string[] {
  if (!existsSync(booksYaml)) return [];
  const catalog = parseYaml(readFileSync(booksYaml, 'utf-8')) as { books?: { id: string }[] };
  return (catalog.books ?? []).map((b) => b.id);
}

/** Every bundle under the content directory, in `books.yaml` order. Throws when there is none. */
export function loadBooks(options: LoadOptions = {}): LoadedBook[] {
  const contentDir = options.contentDir ?? defaultContentDir();
  const dirs = existsSync(contentDir)
    ? readdirSync(contentDir, { withFileTypes: true })
        .filter((d) => d.isDirectory() && existsSync(join(contentDir, d.name, 'book.json')))
        .map((d) => d.name)
    : [];
  if (dirs.length === 0) {
    throw new BundleError(
      `no site bundle (*/book.json) under ${contentDir}; run scripts/build-site.sh to export the site books`,
    );
  }
  const order = bookOrder(options.booksYaml ?? join(repoRoot(), 'books.yaml'));
  const rank = (id: string) => {
    const i = order.indexOf(id);
    return i === -1 ? order.length : i;
  };
  dirs.sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
  return dirs.map((name) => loadBook(join(contentDir, name), options));
}

let cache: LoadedBook[] | undefined;

/** The default content directory's books, loaded once per build. Pages use this. */
export function getBooks(): LoadedBook[] {
  cache ??= loadBooks();
  return cache;
}

export function getBook(id: string): LoadedBook {
  const found = getBooks().find((b) => b.id === id);
  if (!found) throw new BundleError(`no site bundle for book ${JSON.stringify(id)}`);
  return found;
}

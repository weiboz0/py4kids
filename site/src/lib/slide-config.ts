/**
 * A book's slide limits and allow list: the optional `slides:` block of `<book>/site.yaml`
 * (plan 103 D6). `tools/books.py` (`site_config`) is the validator, run by `site-check` and the
 * Python tests; this reader applies the defaults and refuses anything it cannot use.
 */

import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { parse as parseYaml } from 'yaml';
import type { LoadedBook } from './bundle';
import { auditBook, DEFAULT_LIMITS, type AllowEntry, type BookAudit, type SlideConfig } from './slides.ts';

export { auditPasses, formatAudit } from './slides.ts';

const LIMIT_KEYS = {
  max_words: 'maxWords',
  max_unit_words: 'maxUnitWords',
  max_table_rows: 'maxTableRows',
  max_code_lines: 'maxCodeLines',
} as const;

/** The book's root folder: its `books.yaml` `root`, else its id. */
function bookRoot(repo: string, book: string): string {
  const catalog = parseYaml(readFileSync(join(repo, 'books.yaml'), 'utf-8')) as { books?: { id: string; root?: string }[] };
  const entry = (catalog.books ?? []).find((b) => b.id === book);
  return join(repo, entry?.root ?? book);
}

/** Read `<book>/site.yaml` `slides:`, with the defaults for anything unset. */
export function slideConfig(repo: string, book: string): SlideConfig {
  const path = join(bookRoot(repo, book), 'site.yaml');
  const config: SlideConfig = { ...DEFAULT_LIMITS, allow: [] };
  if (!existsSync(path)) return config;
  const data = (parseYaml(readFileSync(path, 'utf-8')) ?? {}) as { slides?: Record<string, unknown> };
  const slides = data.slides;
  if (slides === undefined || slides === null) return config;
  const fail = (detail: string) => new Error(`${book}/site.yaml: slides: ${detail} (run: uv run py4kids-tools --book ${book} site-check)`);
  for (const [yamlKey, key] of Object.entries(LIMIT_KEYS)) {
    if (!(yamlKey in slides)) continue;
    const value = slides[yamlKey];
    if (typeof value !== 'number' || !Number.isInteger(value) || value <= 0) throw fail(`${yamlKey} must be a positive integer`);
    config[key] = value;
  }
  const allow = slides.allow ?? [];
  if (!Array.isArray(allow)) throw fail('allow must be a list');
  config.allow = allow.map((a: unknown, n): AllowEntry => {
    const { key, reason } = (a ?? {}) as { key?: unknown; reason?: unknown };
    if (typeof key !== 'string' || typeof reason !== 'string' || !key || !reason.trim()) {
      throw fail(`allow[${n}] needs a key and a reason`);
    }
    return { key, reason: reason.trim() };
  });
  return config;
}

/** Audit a loaded book's lessons with its own `site.yaml` limits (the audit script, the tests). */
export function auditLoadedBook(repo: string, book: LoadedBook): { audit: BookAudit; config: SlideConfig } {
  const config = slideConfig(repo, book.id);
  const entries = book.entries.flatMap((e) =>
    e.data.lesson === null ? [] : [{ id: e.record.id, blocks: e.data.lesson.blocks }]);
  return { audit: auditBook(book.id, entries, config), config };
}

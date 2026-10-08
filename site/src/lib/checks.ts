/**
 * The practice checks' build-time projections (plan 104 Phase B). Each is a small same-origin
 * JSON file the check island fetches only when it needs it, never bundle JSON:
 *
 * - `/<book>/<entry>/practice/check/<anchor>.json` (every item): what its check needs
 *   (`check-model.ts` `ClientCheck`): a salted hash and the answer format, the shipped asserts
 *   (for the runner only), or the fixture cases' file URLs. Never `answer_md`, never a predict
 *   item's `program`, never a fixture's expected output (only its URL).
 * - `/<book>/<entry>/practice/answer/<anchor>.json`: only for an odd unit exercise
 *   (`answer_visibility: after-attempt`), `answer_md` rendered (`{=latex}` dropped) with its
 *   turtle drawings; fetched only after a genuine attempt, so it is never in the DOM before one.
 * - `/<book>/<entry>/run.json` (every lesson): each runnable block's code, prelude and files.
 * - `/<book>/files/<entry>/...`: the bundle's files (lesson assets, fixture pairs), fetched one
 *   at a time, per check or per run.
 *
 * None of these files is a page, so Pagefind never indexes them.
 */

import type { LoadedBook, LoadedEntry } from './bundle';
import {
  caseBudget,
  DEFAULT_BUDGET_MS,
  orderCases,
  type ClientAnswer,
  type ClientCheck,
  type ClientFile,
  type ClientFormat,
  type LessonRun,
  type RunBlock,
} from './check-model';
import { renderMarkdown } from './markdown';
import { turtleSvg } from './turtle';
import type { AnswerFormat, Block, BundlePath, Item, Segment } from './types';

// ---------------------------------------------------------------------------------------------
// Anchors and URLs

const slug = (text: string) =>
  text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '') || 'item';

/** Each item's anchor on its practice page (unique per page); also its projections' file name. */
export function itemAnchors(items: Item[]): string[] {
  const used = new Set<string>();
  return items.map((item, i) => {
    let anchor = slug(item.label || `item ${i + 1}`);
    if (used.has(anchor)) anchor = `${anchor}-${i + 1}`;
    used.add(anchor);
    return anchor;
  });
}

export const checkUrl = (book: string, entry: string, anchor: string) => `/${book}/${entry}/practice/check/${anchor}.json`;
export const answerUrl = (book: string, entry: string, anchor: string) => `/${book}/${entry}/practice/answer/${anchor}.json`;
export const runUrl = (book: string, entry: string) => `/${book}/${entry}/run.json`;

/** A bundle file's same-origin URL: `files/<entry>/<path>` is served at `/<book>/files/<entry>/<path>`. */
export const fileUrl = (book: string, path: BundlePath) => `/${book}/${path}`;

/** A bundle file mounted in a run's working directory, at its path inside the entry directory. */
export function clientFile(book: string, path: BundlePath): ClientFile {
  const parts = path.split('/');
  if (parts[0] !== 'files' || parts.length < 3) throw new Error(`not a bundle file path: ${path}`);
  return { path: parts.slice(2).join('/'), url: fileUrl(book, path) };
}

/** Does an item ship its answer (an odd unit exercise)? Only these get an answer projection. */
export const shipsAnswer = (item: Item): boolean =>
  item.kind === 'unit' && item.answer_visibility === 'after-attempt' && item.answer_md !== undefined;

// ---------------------------------------------------------------------------------------------
// Asserts

/**
 * Split an asserts check's source into top-level statements, one per runner verdict: a statement
 * starts at column 0 outside any bracket or string; indented or bracketed lines continue it.
 * Blank lines and whole-line comments between statements are dropped.
 */
export function splitAsserts(source: string): string[] {
  const out: string[] = [];
  let current: string[] = [];
  let depth = 0;
  let triple: string | null = null;
  const flush = () => {
    // Blank and comment lines after a statement belong to no statement.
    while (current.length > 0 && /^\s*(#.*)?$/.test(current[current.length - 1]!)) current.pop();
    const text = current.join('\n').trim();
    if (text !== '') out.push(text);
    current = [];
  };
  for (const line of source.replace(/\r\n?/g, '\n').split('\n')) {
    const starts = depth === 0 && triple === null && /^\S/.test(line) && !line.startsWith('#');
    const continuation = current.length > 0 && current[current.length - 1]!.endsWith('\\');
    if (starts && !continuation) flush();
    if (depth === 0 && triple === null && current.length === 0 && (line.trim() === '' || line.trimStart().startsWith('#'))) continue;
    current.push(line);
    // Track brackets and strings to know whether the statement goes on.
    for (let i = 0; i < line.length; i++) {
      const ch = line[i]!;
      if (triple !== null) {
        if (line.startsWith(triple, i)) {
          triple = null;
          i += 2;
        }
        continue;
      }
      if (ch === '#') break;
      if (ch === '"' || ch === "'") {
        if (line.startsWith(ch.repeat(3), i)) {
          triple = ch.repeat(3);
          i += 2;
          continue;
        }
        // A one-line string: skip to its closing quote.
        let j = i + 1;
        while (j < line.length && line[j] !== ch) j += line[j] === '\\' ? 2 : 1;
        i = j;
        continue;
      }
      if ('([{'.includes(ch)) depth++;
      else if (')]}'.includes(ch)) depth = Math.max(0, depth - 1);
    }
  }
  flush();
  return out;
}

// ---------------------------------------------------------------------------------------------
// The check projection

function clientFormat(format: AnswerFormat): ClientFormat {
  const out: ClientFormat = { case: format.case, hint: format.hint };
  // Plan 102's optional fields, when the bundle carries them.
  if (format.whitespace !== undefined) out.whitespace = format.whitespace;
  if (format.aliases !== undefined) out.aliases = { ...format.aliases };
  return out;
}

/** What the item's check island needs (see the module comment). */
export function checkProjection(book: string, item: Item): ClientCheck {
  const check = item.check;
  const files = item.files.map((f) => clientFile(book, f));
  const base = { key: item.key, turtle: check.turtle };
  switch (check.kind) {
    case 'fixtures': {
      const skipped = new Set(check.over_budget);
      return {
        ...base,
        kind: 'fixtures',
        match: check.match,
        cases: orderCases(
          check.cases.map((c) => ({
            n: c.n,
            sample: c.sample,
            input: fileUrl(book, c.in_file),
            expected: fileUrl(book, c.out_file),
            skipped: skipped.has(c.n),
          })),
        ),
        budget_ms: caseBudget(check.cpu_ms),
        files,
      };
    }
    case 'asserts':
      return { ...base, kind: 'asserts', asserts: splitAsserts(check.source), budget_ms: DEFAULT_BUDGET_MS, files };
    case 'expected-output':
      return { ...base, kind: 'expected-output', hash: check.hash, format: clientFormat(check.answer_format), budget_ms: DEFAULT_BUDGET_MS, files };
    case 'answer':
    case 'predict':
      return { ...base, kind: check.kind, hash: check.hash, format: clientFormat(check.answer_format) };
    case 'self-check':
      return { ...base, kind: 'self-check', budget_ms: DEFAULT_BUDGET_MS, files };
  }
}

/** Every drawing in `answer_figures`, whether it holds one figure or several. */
function figureList(figures: Segment[][] | Segment[] | undefined): Segment[][] {
  if (!figures || figures.length === 0) return [];
  return Array.isArray(figures[0]) ? (figures as Segment[][]) : [figures as Segment[]];
}

/** An odd unit item's answer, rendered; null for every other item. */
export function answerProjection(item: Item): ClientAnswer | null {
  if (!shipsAnswer(item)) return null;
  const label = item.title ? `${item.label}: ${item.title}` : item.label;
  return {
    key: item.key,
    html: renderMarkdown(item.answer_md!),
    figures: figureList(item.answer_figures)
      .filter((segments) => segments.length > 0)
      .map((segments, i, all) => turtleSvg(segments, `Answer drawing for ${label}${all.length > 1 ? ` (${i + 1})` : ''}`)),
  };
}

// ---------------------------------------------------------------------------------------------
// Lesson runs

/** The block types a reader can run (a starter is scaffolding, not a program). */
export const RUNNABLE = new Set<Block['type']>(['code', 'tryit', 'error-demo', 'hang-demo', 'turtle-figure', 'program']);

export const isRunnable = (block: Block): boolean => RUNNABLE.has(block.type) && (block.code ?? '').trim() !== '';

/** Replay the block's prelude first when its session is new. */
export const needsPrelude = (block: Block): boolean => (block.needs_prelude || block.probe === 'prelude') && block.prelude.length > 0;

/** The lesson's run data: every runnable block, and every block a prelude names. */
export function lessonRunProjection(book: LoadedBook, entry: LoadedEntry): LessonRun | null {
  const blocks = entry.data.lesson?.blocks;
  if (!blocks) return null;
  const byKey = new Map(blocks.map((b) => [b.key, b]));
  const out: Record<string, RunBlock> = {};
  const add = (block: Block) => {
    if (out[block.key]) return;
    out[block.key] = {
      code: block.code ?? '',
      prelude: needsPrelude(block) ? block.prelude.filter((k) => byKey.has(k)) : [],
      stdin: block.stdin === true,
      sample_input: block.sample_input ?? '',
      files: block.files.map((f) => clientFile(book.id, f)),
    };
  };
  for (const block of blocks) {
    if (!isRunnable(block)) continue;
    add(block);
    if (needsPrelude(block)) for (const key of block.prelude) {
      const pre = byKey.get(key);
      if (pre) add(pre);
    }
  }
  return { session: entry.record.id, budget_ms: DEFAULT_BUDGET_MS, blocks: out };
}

// ---------------------------------------------------------------------------------------------
// Route lists

export interface ItemRoute {
  book: string;
  entry: string;
  anchor: string;
  item: Item;
}

/** Every item of every book, with its anchor. */
export function itemRoutes(books: LoadedBook[]): ItemRoute[] {
  return books.flatMap((b) =>
    b.entries.flatMap((e) => {
      const anchors = itemAnchors(e.data.items);
      return e.data.items.map((item, i) => ({ book: b.id, entry: e.record.id, anchor: anchors[i]!, item }));
    }),
  );
}

/** Every bundle file a run or check may fetch, by book. */
export function bundleFiles(book: LoadedBook): BundlePath[] {
  const paths = new Set<string>();
  for (const entry of book.entries) {
    for (const path of entry.data.files) paths.add(path);
    for (const block of entry.data.lesson?.blocks ?? []) for (const path of block.files) paths.add(path);
    for (const item of entry.data.items) {
      for (const path of item.files) paths.add(path);
      const check = item.check;
      if (check.kind === 'fixtures') for (const c of check.cases) {
        paths.add(c.in_file);
        paths.add(c.out_file);
      }
    }
  }
  return [...paths].sort();
}

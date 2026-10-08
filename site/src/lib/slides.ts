/**
 * Slide rules and the slide audit (plan 103, "Slide mode and the slide audit", design 012 D6).
 *
 * `buildSlides` is the one function that turns a lesson's blocks into slides. The slide player
 * (`src/pages/[book]/[entry]/slides.astro`) renders its result and the slide audit
 * (`scripts/slide-audit.ts`, `pnpm slide-audit`) measures it, so what the audit passes is exactly
 * what a student sees.
 *
 * The rules:
 * - opener, goals and recap blocks start a slide; so does every code-like block (code + output,
 *   program, try-it, error/hang demo, turtle figure), which is one slide on its own;
 * - every prose-like block (prose, opener, goals, recap, notice) is cut inside itself into
 *   *units*: at paragraph boundaries and at top-level list items. A fenced code block is never
 *   cut; a list item keeps its indented continuation lines and nested lists; a pipe table is
 *   one atomic unit, measured by its rows, whose words do not count toward `maxWords`;
 * - units of consecutive prose blocks are packed into slides of up to `maxWords` words. A
 *   heading always starts a slide (a run of headings shares one; heading words are the slide's
 *   title and do not count toward the budget), the unit after a heading always joins it, a
 *   slide holds at most one table, and a unit longer than `maxWords` is a slide on its own;
 * - an HTML comment line (an authoring marker, which the PDFs drop too) is not slide text;
 * - words are whitespace-separated tokens (fence lines excluded);
 * - a notice attaches to the adjacent code slide (the one before it, else the one after it)
 *   when the pair stays within `maxWords`; otherwise it becomes its own slide(s);
 * - a block whose cell is tagged `slide-break` starts a new slide (a cell split into several
 *   blocks breaks once, before its first block); `slide-skip` leaves the cell's blocks out of
 *   the slides (they still show in the reading view).
 *
 * The two limits: `maxWords` is the packing budget; `maxUnitWords`, `maxTableRows` and
 * `maxCodeLines` are the failure limits the audit enforces. A unit between the two word limits
 * is one slide over the packing budget: the audit reports it and does not fail on it.
 *
 * This module is pure (no file system) and reads bundle data only through `Block`.
 */

import type { Block, BlockType, ProseBlockType } from './types';

export interface SlideLimits {
  /** The packing budget (default 90). */
  maxWords: number;
  /** A unit over this fails the audit (default 150). */
  maxUnitWords: number;
  /** A table with more body rows fails the audit (default 12). */
  maxTableRows: number;
  /** A code slide with more code lines fails the audit (default 40). */
  maxCodeLines: number;
}

/** The defaults; `tools/books.py` `SLIDE_DEFAULTS` holds the same numbers. */
export const DEFAULT_LIMITS: SlideLimits = {
  maxWords: 90,
  maxUnitWords: 150,
  maxTableRows: 12,
  maxCodeLines: 40,
};

export const SLIDE_BREAK = 'slide-break';
export const SLIDE_SKIP = 'slide-skip';

const PROSE_TYPES: ReadonlySet<BlockType> = new Set<ProseBlockType>(['prose', 'opener', 'notice', 'goals', 'recap']);
/** Prose-like blocks that always start a slide. */
const STARTS_SLIDE: ReadonlySet<BlockType> = new Set<BlockType>(['opener', 'goals', 'recap']);

export type UnitKind = 'paragraph' | 'item' | 'heading' | 'table';

/** One indivisible piece of a prose-like block's Markdown. */
export interface MdUnit {
  kind: UnitKind;
  md: string;
  /** Words counted toward the packing budget (0 for a table). */
  words: number;
  /** A table's body rows (header and delimiter rows excluded); 0 otherwise. */
  rows: number;
}

const FENCE = /^ {0,3}(`{3,}|~{3,})/;
const TOP_ITEM = /^([-*+]|\d{1,9}[.)])(\s|$)/;
const HEADING = /^#{1,6}(\s|$)/;
const TABLE_ROW = /^ {0,3}\|/;
const TABLE_DELIMITER = /^ {0,3}\|?\s*:?-{1,}:?\s*(\|\s*:?-{1,}:?\s*)*\|?\s*$/;

/** Words in Markdown text: whitespace-separated tokens, fence lines excluded. */
export function countWords(md: string): number {
  let n = 0;
  for (const line of md.split('\n')) {
    if (FENCE.test(line)) continue;
    for (const token of line.split(/\s+/)) if (token !== '') n += 1;
  }
  return n;
}

function makeUnit(kind: UnitKind, lines: string[]): MdUnit {
  while (lines.length > 0 && lines[lines.length - 1]!.trim() === '') lines.pop();
  const md = lines.join('\n');
  if (kind === 'table') {
    const rows = lines.filter((l) => TABLE_ROW.test(l) && !TABLE_DELIMITER.test(l)).length;
    return { kind, md, words: 0, rows: Math.max(0, rows - 1) };
  }
  return { kind, md, words: countWords(md), rows: 0 };
}

/**
 * Cut a prose-like block's Markdown into units: paragraphs, top-level list items, headings and
 * tables. Cuts happen only at blank lines outside fenced code, before a top-level list item,
 * around a heading line and around a table.
 */
export function splitUnits(md: string): MdUnit[] {
  const units: MdUnit[] = [];
  let kind: UnitKind | null = null;
  let lines: string[] = [];
  let fence: string | null = null;
  let blank = false;
  const close = () => {
    if (kind !== null && lines.some((l) => l.trim() !== '')) units.push(makeUnit(kind, lines));
    kind = null;
    lines = [];
  };
  const open = (k: UnitKind, line: string) => {
    close();
    kind = k;
    lines = [line];
  };

  let comment = false;
  for (const line of md.replace(/\r\n?/g, '\n').split('\n')) {
    // An HTML comment line (an authoring marker such as `<!-- pattern: ... -->`) is not slide
    // text: Pandoc drops it from the PDFs too. It separates units like a blank line.
    if (fence === null && (comment || line.trimStart().startsWith('<!--'))) {
      comment = !line.includes('-->');
      blank = true;
      continue;
    }
    if (fence !== null) {
      lines.push(line);
      const m = FENCE.exec(line);
      if (m && m[1]![0] === fence[0] && m[1]!.length >= fence.length && line.trim() === m[1]) fence = null;
      continue;
    }
    if (line.trim() === '') {
      blank = true;
      if (kind !== null) lines.push(line);
      continue;
    }
    const indent = line.length - line.trimStart().length;
    const fenceOpen = FENCE.exec(line);
    if (HEADING.test(line)) {
      open('heading', line);
    } else if (TOP_ITEM.test(line)) {
      open('item', line);
    } else if (TABLE_ROW.test(line) && kind !== 'table' && !(kind === 'item' && indent >= 2)) {
      open('table', line);
    } else if (kind === null || kind === 'heading') {
      open('paragraph', line);
    } else if (kind === 'table') {
      if (TABLE_ROW.test(line) && !blank) lines.push(line);
      else open('paragraph', line);
    } else if (blank) {
      // After a blank line, only an indented line continues a list item (a continuation
      // paragraph, a nested list, an indented fence); anything else starts a new unit.
      if (kind === 'item' && indent >= 2) lines.push(line);
      else open('paragraph', line);
    } else {
      lines.push(line); // a paragraph's next line, a lazy continuation or a nested item
    }
    if (fenceOpen) fence = fenceOpen[1]!;
    blank = false;
  }
  close();
  return units;
}

/** A piece of one block on a slide: some of a prose-like block's units, or a whole code block. */
export type SlidePart =
  | { kind: 'md'; key: string; type: ProseBlockType; units: MdUnit[]; md: string }
  | { kind: 'block'; key: string; block: Block };

export type SlideKind = 'prose' | 'notice' | 'code' | 'tryit' | 'demo' | 'figure';

export interface Slide {
  kind: SlideKind;
  parts: SlidePart[];
  /** Words toward the packing budget (headings and tables excluded; code tokens on code slides). */
  words: number;
}

function slideKindOf(type: BlockType): SlideKind {
  switch (type) {
    case 'tryit':
      return 'tryit';
    case 'error-demo':
    case 'hang-demo':
      return 'demo';
    case 'turtle-figure':
      return 'figure';
    default:
      return 'code';
  }
}

const isCodeSlide = (s: Slide | undefined): s is Slide =>
  s !== undefined && s.kind !== 'prose' && s.kind !== 'notice';

/** Words a code block puts on its slide: tokens of its code and its stored output. */
export function codeWords(block: Block): number {
  const tokens = (text: string | undefined) => (text ?? '').split(/\s+/).filter((t) => t !== '').length;
  return tokens(block.code) + tokens(block.output);
}

/** Code lines of a code-like block (trailing blank lines ignored). */
export function codeLines(block: Block): number {
  const lines = (block.code ?? '').replace(/\s+$/, '').split('\n');
  return lines.length === 1 && lines[0] === '' ? 0 : lines.length;
}

const budgetWords = (u: MdUnit) => (u.kind === 'heading' ? 0 : u.words);

function joinMd(units: MdUnit[]): string {
  return units.map((u) => u.md).join('\n\n');
}

/** Turn a lesson's blocks into slides (the player and the audit both call this). */
export function buildSlides(blocks: readonly Block[], limits: Partial<SlideLimits> = {}): Slide[] {
  const { maxWords } = { ...DEFAULT_LIMITS, ...limits };
  const slides: Slide[] = [];
  /** The prose slide still open for packing, if any. */
  let packing: Slide | null = null;
  /** Units of a notice waiting for the code slide that follows it. */
  let pending: { block: Block; units: MdUnit[] } | null = null;
  let previousCell: string | null = null;

  const visible = blocks.filter((b) => !b.tags.includes(SLIDE_SKIP));
  const cellOf = (b: Block) => b.key.split('#')[0]!;
  const breaksBefore = (b: Block, prevCell: string | null) =>
    b.tags.includes(SLIDE_BREAK) && cellOf(b) !== prevCell;

  const addPart = (slide: Slide, block: Block, units: MdUnit[]) => {
    const last = slide.parts[slide.parts.length - 1];
    if (last && last.kind === 'md' && last.key === block.key) {
      last.units.push(...units);
      last.md = joinMd(last.units);
    } else {
      slide.parts.push({ kind: 'md', key: block.key, type: block.type as ProseBlockType, units: [...units], md: joinMd(units) });
    }
    slide.words += units.reduce((n, u) => n + budgetWords(u), 0);
  };

  /** Pack units into prose (or notice) slides, starting a new slide when `fresh`. */
  const pack = (block: Block, units: MdUnit[], kind: 'prose' | 'notice', fresh: boolean) => {
    let current: Slide | null = fresh || packing === null || packing.kind !== kind ? null : packing;
    for (const unit of units) {
      const onlyHeadings = current !== null && current.parts.every((p) => p.kind === 'md' && p.units.every((u) => u.kind === 'heading'));
      const hasTable = current !== null && current.parts.some((p) => p.kind === 'md' && p.units.some((u) => u.kind === 'table'));
      const startNew =
        current === null ||
        (unit.kind === 'heading' && !onlyHeadings) ||
        (unit.kind === 'table' && hasTable) ||
        (!onlyHeadings && current.words + budgetWords(unit) > maxWords);
      if (startNew) {
        current = { kind, parts: [], words: 0 };
        slides.push(current);
      }
      addPart(current!, block, [unit]);
    }
    packing = current;
  };

  visible.forEach((block, i) => {
    const forced = breaksBefore(block, previousCell);
    previousCell = cellOf(block);
    if (forced) packing = null;

    if (PROSE_TYPES.has(block.type)) {
      const units = splitUnits(block.md ?? '');
      if (units.length === 0) return;
      if (block.type === 'notice') {
        packing = null;
        const words = units.reduce((n, u) => n + budgetWords(u), 0);
        const simple = units.every((u) => u.kind !== 'table' && u.kind !== 'heading');
        const last = slides[slides.length - 1];
        const prev = visible[i - 1];
        const prevIsCode = prev !== undefined && !PROSE_TYPES.has(prev.type);
        if (simple && !forced && prevIsCode && isCodeSlide(last) && last.words + words <= maxWords) {
          addPart(last, block, units);
          return;
        }
        const next = visible[i + 1];
        if (simple && next !== undefined && !PROSE_TYPES.has(next.type) && !breaksBefore(next, previousCell) &&
            codeWords(next) + words <= maxWords) {
          pending = { block, units };
          return;
        }
        pack(block, units, 'notice', true);
        packing = null;
        return;
      }
      pack(block, units, 'prose', forced || STARTS_SLIDE.has(block.type));
      return;
    }

    // A code-like block: one slide, carrying a notice that was waiting for it.
    const slide: Slide = { kind: slideKindOf(block.type), parts: [], words: 0 };
    if (pending) {
      addPart(slide, pending.block, pending.units);
      pending = null;
    }
    slide.parts.push({ kind: 'block', key: block.key, block });
    slide.words += codeWords(block);
    slides.push(slide);
    packing = null;
  });
  return slides;
}

/**
 * Each slide's identifier: the `item_key` of its `slide` progress event (plan 103 content review,
 * [sol] 2). A slide is named by its first block. A long block can be split across several
 * slides, each starting with that same block, so the first such slide keeps the plain block key
 * and the k-th (k >= 2) is `<block key>#slide-<k>`. Block keys never contain `#slide-`, and the
 * schema's `item_key` pattern allows any `#…` suffix, so the keys are distinct and schema-valid
 * without changing the schema; an unsplit block's slide keeps exactly its block key.
 */
export function slideKeys(slides: readonly Slide[]): string[] {
  const seen = new Map<string, number>();
  return slides.map((slide) => {
    const key = slide.parts[0]!.key;
    const ordinal = (seen.get(key) ?? 0) + 1;
    seen.set(key, ordinal);
    return ordinal === 1 ? key : `${key}#slide-${ordinal}`;
  });
}

// --- the audit ------------------------------------------------------------------------------

export interface AllowEntry {
  key: string;
  reason: string;
}

export interface SlideConfig extends SlideLimits {
  allow: AllowEntry[];
}

export type FindingKind = 'unit-words' | 'table-rows' | 'code-lines';

export interface Finding {
  kind: FindingKind;
  entry: string;
  /** The block key of the oversized unit or code block (the `slides.allow` key). */
  key: string;
  /** Words, rows or lines. */
  size: number;
  limit: number;
  /** The allow-list reason, when the finding is allow-listed. */
  allowed?: string;
}

export interface BandReport {
  entry: string;
  key: string;
  words: number;
}

export interface BookAudit {
  book: string;
  slides: number;
  /** Failure-limit findings, allow-listed or not. */
  findings: Finding[];
  /** Units between `maxWords` and `maxUnitWords` words: reported, never failing. */
  band: BandReport[];
  noticeSlides: number;
  /** Allow-list keys that match no finding (a stale entry fails the audit). */
  staleAllow: string[];
}

export interface AuditEntry {
  id: string;
  blocks: readonly Block[];
}

/** Audit one book's lessons against its limits and allow list. */
export function auditBook(book: string, entries: readonly AuditEntry[], config: SlideConfig): BookAudit {
  const allow = new Map(config.allow.map((a) => [a.key, a.reason]));
  const used = new Set<string>();
  const findings: Finding[] = [];
  const band: BandReport[] = [];
  let count = 0;
  let noticeSlides = 0;
  const find = (f: Omit<Finding, 'allowed'>) => {
    const reason = allow.get(f.key);
    if (reason !== undefined) used.add(f.key);
    findings.push(reason === undefined ? f : { ...f, allowed: reason });
  };
  for (const entry of entries) {
    const slides = buildSlides(entry.blocks, config);
    count += slides.length;
    for (const slide of slides) {
      if (slide.kind === 'notice') noticeSlides += 1;
      for (const part of slide.parts) {
        if (part.kind === 'block') {
          const lines = codeLines(part.block);
          if (lines > config.maxCodeLines) {
            find({ kind: 'code-lines', entry: entry.id, key: part.key, size: lines, limit: config.maxCodeLines });
          }
          continue;
        }
        for (const unit of part.units) {
          if (unit.kind === 'table') {
            if (unit.rows > config.maxTableRows) {
              find({ kind: 'table-rows', entry: entry.id, key: part.key, size: unit.rows, limit: config.maxTableRows });
            }
          } else if (unit.words > config.maxUnitWords) {
            find({ kind: 'unit-words', entry: entry.id, key: part.key, size: unit.words, limit: config.maxUnitWords });
          } else if (unit.words > config.maxWords) {
            band.push({ entry: entry.id, key: part.key, words: unit.words });
          }
        }
      }
    }
  }
  const staleAllow = config.allow.map((a) => a.key).filter((k) => !used.has(k));
  return { book, slides: count, findings, band, noticeSlides, staleAllow };
}

/** Whether a book's audit passes: no finding outside the allow list and no stale allow entry. */
export function auditPasses(audit: BookAudit): boolean {
  return audit.findings.every((f) => f.allowed !== undefined) && audit.staleAllow.length === 0;
}

const LABEL: Record<FindingKind, string> = {
  'unit-words': 'unit over max_unit_words',
  'table-rows': 'table over max_table_rows',
  'code-lines': 'code slide over max_code_lines',
};

/** The audit's human-readable report for one book. */
export function formatAudit(audit: BookAudit, config: SlideConfig): string[] {
  const failing = audit.findings.filter((f) => f.allowed === undefined);
  const allowed = audit.findings.filter((f) => f.allowed !== undefined);
  const out = [
    `slide-audit: ${audit.book}: ${audit.slides} slides; ${failing.length} failing, ${allowed.length} allow-listed; ` +
      `${audit.band.length} unit(s) between ${config.maxWords} and ${config.maxUnitWords} words (reported); ` +
      `${audit.noticeSlides} notice-only slide(s) (reported)`,
  ];
  for (const f of failing) out.push(`  FAIL ${LABEL[f.kind]} (${f.size} > ${f.limit}): ${f.key}`);
  for (const k of audit.staleAllow) out.push(`  FAIL slides.allow entry matches no oversized unit: ${k}`);
  for (const f of allowed) out.push(`  allowed ${LABEL[f.kind]} (${f.size} > ${f.limit}): ${f.key} — ${f.allowed}`);
  for (const b of audit.band) out.push(`  report: ${b.words} words (over the ${config.maxWords}-word packing budget): ${b.key}`);
  return out;
}

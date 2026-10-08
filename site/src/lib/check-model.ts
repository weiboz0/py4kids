/**
 * The practice checks' shared model (plan 104 Phase B): the shapes of the build-time projections
 * a check island fetches, and the pure rules both sides use (budgets, case order, verdicts,
 * progress-event kinds and the odd-answer gate). Dependency-free, so client islands import it
 * without the build-time Markdown pipeline; `checks.ts` builds the projections from the bundle.
 *
 * What a check needs and nothing more reaches the client, and only when Check is pressed:
 * - `answer`, `predict`, `expected-output`: the salted hash and the answer format (never the
 *   answer); the comparison is `answerHash` on the device.
 * - `asserts`: the shipped asserts, for the runner only (the island posts them to the runner and
 *   never puts them in the DOM).
 * - `fixtures`: each case's input and expected-output file URLs, fetched lazily per case; only the
 *   sample's input and expected output are ever shown.
 */

import type { Segment } from './types';

export type CheckKind = 'fixtures' | 'answer' | 'asserts' | 'expected-output' | 'predict' | 'self-check';
export type ItemKind = 'unit' | 'challenge' | 'checkpoint' | 'project';

/** How a typed answer (or a program's stdout) is normalised before hashing. */
export interface ClientFormat {
  case: 'sensitive' | 'insensitive';
  hint: string;
  whitespace?: 'collapse' | 'exact';
  aliases?: Record<string, string>;
}

/** A file mounted in the run's working directory: its mount path and its same-origin URL. */
export interface ClientFile {
  path: string;
  url: string;
}

export interface ClientCase {
  n: number;
  sample: boolean;
  /** Same-origin URLs of the case's `.in` and `.out` files. */
  input: string;
  expected: string;
  /** Too slow to run in the browser (the bundle's `over_budget`): listed, never run. */
  skipped: boolean;
}

interface Base {
  /** The item's global key (the hash salt and the progress key). */
  key: string;
  turtle: boolean;
}

export interface FixturesCheck extends Base {
  kind: 'fixtures';
  match: 'line' | 'token';
  /** Sample cases first, then the hidden ones, each in bundle order. */
  cases: ClientCase[];
  /** Every case's budget (plan 104 "Budgets"). */
  budget_ms: number;
  files: ClientFile[];
}

export interface AssertsCheck extends Base {
  kind: 'asserts';
  /** One statement per entry, run one at a time by the runner. Never rendered. */
  asserts: string[];
  budget_ms: number;
  files: ClientFile[];
}

export interface OutputCheck extends Base {
  kind: 'expected-output';
  hash: string;
  format: ClientFormat;
  budget_ms: number;
  files: ClientFile[];
}

export interface TypedCheck extends Base {
  kind: 'answer' | 'predict';
  hash: string;
  format: ClientFormat;
}

export interface SelfCheck extends Base {
  kind: 'self-check';
  budget_ms: number;
  files: ClientFile[];
}

export type ClientCheck = FixturesCheck | AssertsCheck | OutputCheck | TypedCheck | SelfCheck;

/** One drawing of an odd answer: its caption (plain text) and the drawing as inline SVG. */
export interface ClientFigure {
  caption: string;
  svg: string;
}

/** An odd unit item's answer, fetched only after a genuine attempt. */
export interface ClientAnswer {
  key: string;
  /** `answer_md` through the site's Markdown pipeline (`{=latex}` dropped). */
  html: string;
  /** Turtle drawings (`answer_figures`): each caption and its inline SVG. */
  figures: ClientFigure[];
}

/** One lesson block's run data (`/<book>/<entry>/run.json`). */
export interface RunBlock {
  code: string;
  /** Block keys to replay first, silently, when the session is new. */
  prelude: string[];
  stdin: boolean;
  sample_input: string;
  files: ClientFile[];
}

export interface LessonRun {
  /** The runner session: the entry id. */
  session: string;
  budget_ms: number;
  blocks: Record<string, RunBlock>;
}

export type { Segment };

// ---------------------------------------------------------------------------------------------
// Budgets (plan 104 "Budgets")

/** A run that is not a fixture case. */
export const DEFAULT_BUDGET_MS = 5000;
export const CASE_MIN_MS = 1000;
export const CASE_MAX_MS = 10_000;

/**
 * A fixture case's budget: max(1 s, 10x the reference solver's CPython time), capped at 10 s.
 * Schema 1.1.0 requires `cpu_ms`; the 5 s default only guards a malformed or missing value.
 */
export function caseBudget(cpuMs: number | undefined): number {
  if (cpuMs === undefined || !Number.isFinite(cpuMs) || cpuMs < 0) return DEFAULT_BUDGET_MS;
  return Math.min(CASE_MAX_MS, Math.max(CASE_MIN_MS, Math.round(cpuMs * 10)));
}

// ---------------------------------------------------------------------------------------------
// Verdicts and events

export type EventKind = 'exercise' | 'checkpoint' | 'project';
export type Outcome = 'pass' | 'fail' | 'partial' | 'error';

/** The D11 event kind of an item's check. */
export function eventKindOf(kind: ItemKind): EventKind {
  return kind === 'checkpoint' ? 'checkpoint' : kind === 'project' ? 'project' : 'exercise';
}

/** An item's result from its cases: all pass, none pass, or some (no case run: an error). */
export function outcomeOf(cases: { pass: boolean }[]): Outcome {
  if (cases.length === 0) return 'error';
  const passed = cases.filter((c) => c.pass).length;
  return passed === cases.length ? 'pass' : passed === 0 ? 'fail' : 'partial';
}

/** Sample cases first (bundle order kept within each group). */
export function orderCases<T extends { sample: boolean }>(cases: T[]): T[] {
  return [...cases.filter((c) => c.sample), ...cases.filter((c) => !c.sample)];
}

/** A runner verdict detail in words a student reads. */
export function verdictText(pass: boolean, detail: string): string {
  if (pass) return 'passed';
  if (detail === '' || detail === 'wrong output') return 'wrong output';
  return detail;
}

// ---------------------------------------------------------------------------------------------
// The odd-answer gate (plan 104 "Hidden answers stay hidden")

export interface AttemptHistory {
  /** Completed Check runs (any verdict, a failed one included). */
  checks: number;
  /** Submitted typed answers. */
  answers: number;
  /** Runs of the student's code from the item's editor. */
  runs: number;
  /** Every box of a self-check item's checklist ticked. */
  checklistDone: boolean;
}

export const NO_ATTEMPT: AttemptHistory = { checks: 0, answers: 0, runs: 0, checklistDone: false };

/**
 * Whether an item's answer may be shown. Only an item that ships an answer (an odd unit
 * exercise, `answer_visibility: after-attempt`) can unlock, and only after a genuine attempt:
 * a Check run or a submitted answer; for a self-check item, a Run plus the checklist marked done.
 */
export function answerUnlocked(item: { gated: boolean; kind: CheckKind }, history: AttemptHistory): boolean {
  if (!item.gated) return false;
  if (item.kind === 'self-check') return history.runs > 0 && history.checklistDone;
  return history.checks > 0 || history.answers > 0;
}

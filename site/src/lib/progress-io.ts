/**
 * "Export my progress" and "Import progress" (design 012 D11; plan 105 Phase C).
 *
 * The export file is one JSON object, `tools/export/schema/progress-export.schema.json`:
 *
 *     {schema: "py4kids/progress-export/1.0.0", exported_at, events, cards, resume, attempts?}
 *
 * - `events`: the D11 progress events (results only, never code);
 * - `cards`: the Leitner state per card key; `resume`: the last position per book;
 * - `attempts`: the attempt store (the student's own code and typed answers), present only when
 *   the student asks for it ("export my code attempts too"). By default code stays on the device.
 *
 * Import validates the file (size first, then JSON, then the `schema` id, then the whole schema)
 * and merges deterministically (`planMerge`):
 * - events and attempts: union by `event_id` / `attempt_id` (a local record is never rewritten);
 * - cards: per card key, the record with the later `updated_at`; a tie keeps the local record;
 * - resume: per book, the later `updated_at`; a tie keeps the local record.
 * A local record without `updated_at` (written before every record carried it) counts as the
 * oldest; when it is kept, it is written back with the epoch as its `updated_at`.
 * So importing the same file twice changes nothing after the first import, and importing an older
 * file never regresses newer local state.
 *
 * Like `validateEvent`, `validateExport` is a hand-written twin of the schema (the CSP forbids
 * Ajv in the browser); `site/test/progress-io.test.ts` proves the two agree. Every key the file
 * names is looked up as an own key only (`Object.hasOwn`, prototype-free rule maps), so a hostile
 * file with `__proto__`, `constructor` or `toString` keys is refused like any other unexpected key.
 */

import type { CardState } from './leitner';
import { validateEvent, type Attempt, type ProgressEvent, type ProgressStore, type ResumeState, type StoreRecords } from './progress';

export const EXPORT_SCHEMA = 'py4kids/progress-export/1.0.0';
/** The largest file "Import progress" reads: 20 MB. */
export const MAX_IMPORT_BYTES = 20 * 1024 * 1024;
/** The `updated_at` a legacy record without one is given: the oldest possible. */
export const EPOCH = '1970-01-01T00:00:00.000Z';

export interface ProgressExport {
  schema: typeof EXPORT_SCHEMA;
  exported_at: string;
  events: ProgressEvent[];
  cards: CardState[];
  resume: ResumeState[];
  attempts?: Attempt[];
}

// The schema's patterns, verbatim.
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const BOOK = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const KEY = /^[a-z0-9]+(-[a-z0-9]+)*\/[^/#\s]+\/[^/#\s]+\/[^/#\s]+(#\S+)?$/;
const TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$/;
const ENTRY = /^[^/#\s]+$/;
const HREF = /^\/([^/\\\s][^\\\s]*)?$/;
const ATTEMPT_KINDS = new Set(['check', 'answer', 'run']);
const RESULTS = new Set(['pass', 'fail', 'partial', 'done', 'seen', 'error']);

const isObject = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v);
const isStr = (v: unknown): v is string => typeof v === 'string';
const isInt = (v: unknown): v is number => typeof v === 'number' && Number.isInteger(v);
const matches = (re: RegExp) => (v: unknown) => isStr(v) && re.test(v);
const isTimestamp = matches(TIMESTAMP);
/** JSON Schema's `maxLength` counts code points, not UTF-16 units. */
const maxLength = (n: number) => (v: unknown) => isStr(v) && [...v].length <= n;

type Rules = Readonly<Record<string, (v: unknown) => boolean>>;

/**
 * The rules for one record's keys, in a map without a prototype: the keys looked up in it come
 * from the file, so `constructor`, `toString`, `__proto__` and the like must find nothing (and be
 * reported as unexpected), never `Object.prototype`'s members.
 */
const rules = (byKey: Record<string, (v: unknown) => boolean>): Rules => Object.freeze(Object.assign(Object.create(null) as Record<string, (v: unknown) => boolean>, byKey));

function checkRecord(path: string, value: unknown, required: string[], rules: Rules, errors: string[]): void {
  const here = path || '/';
  if (!isObject(value)) {
    errors.push(`${here}: must be an object`);
    return;
  }
  for (const key of required) if (!Object.hasOwn(value, key)) errors.push(`${here}: missing ${key}`);
  for (const key of Object.keys(value)) {
    const rule = Object.hasOwn(rules, key) ? rules[key] : undefined;
    if (!rule) errors.push(`${here}: unexpected ${key}`);
    else if (!rule(value[key])) errors.push(`${path}/${key}: invalid`);
  }
}

const CARD_RULES: Rules = rules({
  key: matches(KEY),
  book: matches(BOOK),
  box: (v) => isInt(v) && v >= 1 && v <= 5,
  due: isTimestamp,
  updated_at: isTimestamp,
});
const RESUME_RULES: Rules = rules({
  book: matches(BOOK),
  entry: matches(ENTRY),
  href: (v) => matches(HREF)(v) && maxLength(2000)(v),
  title: maxLength(500),
  updated_at: isTimestamp,
});
const ATTEMPT_RULES: Rules = rules({
  attempt_id: matches(UUID),
  book: matches(BOOK),
  item_key: matches(KEY),
  kind: (v) => isStr(v) && ATTEMPT_KINDS.has(v),
  code: isStr,
  answer: isStr,
  result: (v) => isStr(v) && RESULTS.has(v),
  timestamp: isTimestamp,
});
const TOP_RULES: Rules = rules({
  schema: (v) => v === EXPORT_SCHEMA,
  exported_at: isTimestamp,
  events: Array.isArray,
  cards: Array.isArray,
  resume: Array.isArray,
  attempts: Array.isArray,
});

/** Every way `data` breaks the progress-export schema; empty when it is valid. */
export function validateExport(data: unknown): string[] {
  const errors: string[] = [];
  checkRecord('', data, ['schema', 'exported_at', 'events', 'cards', 'resume'], TOP_RULES, errors);
  if (!isObject(data)) return errors;
  const each = (name: string, check: (item: unknown, path: string) => void) => {
    const list = Object.hasOwn(data, name) ? data[name] : undefined;
    if (Array.isArray(list)) list.forEach((item, i) => check(item, `/${name}/${i}`));
  };
  each('events', (item, path) => {
    for (const error of validateEvent(item)) errors.push(`${path}${error}`);
  });
  each('cards', (item, path) => checkRecord(path, item, ['key', 'book', 'box', 'due', 'updated_at'], CARD_RULES, errors));
  each('resume', (item, path) => checkRecord(path, item, ['book', 'entry', 'href', 'title', 'updated_at'], RESUME_RULES, errors));
  each('attempts', (item, path) =>
    checkRecord(path, item, ['attempt_id', 'book', 'item_key', 'kind', 'result', 'timestamp'], ATTEMPT_RULES, errors),
  );
  return errors;
}

/** Why an import was refused; `message` is written for a student. */
export class ImportError extends Error {
  constructor(
    public readonly reason: 'too-big' | 'not-json' | 'unknown-schema' | 'invalid' | 'empty',
    message: string,
    public readonly details: string[] = [],
  ) {
    super(message);
    this.name = 'ImportError';
  }
}

const NOTHING_CHANGED = 'Nothing was changed.';

/**
 * Reads and validates an export file's text. `size` is the file's size in bytes (checked before
 * the text is read, by `readImportFile`; checked again here on the text itself).
 */
export function parseExport(text: string, size: number = new TextEncoder().encode(text).length): ProgressExport {
  if (size > MAX_IMPORT_BYTES) {
    throw new ImportError('too-big', `That file is too big to be a py4kids progress file (the limit is 20 MB). ${NOTHING_CHANGED}`);
  }
  if (size === 0 || text.trim() === '') {
    throw new ImportError('empty', `That file is empty, so there is no progress in it to bring back. ${NOTHING_CHANGED}`);
  }
  let data: unknown;
  try {
    data = JSON.parse(text);
  } catch {
    throw new ImportError(
      'not-json',
      `That file is not a py4kids progress file, or it got damaged. Choose the file that "Export my progress" saved. ${NOTHING_CHANGED}`,
    );
  }
  if (!isObject(data) || !Object.hasOwn(data, 'schema')) {
    throw new ImportError(
      'invalid',
      `That file is not a py4kids progress file. Choose the file that "Export my progress" saved. ${NOTHING_CHANGED}`,
    );
  }
  if (data.schema !== EXPORT_SCHEMA) {
    throw new ImportError(
      'unknown-schema',
      `That progress file comes from a different version of py4kids, so this page cannot read it. ${NOTHING_CHANGED}`,
    );
  }
  const errors = validateExport(data);
  if (errors.length > 0) {
    throw new ImportError(
      'invalid',
      `That progress file has something wrong inside it (it may have been edited or damaged), so it was not used. ${NOTHING_CHANGED}`,
      errors,
    );
  }
  return data as unknown as ProgressExport;
}

/** Reads a chosen `File` (or `Blob`), refusing one over the size limit before reading it. */
export async function readImportFile(file: Blob): Promise<ProgressExport> {
  if (file.size > MAX_IMPORT_BYTES) return parseExport('', file.size);
  return parseExport(await file.text(), file.size);
}

/** A record's `updated_at` in ms; a missing or unreadable one counts as the oldest. */
export function stamp(record: { updated_at?: unknown } | undefined): number {
  const at = record?.updated_at;
  const ms = typeof at === 'string' ? Date.parse(at) : Number.NaN;
  return Number.isNaN(ms) ? Number.NEGATIVE_INFINITY : ms;
}

const withStamp = <T extends { updated_at?: string }>(record: T): T & { updated_at: string } =>
  typeof record.updated_at === 'string' ? (record as T & { updated_at: string }) : { ...record, updated_at: EPOCH };

/** Of two records for the same key, the later; a tie (or two unreadable stamps) keeps `local`. */
function later<T extends { updated_at?: string }>(local: T | undefined, incoming: T): { winner: T; incoming: boolean } {
  if (local === undefined || stamp(incoming) > stamp(local)) return { winner: incoming, incoming: true };
  return { winner: local, incoming: false };
}

export type MergePlan = StoreRecords;

export interface MergeSummary {
  events: number;
  cards: number;
  resume: number;
  attempts: number;
}

/**
 * What an import writes: only the records that change the store. `local` is the store's current
 * records (`ProgressStore.records`); the file's own duplicates resolve by the same rules.
 */
export function planMerge(local: StoreRecords, incoming: ProgressExport): MergePlan {
  const eventIds = new Set(local.events.map((e) => e.event_id));
  const events: ProgressEvent[] = [];
  for (const event of incoming.events) {
    if (eventIds.has(event.event_id)) continue;
    eventIds.add(event.event_id);
    events.push(event);
  }

  const attemptIds = new Set(local.attempts.map((a) => a.attempt_id));
  const attempts: Attempt[] = [];
  for (const attempt of incoming.attempts ?? []) {
    if (attemptIds.has(attempt.attempt_id)) continue;
    attemptIds.add(attempt.attempt_id);
    attempts.push(attempt);
  }

  const cards = mergeKeyed(local.cards, incoming.cards, (c) => c.key);
  const resume = mergeKeyed(local.resume, incoming.resume, (r) => r.book);
  return { events, cards, resume, attempts };
}

/**
 * Per key, the later record. A record is written when the file's one wins, or when the local one
 * wins but lacks `updated_at` (it gains the epoch, so every stored record carries one).
 */
function mergeKeyed<T extends { updated_at?: string }>(local: T[], incoming: T[], keyOf: (r: T) => string): T[] {
  const mine = new Map(local.map((r) => [keyOf(r), r]));
  const best = new Map<string, { record: T; incoming: boolean }>();
  for (const record of incoming) {
    const key = keyOf(record);
    const current = best.get(key);
    const base = current?.record ?? mine.get(key);
    const { winner, incoming: won } = later(base, record);
    best.set(key, { record: winner, incoming: won || (current?.incoming ?? false) });
  }
  const out: T[] = [];
  for (const [key, { record, incoming: won }] of [...best].sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))) {
    if (won) out.push(withStamp(record));
    else if (typeof mine.get(key)?.updated_at !== 'string') out.push(withStamp(record));
  }
  return out;
}

const byEvent = (a: ProgressEvent, b: ProgressEvent) => a.timestamp.localeCompare(b.timestamp) || a.event_id.localeCompare(b.event_id);
const byKey = <T>(keyOf: (r: T) => string) => (a: T, b: T) => (keyOf(a) < keyOf(b) ? -1 : keyOf(a) > keyOf(b) ? 1 : 0);

/**
 * The export file's object, from the store's records: sorted for a stable file, and every card
 * and resume record given `updated_at` (the epoch for a legacy record).
 */
export function buildExport(records: StoreRecords, options: { attempts?: boolean } = {}, now: Date = new Date()): ProgressExport {
  const out: ProgressExport = {
    schema: EXPORT_SCHEMA,
    exported_at: now.toISOString(),
    events: [...records.events].sort(byEvent),
    cards: records.cards.map(withStamp).sort(byKey((c) => c.key)),
    resume: records.resume.map(withStamp).sort(byKey((r) => r.book)),
  };
  if (options.attempts) {
    out.attempts = [...records.attempts].sort((a, b) => a.timestamp.localeCompare(b.timestamp) || a.attempt_id.localeCompare(b.attempt_id));
  }
  return out;
}

/** The store's export, as the file's text. */
export async function exportProgress(store: ProgressStore, options: { attempts?: boolean } = {}, now: Date = new Date()): Promise<string> {
  const data = buildExport(await store.records(options), options, now);
  const errors = validateExport(data);
  if (errors.length > 0) throw new Error(`the export does not match its schema: ${errors.slice(0, 5).join('; ')}`);
  return `${JSON.stringify(data, null, 1)}\n`;
}

/** The suggested file name: `py4kids-progress-2026-10-08.json` (with attempts: `…-and-code-…`). */
export function exportFileName(options: { attempts?: boolean } = {}, now: Date = new Date()): string {
  return `py4kids-progress${options.attempts ? '-and-code' : ''}-${now.toISOString().slice(0, 10)}.json`;
}

/** Validates and merges an export into the store; returns how many records it added or replaced. */
export async function importProgress(store: ProgressStore, data: ProgressExport): Promise<MergeSummary> {
  const local = await store.records({ attempts: (data.attempts?.length ?? 0) > 0 });
  const plan = planMerge(local, data);
  const summary = { events: plan.events.length, cards: plan.cards.length, resume: plan.resume.length, attempts: plan.attempts.length };
  if (summary.events + summary.cards + summary.resume + summary.attempts > 0) await store.putRecords(plan);
  return summary;
}

/**
 * The on-device progress store (design 012 D9, D11; plan 103 Architecture "Progress").
 *
 * IndexedDB database `py4kids`, with no identifiers and nothing sent anywhere:
 * - `events`: D11 progress events, each validated against
 *   `tools/export/schema/progress-event.schema.json` before it is written (UUID `event_id`,
 *   UTC `Z` timestamps). Part B writes `slide`, `card` and `self-check` events; part C (plan 104)
 *   adds `lesson-run` (a Run in the reading view) and `exercise`, `checkpoint` and `project`
 *   (a Check, with `detail.cases`). An event holds results only, never code or a typed answer.
 * - `cards`: the Leitner state per card key (box 1..5, due date, updated_at). Every record stores
 *   `updated_at` (plan 105 Phase C: the import merge keeps the later one); a legacy record without
 *   it counts as the oldest (`progress-io.ts`).
 * - `resume`: the last position per book (updated_at).
 * - `attempts` (plan 104, version 2): the student's own work, on this device only: the code of each
 *   Run and Check and each typed answer, with its outcome. It is never put in an event; it
 *   restores the editor and records the genuine attempt that unlocks an odd exercise's answer.
 *
 * When IndexedDB is unavailable (a private window, blocked site data), `openProgress` returns an
 * in-memory store with `persistent: false`: the site keeps working for the visit without saving,
 * and the page says so once (see `onceUnsaved`).
 *
 * The browser cannot run Ajv (it compiles validators with `new Function`, which the CSP forbids),
 * so `validateEvent` is a hand-written twin of the schema; `site/test/progress.test.ts` proves it
 * agrees with Ajv on valid and mutated events.
 */

import { review, type CardState } from './leitner';

export const DB_NAME = 'py4kids';
export const DB_VERSION = 2;
export const EVENT_SCHEMA = 'py4kids/progress-event/1.0.0';

export type EventKind = 'lesson-run' | 'slide' | 'card' | 'exercise' | 'checkpoint' | 'project' | 'self-check';
export type EventResult = 'pass' | 'fail' | 'partial' | 'done' | 'seen' | 'error';
/** The kinds part B writes. */
export type PartBKind = 'slide' | 'card' | 'self-check';
/** The kinds part C (plan 104) adds. */
export type PartCKind = 'lesson-run' | 'exercise' | 'checkpoint' | 'project';

export interface EventDetail {
  cases?: { n: number; pass: boolean }[];
  self_grade?: 'got-it' | 'not-yet';
  box?: number;
  checklist?: boolean[];
}

export interface ProgressEvent {
  schema: typeof EVENT_SCHEMA;
  event_id: string;
  book: string;
  item_key: string;
  kind: EventKind;
  result: EventResult;
  detail: EventDetail;
  duration_ms: number;
  timestamp: string;
  content_hash: string;
}

export interface EventInput {
  item_key: string;
  kind: PartBKind | PartCKind;
  result: EventResult;
  detail?: EventDetail;
  duration_ms?: number;
  /** The bundle's `release.content_hash`. */
  content_hash: string;
}

/** One attempt at an item, kept on this device only (the `attempts` store). */
export interface Attempt {
  attempt_id: string;
  book: string;
  item_key: string;
  /** `check`: a Check run; `answer`: a submitted typed answer; `run`: a Run of the item's code. */
  kind: 'check' | 'answer' | 'run';
  /** The student's code (Run, Check). */
  code?: string;
  /** The typed answer. */
  answer?: string;
  result: EventResult;
  timestamp: string;
}

export type AttemptInput = Omit<Attempt, 'attempt_id' | 'book' | 'timestamp'>;

export interface ResumeState {
  book: string;
  /** The entry id. */
  entry: string;
  /** A same-site path (with an optional `#slide` hash). */
  href: string;
  title: string;
  updated_at: string;
}

// The schema's patterns, verbatim.
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const BOOK = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const ITEM_KEY = /^[a-z0-9]+(-[a-z0-9]+)*\/[^/#\s]+\/[^/#\s]+\/[^/#\s]+(#\S+)?$/;
const TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$/;
const SHA256 = /^sha256:[0-9a-f]{64}$/;
const KINDS = new Set<string>(['lesson-run', 'slide', 'card', 'exercise', 'checkpoint', 'project', 'self-check']);
const RESULTS = new Set<string>(['pass', 'fail', 'partial', 'done', 'seen', 'error']);
const EVENT_KEYS = new Set(['schema', 'event_id', 'book', 'item_key', 'kind', 'result', 'detail', 'duration_ms', 'timestamp', 'content_hash']);
const DETAIL_KEYS = new Set(['cases', 'self_grade', 'box', 'checklist']);

const isObject = (v: unknown): v is Record<string, unknown> => typeof v === 'object' && v !== null && !Array.isArray(v);
const isInt = (v: unknown): v is number => typeof v === 'number' && Number.isInteger(v);
const isStr = (v: unknown): v is string => typeof v === 'string';

/** Every way `event` breaks the progress-event schema; empty when it is valid. */
export function validateEvent(event: unknown): string[] {
  if (!isObject(event)) return ['/: must be an object'];
  const errors: string[] = [];
  // Own keys only: the event may come from an imported file (plan 105 Phase C).
  const has = (o: object, key: string) => Object.hasOwn(o, key);
  for (const key of EVENT_KEYS) if (!has(event, key)) errors.push(`/: missing ${key}`);
  for (const key of Object.keys(event)) if (!EVENT_KEYS.has(key)) errors.push(`/: unexpected ${key}`);
  const check = (key: string, ok: (v: unknown) => boolean) => {
    if (has(event, key) && !ok(event[key])) errors.push(`/${key}: invalid`);
  };
  check('schema', (v) => v === EVENT_SCHEMA);
  check('event_id', (v) => isStr(v) && UUID.test(v));
  check('book', (v) => isStr(v) && BOOK.test(v));
  check('item_key', (v) => isStr(v) && ITEM_KEY.test(v));
  check('kind', (v) => isStr(v) && KINDS.has(v));
  check('result', (v) => isStr(v) && RESULTS.has(v));
  check('duration_ms', (v) => isInt(v) && v >= 0);
  check('timestamp', (v) => isStr(v) && TIMESTAMP.test(v));
  check('content_hash', (v) => isStr(v) && SHA256.test(v));
  const detail = has(event, 'detail') ? event.detail : undefined;
  if (has(event, 'detail')) {
    if (!isObject(detail)) errors.push('/detail: must be an object');
    else {
      for (const key of Object.keys(detail)) if (!DETAIL_KEYS.has(key)) errors.push(`/detail: unexpected ${key}`);
      if (has(detail, 'cases')) {
        const cases = detail.cases;
        const okCase = (c: unknown) =>
          isObject(c) && isInt(c.n) && c.n >= 1 && typeof c.pass === 'boolean' && Object.keys(c).every((k) => k === 'n' || k === 'pass');
        if (!Array.isArray(cases) || !cases.every(okCase)) errors.push('/detail/cases: invalid');
      }
      if (has(detail, 'self_grade') && detail.self_grade !== 'got-it' && detail.self_grade !== 'not-yet') errors.push('/detail/self_grade: invalid');
      if (has(detail, 'box') && !(isInt(detail.box) && detail.box >= 0)) errors.push('/detail/box: invalid');
      if (has(detail, 'checklist') && !(Array.isArray(detail.checklist) && detail.checklist.every((b) => typeof b === 'boolean'))) {
        errors.push('/detail/checklist: invalid');
      }
    }
  }
  return errors;
}

export class InvalidEventError extends Error {
  constructor(public readonly errors: string[]) {
    super(`invalid progress event: ${errors.join('; ')}`);
    this.name = 'InvalidEventError';
  }
}

/** A random (version 4) UUID; `crypto.randomUUID` needs a secure context, so fall back. */
export function uuid(): string {
  const c = globalThis.crypto;
  if (typeof c.randomUUID === 'function') return c.randomUUID();
  const b = c.getRandomValues(new Uint8Array(16));
  b[6] = (b[6]! & 0x0f) | 0x40;
  b[8] = (b[8]! & 0x3f) | 0x80;
  const h = [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}

/** The book id is the item key's first segment. */
export const bookOfKey = (key: string): string => key.split('/')[0] ?? '';

/** A complete, validated event from its input. Throws `InvalidEventError`. */
export function makeEvent(input: EventInput, now: Date = new Date()): ProgressEvent {
  const event: ProgressEvent = {
    schema: EVENT_SCHEMA,
    event_id: uuid(),
    book: bookOfKey(input.item_key),
    item_key: input.item_key,
    kind: input.kind,
    result: input.result,
    detail: input.detail ?? {},
    duration_ms: Math.max(0, Math.round(input.duration_ms ?? 0)),
    timestamp: now.toISOString(),
    content_hash: input.content_hash,
  };
  const errors = validateEvent(event);
  if (errors.length > 0) throw new InvalidEventError(errors);
  return event;
}

export interface ProgressStore {
  /** False when IndexedDB is unavailable: everything works for this visit, nothing is saved. */
  readonly persistent: boolean;
  addEvent(input: EventInput, now?: Date): Promise<ProgressEvent>;
  /** Events, oldest first; optionally only one item's. */
  events(itemKey?: string): Promise<ProgressEvent[]>;
  /** The newest event for an item (and kind, if given). */
  latestEvent(itemKey: string, kind?: EventKind): Promise<ProgressEvent | undefined>;
  getCard(key: string): Promise<CardState | undefined>;
  /** One book's card states, by card key. */
  cards(book: string): Promise<Map<string, CardState>>;
  putCard(state: CardState): Promise<void>;
  getResume(book: string): Promise<ResumeState | undefined>;
  setResume(state: Omit<ResumeState, 'updated_at'>, now?: Date): Promise<ResumeState>;
  addAttempt(input: AttemptInput, now?: Date): Promise<Attempt>;
  /** One item's attempts, oldest first. */
  attempts(itemKey: string): Promise<Attempt[]>;
  /**
   * Every record, for "Export my progress" (plan 105 Phase C); the attempt store only when asked
   * (`attempts` is empty otherwise). Records are returned as stored: a legacy card or resume
   * record may lack `updated_at`.
   */
  records(options?: { attempts?: boolean }): Promise<StoreRecords>;
  /** Writes an import's merge result (`progress-io.ts` `planMerge`), all in one transaction. */
  putRecords(records: StoreRecords): Promise<void>;
}

/** The store's four kinds of record, in bulk (export and import, plan 105 Phase C). */
export interface StoreRecords {
  events: ProgressEvent[];
  cards: CardState[];
  resume: ResumeState[];
  attempts: Attempt[];
}

const byAttemptTime = (a: Attempt, b: Attempt) => a.timestamp.localeCompare(b.timestamp);

function makeAttempt(input: AttemptInput, now: Date): Attempt {
  if (!ITEM_KEY.test(input.item_key)) throw new Error(`not an item key: ${input.item_key}`);
  return { ...input, attempt_id: uuid(), book: bookOfKey(input.item_key), timestamp: now.toISOString() };
}

const byTime = (a: ProgressEvent, b: ProgressEvent) => a.timestamp.localeCompare(b.timestamp);

/** The in-memory store used when IndexedDB is unavailable (and the base of nothing else). */
export class MemoryProgress implements ProgressStore {
  readonly persistent = false;
  private log: ProgressEvent[] = [];
  private cardMap = new Map<string, CardState>();
  private resumeMap = new Map<string, ResumeState>();
  private attemptLog: Attempt[] = [];

  async addEvent(input: EventInput, now?: Date): Promise<ProgressEvent> {
    const event = makeEvent(input, now);
    this.log.push(event);
    return event;
  }
  async events(itemKey?: string): Promise<ProgressEvent[]> {
    return this.log.filter((e) => itemKey === undefined || e.item_key === itemKey).sort(byTime);
  }
  async latestEvent(itemKey: string, kind?: EventKind): Promise<ProgressEvent | undefined> {
    return (await this.events(itemKey)).filter((e) => kind === undefined || e.kind === kind).pop();
  }
  async getCard(key: string): Promise<CardState | undefined> {
    return this.cardMap.get(key);
  }
  async cards(book: string): Promise<Map<string, CardState>> {
    return new Map([...this.cardMap].filter(([, s]) => s.book === book));
  }
  async putCard(state: CardState): Promise<void> {
    this.cardMap.set(state.key, { ...state });
  }
  async getResume(book: string): Promise<ResumeState | undefined> {
    return this.resumeMap.get(book);
  }
  async setResume(state: Omit<ResumeState, 'updated_at'>, now: Date = new Date()): Promise<ResumeState> {
    const full = { ...state, updated_at: now.toISOString() };
    this.resumeMap.set(state.book, full);
    return full;
  }
  async addAttempt(input: AttemptInput, now: Date = new Date()): Promise<Attempt> {
    const attempt = makeAttempt(input, now);
    this.attemptLog.push(attempt);
    return attempt;
  }
  async attempts(itemKey: string): Promise<Attempt[]> {
    return this.attemptLog.filter((a) => a.item_key === itemKey).sort(byAttemptTime);
  }
  async records(options: { attempts?: boolean } = {}): Promise<StoreRecords> {
    return {
      events: this.log.map((e) => structuredClone(e)),
      cards: [...this.cardMap.values()].map((c) => ({ ...c })),
      resume: [...this.resumeMap.values()].map((r) => ({ ...r })),
      attempts: options.attempts ? this.attemptLog.map((a) => ({ ...a })) : [],
    };
  }
  async putRecords(records: StoreRecords): Promise<void> {
    for (const event of records.events) {
      if (!this.log.some((e) => e.event_id === event.event_id)) this.log.push(structuredClone(event));
    }
    for (const card of records.cards) this.cardMap.set(card.key, { ...card });
    for (const resume of records.resume) this.resumeMap.set(resume.book, { ...resume });
    for (const attempt of records.attempts) {
      if (!this.attemptLog.some((a) => a.attempt_id === attempt.attempt_id)) this.attemptLog.push({ ...attempt });
    }
  }
}

const request = <T>(req: IDBRequest<T>): Promise<T> =>
  new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error ?? new Error('IndexedDB request failed'));
  });

const done = (tx: IDBTransaction): Promise<void> =>
  new Promise((resolve, reject) => {
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error ?? new Error('IndexedDB transaction failed'));
    tx.onabort = () => reject(tx.error ?? new Error('IndexedDB transaction aborted'));
  });

export class IdbProgress implements ProgressStore {
  readonly persistent = true;
  constructor(private readonly db: IDBDatabase) {
    // Another tab upgrading the database: let it (this page keeps its open transactions).
    db.onversionchange = () => db.close();
  }

  private async write(store: string, value: unknown): Promise<void> {
    const tx = this.db.transaction(store, 'readwrite');
    tx.objectStore(store).put(value);
    await done(tx);
  }
  private read<T>(store: string, run: (s: IDBObjectStore) => IDBRequest<T>): Promise<T> {
    return request(run(this.db.transaction(store, 'readonly').objectStore(store)));
  }

  async addEvent(input: EventInput, now?: Date): Promise<ProgressEvent> {
    const event = makeEvent(input, now);
    await this.write('events', event);
    return event;
  }
  async events(itemKey?: string): Promise<ProgressEvent[]> {
    const all = await this.read<ProgressEvent[]>('events', (s) =>
      itemKey === undefined ? s.getAll() : s.index('item_key').getAll(itemKey),
    );
    return all.sort(byTime);
  }
  async latestEvent(itemKey: string, kind?: EventKind): Promise<ProgressEvent | undefined> {
    return (await this.events(itemKey)).filter((e) => kind === undefined || e.kind === kind).pop();
  }
  async getCard(key: string): Promise<CardState | undefined> {
    return this.read<CardState | undefined>('cards', (s) => s.get(key));
  }
  async cards(book: string): Promise<Map<string, CardState>> {
    const all = await this.read<CardState[]>('cards', (s) => s.index('book').getAll(book));
    return new Map(all.map((s) => [s.key, s]));
  }
  async putCard(state: CardState): Promise<void> {
    await this.write('cards', state);
  }
  async getResume(book: string): Promise<ResumeState | undefined> {
    return this.read<ResumeState | undefined>('resume', (s) => s.get(book));
  }
  async setResume(state: Omit<ResumeState, 'updated_at'>, now: Date = new Date()): Promise<ResumeState> {
    const full = { ...state, updated_at: now.toISOString() };
    await this.write('resume', full);
    return full;
  }
  async addAttempt(input: AttemptInput, now: Date = new Date()): Promise<Attempt> {
    const attempt = makeAttempt(input, now);
    await this.write('attempts', attempt);
    return attempt;
  }
  async attempts(itemKey: string): Promise<Attempt[]> {
    const all = await this.read<Attempt[]>('attempts', (s) => s.index('item_key').getAll(itemKey));
    return all.sort(byAttemptTime);
  }
  async records(options: { attempts?: boolean } = {}): Promise<StoreRecords> {
    const names = options.attempts ? ['events', 'cards', 'resume', 'attempts'] : ['events', 'cards', 'resume'];
    // One read-only transaction: a consistent snapshot of every store.
    const tx = this.db.transaction(names, 'readonly');
    const all = (name: string) => request(tx.objectStore(name).getAll());
    const [events, cards, resume, attempts] = await Promise.all([
      all('events') as Promise<ProgressEvent[]>,
      all('cards') as Promise<CardState[]>,
      all('resume') as Promise<ResumeState[]>,
      options.attempts ? (all('attempts') as Promise<Attempt[]>) : Promise.resolve([] as Attempt[]),
    ]);
    return { events, cards, resume, attempts };
  }
  async putRecords(records: StoreRecords): Promise<void> {
    const tx = this.db.transaction(['events', 'cards', 'resume', 'attempts'], 'readwrite');
    for (const event of records.events) tx.objectStore('events').put(event);
    for (const card of records.cards) tx.objectStore('cards').put(card);
    for (const resume of records.resume) tx.objectStore('resume').put(resume);
    for (const attempt of records.attempts) tx.objectStore('attempts').put(attempt);
    await done(tx);
  }
}

function upgrade(db: IDBDatabase): void {
  if (!db.objectStoreNames.contains('events')) {
    const events = db.createObjectStore('events', { keyPath: 'event_id' });
    events.createIndex('item_key', 'item_key');
    events.createIndex('book', 'book');
  }
  if (!db.objectStoreNames.contains('cards')) db.createObjectStore('cards', { keyPath: 'key' }).createIndex('book', 'book');
  if (!db.objectStoreNames.contains('resume')) db.createObjectStore('resume', { keyPath: 'book' });
  // Version 2 (plan 104): the on-device attempt store.
  if (!db.objectStoreNames.contains('attempts')) db.createObjectStore('attempts', { keyPath: 'attempt_id' }).createIndex('item_key', 'item_key');
}

export interface OpenOptions {
  /** Defaults to `globalThis.indexedDB`; `null` forces the in-memory fallback. */
  indexedDB?: IDBFactory | null;
  name?: string;
}

/** Opens the store, falling back to memory when IndexedDB is missing or refuses to open. */
export async function openProgress(options: OpenOptions = {}): Promise<ProgressStore> {
  let factory: IDBFactory | null | undefined;
  try {
    factory = options.indexedDB === undefined ? globalThis.indexedDB : options.indexedDB;
  } catch {
    factory = null; // some browsers throw on access when site data is blocked
  }
  if (!factory) return new MemoryProgress();
  try {
    const req = factory.open(options.name ?? DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => upgrade(req.result);
    const db = await request(req);
    return new IdbProgress(db);
  } catch {
    return new MemoryProgress();
  }
}

let shared: Promise<ProgressStore> | undefined;

/** The page's one store (every island on a page shares it). */
export function sharedProgress(options?: OpenOptions): Promise<ProgressStore> {
  shared ??= openProgress(options);
  return shared;
}

/** Test hook: forget the page's store. */
export function resetSharedProgress(): void {
  shared = undefined;
}

let warned = false;

/**
 * Calls `show` the first time it is given a store that cannot save, and never again on this
 * page; `remember` (sessionStorage when it works) keeps it to once per visit across pages.
 */
export function onceUnsaved(
  store: ProgressStore,
  show: () => void,
  remember?: { get(): boolean; set(): void },
): boolean {
  if (store.persistent || warned) return false;
  warned = true;
  if (remember?.get()) return false;
  remember?.set();
  show();
  return true;
}

/** Test hook: allow the notice again. */
export function resetUnsavedNotice(): void {
  warned = false;
}

/**
 * One card review: the new Leitner state and a `card` event carrying the new box (and the
 * self-grade for flip cards); `pass`/`fail` follows `correct`. A correct answer on a card that
 * is not due yet is still recorded, but keeps its box (`leitner.review`). The event is validated and
 * written first, so an invalid one leaves the card state untouched.
 */
export async function recordCardReview(
  store: ProgressStore,
  card: { key: string; book: string },
  correct: boolean,
  options: { content_hash: string; self_grade?: 'got-it' | 'not-yet'; duration_ms?: number },
  now: Date = new Date(),
): Promise<{ state: CardState; event: ProgressEvent }> {
  const state = review(await store.getCard(card.key), card, correct, now);
  const detail: EventDetail = { box: state.box };
  if (options.self_grade) detail.self_grade = options.self_grade;
  const event = await store.addEvent(
    {
      item_key: card.key,
      kind: 'card',
      result: correct ? 'pass' : 'fail',
      detail,
      duration_ms: options.duration_ms ?? 0,
      content_hash: options.content_hash,
    },
    now,
  );
  await store.putCard(state);
  return { state, event };
}

/** A self-check item's checklist: `done` when every box is ticked, else `partial`. */
export function recordChecklist(
  store: ProgressStore,
  itemKey: string,
  checklist: boolean[],
  contentHash: string,
  now: Date = new Date(),
): Promise<ProgressEvent> {
  const result = checklist.length > 0 && checklist.every(Boolean) ? 'done' : 'partial';
  return store.addEvent({ item_key: itemKey, kind: 'self-check', result, detail: { checklist }, content_hash: contentHash }, now);
}

/** One slide viewed, keyed by the slide's identifier (`slides.ts` `slideKeys`). */
export function recordSlide(store: ProgressStore, slideKey: string, contentHash: string, now: Date = new Date()): Promise<ProgressEvent> {
  return store.addEvent({ item_key: slideKey, kind: 'slide', result: 'seen', content_hash: contentHash }, now);
}

/** One Check of an item: an `exercise`, `checkpoint` or `project` event with its cases' results. */
export function recordCheck(
  store: ProgressStore,
  input: {
    item_key: string;
    kind: 'exercise' | 'checkpoint' | 'project';
    result: EventResult;
    cases: { n: number; pass: boolean }[];
    duration_ms: number;
    content_hash: string;
  },
  now: Date = new Date(),
): Promise<ProgressEvent> {
  const detail: EventDetail = input.cases.length > 0 ? { cases: input.cases.map((c) => ({ n: c.n, pass: c.pass })) } : {};
  return store.addEvent(
    { item_key: input.item_key, kind: input.kind, result: input.result, detail, duration_ms: input.duration_ms, content_hash: input.content_hash },
    now,
  );
}

/** One Run of a lesson block: `pass` when it ran to the end, `error` otherwise. */
export function recordLessonRun(
  store: ProgressStore,
  blockKey: string,
  ok: boolean,
  durationMs: number,
  contentHash: string,
  now: Date = new Date(),
): Promise<ProgressEvent> {
  return store.addEvent(
    { item_key: blockKey, kind: 'lesson-run', result: ok ? 'pass' : 'error', duration_ms: durationMs, content_hash: contentHash },
    now,
  );
}

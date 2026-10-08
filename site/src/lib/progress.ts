/**
 * The on-device progress store (design 012 D9, D11; plan 103 Architecture "Progress").
 *
 * IndexedDB database `py4kids`, with no identifiers and nothing sent anywhere:
 * - `events`: D11 progress events, each validated against
 *   `tools/export/schema/progress-event.schema.json` before it is written (UUID `event_id`,
 *   UTC `Z` timestamps). Part B writes `slide`, `card` and `self-check` events only; reading
 *   position lives in `resume`, so no `lesson-run` event is ever written here.
 * - `cards`: the Leitner state per card key (box 1..5, due date, updated_at).
 * - `resume`: the last position per book (updated_at).
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
export const DB_VERSION = 1;
export const EVENT_SCHEMA = 'py4kids/progress-event/1.0.0';

export type EventKind = 'lesson-run' | 'slide' | 'card' | 'exercise' | 'checkpoint' | 'project' | 'self-check';
export type EventResult = 'pass' | 'fail' | 'partial' | 'done' | 'seen' | 'error';
/** The kinds part B writes. */
export type PartBKind = 'slide' | 'card' | 'self-check';

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
  kind: PartBKind;
  result: EventResult;
  detail?: EventDetail;
  duration_ms?: number;
  /** The bundle's `release.content_hash`. */
  content_hash: string;
}

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
  for (const key of EVENT_KEYS) if (!(key in event)) errors.push(`/: missing ${key}`);
  for (const key of Object.keys(event)) if (!EVENT_KEYS.has(key)) errors.push(`/: unexpected ${key}`);
  const check = (key: string, ok: (v: unknown) => boolean) => {
    if (key in event && !ok(event[key])) errors.push(`/${key}: invalid`);
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
  const detail = event.detail;
  if ('detail' in event) {
    if (!isObject(detail)) errors.push('/detail: must be an object');
    else {
      for (const key of Object.keys(detail)) if (!DETAIL_KEYS.has(key)) errors.push(`/detail: unexpected ${key}`);
      if ('cases' in detail) {
        const cases = detail.cases;
        const okCase = (c: unknown) =>
          isObject(c) && isInt(c.n) && c.n >= 1 && typeof c.pass === 'boolean' && Object.keys(c).every((k) => k === 'n' || k === 'pass');
        if (!Array.isArray(cases) || !cases.every(okCase)) errors.push('/detail/cases: invalid');
      }
      if ('self_grade' in detail && detail.self_grade !== 'got-it' && detail.self_grade !== 'not-yet') errors.push('/detail/self_grade: invalid');
      if ('box' in detail && !(isInt(detail.box) && detail.box >= 0)) errors.push('/detail/box: invalid');
      if ('checklist' in detail && !(Array.isArray(detail.checklist) && detail.checklist.every((b) => typeof b === 'boolean'))) {
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
}

const byTime = (a: ProgressEvent, b: ProgressEvent) => a.timestamp.localeCompare(b.timestamp);

/** The in-memory store used when IndexedDB is unavailable (and the base of nothing else). */
export class MemoryProgress implements ProgressStore {
  readonly persistent = false;
  private log: ProgressEvent[] = [];
  private cardMap = new Map<string, CardState>();
  private resumeMap = new Map<string, ResumeState>();

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
  constructor(private readonly db: IDBDatabase) {}

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
}

function upgrade(db: IDBDatabase): void {
  if (!db.objectStoreNames.contains('events')) {
    const events = db.createObjectStore('events', { keyPath: 'event_id' });
    events.createIndex('item_key', 'item_key');
    events.createIndex('book', 'book');
  }
  if (!db.objectStoreNames.contains('cards')) db.createObjectStore('cards', { keyPath: 'key' }).createIndex('book', 'book');
  if (!db.objectStoreNames.contains('resume')) db.createObjectStore('resume', { keyPath: 'book' });
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

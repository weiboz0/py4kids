/**
 * The progress store (plan 103 Phase D): IndexedDB through fake-indexeddb, the no-IndexedDB
 * fallback, and every event validated against tools/export/schema/progress-event.schema.json.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { Ajv2020 } from 'ajv/dist/2020.js';
import { IDBFactory } from 'fake-indexeddb';
import { beforeEach, describe, expect, it } from 'vitest';
import { repoRoot } from '../src/lib/bundle';
import {
  DB_NAME,
  InvalidEventError,
  makeEvent,
  MemoryProgress,
  onceUnsaved,
  openProgress,
  recordCardReview,
  recordChecklist,
  recordSlide,
  resetSharedProgress,
  resetUnsavedNotice,
  sharedProgress,
  uuid,
  validateEvent,
  type ProgressStore,
} from '../src/lib/progress';

const schema = JSON.parse(readFileSync(join(repoRoot(), 'tools', 'export', 'schema', 'progress-event.schema.json'), 'utf-8')) as object;
const ajvValidate = new Ajv2020({ strict: true, allErrors: true }).compile(schema);
const HASH = `sha256:${'b'.repeat(64)}`;
const CARD = { key: 'python-concepts/unit-03-decisions/lesson/u03l003#predict', book: 'python-concepts' };
const ITEM = 'python-projects/unit-02-x/exercises/e7';
const BLOCK = 'acsl/unit-08-boolean/lesson/l-003#2';
const now = new Date('2026-10-07T12:34:56.789Z');

function assertSchemaValid(event: unknown): void {
  const ok = ajvValidate(event);
  expect(ajvValidate.errors ?? [], JSON.stringify(event)).toEqual([]);
  expect(ok).toBe(true);
  expect(validateEvent(event)).toEqual([]);
}

async function allEventsValid(store: ProgressStore): Promise<number> {
  const events = await store.events();
  for (const event of events) assertSchemaValid(event);
  return events.length;
}

describe('events', () => {
  it('makes a schema-valid event with a UUID and a UTC Z timestamp', () => {
    const event = makeEvent({ item_key: CARD.key, kind: 'card', result: 'pass', detail: { box: 2 }, content_hash: HASH }, now);
    assertSchemaValid(event);
    expect(event.timestamp).toBe('2026-10-07T12:34:56.789Z');
    expect(event.event_id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
    expect(event.book).toBe('python-concepts');
    expect(event.schema).toBe('py4kids/progress-event/1.0.0');
  });

  it('makes distinct UUIDs, also without crypto.randomUUID', () => {
    const seen = new Set(Array.from({ length: 200 }, uuid));
    expect(seen.size).toBe(200);
    const original = globalThis.crypto.randomUUID;
    try {
      Object.defineProperty(globalThis.crypto, 'randomUUID', { value: undefined, configurable: true });
      expect(uuid()).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);
    } finally {
      Object.defineProperty(globalThis.crypto, 'randomUUID', { value: original, configurable: true });
    }
  });

  it('refuses an event the schema rejects', () => {
    expect(() => makeEvent({ item_key: 'not a key', kind: 'slide', result: 'seen', content_hash: HASH })).toThrow(InvalidEventError);
    expect(() => makeEvent({ item_key: ITEM, kind: 'slide', result: 'seen', content_hash: 'sha256:xyz' })).toThrow(InvalidEventError);
  });

  it('validateEvent agrees with Ajv on valid and mutated events', () => {
    const base = makeEvent({ item_key: ITEM, kind: 'self-check', result: 'partial', detail: { checklist: [true, false] }, content_hash: HASH }, now);
    const mutations: Record<string, unknown>[] = [
      {},
      { schema: 'py4kids/progress-event/2.0.0' },
      { event_id: 'ABCDEFAB-0000-4000-8000-000000000000' },
      { book: 'Bad_Book' },
      { item_key: 'book/entry/nb' },
      { item_key: 'book/entry/nb/cell#part' },
      { item_key: 'book/entry/nb/cell#' },
      { kind: 'quiz' },
      { kind: 'lesson-run' },
      { result: 'ok' },
      { duration_ms: -1 },
      { duration_ms: 1.5 },
      { timestamp: '2026-10-07T12:34:56+00:00' },
      { timestamp: '2026-10-07T12:34:56Z' },
      { content_hash: `sha256:${'B'.repeat(64)}` },
      { detail: [] },
      { detail: { box: 0 } },
      { detail: { box: -1 } },
      { detail: { self_grade: 'maybe' } },
      { detail: { checklist: [1] } },
      { detail: { cases: [{ n: 1, pass: true }] } },
      { detail: { cases: [{ n: 0, pass: true }] } },
      { detail: { cases: [{ n: 1, pass: true, extra: 1 }] } },
      { detail: { code: 'print(1)' } },
      { extra: true },
    ];
    for (const change of mutations) {
      const event = { ...base, ...change };
      expect(validateEvent(event).length === 0, JSON.stringify(change)).toBe(ajvValidate(event) as boolean);
    }
    for (const key of Object.keys(base)) {
      const event: Record<string, unknown> = { ...base };
      delete event[key];
      expect(validateEvent(event).length > 0, key).toBe(true);
      expect(ajvValidate(event)).toBe(false);
    }
  });
});

describe('IndexedDB store', () => {
  let factory: IDBFactory;
  beforeEach(() => {
    factory = new IDBFactory();
  });

  it('opens database py4kids with the events, cards, resume and attempts stores', async () => {
    const store = await openProgress({ indexedDB: factory });
    expect(store.persistent).toBe(true);
    const names = await new Promise<string[]>((resolve) => {
      const req = factory.open(DB_NAME);
      req.onsuccess = () => {
        resolve([...req.result.objectStoreNames]);
        req.result.close();
      };
    });
    expect(names.sort()).toEqual(['attempts', 'cards', 'events', 'resume']);
  });

  it('records a card review: Leitner state plus a schema-valid card event', async () => {
    const store = await openProgress({ indexedDB: factory });
    const first = await recordCardReview(store, CARD, true, { content_hash: HASH, duration_ms: 1234.4 }, now);
    expect(first.state.box).toBe(2);
    expect(first.event).toMatchObject({ kind: 'card', result: 'pass', detail: { box: 2 }, duration_ms: 1234 });
    const second = await recordCardReview(store, CARD, false, { content_hash: HASH, self_grade: 'not-yet' }, now);
    expect(second.state.box).toBe(1);
    expect(second.event.detail).toEqual({ box: 1, self_grade: 'not-yet' });
    expect(await store.getCard(CARD.key)).toEqual(second.state);
    expect([...(await store.cards('python-concepts')).keys()]).toEqual([CARD.key]);
    expect((await store.cards('acsl')).size).toBe(0);
    expect(await allEventsValid(store)).toBe(2);
  });

  it('records an early correct review as a card event without promoting the card', async () => {
    const store = await openProgress({ indexedDB: factory });
    const first = await recordCardReview(store, CARD, true, { content_hash: HASH }, now); // box 2, due in a day
    const early = await recordCardReview(store, CARD, true, { content_hash: HASH, self_grade: 'got-it' }, new Date(now.getTime() + 60_000));
    expect(early.state.box).toBe(2);
    expect(early.state.due).toBe(first.state.due);
    expect(early.event).toMatchObject({ kind: 'card', result: 'pass', detail: { box: 2, self_grade: 'got-it' } });
    expect((await store.getCard(CARD.key))?.box).toBe(2);
    expect(await allEventsValid(store)).toBe(2);
  });

  it('leaves the card state untouched when the event is invalid', async () => {
    const store = await openProgress({ indexedDB: factory });
    await expect(recordCardReview(store, { key: 'bad key', book: 'x' }, true, { content_hash: HASH })).rejects.toThrow(InvalidEventError);
    expect(await store.getCard('bad key')).toBeUndefined();
  });

  it('records self-check checklists and slides', async () => {
    const store = await openProgress({ indexedDB: factory });
    const partial = await recordChecklist(store, ITEM, [true, false, true], HASH, now);
    expect(partial).toMatchObject({ kind: 'self-check', result: 'partial', detail: { checklist: [true, false, true] } });
    const done = await recordChecklist(store, ITEM, [true, true, true], HASH, new Date(now.getTime() + 1000));
    expect(done.result).toBe('done');
    expect((await store.latestEvent(ITEM, 'self-check'))?.detail.checklist).toEqual([true, true, true]);
    const slide = await recordSlide(store, BLOCK, HASH, now);
    expect(slide).toMatchObject({ kind: 'slide', result: 'seen', book: 'acsl', item_key: BLOCK });
    expect((await store.events(ITEM)).map((e) => e.result)).toEqual(['partial', 'done']);
    expect(await allEventsValid(store)).toBe(3);
    // Only a Run writes a lesson-run event (plan 104); a checklist and a slide do not.
    expect((await store.events()).some((e) => e.kind === 'lesson-run')).toBe(false);
  });

  it('keeps the resume position per book, with updated_at', async () => {
    const store = await openProgress({ indexedDB: factory });
    await store.setResume({ book: 'acsl', entry: 'unit-08-boolean', href: '/acsl/unit-08-boolean/', title: 'Unit 8' }, now);
    const r = await store.setResume({ book: 'acsl', entry: 'unit-09', href: '/acsl/unit-09/slides/#4', title: 'Unit 9' }, now);
    expect(r.updated_at).toBe(now.toISOString());
    expect(await store.getResume('acsl')).toEqual(r);
    expect(await store.getResume('python-projects')).toBeUndefined();
  });

  it('persists across reopening', async () => {
    const one = await openProgress({ indexedDB: factory });
    await recordCardReview(one, CARD, true, { content_hash: HASH }, now);
    await one.setResume({ book: 'acsl', entry: 'u', href: '/acsl/u/', title: 'U' }, now);
    const two = await openProgress({ indexedDB: factory });
    expect((await two.getCard(CARD.key))?.box).toBe(2);
    expect((await two.getResume('acsl'))?.href).toBe('/acsl/u/');
    expect((await two.events()).length).toBe(1);
  });
});

describe('the no-IndexedDB fallback', () => {
  beforeEach(() => {
    resetSharedProgress();
    resetUnsavedNotice();
  });

  it('works in memory without saving when IndexedDB is missing', async () => {
    const store = await openProgress({ indexedDB: null });
    expect(store).toBeInstanceOf(MemoryProgress);
    expect(store.persistent).toBe(false);
    await recordCardReview(store, CARD, true, { content_hash: HASH }, now);
    expect((await store.getCard(CARD.key))?.box).toBe(2);
    await recordChecklist(store, ITEM, [true], HASH, now);
    await store.setResume({ book: 'acsl', entry: 'u', href: '/acsl/u/', title: 'U' }, now);
    expect((await store.getResume('acsl'))?.entry).toBe('u');
    expect(await allEventsValid(store)).toBe(2);
    // Nothing survives: a new store starts empty.
    expect((await (await openProgress({ indexedDB: null })).events()).length).toBe(0);
  });

  it('falls back when IndexedDB refuses to open (a private window)', async () => {
    const broken = {
      open() {
        throw new DOMException('The operation is insecure.', 'SecurityError');
      },
    } as unknown as IDBFactory;
    expect((await openProgress({ indexedDB: broken })).persistent).toBe(false);
    const failing = {
      open() {
        const req: Partial<IDBOpenDBRequest> & { error: DOMException } = { error: new DOMException('denied', 'InvalidStateError') };
        setTimeout(() => (req.onerror as ((e: Event) => void) | undefined)?.(new Event('error')), 0);
        return req;
      },
    } as unknown as IDBFactory;
    expect((await openProgress({ indexedDB: failing })).persistent).toBe(false);
  });

  it('falls back when no indexedDB global exists (Node has none)', async () => {
    expect('indexedDB' in globalThis).toBe(false);
    expect((await openProgress()).persistent).toBe(false);
  });

  it('says so once', async () => {
    const store = await sharedProgress({ indexedDB: null });
    expect(await sharedProgress()).toBe(store);
    let shown = 0;
    expect(onceUnsaved(store, () => shown++)).toBe(true);
    expect(onceUnsaved(store, () => shown++)).toBe(false);
    expect(onceUnsaved(await openProgress({ indexedDB: null }), () => shown++)).toBe(false);
    expect(shown).toBe(1);
  });

  it('says so once per visit when the page can remember it', async () => {
    const store = await openProgress({ indexedDB: null });
    let flag = false;
    const remember = { get: () => flag, set: () => void (flag = true) };
    let shown = 0;
    expect(onceUnsaved(store, () => shown++, remember)).toBe(true);
    resetUnsavedNotice(); // a new page in the same visit
    expect(onceUnsaved(store, () => shown++, remember)).toBe(false);
    expect(shown).toBe(1);
  });

  it('never shows the notice when progress is saved', async () => {
    const store = await openProgress({ indexedDB: new IDBFactory() });
    let shown = 0;
    expect(onceUnsaved(store, () => shown++)).toBe(false);
    expect(shown).toBe(0);
  });
});

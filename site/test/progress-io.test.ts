/**
 * "Export my progress" and "Import progress" (plan 105 Phase C): the export file validated against
 * tools/export/schema/progress-export.schema.json (Ajv) and its hand-written twin, and the
 * deterministic merge rules on IndexedDB (fake-indexeddb) and the in-memory store.
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { Ajv2020 } from 'ajv/dist/2020.js';
import { IDBFactory } from 'fake-indexeddb';
import { beforeEach, describe, expect, it } from 'vitest';
import { repoRoot } from '../src/lib/bundle';
import type { CardState } from '../src/lib/leitner';
import {
  buildExport,
  EPOCH,
  EXPORT_SCHEMA,
  exportFileName,
  exportProgress,
  ImportError,
  importProgress,
  MAX_IMPORT_BYTES,
  parseExport,
  planMerge,
  readImportFile,
  stamp,
  validateExport,
  type ProgressExport,
} from '../src/lib/progress-io';
import { MemoryProgress, openProgress, recordCardReview, recordSlide, type ProgressStore, type StoreRecords } from '../src/lib/progress';

const SCHEMA_DIR = join(repoRoot(), 'tools', 'export', 'schema');
const load = (name: string) => JSON.parse(readFileSync(join(SCHEMA_DIR, name), 'utf-8')) as object;
const ajv = new Ajv2020({ strict: true, allErrors: true });
ajv.addSchema(load('progress-event.schema.json'));
const ajvValidate = ajv.compile(load('progress-export.schema.json'));

const HASH = `sha256:${'c'.repeat(64)}`;
const CARD_A = { key: 'python-concepts/unit-03-decisions/lesson/u03l003#predict', book: 'python-concepts' };
const CARD_B = { key: 'acsl/unit-08-boolean/lesson/l-003#concept', book: 'acsl' };
const SLIDE = 'acsl/unit-08-boolean/lesson/l-003#2';
const ITEM = 'python-projects/unit-02-x/exercises/e7';
const t0 = new Date('2026-10-01T10:00:00.000Z');
const at = (minutes: number) => new Date(t0.getTime() + minutes * 60_000);

function assertValid(data: unknown): void {
  const ok = ajvValidate(data);
  expect(ajvValidate.errors ?? [], 'Ajv').toEqual([]);
  expect(ok).toBe(true);
  expect(validateExport(data)).toEqual([]);
}

/** A store with two cards, two events, a resume position and one attempt, all at `t0`. */
async function seeded(store: ProgressStore): Promise<ProgressStore> {
  await recordCardReview(store, CARD_A, true, { content_hash: HASH }, at(0)); // box 2
  await recordCardReview(store, CARD_B, true, { content_hash: HASH }, at(1)); // box 2
  await recordSlide(store, SLIDE, HASH, at(2));
  await store.setResume({ book: 'acsl', entry: 'unit-08-boolean', href: '/acsl/unit-08-boolean/slides/#3', title: 'Unit 8 (slides)' }, at(3));
  await store.addAttempt({ item_key: ITEM, kind: 'check', code: 'print("hi")', result: 'pass' }, at(4));
  return store;
}

/** The whole store, as JSON text (the "byte-for-byte" comparison). */
async function dump(store: ProgressStore): Promise<string> {
  const r = await store.records({ attempts: true });
  const sort = <T>(list: T[], key: (x: T) => string) => [...list].sort((a, b) => key(a).localeCompare(key(b)));
  return JSON.stringify({
    events: sort(r.events, (e) => e.event_id),
    cards: sort(r.cards, (c) => c.key),
    resume: sort(r.resume, (x) => x.book),
    attempts: sort(r.attempts, (a) => a.attempt_id),
  });
}

const fileOf = async (store: ProgressStore, options: { attempts?: boolean } = {}, now = at(10)) =>
  parseExport(await exportProgress(store, options, now));

describe('the export file', () => {
  it('validates against the schema, with events, cards and resume and no attempts by default', async () => {
    const store = await seeded(new MemoryProgress());
    const text = await exportProgress(store, {}, at(10));
    const data = JSON.parse(text) as ProgressExport;
    assertValid(data);
    expect(data.schema).toBe(EXPORT_SCHEMA);
    expect(data.schema).toBe((load('progress-export.schema.json') as { $id: string }).$id);
    expect(data.exported_at).toBe(at(10).toISOString());
    expect(data.events).toHaveLength(3);
    expect(data.cards.map((c) => c.key)).toEqual([CARD_B.key, CARD_A.key]); // sorted by key
    expect(data.resume).toHaveLength(1);
    expect('attempts' in data).toBe(false);
    expect(text).not.toContain('print(');
    expect(exportFileName({}, at(10))).toBe('py4kids-progress-2026-10-01.json');
  });

  it('adds the attempt store only when asked, clearly named', async () => {
    const store = await seeded(new MemoryProgress());
    const data = JSON.parse(await exportProgress(store, { attempts: true }, at(10))) as ProgressExport;
    assertValid(data);
    expect(data.attempts).toHaveLength(1);
    expect(data.attempts![0]!.code).toBe('print("hi")');
    expect(exportFileName({ attempts: true }, at(10))).toBe('py4kids-progress-and-code-2026-10-01.json');
  });

  it('gives a legacy record without updated_at the epoch', () => {
    const legacy = { key: CARD_A.key, book: CARD_A.book, box: 3, due: t0.toISOString() } as CardState;
    const data = buildExport({ events: [], cards: [legacy], resume: [], attempts: [] }, {}, t0);
    expect(data.cards[0]!.updated_at).toBe(EPOCH);
    assertValid(data);
  });

  it('validateExport agrees with Ajv on valid and mutated files', async () => {
    const base = JSON.parse(await exportProgress(await seeded(new MemoryProgress()), { attempts: true }, at(10))) as Record<string, unknown>;
    const card = (base.cards as Record<string, unknown>[])[0]!;
    const resume = (base.resume as Record<string, unknown>[])[0]!;
    const event = (base.events as Record<string, unknown>[])[0]!;
    const attempt = (base.attempts as Record<string, unknown>[])[0]!;
    const mutations: Record<string, unknown>[] = [
      {},
      { schema: 'py4kids/progress-export/2.0.0' },
      { exported_at: '2026-10-01 10:00' },
      { events: {} },
      { cards: null },
      { extra: 1 },
      { attempts: [] },
      { events: [{ ...event, detail: { code: 'x' } }] },
      { events: [{ ...event, event_id: 'nope' }] },
      { events: [42] },
      { cards: [{ ...card, box: 0 }] },
      { cards: [{ ...card, box: 6 }] },
      { cards: [{ ...card, box: 2.5 }] },
      { cards: [{ ...card, key: 'not a key' }] },
      { cards: [{ ...card, due: 'tomorrow' }] },
      { cards: [{ ...card, extra: true }] },
      { cards: [{ ...card, updated_at: undefined }] },
      { resume: [{ ...resume, href: '//evil.example/' }] },
      { resume: [{ ...resume, href: 'javascript:alert(1)' }] },
      { resume: [{ ...resume, href: '/\\evil.example' }] },
      { resume: [{ ...resume, href: '/' }] },
      { resume: [{ ...resume, href: '/a b' }] },
      { resume: [{ ...resume, entry: 'a/b' }] },
      { resume: [{ ...resume, title: 'x'.repeat(500) }] },
      { resume: [{ ...resume, title: 'x'.repeat(501) }] },
      { resume: [{ ...resume, title: '🙂'.repeat(500) }] },
      { resume: [{ ...resume, book: 'Bad_Book' }] },
      { attempts: [{ ...attempt, kind: 'paste' }] },
      { attempts: [{ ...attempt, code: 3 }] },
      { attempts: [{ ...attempt, answer: '42' }] },
      { attempts: [{ ...attempt, result: 'ok' }] },
      { attempts: [{ ...attempt, attempt_id: undefined }] },
    ];
    for (const change of mutations) {
      const data = JSON.parse(JSON.stringify({ ...base, ...change })) as unknown;
      expect(validateExport(data).length === 0, JSON.stringify(change).slice(0, 80)).toBe(ajvValidate(data) as boolean);
    }
    for (const key of Object.keys(base)) {
      const data: Record<string, unknown> = { ...base };
      delete data[key];
      expect(validateExport(data).length === 0, key).toBe(ajvValidate(data) as boolean);
    }
    for (const value of [null, [], 'x', 3]) expect(validateExport(value).length > 0).toBe(!ajvValidate(value));
  });

  it('refuses Object.prototype key names at every record level with the schema message, never a TypeError', async () => {
    const base = JSON.parse(await exportProgress(await seeded(new MemoryProgress()), { attempts: true }, at(10))) as Record<string, unknown>;
    // An event with detail.cases, so the detail and case levels are probed too.
    const event = { ...(base.events as Record<string, unknown>[])[0]!, kind: 'exercise', item_key: ITEM, book: 'python-projects', result: 'fail', detail: { cases: [{ n: 1, pass: false }] } };
    const valid: Record<string, unknown> = { ...base, events: [event] };
    assertValid(valid);
    /** `value` with one more own key `key` (defined, so even `__proto__` is an own data key). */
    const withKey = (value: Record<string, unknown>, key: string): Record<string, unknown> =>
      Object.defineProperty({ ...value }, key, { value: 1, enumerable: true, writable: true, configurable: true });
    type Level = { name: string; add: (key: string) => Record<string, unknown> };
    const first = (name: string) => (valid[name] as Record<string, unknown>[])[0]!;
    const levels: Level[] = [
      { name: 'top', add: (k) => withKey(valid, k) },
      { name: 'event', add: (k) => ({ ...valid, events: [withKey(event, k)] }) },
      { name: 'event detail', add: (k) => ({ ...valid, events: [{ ...event, detail: withKey(event.detail, k) }] }) },
      { name: 'event case', add: (k) => ({ ...valid, events: [{ ...event, detail: { cases: [withKey(event.detail.cases[0]!, k)] } }] }) },
      { name: 'card', add: (k) => ({ ...valid, cards: [withKey(first('cards'), k)] }) },
      { name: 'resume', add: (k) => ({ ...valid, resume: [withKey(first('resume'), k)] }) },
      { name: 'attempt', add: (k) => ({ ...valid, attempts: [withKey(first('attempts'), k)] }) },
    ];
    let probed = 0;
    for (const key of ['constructor', 'toString', 'hasOwnProperty', '__proto__', 'valueOf', 'isPrototypeOf', 'propertyIsEnumerable', 'toLocaleString']) {
      for (const level of levels) {
        // Through the text, as a real file arrives: JSON.parse makes `__proto__` an own key.
        const text = JSON.stringify(level.add(key));
        expect(text, `${level.name} ${key}`).toContain(`"${key}":1`);
        const data = JSON.parse(text) as unknown;
        const what = `${key} on the ${level.name}`;
        expect(ajvValidate(data), `Ajv refuses ${what}`).toBe(false);
        expect(() => validateExport(data), what).not.toThrow();
        expect(validateExport(data).length, `the twin refuses ${what}`).toBeGreaterThan(0);
        let error: unknown;
        try {
          parseExport(text);
        } catch (e) {
          error = e;
        }
        expect(error, what).toBeInstanceOf(ImportError);
        expect((error as ImportError).reason, what).toBe('invalid');
        expect((error as ImportError).message, what).toMatch(/^That progress file has something wrong inside it/);
        // Named as unexpected (a case's checker reports the whole list of cases as invalid).
        expect((error as ImportError).details.join('; '), what).toMatch(level.name === 'event case' ? /\/detail\/cases: invalid/ : new RegExp(`unexpected ${key}`));
        probed++;
      }
    }
    expect(probed).toBe(8 * levels.length);
  });
});

describe('import refuses a bad file with a student-friendly message', () => {
  const reasonOf = (fn: () => unknown): string => {
    try {
      fn();
    } catch (error) {
      expect(error).toBeInstanceOf(ImportError);
      expect((error as ImportError).message).toMatch(/Nothing was changed\.$/);
      return (error as ImportError).reason;
    }
    throw new Error('no error');
  };

  it('malformed JSON', () => {
    expect(reasonOf(() => parseExport('{"schema": "py4kids/progress-export/1.0.0", '))).toBe('not-json');
    expect(reasonOf(() => parseExport('<html></html>'))).toBe('not-json');
  });

  it('an empty file, or JSON that is not a progress file', () => {
    expect(reasonOf(() => parseExport(''))).toBe('empty');
    expect(reasonOf(() => parseExport('[1, 2]'))).toBe('invalid');
    expect(reasonOf(() => parseExport('{"hello": 1}'))).toBe('invalid');
  });

  it('an unknown schema', () => {
    for (const schema of ['py4kids/progress-export/2.0.0', 'py4kids/progress-event/1.0.0', 7]) {
      const text = JSON.stringify({ schema, exported_at: t0.toISOString(), events: [], cards: [], resume: [] });
      expect(reasonOf(() => parseExport(text))).toBe('unknown-schema');
    }
  });

  it('a file that breaks the schema', async () => {
    const data = await fileOf(await seeded(new MemoryProgress()));
    const bad = { ...data, cards: [{ ...data.cards[0]!, box: 9 }] };
    let error: ImportError | undefined;
    try {
      parseExport(JSON.stringify(bad));
    } catch (e) {
      error = e as ImportError;
    }
    expect(error?.reason).toBe('invalid');
    expect(error?.details).toContain('/cards/0/box: invalid');
  });

  it('a file over 20 MB, before reading it', async () => {
    const big = new Blob([new Uint8Array(MAX_IMPORT_BYTES + 1)]);
    let text = false;
    const spy = Object.assign(big, {
      text: () => {
        text = true;
        return Promise.resolve('');
      },
    });
    await expect(readImportFile(spy)).rejects.toMatchObject({ reason: 'too-big' });
    expect(text).toBe(false);
    expect(reasonOf(() => parseExport('{}', MAX_IMPORT_BYTES + 1))).toBe('too-big');
    // Exactly 20 MB is allowed (then fails as not JSON, not as too big).
    expect(reasonOf(() => parseExport(' '.repeat(10) + 'x', MAX_IMPORT_BYTES))).toBe('not-json');
  });
});

for (const kind of ['IndexedDB', 'memory'] as const) {
  describe(`merge (${kind})`, () => {
    let open: () => Promise<ProgressStore>;
    beforeEach(() => {
      const factory = new IDBFactory();
      open = () => (kind === 'IndexedDB' ? openProgress({ indexedDB: factory, name: `db-${Math.random()}` }) : Promise.resolve(new MemoryProgress()));
    });

    it('export -> fresh store -> import restores cards, resume and events', async () => {
      const source = await seeded(await open());
      const file = await fileOf(source);
      const target = await open();
      const summary = await importProgress(target, file);
      expect(summary).toEqual({ events: 3, cards: 2, resume: 1, attempts: 0 });
      const a = await source.records();
      const b = await target.records();
      expect(await target.getCard(CARD_A.key)).toEqual(await source.getCard(CARD_A.key));
      expect(await target.getResume('acsl')).toEqual(await source.getResume('acsl'));
      expect(b.events.map((e) => e.event_id).sort()).toEqual(a.events.map((e) => e.event_id).sort());
      expect(b.attempts).toEqual([]); // attempts were not exported
    });

    it('imports attempts by attempt_id when the file has them', async () => {
      const file = await fileOf(await seeded(await open()), { attempts: true });
      const target = await open();
      expect((await importProgress(target, file)).attempts).toBe(1);
      expect((await target.attempts(ITEM))[0]?.code).toBe('print("hi")');
      expect((await importProgress(target, file)).attempts).toBe(0);
      expect(await target.attempts(ITEM)).toHaveLength(1);
    });

    it('importing the same file twice into an existing, newer store leaves it byte-for-byte unchanged', async () => {
      const store = await seeded(await open());
      const file = await fileOf(store, { attempts: true });
      // The store moves on after the export: newer cards, a newer resume, more events.
      await recordCardReview(store, CARD_A, false, { content_hash: HASH }, at(60)); // box 1, newer
      await recordCardReview(store, CARD_B, true, { content_hash: HASH }, at(60 * 24 * 2)); // box 3, newer
      await store.setResume({ book: 'acsl', entry: 'unit-09', href: '/acsl/unit-09/', title: 'Unit 9' }, at(61));
      await recordSlide(store, SLIDE, HASH, at(62));
      const before = await dump(store);
      const eventsBefore = (await store.events()).length;

      const first = await importProgress(store, file);
      expect(first).toEqual({ events: 0, cards: 0, resume: 0, attempts: 0 });
      expect(await dump(store)).toBe(before);
      const second = await importProgress(store, file);
      expect(second).toEqual({ events: 0, cards: 0, resume: 0, attempts: 0 });
      expect(await dump(store)).toBe(before);
      expect((await store.events()).length).toBe(eventsBefore);
      expect((await store.getCard(CARD_A.key))?.box).toBe(1);
      expect((await store.getCard(CARD_B.key))?.box).toBe(3);
      expect((await store.getResume('acsl'))?.entry).toBe('unit-09');
    });

    it('importing twice after a real merge changes nothing the second time', async () => {
      const other = await seeded(await open());
      const file = await fileOf(other);
      const store = await open();
      await recordCardReview(store, CARD_A, true, { content_hash: HASH }, at(-60)); // older than the file's
      await recordSlide(store, SLIDE, HASH, at(-59));
      const first = await importProgress(store, file);
      expect(first).toEqual({ events: 3, cards: 2, resume: 1, attempts: 0 });
      const after = await dump(store);
      expect((await store.events()).length).toBe(5); // union: 2 local + 3 from the file
      expect(await importProgress(store, file)).toEqual({ events: 0, cards: 0, resume: 0, attempts: 0 });
      expect(await dump(store)).toBe(after);
    });

    it('an older export never regresses newer cards or resume', async () => {
      const store = await seeded(await open());
      const old = await fileOf(store); // CARD_A box 2 at t0
      await recordCardReview(store, CARD_A, true, { content_hash: HASH }, at(60 * 24 * 2)); // box 3
      await store.setResume({ book: 'acsl', entry: 'unit-10', href: '/acsl/unit-10/', title: 'Unit 10' }, at(60 * 24 * 2));
      await importProgress(store, old);
      expect((await store.getCard(CARD_A.key))?.box).toBe(3);
      expect((await store.getResume('acsl'))?.entry).toBe('unit-10');
    });

    it('a newer export wins over older local cards and resume', async () => {
      const store = await seeded(await open());
      const newer = await seeded(await open());
      await recordCardReview(newer, CARD_A, true, { content_hash: HASH }, at(60 * 24 * 2)); // box 3
      await newer.setResume({ book: 'acsl', entry: 'unit-10', href: '/acsl/unit-10/', title: 'Unit 10' }, at(60 * 24 * 2));
      const summary = await importProgress(store, await fileOf(newer));
      expect(summary.cards).toBe(1);
      expect(summary.resume).toBe(1);
      expect((await store.getCard(CARD_A.key))?.box).toBe(3);
      expect((await store.getResume('acsl'))?.entry).toBe('unit-10');
    });

    it('a tie on updated_at keeps the local record', async () => {
      const store = await open();
      const local: CardState = { ...CARD_A, box: 4, due: at(100).toISOString(), updated_at: at(5).toISOString() };
      await store.putCard(local);
      await store.setResume({ book: 'acsl', entry: 'mine', href: '/acsl/mine/', title: 'Mine' }, at(5));
      const file = parseExport(
        JSON.stringify({
          schema: EXPORT_SCHEMA,
          exported_at: at(6).toISOString(),
          events: [],
          // Same instant, written with a different precision: still a tie.
          cards: [{ ...CARD_A, box: 1, due: at(5).toISOString(), updated_at: '2026-10-01T10:05:00Z' }],
          resume: [{ book: 'acsl', entry: 'theirs', href: '/acsl/theirs/', title: 'Theirs', updated_at: at(5).toISOString() }],
        }),
      );
      expect(await importProgress(store, file)).toEqual({ events: 0, cards: 0, resume: 0, attempts: 0 });
      expect(await store.getCard(CARD_A.key)).toEqual(local);
      expect((await store.getResume('acsl'))?.entry).toBe('mine');
    });

    it('a legacy local record without updated_at counts as the oldest', async () => {
      const store = await open();
      const legacyCard = { ...CARD_A, box: 5, due: at(0).toISOString() } as CardState;
      const legacyResume = { book: 'acsl', entry: 'old', href: '/acsl/old/', title: 'Old' } as StoreRecords['resume'][number];
      await store.putRecords({ events: [], cards: [legacyCard], resume: [legacyResume], attempts: [] });
      const file = parseExport(
        JSON.stringify({
          schema: EXPORT_SCHEMA,
          exported_at: t0.toISOString(),
          events: [],
          cards: [{ ...CARD_A, box: 2, due: t0.toISOString(), updated_at: EPOCH.replace('.000', '.001') }],
          resume: [{ book: 'acsl', entry: 'new', href: '/acsl/new/', title: 'New', updated_at: t0.toISOString() }],
        }),
      );
      await importProgress(store, file);
      expect((await store.getCard(CARD_A.key))?.box).toBe(2);
      const resume = await store.getResume('acsl');
      expect(resume?.entry).toBe('new');
      expect(resume?.updated_at).toBe(t0.toISOString());
    });
  });
}

describe('planMerge', () => {
  const card = (box: number, minutes: number): CardState => ({ ...CARD_A, box, due: at(minutes).toISOString(), updated_at: at(minutes).toISOString() });
  const empty: StoreRecords = { events: [], cards: [], resume: [], attempts: [] };
  const file = (cards: CardState[]): ProgressExport => ({ schema: EXPORT_SCHEMA, exported_at: t0.toISOString(), events: [], cards, resume: [] });

  it("resolves a file's duplicate keys by the later updated_at, the first on a tie", () => {
    expect(planMerge(empty, file([card(2, 1), card(4, 3), card(3, 2)])).cards.map((c) => c.box)).toEqual([4]);
    const tie = { ...card(5, 1) };
    expect(planMerge(empty, file([card(2, 1), tie])).cards.map((c) => c.box)).toEqual([2]);
  });

  it('writes a kept legacy local record with the epoch (a file record that cannot be read never wins)', () => {
    const legacy = { ...CARD_A, box: 4, due: t0.toISOString() } as CardState;
    const unreadable = { ...card(1, 0), updated_at: 'never' };
    const plan = planMerge({ ...empty, cards: [legacy] }, file([unreadable]));
    expect(plan.cards).toEqual([{ ...legacy, updated_at: EPOCH }]);
  });

  it('stamps a missing or unreadable updated_at as the oldest', () => {
    expect(stamp(undefined)).toBe(Number.NEGATIVE_INFINITY);
    expect(stamp({})).toBe(Number.NEGATIVE_INFINITY);
    expect(stamp({ updated_at: 'x' })).toBe(Number.NEGATIVE_INFINITY);
    expect(stamp({ updated_at: EPOCH })).toBe(0);
  });
});

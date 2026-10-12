/**
 * The hand-written envelope validators (src/envelope.ts) agree with the JSON Schemas
 * (schema/request.schema.json, schema/reply.schema.json) checked by Ajv, on valid envelopes and
 * on every single-point mutation of them (a key removed, a key added, a value replaced).
 */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import Ajv2020 from 'ajv/dist/2020.js';
import { describe, expect, it } from 'vitest';
import { ACCEPTED_VERSIONS, ENVELOPE_VERSION, parseReply, parseRequest, versionOf } from '../src/envelope';

const RID = 'a'.repeat(64);
const HASH = '0123456789abcdef'.repeat(4);

const SCHEMA = join(import.meta.dirname, '..', 'schema');
const ajv = new Ajv2020({ strict: true, allErrors: false });
const requestSchema = ajv.compile(JSON.parse(readFileSync(join(SCHEMA, 'request.schema.json'), 'utf-8')));
const replySchema = ajv.compile(JSON.parse(readFileSync(join(SCHEMA, 'reply.schema.json'), 'utf-8')));

const VALID_REQUESTS: unknown[] = [
  {
    type: 'run',
    id: 'r-1',
    session: 'u03-loops',
    code: 'print(1)',
    stdin: '',
    files: [],
    check: null,
    budget_ms: 5000,
  },
  {
    type: 'run',
    id: 'abc_DEF-123',
    session: 'check-9f2',
    code: 'n = int(input())\nprint(n * 2)\n',
    stdin: '21\n',
    files: [
      { path: 'data/scores.txt', data: '1 2 3\n', encoding: 'utf-8' },
      { path: 'img.png', data: 'iVBORw0KGgo=', encoding: 'base64' },
    ],
    check: { kind: 'fixture', expected: '42\n', match: 'token', turtle: false },
    budget_ms: 100,
  },
  {
    type: 'run',
    id: 'x',
    session: 's',
    code: 'def f(x):\n    return x\n',
    stdin: '',
    files: [],
    check: { kind: 'asserts', asserts: ['assert f(1) == 1', 'assert f(2) == 2'], turtle: false },
    budget_ms: 60000,
  },
  { type: 'run', id: 'x', session: 's', code: '', stdin: '', files: [], check: { kind: 'output', turtle: true }, budget_ms: 1000 },
  { type: 'run', id: 'x', session: 's', code: '', stdin: '', files: [], check: { kind: 'fixture', expected: '', match: 'line', turtle: true }, budget_ms: 1000 },
  { type: 'reset', id: 'r2', session: 'u01' },
  { type: 'ping', id: 'p' },
  { type: 'interrupt', id: 'r-1' },
  // Version 2 (plan 105): the same requests with v: 2, and the offline messages.
  { v: 2, type: 'run', id: 'r-2', session: 'u03', code: 'print(1)', stdin: '', files: [], check: null, budget_ms: 5000 },
  { v: 2, type: 'reset', id: 'r3', session: 'u01' },
  { v: 2, type: 'ping', id: 'p2' },
  { v: 2, type: 'interrupt', id: 'r-2' },
  { v: 2, type: 'precache', id: 'pc-1', book: 'python-projects', content_hash: HASH, files: [], release_id: RID },
  { v: 2, type: 'precache', id: 'pc-2', book: 'acsl', content_hash: HASH, files: ['/books/acsl/a.txt', '/x'], release_id: RID },
  { v: 2, type: 'prepare-activate', id: 'pa-1', release_id: RID },
  { v: 2, type: 'get-state', id: 'gs-1', book: 'python-projects' },
  { v: 2, type: 'get-state', id: 'gs-2', book: null },
];

const VALID_REPLIES: unknown[] = [
  {
    type: 'result',
    id: 'r-1',
    session: 'u03',
    stdout: 'hello\n',
    stderr: '',
    results: [{ name: 'case', pass: true, detail: '' }],
    timing: { boot_ms: 1200.5, run_ms: 3, restart_ms: 0 },
    status: 'ok',
    interrupts: 'sab',
    session_new: true,
    truncated: false,
    segments: [{ x1: 0, y1: 0, x2: 100, y2: -0.5, color: 'red', width: 2 }],
  },
  {
    type: 'result',
    id: 'r-2',
    session: 'c',
    stdout: '',
    stderr: 'time limit',
    results: [],
    timing: { boot_ms: 0, run_ms: 1000, restart_ms: 900 },
    status: 'timeout',
    interrupts: 'restart',
    session_new: false,
    truncated: true,
    segments: [],
  },
  { type: 'ready', id: 'p', python: '3.12.7 (main, ...)', pyodide: '0.27.8', isolated: true, boot_ms: 1500 },
  { type: 'restarted', id: 'r', boot_ms: 1100 },
  // Version 2 (plan 105).
  { v: 2, type: 'ready', id: 'p', python: '3.12.7', pyodide: '0.27.8', isolated: true, boot_ms: 1500 },
  { v: 2, type: 'restarted', id: 'r', boot_ms: 1100 },
  {
    v: 2,
    type: 'result',
    id: 'r-3',
    session: 'c',
    stdout: '',
    stderr: '',
    results: [],
    timing: { boot_ms: 0, run_ms: 1, restart_ms: 0 },
    status: 'ok',
    interrupts: 'sab',
    session_new: false,
    truncated: false,
    segments: [],
  },
  { v: 2, type: 'precache-progress', id: 'pc-1', bytes: 1024, total: 15_000_000 },
  { v: 2, type: 'precached', id: 'pc-1', ok: true, bytes: 15_000_000, persisted: false },
  { v: 2, type: 'runner-activated', id: 'pa-1', release_id: RID },
  { v: 2, type: 'state', id: 'gs-1', active: RID, waiting: null, installing: false, record: { content_hash: HASH, release_id: RID } },
  { v: 2, type: 'state', id: 'gs-2', active: null, waiting: RID, installing: true, record: null },
  { type: 'version-mismatch', id: 'x', supported: [1, 2] },
];

// Replacement values that probe types, ranges, patterns and lengths.
const PROBES: unknown[] = [
  null,
  true,
  0,
  -1,
  1.5,
  99,
  60001,
  '',
  'x',
  'a'.repeat(65),
  '../etc',
  '/abs',
  'a//b',
  '.hidden',
  'a/./b',
  'ok/path.txt',
  'line',
  'token',
  'utf-8',
  'sab',
  'ok',
  [],
  ['assert True'],
  {},
  { kind: 'output', turtle: false },
  2,
  3,
  'b'.repeat(64),
  'A'.repeat(64),
  ['/ok'],
  ['../x'],
  'python-projects',
];

/** Every single-point mutation of `value`: each key removed, a key added, each leaf replaced. */
function* mutations(value: unknown): Generator<unknown> {
  if (Array.isArray(value)) {
    for (let i = 0; i < value.length; i++) {
      for (const m of mutations(value[i])) yield value.map((v, j) => (j === i ? m : v));
      yield value.filter((_, j) => j !== i);
    }
    yield [...value, value[0] ?? 'extra'];
    for (const p of PROBES) yield p;
    return;
  }
  if (typeof value === 'object' && value !== null) {
    const obj = value as Record<string, unknown>;
    for (const key of Object.keys(obj)) {
      const { [key]: _, ...rest } = obj;
      yield rest;
      for (const m of mutations(obj[key])) yield { ...obj, [key]: m };
    }
    yield { ...obj, extra: 1 };
    for (const p of PROBES) yield p;
    return;
  }
  for (const p of PROBES) yield p;
}

function agree(parse: (v: unknown) => unknown, schema: (v: unknown) => boolean, samples: unknown[]) {
  let count = 0;
  const disagreements: string[] = [];
  for (const sample of samples) {
    for (const v of [sample, ...mutations(sample)]) {
      count++;
      const mine = parse(v) !== null;
      const theirs = schema(v);
      if (mine !== theirs) disagreements.push(`${JSON.stringify(v).slice(0, 300)}: hand=${mine} ajv=${theirs}`);
    }
  }
  return { count, disagreements };
}

describe('request envelopes', () => {
  it('accepts every valid request', () => {
    for (const r of VALID_REQUESTS) {
      expect(requestSchema(r), JSON.stringify(requestSchema.errors)).toBe(true);
      expect(parseRequest(r)).not.toBeNull();
    }
  });
  it('agrees with Ajv on every single-point mutation', () => {
    const { count, disagreements } = agree(parseRequest, requestSchema, VALID_REQUESTS);
    expect(count).toBeGreaterThan(1000);
    expect(disagreements).toEqual([]);
  });
  it('drops non-envelopes', () => {
    for (const v of [undefined, null, 'run', 42, [], new Map(), { type: 'eval', id: 'x' }]) expect(parseRequest(v)).toBeNull();
    // a non-plain object (class instance) is not an envelope
    class Fake {
      type = 'ping';
      id = 'x';
    }
    expect(parseRequest(new Fake())).toBeNull();
  });
  it('rejects unsafe file paths and out-of-range budgets', () => {
    const base = VALID_REQUESTS[1] as Record<string, unknown>;
    for (const path of ['../x', '/etc/passwd', 'a/../b', '.git/config', 'a\\b', 'a/', '']) {
      expect(parseRequest({ ...base, files: [{ path, data: '', encoding: 'utf-8' }] })).toBeNull();
    }
    for (const budget_ms of [99, 60001, 1000.5, Number.NaN]) expect(parseRequest({ ...base, budget_ms })).toBeNull();
  });
});

describe('reply envelopes', () => {
  it('accepts every valid reply', () => {
    for (const r of VALID_REPLIES) {
      expect(replySchema(r), JSON.stringify(replySchema.errors)).toBe(true);
      expect(parseReply(r)).not.toBeNull();
    }
  });
  it('agrees with Ajv on every single-point mutation', () => {
    const { count, disagreements } = agree(parseReply, replySchema, VALID_REPLIES);
    expect(count).toBeGreaterThan(1000);
    expect(disagreements).toEqual([]);
  });
  it('drops a request posing as a reply and a reply posing as a request', () => {
    for (const r of VALID_REQUESTS) expect(parseReply(r)).toBeNull();
    for (const r of VALID_REPLIES) expect(parseRequest(r)).toBeNull();
  });
});

describe('envelope versions (plan 105)', () => {
  it('speaks version 2 and accepts version N-1 (plan 104 envelopes, without v)', () => {
    expect(ENVELOPE_VERSION).toBe(2);
    expect([...ACCEPTED_VERSIONS]).toEqual([ENVELOPE_VERSION - 1, ENVELOPE_VERSION]);
    // Every plan 104 (version 1) request still parses, and is version 1.
    for (const r of VALID_REQUESTS.filter((r) => versionOf(r) === 1)) {
      expect(parseRequest(r), JSON.stringify(r)).not.toBeNull();
      expect(requestSchema(r)).toBe(true);
    }
    expect(VALID_REQUESTS.filter((r) => versionOf(r) === 1).length).toBeGreaterThanOrEqual(4);
  });
  it('has the offline messages only in version 2, and refuses any other v', () => {
    const precache = VALID_REQUESTS.find((r) => (r as { type: string }).type === 'precache') as Record<string, unknown>;
    const { v: _, ...v1 } = precache;
    expect(parseRequest(v1)).toBeNull();
    for (const v of [0, 1, 3, '2', null]) {
      expect(parseRequest({ ...precache, v })).toBeNull();
      expect(parseRequest({ type: 'ping', id: 'p', v })).toBeNull();
      expect(requestSchema({ type: 'ping', id: 'p', v })).toBe(false);
    }
    expect(versionOf({ type: 'ping', id: 'p', v: 3 })).toBe(3);
    expect(versionOf({ type: 'ping', id: 'p' })).toBe(1);
  });
  it('refuses a malformed release id, content hash, book or runner path', () => {
    const precache = VALID_REQUESTS.find((r) => (r as { type: string }).type === 'precache') as Record<string, unknown>;
    expect(parseRequest({ ...precache, release_id: 'A'.repeat(64) })).toBeNull();
    expect(parseRequest({ ...precache, content_hash: 'sha256:' + 'a'.repeat(64) })).toBeNull();
    expect(parseRequest({ ...precache, book: '../acsl' })).toBeNull();
    for (const path of ['x', '/../x', '/a/../b', '/.git', '//host/x', '/a?b', 'https://x/y']) {
      expect(parseRequest({ ...precache, files: [path] }), path).toBeNull();
    }
  });
});

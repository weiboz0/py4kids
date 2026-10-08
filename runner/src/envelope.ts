/**
 * The runner's message envelopes (design 012 D7, plan 104 "Message boundary"), shared by the
 * runner page and the site's client (site/src/lib/runner-client.ts).
 *
 * The browser cannot run Ajv (it compiles validators with `new Function`, which both CSPs forbid),
 * so `parseRequest` and `parseReply` are hand-written twins of `runner/schema/request.schema.json`
 * and `runner/schema/reply.schema.json`; `runner/test/envelope.test.ts` proves they agree with Ajv
 * on valid and mutated envelopes. Anything that does not validate is dropped by the caller.
 */

export type Id = string;

export interface RunFile {
  path: string;
  data: string;
  encoding: 'utf-8' | 'base64';
}

export type Check =
  | { kind: 'output'; turtle: boolean }
  | { kind: 'fixture'; expected: string; match: 'line' | 'token'; turtle: boolean }
  | { kind: 'asserts'; asserts: string[]; turtle: boolean };

export interface RunRequest {
  type: 'run';
  id: Id;
  session: string;
  code: string;
  stdin: string;
  files: RunFile[];
  check: Check | null;
  budget_ms: number;
}
export interface ResetRequest {
  type: 'reset';
  id: Id;
  session: string;
}
export interface PingRequest {
  type: 'ping';
  id: Id;
}
export interface InterruptRequest {
  type: 'interrupt';
  id: Id;
}
export type Request = RunRequest | ResetRequest | PingRequest | InterruptRequest;

export interface CaseResult {
  name: string;
  pass: boolean;
  detail: string;
}
export interface Segment {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  color: string;
  width: number;
}
export type Status = 'ok' | 'error' | 'timeout' | 'interrupted';
export interface ResultReply {
  type: 'result';
  id: Id;
  session: string;
  stdout: string;
  stderr: string;
  results: CaseResult[];
  timing: { boot_ms: number; run_ms: number; restart_ms: number };
  status: Status;
  interrupts: 'sab' | 'restart';
  session_new: boolean;
  truncated: boolean;
  segments: Segment[];
}
export interface ReadyReply {
  type: 'ready';
  id: Id;
  python: string;
  pyodide: string;
  isolated: boolean;
  boot_ms: number;
}
export interface RestartedReply {
  type: 'restarted';
  id: Id;
  boot_ms: number;
}
export type Reply = ResultReply | ReadyReply | RestartedReply;

// Limits, as in the schemas.
export const LIMITS = {
  code: 500_000,
  stdin: 2_000_000,
  files: 64,
  fileData: 8_000_000,
  filePath: 200,
  expected: 2_000_000,
  asserts: 200,
  assertSource: 100_000,
  budgetMin: 100,
  budgetMax: 60_000,
  results: 300,
  caseName: 200,
  caseDetail: 2000,
  segments: 10_000,
  color: 100,
  python: 200,
  pyodide: 50,
} as const;

const ID = /^[A-Za-z0-9_-]{1,64}$/;
const PATH = /^[A-Za-z0-9_-][A-Za-z0-9_.-]*(\/[A-Za-z0-9_-][A-Za-z0-9_.-]*)*$/;

type Obj = Record<string, unknown>;

/** A JSON-like plain object whose keys are exactly `required` (all present, nothing else). */
function exact(value: unknown, required: readonly string[]): value is Obj {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) return false;
  const proto = Object.getPrototypeOf(value);
  if (proto !== Object.prototype && proto !== null) return false;
  const keys = Object.keys(value);
  return keys.length === required.length && required.every((k) => Object.hasOwn(value, k));
}

// JSON Schema's maxLength counts code points, not UTF-16 units.
function codePoints(s: string): number {
  let n = 0;
  for (const _ of s) n++;
  return n;
}
const str = (v: unknown, max?: number): v is string =>
  typeof v === 'string' && (max === undefined || v.length <= max || codePoints(v) <= max);
const bool = (v: unknown): v is boolean => typeof v === 'boolean';
const num = (v: unknown): v is number => typeof v === 'number' && Number.isFinite(v);
const ms = (v: unknown): v is number => num(v) && v >= 0;
const id = (v: unknown): v is string => typeof v === 'string' && ID.test(v);
const arrayOf = (v: unknown, max: number, item: (x: unknown) => boolean, min = 0): v is unknown[] =>
  Array.isArray(v) && v.length >= min && v.length <= max && v.every(item);

function isFile(v: unknown): boolean {
  return (
    exact(v, ['path', 'data', 'encoding']) &&
    str(v.path, LIMITS.filePath) &&
    PATH.test(v.path) &&
    str(v.data, LIMITS.fileData) &&
    (v.encoding === 'utf-8' || v.encoding === 'base64')
  );
}

function isCheck(v: unknown): boolean {
  if (v === null) return true;
  if (typeof v !== 'object' || Array.isArray(v)) return false;
  const kind = (v as Obj).kind;
  if (kind === 'output') return exact(v, ['kind', 'turtle']) && bool(v.turtle);
  if (kind === 'fixture')
    return (
      exact(v, ['kind', 'expected', 'match', 'turtle']) &&
      str(v.expected, LIMITS.expected) &&
      (v.match === 'line' || v.match === 'token') &&
      bool(v.turtle)
    );
  if (kind === 'asserts')
    return (
      exact(v, ['kind', 'asserts', 'turtle']) &&
      arrayOf(v.asserts, LIMITS.asserts, (a) => str(a, LIMITS.assertSource), 1) &&
      bool(v.turtle)
    );
  return false;
}

/** The request if `data` is a valid site -> runner envelope, else `null`. */
export function parseRequest(data: unknown): Request | null {
  if (typeof data !== 'object' || data === null) return null;
  switch ((data as Obj).type) {
    case 'run':
      return exact(data, ['type', 'id', 'session', 'code', 'stdin', 'files', 'check', 'budget_ms']) &&
        id(data.id) &&
        id(data.session) &&
        str(data.code, LIMITS.code) &&
        str(data.stdin, LIMITS.stdin) &&
        arrayOf(data.files, LIMITS.files, isFile) &&
        isCheck(data.check) &&
        Number.isInteger(data.budget_ms) &&
        (data.budget_ms as number) >= LIMITS.budgetMin &&
        (data.budget_ms as number) <= LIMITS.budgetMax
        ? (data as unknown as RunRequest)
        : null;
    case 'reset':
      return exact(data, ['type', 'id', 'session']) && id(data.id) && id(data.session)
        ? (data as unknown as ResetRequest)
        : null;
    case 'ping':
    case 'interrupt':
      return exact(data, ['type', 'id']) && id(data.id) ? (data as unknown as PingRequest | InterruptRequest) : null;
    default:
      return null;
  }
}

function isCase(v: unknown): boolean {
  return (
    exact(v, ['name', 'pass', 'detail']) &&
    str(v.name, LIMITS.caseName) &&
    bool(v.pass) &&
    str(v.detail, LIMITS.caseDetail)
  );
}

function isSegment(v: unknown): boolean {
  return (
    exact(v, ['x1', 'y1', 'x2', 'y2', 'color', 'width']) &&
    num(v.x1) &&
    num(v.y1) &&
    num(v.x2) &&
    num(v.y2) &&
    str(v.color, LIMITS.color) &&
    num(v.width)
  );
}

/** The reply if `data` is a valid runner -> site envelope, else `null`. */
export function parseReply(data: unknown): Reply | null {
  if (typeof data !== 'object' || data === null) return null;
  switch ((data as Obj).type) {
    case 'result': {
      const keys = ['type', 'id', 'session', 'stdout', 'stderr', 'results', 'timing', 'status', 'interrupts', 'session_new', 'truncated', 'segments'];
      if (!exact(data, keys)) return null;
      const t = data.timing;
      return id(data.id) &&
        id(data.session) &&
        str(data.stdout) &&
        str(data.stderr) &&
        arrayOf(data.results, LIMITS.results, isCase) &&
        exact(t, ['boot_ms', 'run_ms', 'restart_ms']) &&
        ms(t.boot_ms) &&
        ms(t.run_ms) &&
        ms(t.restart_ms) &&
        ['ok', 'error', 'timeout', 'interrupted'].includes(data.status as string) &&
        (data.interrupts === 'sab' || data.interrupts === 'restart') &&
        bool(data.session_new) &&
        bool(data.truncated) &&
        arrayOf(data.segments, LIMITS.segments, isSegment)
        ? (data as unknown as ResultReply)
        : null;
    }
    case 'ready':
      return exact(data, ['type', 'id', 'python', 'pyodide', 'isolated', 'boot_ms']) &&
        id(data.id) &&
        str(data.python, LIMITS.python) &&
        str(data.pyodide, LIMITS.pyodide) &&
        bool(data.isolated) &&
        ms(data.boot_ms)
        ? (data as unknown as ReadyReply)
        : null;
    case 'restarted':
      return exact(data, ['type', 'id', 'boot_ms']) && id(data.id) && ms(data.boot_ms)
        ? (data as unknown as RestartedReply)
        : null;
    default:
      return null;
  }
}

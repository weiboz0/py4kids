/**
 * The runner's message envelopes (design 012 D7, plan 104 "Message boundary"), shared by the
 * runner page and the site's client (site/src/lib/runner-client.ts).
 *
 * The browser cannot run Ajv (it compiles validators with `new Function`, which both CSPs forbid),
 * so `parseRequest` and `parseReply` are hand-written twins of `runner/schema/request.schema.json`
 * and `runner/schema/reply.schema.json`; `runner/test/envelope.test.ts` proves they agree with Ajv
 * on valid and mutated envelopes. Anything that does not validate is dropped by the caller.
 *
 * **Schema version (plan 105).** The current envelope version is `ENVELOPE_VERSION` (2): every
 * message the site sends carries `v: 2`. Version 1 is plan 104's envelope, identical but without
 * `v`. Each runner release must accept version N−1 too (the update handshake leaves runner B
 * serving site A until the site's worker activates), so the runner accepts both and answers in
 * the request's own version. The site accepts only its own version. A request whose `v` is newer
 * than the runner's is answered with `version-mismatch` (a version-independent reply), so a newer
 * site page talking to an older runner asks for a reload.
 * Version 2 adds the offline messages: `precache` (cache a book's runner files and confirm it
 * for a release) with `precache-progress` and `precached`, and the update handshake's
 * `prepare-activate` with `runner-activated`.
 */

export type Id = string;

/** The envelope schema version this code speaks (plan 105); version 1 is plan 104's. */
export const ENVELOPE_VERSION = 2;
/** The versions the runner accepts: its own and the one before (N−1). */
export const ACCEPTED_VERSIONS = [1, 2] as const;
export type Version = (typeof ACCEPTED_VERSIONS)[number];
/** Present (2) on a version-2 message, absent on a version-1 message. */
interface Versioned {
  v?: 2;
}

export interface RunFile {
  path: string;
  data: string;
  encoding: 'utf-8' | 'base64';
}

export type Check =
  | { kind: 'output'; turtle: boolean }
  | { kind: 'fixture'; expected: string; match: 'line' | 'token'; turtle: boolean }
  | { kind: 'asserts'; asserts: string[]; turtle: boolean };

export interface RunRequest extends Versioned {
  type: 'run';
  id: Id;
  session: string;
  code: string;
  stdin: string;
  files: RunFile[];
  check: Check | null;
  budget_ms: number;
}
export interface ResetRequest extends Versioned {
  type: 'reset';
  id: Id;
  session: string;
}
export interface PingRequest extends Versioned {
  type: 'ping';
  id: Id;
}
export interface InterruptRequest extends Versioned {
  type: 'interrupt';
  id: Id;
}
/**
 * Version 2: cache this book's runner files, with the shell and Pyodide, and confirm the book for
 * `release_id` (refused when it is not the runner's own release). `files` are runner-origin paths
 * (none today: fixture and asset files live on the site origin and travel inside `run`).
 */
export interface PrecacheRequest {
  v: 2;
  type: 'precache';
  id: Id;
  book: string;
  content_hash: string;
  files: string[];
  release_id: string;
}
/** Version 2: the update handshake's step 1 (activate the runner's waiting worker for `release_id`). */
export interface PrepareActivateRequest {
  v: 2;
  type: 'prepare-activate';
  id: Id;
  release_id: string;
}
export type Request = RunRequest | ResetRequest | PingRequest | InterruptRequest | PrecacheRequest | PrepareActivateRequest;

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
export interface ResultReply extends Versioned {
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
export interface ReadyReply extends Versioned {
  type: 'ready';
  id: Id;
  python: string;
  pyodide: string;
  isolated: boolean;
  boot_ms: number;
}
export interface RestartedReply extends Versioned {
  type: 'restarted';
  id: Id;
  boot_ms: number;
}
/** Version 2: progress of a `precache` (bytes now in the runner's caches, of `total`). */
export interface PrecacheProgressReply {
  v: 2;
  type: 'precache-progress';
  id: Id;
  bytes: number;
  total: number;
}
/** Version 2: the answer to `precache`; `persisted` is the runner's own persist() result (informational). */
export interface PrecachedReply {
  v: 2;
  type: 'precached';
  id: Id;
  ok: boolean;
  bytes: number;
  persisted: boolean;
}
/** Version 2: the update handshake's step 2 is done (the runner's worker for `release_id` controls it). */
export interface RunnerActivatedReply {
  v: 2;
  type: 'runner-activated';
  id: Id;
  release_id: string;
}
/** Any version: the request's `v` is newer than this runner speaks (`supported`): reload. */
export interface VersionMismatchReply {
  type: 'version-mismatch';
  id: Id;
  supported: number[];
}
export type Reply =
  | ResultReply
  | ReadyReply
  | RestartedReply
  | PrecacheProgressReply
  | PrecachedReply
  | RunnerActivatedReply
  | VersionMismatchReply;

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
  precacheFiles: 5000,
  precachePath: 300,
} as const;

/** A release id (deploy/release.mjs) or a book content hash: 64 lower-case hex digits. */
const HEX64 = /^[0-9a-f]{64}$/;
/** A book id (a folder name in books.yaml). */
const BOOK = /^[a-z0-9][a-z0-9-]{0,63}$/;
/** A runner-origin path: absolute, no `.`-led segment (so no `..`), no query. */
const ORIGIN_PATH = /^\/(?:[A-Za-z0-9_-][A-Za-z0-9_.-]*\/)*(?:[A-Za-z0-9_-][A-Za-z0-9_.-]*)?$/;

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

/**
 * The keys of a message that has `base` keys in version 1: version 2 adds `v`, which must be 2.
 * Returns null when `v` is present but not 2.
 */
function versionKeys(data: object, base: string[]): string[] | null {
  if (!Object.hasOwn(data, 'v')) return base;
  return (data as Obj).v === 2 ? [...base, 'v'] : null;
}

/** `data`'s envelope version: 1 without `v`, else its `v` when it is an integer (or null). */
export function versionOf(data: unknown): number | null {
  if (typeof data !== 'object' || data === null || Array.isArray(data)) return null;
  if (!Object.hasOwn(data, 'v')) return 1;
  const v = (data as Obj).v;
  return Number.isInteger(v) ? (v as number) : null;
}

/** The request if `data` is a valid site -> runner envelope (version 1 or 2), else `null`. */
export function parseRequest(data: unknown): Request | null {
  if (typeof data !== 'object' || data === null) return null;
  const k = (base: string[]) => versionKeys(data, base) ?? ['(invalid v)'];
  switch ((data as Obj).type) {
    case 'run':
      return exact(data, k(['type', 'id', 'session', 'code', 'stdin', 'files', 'check', 'budget_ms'])) &&
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
      return exact(data, k(['type', 'id', 'session'])) && id(data.id) && id(data.session)
        ? (data as unknown as ResetRequest)
        : null;
    case 'ping':
    case 'interrupt':
      return exact(data, k(['type', 'id'])) && id(data.id) ? (data as unknown as PingRequest | InterruptRequest) : null;
    case 'precache':
      return exact(data, ['v', 'type', 'id', 'book', 'content_hash', 'files', 'release_id']) &&
        data.v === 2 &&
        id(data.id) &&
        typeof data.book === 'string' &&
        BOOK.test(data.book) &&
        typeof data.content_hash === 'string' &&
        HEX64.test(data.content_hash) &&
        arrayOf(data.files, LIMITS.precacheFiles, (f) => str(f, LIMITS.precachePath) && ORIGIN_PATH.test(f as string)) &&
        typeof data.release_id === 'string' &&
        HEX64.test(data.release_id)
        ? (data as unknown as PrecacheRequest)
        : null;
    case 'prepare-activate':
      return exact(data, ['v', 'type', 'id', 'release_id']) &&
        data.v === 2 &&
        id(data.id) &&
        typeof data.release_id === 'string' &&
        HEX64.test(data.release_id)
        ? (data as unknown as PrepareActivateRequest)
        : null;
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

/** The reply if `data` is a valid runner -> site envelope (version 1 or 2), else `null`. */
export function parseReply(data: unknown): Reply | null {
  if (typeof data !== 'object' || data === null) return null;
  const k = (base: string[]) => versionKeys(data, base) ?? ['(invalid v)'];
  switch ((data as Obj).type) {
    case 'result': {
      const keys = k(['type', 'id', 'session', 'stdout', 'stderr', 'results', 'timing', 'status', 'interrupts', 'session_new', 'truncated', 'segments']);
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
      return exact(data, k(['type', 'id', 'python', 'pyodide', 'isolated', 'boot_ms'])) &&
        id(data.id) &&
        str(data.python, LIMITS.python) &&
        str(data.pyodide, LIMITS.pyodide) &&
        bool(data.isolated) &&
        ms(data.boot_ms)
        ? (data as unknown as ReadyReply)
        : null;
    case 'restarted':
      return exact(data, k(['type', 'id', 'boot_ms'])) && id(data.id) && ms(data.boot_ms)
        ? (data as unknown as RestartedReply)
        : null;
    case 'precache-progress':
      return exact(data, ['v', 'type', 'id', 'bytes', 'total']) && data.v === 2 && id(data.id) && ms(data.bytes) && ms(data.total)
        ? (data as unknown as PrecacheProgressReply)
        : null;
    case 'precached':
      return exact(data, ['v', 'type', 'id', 'ok', 'bytes', 'persisted']) &&
        data.v === 2 &&
        id(data.id) &&
        bool(data.ok) &&
        ms(data.bytes) &&
        bool(data.persisted)
        ? (data as unknown as PrecachedReply)
        : null;
    case 'runner-activated':
      return exact(data, ['v', 'type', 'id', 'release_id']) &&
        data.v === 2 &&
        id(data.id) &&
        typeof data.release_id === 'string' &&
        HEX64.test(data.release_id)
        ? (data as unknown as RunnerActivatedReply)
        : null;
    case 'version-mismatch':
      return exact(data, ['type', 'id', 'supported']) &&
        id(data.id) &&
        arrayOf(data.supported, 16, (n) => Number.isInteger(n) && (n as number) >= 1, 1)
        ? (data as unknown as VersionMismatchReply)
        : null;
    default:
      return null;
  }
}

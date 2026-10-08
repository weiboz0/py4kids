/**
 * The site page's side of the installable, offline site (design 012 D10; plan 105 Phase A):
 * the update check and registration, this page's release, "download this book" (the site's
 * worker plus the runner's precache), a book's offline status, and the page-mediated update
 * handshake. The UI is in src/scripts/pwa.ts and src/scripts/offline-book.ts.
 *
 * - **Update check:** one `GET /release.json` with `cache: "no-store"` per page load (never
 *   answered by the worker); on success the worker is registered as `/sw.js?r=<release_id>`. On
 *   failure (offline, servers down) the current registration stays: no error, no banner.
 * - **Offline status** (plan 105 "Offline status"): "available" only when the site's record and the
 *   runner's own record (asked through the runner iframe, `get-state`) name the same release and
 *   content. Until the runner answers the status is "checking"; a runner without the record (its
 *   storage was cleared) is "runner-missing", one that cannot be asked "unverified".
 * - **Download:** the site's part fails as stalled when no progress arrives for 60 s.
 * - **Handshake** (plan 105 "Activation is user-controlled, page-mediated"), offered only when this
 *   page is the site's only window, each step with a 10 s timeout:
 *     0. while the runner's next release is still installing (a new Pyodide is about 15 MB), the
 *        page says "Preparing the update…" and waits (at most 5 minutes) before step 1;
 *     1. the runner iframe gets `prepare-activate`; 2. it activates its waiting worker and answers
 *     `runner-activated`; 3. the site's waiting worker gets `skip-waiting`; 4. on the site's
 *     `controllerchange` the page reloads.
 *   Forward-only recovery: a failure before step 2 leaves both origins on the old release ("update
 *   failed — try again"); after it, step 3 is retried ("finishing the update…"), each attempt with
 *   the waiting worker read afresh (a newer one is accepted), at most 5 times, then the page simply
 *   reloads; meanwhile it keeps working (the runner accepts the previous envelope version); after
 *   step 3, the reload is retried.
 * - **Test hooks** (`window.__py4kidsPwaTest`, see `TestHooks`): built in only when the build sets
 *   PY4KIDS_TEST_HOOKS=1 (`import.meta.env.PY4KIDS_TEST_HOOKS`, false otherwise, so the minifier
 *   drops them from production builds; scripts/build-release.sh refuses a test build).
 */
import { RunnerUnavailableError, type RunnerClient } from './runner-client';
import { putRecord, getRecord } from '../../../runner/src/offline-store';
import { bookStatus, releaseOfScript, STEP_TIMEOUT_MS, workerScriptUrl, type BookStatus, type OfflineRecord } from '../../../runner/src/offline';

export interface BookSummary {
  content_hash: string;
  bytes: number;
  count: number;
  manifest: string;
}
export interface WorkerStatus {
  release_id: string;
  books: Record<string, BookSummary>;
  runner: { bytes: number };
}

const TEST_HOOKS: boolean = import.meta.env.PY4KIDS_TEST_HOOKS === true;

/** A site download with no progress for this long has stalled. */
export const STALL_MS = 60_000;
/** How long the handshake waits for the runner's next release to finish installing. */
export const PREPARE_CAP_MS = 5 * 60_000;
/** Step 3 (the site's worker) is tried this many times before the page simply reloads. */
export const SITE_ATTEMPTS = 5;
/** How long the runner may take to report its state (it loads, then reads its own store). */
const STATE_TIMEOUT_MS = 2 * STEP_TIMEOUT_MS;

/** The download stopped making progress. */
export class StalledError extends Error {
  constructor() {
    super('the download stopped');
    this.name = 'StalledError';
  }
}

// ------------------------------------------------------------------------------------------------
// Test hooks (test builds only)

/**
 * The update-handshake steps a test can force to fail. (The runner step fails in the runner page
 * itself, `__py4kidsRunnerTest.swallowPrepareActivate`, so the real request times out.)
 */
export type Step = 'site' | 'reload';
/** Points a test can pause at: before step 1, after the runner activated, after the site activated. */
export type PausePoint = 'before-runner' | 'after-runner' | 'after-site';

export interface TestHooks {
  /** Pause the handshake at a point until `resume(point)`. */
  pause(point: PausePoint): void;
  resume(point: PausePoint): void;
  /** Make a step fail its next `times` attempts. */
  fail(step: Step, times?: number): void;
  /** The handshake's step timeout in ms (default 10 000). */
  stepTimeoutMs: number;
  /** How long the handshake waits for the runner's next release to install, in ms (default 5 min). */
  prepareCapMs: number;
  /** A pause before each chunk of a book download, in ms (default 0), so a test can stop the servers mid-download. */
  downloadDelayMs: number;
  /** A site download with no progress for this long, in ms, has stalled (default 60 000). */
  downloadStallMs: number;
  /**
   * Where the handshake is: idle, preparing, runner, site, reload, failed, finishing, gave-up,
   * paused:<point>, done.
   */
  state: string;
  /** Every state the handshake passed through, in order. */
  log: string[];
}

interface HookState {
  paused: Set<PausePoint>;
  waiters: Map<PausePoint, () => void>;
  failures: Map<Step, number>;
  api: TestHooks;
}
let hooks: HookState | null = null;

function testHooks(): HookState | null {
  if (!TEST_HOOKS) return null;
  if (!hooks) {
    const h: HookState = {
      paused: new Set(),
      waiters: new Map(),
      failures: new Map(),
      api: {
        pause: (p) => void h.paused.add(p),
        resume: (p) => {
          h.paused.delete(p);
          h.waiters.get(p)?.();
          h.waiters.delete(p);
        },
        fail: (step, times = 1) => void h.failures.set(step, times),
        stepTimeoutMs: STEP_TIMEOUT_MS,
        prepareCapMs: PREPARE_CAP_MS,
        downloadDelayMs: 0,
        downloadStallMs: STALL_MS,
        state: 'idle',
        log: [],
      },
    };
    hooks = h;
    (globalThis as unknown as { __py4kidsPwaTest: TestHooks }).__py4kidsPwaTest = h.api;
  }
  return hooks;
}
if (TEST_HOOKS) testHooks();

function setState(state: string): void {
  const h = testHooks();
  if (h) {
    h.api.state = state;
    h.api.log.push(state);
  }
}

async function pausePoint(point: PausePoint): Promise<void> {
  const h = testHooks();
  if (!h || !h.paused.has(point)) return;
  setState(`paused:${point}`);
  await new Promise<void>((resolve) => h.waiters.set(point, resolve));
}

function forcedFailure(step: Step): boolean {
  const h = testHooks();
  const n = h?.failures.get(step) ?? 0;
  if (!h || n <= 0) return false;
  h.failures.set(step, n - 1);
  return true;
}

const stepTimeout = () => testHooks()?.api.stepTimeoutMs ?? STEP_TIMEOUT_MS;
const prepareCap = () => testHooks()?.api.prepareCapMs ?? PREPARE_CAP_MS;
const stallTimeout = () => testHooks()?.api.downloadStallMs ?? STALL_MS;

/** `record[key]` for an own key only (keys come from pages and data attributes). */
const own = <T>(record: Record<string, T> | undefined, key: string): T | undefined =>
  record && Object.hasOwn(record, key) ? record[key] : undefined;

// ------------------------------------------------------------------------------------------------
// Registration and releases

const container = (): ServiceWorkerContainer | null =>
  typeof navigator !== 'undefined' && 'serviceWorker' in navigator ? navigator.serviceWorker : null;

/** Can this browser keep the site offline at all? */
export const offlineSupported = (): boolean => container() !== null && typeof caches !== 'undefined' && typeof indexedDB !== 'undefined';

/** The release of the worker that served this page, captured at load (null: not served by one). */
const loadedUnder: string | null = releaseOfScript(container()?.controller?.scriptURL);
let pageRelease: string | null = loadedUnder;

let checked: Promise<string | null> | null = null;
/** The update check: the release `/release.json` names (once per page load), or null. */
export function serverRelease(): Promise<string | null> {
  checked ??= (async () => {
    try {
      const response = await fetch('/release.json', { cache: 'no-store', credentials: 'same-origin' });
      if (!response.ok) return null;
      const body = (await response.json()) as { release_id?: unknown };
      return typeof body.release_id === 'string' && /^[0-9a-f]{64}$/.test(body.release_id) ? body.release_id : null;
    } catch {
      return null;
    }
  })();
  return checked;
}

let registering: Promise<ServiceWorkerRegistration | null> | null = null;
/**
 * Register the worker for the server's release (or keep the current registration when the check
 * fails). Also answers the worker's `which-release`, and asks a worker of this page's own
 * release to clean up the old releases' caches.
 */
export function startPwa(): Promise<ServiceWorkerRegistration | null> {
  registering ??= (async () => {
    const sw = container();
    if (!sw) return null;
    sw.addEventListener('message', (event: MessageEvent<{ type?: unknown }>) => {
      if (event.data?.type === 'which-release') event.ports[0]?.postMessage({ release_id: pageRelease });
    });
    const id = await serverRelease();
    pageRelease ??= id;
    let reg: ServiceWorkerRegistration | null = null;
    try {
      reg = id ? await sw.register(workerScriptUrl(id), { scope: '/', updateViaCache: 'none' }) : ((await sw.getRegistration('/')) ?? null);
    } catch {
      return null; // blocked or unavailable: the site works online without it
    }
    // A page of the current release asks its worker to delete the other releases' caches; again a
    // little later, since a page of the old release may still be closing (it blocks cleanup).
    if (id && loadedUnder === id) for (const ms of [0, 3000, 15000]) setTimeout(requestCleanup, ms);
    return reg;
  })();
  return registering;
}

/** Ask the controlling worker (of this page's own release) to delete old releases' caches. */
export function requestCleanup(): void {
  const controller = container()?.controller;
  if (controller && pageRelease && releaseOfScript(controller.scriptURL) === pageRelease) controller.postMessage({ type: 'cleanup' });
}

/** The active worker's release (what serves this origin now), or null. */
export async function activeRelease(): Promise<string | null> {
  const sw = container();
  if (!sw) return null;
  const reg = await sw.getRegistration('/');
  return releaseOfScript(reg?.active?.scriptURL);
}

/** A waiting worker of a newer release than the one serving this page, or null. */
export async function pendingUpdate(): Promise<string | null> {
  const sw = container();
  const reg = await sw?.getRegistration('/');
  const waiting = releaseOfScript(reg?.waiting?.scriptURL);
  return waiting && waiting !== releaseOfScript(reg?.active?.scriptURL) ? waiting : null;
}

/**
 * Send `message` to `worker` with a reply port; resolves with the first reply that is not
 * progress. `timeoutMs` bounds the whole exchange; `stallMs` fails it with `StalledError` when no
 * message (progress included) arrives for that long. 0: no limit.
 */
function ask<T>(
  worker: ServiceWorker,
  message: object,
  onMessage?: (data: Record<string, unknown>) => void,
  { timeoutMs = 0, stallMs = 0 }: { timeoutMs?: number; stallMs?: number } = {},
): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const channel = new MessageChannel();
    let stall: ReturnType<typeof setTimeout> | undefined;
    const end = () => {
      clearTimeout(timer);
      clearTimeout(stall);
      channel.port1.onmessage = null;
      channel.port1.close();
    };
    const timer = timeoutMs > 0 ? setTimeout(() => (end(), reject(new Error('the service worker did not answer'))), timeoutMs) : undefined;
    const watch = () => {
      clearTimeout(stall);
      if (stallMs > 0) stall = setTimeout(() => (end(), reject(new StalledError())), stallMs);
    };
    channel.port1.onmessage = (event: MessageEvent<Record<string, unknown>>) => {
      if (event.data?.type === 'progress') {
        watch();
        onMessage?.(event.data);
        return;
      }
      end();
      resolve(event.data as T);
    };
    watch();
    worker.postMessage(message, [channel.port2]);
  });
}

async function activeWorker(timeoutMs = STEP_TIMEOUT_MS): Promise<ServiceWorker | null> {
  const sw = container();
  if (!sw) return null;
  await startPwa();
  const ready = await Promise.race([sw.ready, new Promise<null>((r) => setTimeout(() => r(null), timeoutMs))]);
  return ready?.active ?? null;
}

/** The active worker's release and its books' download sizes. */
export async function workerStatus(): Promise<WorkerStatus | null> {
  const worker = await activeWorker();
  if (!worker) return null;
  try {
    return await ask<WorkerStatus>(worker, { type: 'status' }, undefined, { timeoutMs: STEP_TIMEOUT_MS });
  } catch {
    return null;
  }
}

/** How many site windows are open (the update is offered only to the only one). */
export async function windowCount(): Promise<number> {
  const worker = await activeWorker();
  if (!worker) return 1;
  try {
    return (await ask<{ count: number }>(worker, { type: 'client-count' }, undefined, { timeoutMs: STEP_TIMEOUT_MS })).count;
  } catch {
    return 2; // unknown: do not risk activating under another open page
  }
}

// ------------------------------------------------------------------------------------------------
// A book offline

/**
 * A book's offline status on this page: the site record's (`BookStatus`), and, once the site's
 * record says "available", what the runner's own record says:
 * - `runner-missing`: the runner answered without a matching record (its storage was cleared,
 *   while the site's was kept): Python cannot run offline; download again;
 * - `unverified`: the runner could not be asked (it did not load or answer), so "available" cannot
 *   be confirmed.
 */
export type OfflineStatus = BookStatus | 'runner-missing' | 'unverified';

export interface BookState {
  status: OfflineStatus;
  record: OfflineRecord | null;
  summary: BookSummary | null;
  /** The runner's share (shell and Pyodide), downloaded once for every book. */
  runnerBytes: number;
  activeRelease: string | null;
}

/**
 * The book's state from the site's record. With `verifyRunner`, a book the site's record shows as
 * available is "available" only if the runner's own record (asked through the runner iframe)
 * names the same content and release; it is never taken on the site record's word alone.
 */
export async function bookState(book: string, verifyRunner?: () => Promise<RunnerClient>): Promise<BookState> {
  const [record, status] = await Promise.all([getRecord(book).catch(() => null), workerStatus()]);
  const active = status?.release_id ?? (await activeRelease());
  const state: BookState = {
    status: bookStatus(record, active),
    record,
    summary: own(status?.books, book) ?? null,
    runnerBytes: status?.runner.bytes ?? 0,
    activeRelease: active,
  };
  if (state.status === 'available' && record && verifyRunner) state.status = await runnerConfirms(book, record, verifyRunner);
  return state;
}

/** Does the runner's own record confirm `record` (same content hash and release)? */
async function runnerConfirms(book: string, record: OfflineRecord, connect: () => Promise<RunnerClient>): Promise<OfflineStatus> {
  try {
    const client = await connect();
    const { record: theirs } = await client.state(book, STATE_TIMEOUT_MS);
    return theirs && theirs.content_hash === record.content_hash && theirs.release_id === record.release_id ? 'available' : 'runner-missing';
  } catch {
    return 'unverified';
  }
}

export interface DownloadProgress {
  siteBytes: number;
  siteTotal: number;
  runnerBytes: number;
  runnerTotal: number;
}
export interface DownloadResult {
  ok: boolean;
  /** The runner's own persist() result (informational). */
  runnerPersisted: boolean | null;
  /** The site's part stopped making progress (`StalledError`). */
  stalled?: boolean;
  /** For the console, never shown to the student. */
  error?: string;
}

/**
 * Ask for persistent storage. Call it synchronously inside the click handler (Firefox prompts,
 * and only for a user gesture); the result comes later.
 */
export function requestPersistence(): Promise<boolean> {
  try {
    const p = navigator.storage?.persist?.();
    return p ? p.then((v) => v === true, () => false) : Promise.resolve(false);
  } catch {
    return Promise.resolve(false);
  }
}

/**
 * Download `book` for offline use: the site's worker caches the site's files and confirms its
 * record; the runner (through the page's runner iframe) caches its own and confirms; then the
 * site record notes the runner's confirmation. "Available offline" needs both.
 */
export async function downloadBook(
  book: string,
  connect: () => Promise<RunnerClient>,
  onProgress: (p: DownloadProgress) => void,
): Promise<DownloadResult> {
  const worker = await activeWorker();
  if (!worker) return { ok: false, runnerPersisted: null, error: 'This browser cannot keep the site offline.' };
  const status = await workerStatus();
  const summary = own(status?.books, book);
  if (!status || !summary) return { ok: false, runnerPersisted: null, error: 'This book is not in this version of the site.' };
  const progress: DownloadProgress = { siteBytes: 0, siteTotal: summary.bytes, runnerBytes: 0, runnerTotal: status.runner.bytes };
  const delay = testHooks()?.api.downloadDelayMs ?? 0;
  // No overall limit (a book can take long on a slow link), but a stall fails it: no progress
  // message from the site's worker for `stallTimeout()` (a new download aborts the stalled one).
  const site = ask<{ ok: boolean; error?: string }>(
    worker,
    { type: 'download', book, ...(delay > 0 ? { delay_ms: delay } : {}) },
    (p) => {
      progress.siteBytes = Number(p.bytes) || 0;
      progress.siteTotal = Number(p.total) || progress.siteTotal;
      onProgress({ ...progress });
    },
    { stallMs: stallTimeout() },
  ).catch((error: unknown) => ({ ok: false, stalled: error instanceof StalledError, error: String(error) }));
  const runner = (async () => {
    try {
      const client = await connect();
      return await client.precache({ book, content_hash: summary.content_hash, release_id: status.release_id }, (bytes, total) => {
        progress.runnerBytes = bytes;
        progress.runnerTotal = total || progress.runnerTotal;
        onProgress({ ...progress });
      });
    } catch (error) {
      return { ok: false, persisted: null, error: error instanceof RunnerUnavailableError ? error.message : String(error) };
    }
  })();
  // A failed site download ends the attempt at once (the runner's part, if it is still running,
  // is left to finish or fail on its own; nothing is confirmed without the site's record).
  const siteDone: { ok: boolean; stalled?: boolean; error?: string } = await site;
  if (!siteDone.ok) return { ok: false, runnerPersisted: null, stalled: siteDone.stalled === true, error: siteDone.error ?? 'The download did not finish.' };
  const runnerDone = await runner;
  const runnerPersisted = 'persisted' in runnerDone ? (runnerDone.persisted as boolean | null) : null;
  if (!runnerDone.ok) return { ok: false, runnerPersisted, error: 'Python could not be stored for offline use.' };
  // Written after the site worker's own record (which it wrote last in its download).
  const record = await getRecord(book);
  if (!record || record.release_id !== status.release_id) return { ok: false, runnerPersisted, error: 'The download was not confirmed.' };
  await putRecord({ ...record, runner_release_id: status.release_id });
  onProgress({ ...progress, siteBytes: progress.siteTotal, runnerBytes: progress.runnerTotal });
  requestCleanup();
  return { ok: true, runnerPersisted };
}

// ------------------------------------------------------------------------------------------------
// The update handshake

export type UpdateOutcome = 'busy' | 'failed' | 'reloading';

function waitFor(predicate: () => boolean | Promise<boolean>, event: { target: EventTarget; type: string } | null, ms: number): Promise<boolean> {
  return new Promise((resolve) => {
    let done = false;
    const finish = (v: boolean) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      clearInterval(poll);
      event?.target.removeEventListener(event.type, check);
      resolve(v);
    };
    const check = () => void Promise.resolve(predicate()).then((ok) => ok && finish(true));
    const timer = setTimeout(() => finish(false), ms);
    const poll = setInterval(check, 100);
    event?.target.addEventListener(event.type, check);
    check();
  });
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/**
 * Accept "a new version is available — reload": run the handshake. `say` shows a message.
 * Resolves `busy` (another site window is open), `failed` (before the runner activated: both
 * origins stay on the old release), or `reloading`.
 */
/**
 * Step 0: wait while the runner's next release is still installing (its new Pyodide can take a
 * while), saying "Preparing the update…", at most `prepareCap()`. Resolves false when the cap ran
 * out. A runner that cannot report its state (an older one) is not waited for.
 */
async function runnerInstalled(client: RunnerClient, target: string, say: (message: string) => void): Promise<boolean> {
  const deadline = Date.now() + prepareCap();
  for (;;) {
    let state;
    try {
      state = await client.state(null, stepTimeout());
    } catch {
      return true; // no state: let step 1 decide within its own timeout
    }
    if (state.active === target || state.waiting === target || !state.installing) return true;
    if (Date.now() >= deadline) return false;
    setState('preparing');
    say('Preparing the update…');
    await sleep(Math.min(1000, Math.max(0, deadline - Date.now())));
  }
}

export async function applyUpdate(connect: () => Promise<RunnerClient>, say: (message: string) => void): Promise<UpdateOutcome> {
  const sw = container();
  const target = await pendingUpdate();
  if (!sw || !target) return 'failed';
  if ((await windowCount()) > 1) {
    say('Close your other py4kids tabs to update.');
    return 'busy';
  }
  /**
   * The release the site runs now: step 3 is done once another one is active. An uncontrolled page
   * (a hard reload, the first load) takes it from the registration's active worker, so the old
   * active release never counts as the new one ([fable] content review round 2).
   */
  const from = releaseOfScript(sw.controller?.scriptURL) ?? releaseOfScript((await sw.getRegistration('/'))?.active?.scriptURL);
  await pausePoint('before-runner');
  // Steps 0-2: the runner activates first, once its next release has installed.
  say('Updating…');
  try {
    const client = await Promise.race([connect(), sleep(stepTimeout()).then(() => Promise.reject(new Error('runner timeout')))]);
    if (!(await runnerInstalled(client, target, say))) {
      setState('failed');
      say('The update is taking too long to download. Try again later.');
      return 'failed';
    }
    setState('runner');
    say('Updating…');
    await client.prepareActivate(target, stepTimeout());
  } catch {
    setState('failed');
    say('Update failed — try again.');
    return 'failed';
  }
  await pausePoint('after-runner');
  // Step 3, retried (forward only: the runner is already on the new release). Each attempt reads
  // the waiting worker afresh, so a newer release that replaced the one first offered is accepted.
  setState('site');
  const isNew = (release: string | null) => release !== null && release !== from;
  const siteActive = async () =>
    sw.controller ? isNew(releaseOfScript(sw.controller.scriptURL)) : isNew(releaseOfScript((await sw.getRegistration('/'))?.active?.scriptURL));
  for (let attempt = 0; !(await siteActive()); attempt++) {
    if (attempt >= SITE_ATTEMPTS) {
      // Give up on the handshake and reload: the reloaded page runs on whichever release is active
      // and offers the update again if one is still waiting.
      setState('gave-up');
      say('Finishing the update…');
      location.reload();
      return 'reloading';
    }
    if (attempt > 0) {
      setState('finishing');
      say('Finishing the update…');
      await sleep(Math.min(1000 * attempt, 5000));
    }
    if (forcedFailure('site')) {
      await sleep(stepTimeout());
      continue;
    }
    const waiting = (await sw.getRegistration('/'))?.waiting;
    if (waiting && isNew(releaseOfScript(waiting.scriptURL))) waiting.postMessage({ type: 'skip-waiting' });
    await waitFor(siteActive, { target: sw, type: 'controllerchange' }, stepTimeout());
  }
  await pausePoint('after-site');
  // Step 4: reload, retried.
  setState('reload');
  for (;;) {
    if (forcedFailure('reload')) {
      setState('finishing');
      say('Finishing the update…');
      await sleep(1000);
      continue;
    }
    setState('done');
    location.reload();
    return 'reloading';
  }
}

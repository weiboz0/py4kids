/**
 * The runner page (design 012 D7, plan 104): the sandboxed iframe on the runner origin that owns
 * the Python workers.
 *
 * - **Boundary.** A message is accepted only if `event.origin` is the site origin,
 *   `event.source === window.parent`, and it validates as a request envelope; replies go to
 *   `window.parent` with the exact site origin as `targetOrigin`. Anything else is dropped.
 * - **Workers.** At most three Pyodide workers exist: the lesson worker, one prewarmed spare,
 *   and the worker running a check. Every check (and every fixture case: the site sends one run
 *   per case) takes the spare, which is retired after that run; the next spare starts booting the
 *   moment the current one is handed out (pipelined). Lesson sessions share the lesson worker;
 *   `reset` restarts it.
 * - **Interrupts.** This page allocates a SharedArrayBuffer per worker (`setInterruptBuffer`) and
 *   owns the budget timer. On expiry (or `interrupt`, the Stop button) it raises SIGINT in Python;
 *   if the worker has not answered 1 s later (the student caught KeyboardInterrupt), or the page
 *   is not cross-origin isolated, it terminates the worker and restarts. Every result reports
 *   `interrupts: "sab"` (the worker survived) or `"restart"`.
 * - **Envelope versions (plan 105).** Requests of version 2 and of version 1 (N−1, plan 104's,
 *   without `v`) are both served, and each is answered in its own version; a request newer than
 *   this runner gets `version-mismatch`.
 * - **Offline (plan 105 Phase B).** `precache` is forwarded to this origin's service worker
 *   (pwa-page.ts); `prepare-activate` is the runner's step of the update handshake.
 */
import { ACCEPTED_VERSIONS, ENVELOPE_VERSION, parseReply, parseRequest, versionOf, type ResultReply, type Reply, type RunRequest, type Request } from './envelope';
import { activate, persist, precache, requestCleanup, startPwa } from './pwa-page';
import type { FromWorker, HarnessOut, Job, ToWorker } from './worker';

// Build-time constants (scripts/build.ts).
declare const ORIGIN_PAIRS: { site: string; runner: string }[];
declare const WORKER_URL: string;

/**
 * The one site origin this runner serves: the partner of this runner's own origin in
 * deploy/origins.json (a production build also lists the preview pair), else the primary pair's.
 */
const SITE_ORIGIN: string = (ORIGIN_PAIRS.find((p) => p.runner === location.origin) ?? ORIGIN_PAIRS[0]!).site;

export const GRACE_MS = 1000;
export const MAX_WORKERS = 3;
const SIGINT = 2;

interface BootInfo {
  python: string;
  pyodide: string;
  isolated: boolean;
  boot_ms: number;
}

let alive = 0;

class PyWorker {
  readonly worker: Worker;
  readonly interrupt: Int32Array | null;
  readonly booted: Promise<BootInfo>;
  bootInfo: BootInfo | null = null;
  private onDone: ((message: FromWorker) => void) | null = null;
  dead = false;

  constructor() {
    if (alive >= MAX_WORKERS) throw new Error(`more than ${MAX_WORKERS} Python workers`);
    alive++;
    this.worker = new Worker(WORKER_URL, { name: 'py4kids-python' });
    this.interrupt = self.crossOriginIsolated ? new Int32Array(new SharedArrayBuffer(4)) : null;
    this.booted = new Promise<BootInfo>((resolve, reject) => {
      this.worker.onmessage = (event: MessageEvent<FromWorker>) => {
        const message = event.data;
        if (message.type === 'booted') {
          this.bootInfo = message;
          resolve(message);
        } else if (message.type === 'boot-failed') {
          reject(new Error(message.error));
        } else {
          this.onDone?.(message);
        }
      };
      this.worker.onerror = (event) => {
        event.preventDefault();
        reject(new Error(event.message || 'worker error'));
        this.onDone?.({ type: 'crashed', error: event.message || 'worker error' });
      };
    });
    // A failed boot is reported to whoever awaits it; never an unhandled rejection.
    this.booted.catch(() => {});
    this.post({ type: 'boot', interrupt: this.interrupt });
  }

  post(message: ToWorker): void {
    this.worker.postMessage(message);
  }

  /** Run one job; resolves with the worker's answer (`done` or `crashed`). */
  start(job: Job, onAnswer: (message: FromWorker) => void): void {
    if (this.interrupt) Atomics.store(this.interrupt, 0, 0);
    this.onDone = onAnswer;
    this.post({ type: 'run', job });
  }

  terminate(): void {
    if (this.dead) return;
    this.dead = true;
    this.worker.terminate();
    alive--;
  }
}

// --- the pool ----------------------------------------------------------------------------------

let spare: PyWorker | null = null;
let lesson: PyWorker | null = null;

function ensureSpare(): void {
  if (!spare && alive < MAX_WORKERS) spare = new PyWorker();
}

/** Hand out the spare (booting or booted) and start the next one at once. */
function takeSpare(): PyWorker {
  ensureSpare();
  const taken = spare;
  if (!taken) throw new Error('no worker available');
  spare = null;
  ensureSpare();
  return taken;
}

/** One queue per worker kind: checks run one at a time, lesson runs one at a time. */
function queue() {
  let tail: Promise<unknown> = Promise.resolve();
  return <T>(task: () => Promise<T>): Promise<T> => {
    const next = tail.then(task, task);
    tail = next.catch(() => {});
    return next;
  };
}
const checkQueue = queue();
const lessonQueue = queue();

/** Stop functions of running jobs, and ids of queued jobs a Stop arrived for, by request id. */
const running = new Map<string, () => void>();
const cancelled = new Set<string>();
const queued = new Set<string>();

// --- running a job -----------------------------------------------------------------------------

function emptyOut(stderr: string): HarnessOut {
  return { stdout: '', stderr, status: 'interrupted', results: [], session_new: false, truncated: false, segments: [] };
}

function result(req: RunRequest, out: HarnessOut, fields: Pick<ResultReply, 'status' | 'interrupts' | 'timing'>): ResultReply {
  return {
    type: 'result',
    id: req.id,
    session: req.session,
    stdout: out.stdout,
    stderr: out.stderr,
    results: out.results,
    session_new: out.session_new,
    truncated: out.truncated,
    segments: out.segments,
    ...fields,
  };
}

/**
 * Run `req` on `w` within its budget. `onKilled` is called if the worker had to be terminated
 * (the caller restarts what it needs).
 */
async function execute(w: PyWorker, req: RunRequest, onKilled: () => void): Promise<ResultReply> {
  const waitStart = performance.now();
  try {
    await w.booted;
  } catch (error) {
    w.terminate();
    onKilled();
    return result(req, { ...emptyOut(`Python could not start: ${String(error)}\n`), status: 'error' }, {
      status: 'error',
      interrupts: 'restart',
      timing: { boot_ms: performance.now() - waitStart, run_ms: 0, restart_ms: 0 },
    });
  }
  const boot_ms = performance.now() - waitStart;
  const job: Job = { session: req.session, code: req.code, stdin: req.stdin, files: req.files, check: req.check };

  return new Promise<ResultReply>((resolve) => {
    const started = performance.now();
    let reason: 'timeout' | 'interrupted' | null = null;
    let budgetTimer: ReturnType<typeof setTimeout> | undefined;
    let graceTimer: ReturnType<typeof setTimeout> | undefined;
    let settled = false;

    const settle = (reply: ResultReply) => {
      if (settled) return;
      settled = true;
      clearTimeout(budgetTimer);
      clearTimeout(graceTimer);
      running.delete(req.id);
      resolve(reply);
    };

    const kill = () => {
      const restartStart = performance.now();
      w.terminate();
      onKilled();
      const status = reason ?? 'error';
      const note = status === 'timeout' ? 'time limit: Python was restarted\n' : status === 'interrupted' ? 'stopped: Python was restarted\n' : 'Python stopped unexpectedly and was restarted\n';
      const out = emptyOut(note);
      if (req.check?.kind === 'fixture') out.results = [{ name: 'case', pass: false, detail: status === 'timeout' ? 'time limit' : status === 'interrupted' ? 'stopped' : 'Python stopped unexpectedly' }];
      settle(
        result(req, out, {
          status,
          interrupts: 'restart',
          timing: { boot_ms, run_ms: restartStart - started, restart_ms: performance.now() - restartStart },
        }),
      );
    };

    const stop = (why: 'timeout' | 'interrupted') => {
      if (reason || settled) return;
      reason = why;
      if (w.interrupt) {
        Atomics.store(w.interrupt, 0, SIGINT);
        graceTimer = setTimeout(kill, GRACE_MS);
      } else {
        kill();
      }
    };

    running.set(req.id, () => stop('interrupted'));
    budgetTimer = setTimeout(() => stop('timeout'), req.budget_ms);

    w.start(job, (message) => {
      if (message.type === 'crashed') {
        kill();
        return;
      }
      if (message.type !== 'done') return;
      const out = message.out;
      let status: ResultReply['status'] = out.status === 'interrupted' ? 'interrupted' : out.status;
      if (reason) {
        // The budget ran out or Stop was pressed: whatever Python did after the interrupt (a
        // swallowed KeyboardInterrupt that then finished) does not count.
        status = reason;
        if (req.check?.kind === 'fixture') out.results = [{ name: 'case', pass: false, detail: reason === 'timeout' ? 'time limit' : 'stopped' }];
        else out.results = [];
        if (reason === 'timeout' && !/time limit/.test(out.stderr)) out.stderr += 'time limit\n';
      }
      settle(result(req, out, { status, interrupts: 'sab', timing: { boot_ms, run_ms: performance.now() - started, restart_ms: 0 } }));
    });
  });
}

async function runCheck(req: RunRequest): Promise<ResultReply> {
  const w = takeSpare();
  try {
    return await execute(w, req, () => {});
  } finally {
    // Retire the check's worker: one Python process per check, never reused.
    w.terminate();
    ensureSpare();
  }
}

function lessonWorker(): PyWorker {
  if (!lesson || lesson.dead) lesson = takeSpare();
  return lesson;
}

async function runLesson(req: RunRequest): Promise<ResultReply> {
  const w = lessonWorker();
  return execute(w, req, () => {
    if (lesson === w) lesson = null;
    ensureSpare();
  });
}

function stopped(req: RunRequest): ResultReply {
  return result(req, emptyOut('stopped\n'), { status: 'interrupted', interrupts: 'sab', timing: { boot_ms: 0, run_ms: 0, restart_ms: 0 } });
}

// --- the boundary ------------------------------------------------------------------------------

/** A reply without its version: `send` adds `v` to match the request's. */
type Unversioned = Reply extends infer R ? (R extends Reply ? Omit<R, 'v'> : never) : never;

function post(message: Reply): void {
  // Validated on the way out too: the site drops anything that does not validate.
  if (!parseReply(message)) {
    console.error('runner: refusing to send an invalid reply', message.type, message.id);
    return;
  }
  window.parent.postMessage(message, SITE_ORIGIN);
}

async function handle(req: Request): Promise<void> {
  // Answer in the request's own envelope version (version 1 has no `v`).
  const v2 = versionOf(req) === ENVELOPE_VERSION;
  const reply = (message: Unversioned) => post((v2 ? { v: ENVELOPE_VERSION, ...message } : message) as Reply);
  switch (req.type) {
    case 'ping': {
      ensureSpare();
      const w = spare ?? lesson;
      if (!w) return;
      try {
        const info = await w.booted;
        reply({ type: 'ready', id: req.id, python: info.python, pyodide: info.pyodide, isolated: self.crossOriginIsolated && info.isolated, boot_ms: info.boot_ms });
      } catch (error) {
        console.error('runner: Python failed to boot', error);
      }
      return;
    }
    case 'interrupt': {
      const stop = running.get(req.id);
      if (stop) stop();
      else if (queued.has(req.id)) cancelled.add(req.id);
      return;
    }
    case 'reset': {
      await lessonQueue(async () => {
        if (lesson) {
          lesson.terminate();
          lesson = null;
        }
        const w = lessonWorker();
        const started = performance.now();
        try {
          await w.booted;
        } catch {
          return;
        }
        reply({ type: 'restarted', id: req.id, boot_ms: performance.now() - started });
      });
      return;
    }
    case 'run': {
      queued.add(req.id);
      const q = req.check === null ? lessonQueue : checkQueue;
      const out = await q(async () => {
        queued.delete(req.id);
        if (cancelled.delete(req.id)) return stopped(req);
        return req.check === null ? runLesson(req) : runCheck(req);
      });
      const { v: _, ...unversioned } = out as ResultReply & { v?: 2 };
      reply(unversioned);
      return;
    }
    case 'precache': {
      // Ask for persistent storage here too; the result is informational (the site's counts).
      const persisted = persist();
      let lastSent = 0;
      const done = await precache(
        { book: req.book, content_hash: req.content_hash, files: req.files, release_id: req.release_id },
        (bytes, total) => {
          const now = performance.now();
          if (now - lastSent < 250) return;
          lastSent = now;
          reply({ type: 'precache-progress', id: req.id, bytes, total });
        },
      );
      reply({ type: 'precached', id: req.id, ok: done.ok, bytes: done.bytes, persisted: await persisted });
      if (done.ok) requestCleanup();
      return;
    }
    case 'prepare-activate': {
      // Step 2 of the update handshake; no answer when it cannot happen (the site's step times out).
      if (await activate(req.release_id)) reply({ type: 'runner-activated', id: req.id, release_id: req.release_id });
      return;
    }
  }
}

window.addEventListener('message', (event: MessageEvent) => {
  if (window.parent === window) return;
  if (event.origin !== SITE_ORIGIN || event.source !== window.parent) return;
  const req = parseRequest(event.data);
  if (!req) {
    // A newer site page (a version this runner does not speak): tell it, so it asks for a reload.
    const v = versionOf(event.data);
    const id = (event.data as { id?: unknown }).id;
    if (v !== null && v > ENVELOPE_VERSION && typeof id === 'string' && /^[A-Za-z0-9_-]{1,64}$/.test(id)) {
      post({ type: 'version-mismatch', id, supported: [...ACCEPTED_VERSIONS] });
    }
    return;
  }
  void handle(req);
});

// Test hook (Playwright reads it in the runner frame): how many Python workers exist.
(globalThis as unknown as { py4kidsRunner: object }).py4kidsRunner = {
  workers: () => alive,
  isolated: () => self.crossOriginIsolated,
};

// Prewarm: boot the first spare as soon as the page loads; check for an update (plan 105).
if (window.parent !== window) {
  ensureSpare();
  void startPwa();
}

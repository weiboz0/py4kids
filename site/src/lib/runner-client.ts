/**
 * The site's side of the runner boundary (design 012 D7, plan 104 Phase A). The site never runs
 * student code itself: it embeds the runner page (a separate origin) in a sandboxed iframe and
 * talks to it only through `postMessage` with schema-validated envelopes
 * (runner/schema/*.json; runner/src/envelope.ts is their hand-written twin).
 *
 * - Every message is posted with the exact runner origin as `targetOrigin`, never `*`: if the
 *   iframe has been navigated elsewhere the browser drops it, so code never reaches another page.
 * - A reply is accepted only if `event.origin` is the runner origin, `event.source` is the
 *   iframe's window, it validates as a reply envelope, and its `id` (and type, and for a result
 *   its session) matches a pending request. Anything else is dropped; a completed id is gone.
 * - Every request has a timeout; on expiry it rejects with `RunnerUnavailableError` (the UI shows
 *   the runner as unavailable and offers a reload).
 *
 * Phase B's check UIs build on `connectRunner` (or `RunnerClient` directly in tests).
 */
import {
  parseReply,
  parseRequest,
  type Check,
  type ReadyReply,
  type Reply,
  type Request,
  type RestartedReply,
  type ResultReply,
  type RunFile,
} from '../../../runner/src/envelope';

export type { Check, ReadyReply, RestartedReply, ResultReply, RunFile } from '../../../runner/src/envelope';

/** The runner origin, from runner/origins.json (or PY4KIDS_RUNNER_ORIGIN) via astro.config.mjs. */
export const RUNNER_ORIGIN: string =
  (import.meta.env as Record<string, string | undefined>).PY4KIDS_RUNNER_ORIGIN ?? '';

/** The iframe's sandbox and permissions (plan 104 Global constraints). */
export const SANDBOX = 'allow-scripts allow-same-origin';
export const ALLOW = 'cross-origin-isolated';

/** The runner's grace period after an interrupt before it restarts the worker. */
export const GRACE_MS = 1000;
/** Default budget of a run that is not a fixture case (plan 104 "Budgets"). */
export const DEFAULT_BUDGET_MS = 5000;

export interface Timeouts {
  /** ping and reset (both may wait for Python to boot). */
  bootMs: number;
  /** Added to a run's budget and grace: queueing behind other runs, a fresh worker's boot. */
  runSlackMs: number;
}
export const DEFAULT_TIMEOUTS: Timeouts = { bootMs: 60_000, runSlackMs: 60_000 };

export class RunnerUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RunnerUnavailableError';
  }
}

/** The window the client posts to (the iframe's `contentWindow`). */
export interface RunnerPort {
  postMessage(message: unknown, targetOrigin: string): void;
}

/** What a received message must carry (a `MessageEvent` has these). */
export interface Incoming {
  origin: string;
  source: unknown;
  data: unknown;
}

export interface RunnerClientOptions {
  runnerOrigin: string;
  /** The iframe's current window: replies must come from it (`event.source`). */
  frame: () => RunnerPort | null;
  /** Subscribe to the page's `message` events; returns the unsubscribe function. */
  listen: (handler: (event: Incoming) => void) => () => void;
  /** Resolves when the runner page has loaded (messages wait for it). */
  loaded?: Promise<void>;
  timeouts?: Partial<Timeouts>;
  newId?: () => string;
}

export interface RunOptions {
  session: string;
  code: string;
  stdin?: string;
  files?: RunFile[];
  check?: Check | null;
  budget_ms?: number;
}

interface Pending {
  type: Reply['type'];
  session?: string;
  resolve: (reply: Reply) => void;
  reject: (error: Error) => void;
  timer: ReturnType<typeof setTimeout>;
}

/** Why `receive` dropped a message (for tests and debugging); `accepted` when it did not. */
export type Verdict = 'accepted' | 'wrong-origin' | 'wrong-source' | 'invalid' | 'unknown-id';

export class RunnerClient {
  private readonly pending = new Map<string, Pending>();
  private readonly unlisten: () => void;
  private readonly timeouts: Timeouts;
  private readonly newId: () => string;
  private readonly options: RunnerClientOptions;
  private disposed = false;

  constructor(options: RunnerClientOptions) {
    this.options = options;
    if (!options.runnerOrigin || new URL(options.runnerOrigin).origin !== options.runnerOrigin) {
      throw new Error(`not a runner origin: ${options.runnerOrigin}`);
    }
    this.timeouts = { ...DEFAULT_TIMEOUTS, ...options.timeouts };
    this.newId = options.newId ?? (() => crypto.randomUUID());
    this.unlisten = options.listen((event) => {
      this.receive(event);
    });
  }

  /** Handle one incoming message: resolve its pending request, or drop it. */
  receive(event: Incoming): Verdict {
    if (event.origin !== this.options.runnerOrigin) return 'wrong-origin';
    const frame = this.options.frame();
    if (!frame || event.source !== frame) return 'wrong-source';
    const reply = parseReply(event.data);
    if (!reply) return 'invalid';
    const pending = this.pending.get(reply.id);
    if (!pending || pending.type !== reply.type) return 'unknown-id';
    if (reply.type === 'result' && reply.session !== pending.session) return 'unknown-id';
    this.pending.delete(reply.id);
    clearTimeout(pending.timer);
    pending.resolve(reply);
    return 'accepted';
  }

  private async post(request: Request): Promise<void> {
    if (!parseRequest(request)) throw new TypeError(`invalid runner request (${request.type})`);
    await this.options.loaded;
    const frame = this.options.frame();
    if (!frame) throw new RunnerUnavailableError('the runner frame is gone');
    frame.postMessage(request, this.options.runnerOrigin);
  }

  private request<T extends Reply>(request: Request, type: T['type'], timeoutMs: number, session?: string): Promise<T> {
    if (this.disposed) return Promise.reject(new RunnerUnavailableError('the runner client is closed'));
    if (this.pending.has(request.id)) return Promise.reject(new Error(`duplicate request id ${request.id}`));
    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(request.id);
        reject(new RunnerUnavailableError(`the runner did not answer (${request.type})`));
      }, timeoutMs);
      this.pending.set(request.id, { type, session, resolve: resolve as (r: Reply) => void, reject, timer });
      this.post(request).catch((error: unknown) => {
        clearTimeout(timer);
        this.pending.delete(request.id);
        reject(error instanceof Error ? error : new Error(String(error)));
      });
    });
  }

  /** Is a request with this id still waiting? */
  isPending(id: string): boolean {
    return this.pending.has(id);
  }

  /** Is Python booted? Resolves with its versions and boot time. */
  ping(): Promise<ReadyReply> {
    return this.request<ReadyReply>({ type: 'ping', id: this.newId() }, 'ready', this.timeouts.bootMs);
  }

  /**
   * Run code. `id` names the run (for `interrupt`); `result` resolves with the runner's result.
   * A `check` runs in a fresh Python worker; `check: null` runs in the lesson session.
   */
  run(options: RunOptions): { id: string; result: Promise<ResultReply> } {
    const id = this.newId();
    const budget = options.budget_ms ?? DEFAULT_BUDGET_MS;
    const request: Request = {
      type: 'run',
      id,
      session: options.session,
      code: options.code,
      stdin: options.stdin ?? '',
      files: options.files ?? [],
      check: options.check ?? null,
      budget_ms: budget,
    };
    const timeout = budget + GRACE_MS + this.timeouts.runSlackMs;
    return { id, result: this.request<ResultReply>(request, 'result', timeout, options.session) };
  }

  /** The Stop button: the run's own result answers (status `interrupted`). */
  interrupt(runId: string): void {
    if (!this.pending.has(runId)) return;
    void this.post({ type: 'interrupt', id: runId }).catch(() => {});
  }

  /** Clear a lesson session (the runner restarts the lesson worker). */
  reset(session: string): Promise<RestartedReply> {
    return this.request<RestartedReply>({ type: 'reset', id: this.newId(), session }, 'restarted', this.timeouts.bootMs);
  }

  /** Stop listening and reject everything still pending. */
  dispose(): void {
    this.disposed = true;
    this.unlisten();
    for (const [id, pending] of this.pending) {
      clearTimeout(pending.timer);
      pending.reject(new RunnerUnavailableError('the runner client is closed'));
      this.pending.delete(id);
    }
  }
}

/** The runner iframe: sandboxed, cross-origin-isolated-capable, hidden (it has no UI). */
export function createRunnerFrame(parent: HTMLElement, runnerOrigin: string = RUNNER_ORIGIN): HTMLIFrameElement {
  const iframe = parent.ownerDocument.createElement('iframe');
  // sandbox and allow must be set before src: they apply at navigation.
  iframe.setAttribute('sandbox', SANDBOX);
  iframe.setAttribute('allow', ALLOW);
  iframe.title = 'Python runner';
  iframe.hidden = true;
  iframe.tabIndex = -1;
  iframe.setAttribute('aria-hidden', 'true');
  iframe.src = `${runnerOrigin}/`;
  parent.append(iframe);
  return iframe;
}

/** Create the runner iframe in `parent` and a client bound to it. */
export function connectRunner(
  parent: HTMLElement,
  runnerOrigin: string = RUNNER_ORIGIN,
  timeouts?: Partial<Timeouts>,
): { iframe: HTMLIFrameElement; client: RunnerClient } {
  const win = parent.ownerDocument.defaultView;
  if (!win) throw new Error('connectRunner: the parent is not in a window');
  const iframe = createRunnerFrame(parent, runnerOrigin);
  const loaded = new Promise<void>((resolve) => iframe.addEventListener('load', () => resolve(), { once: true }));
  const client = new RunnerClient({
    runnerOrigin,
    frame: () => iframe.contentWindow,
    listen: (handler) => {
      const listener = (event: MessageEvent) => handler(event);
      win.addEventListener('message', listener);
      return () => win.removeEventListener('message', listener);
    },
    loaded,
    timeouts,
  });
  return { iframe, client };
}

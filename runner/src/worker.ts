/**
 * The runner's Web Worker (plan 104 "Architecture"): boots the self-hosted Pyodide, loads the
 * Python harness (runner/py/harness.py, with the fake_turtle port) and executes `run` jobs.
 *
 * It only ever talks to the runner page that created it (same origin, a dedicated worker); the
 * page owns the budget timer and the SharedArrayBuffer interrupt (it hands the buffer over at
 * boot) and terminates this worker when an interrupt is swallowed. One worker is one Python
 * process: the page gives each check (and each fixture case) a fresh worker, and lesson sessions
 * share one.
 *
 * Built as a classic worker (IIFE) so `importScripts` can load Pyodide's `pyodide.js`.
 */
/// <reference lib="webworker" />
import type { loadPyodide as LoadPyodide, PyodideInterface } from 'pyodide';
import HARNESS from '../py/harness.py';
import FAKE_TURTLE from '../py/fake_turtle.py';
import type { Check, RunFile } from './envelope';

// Build-time constants (scripts/build.ts).
declare const PYODIDE_INDEX: string;
declare const PYODIDE_VERSION: string;

declare const self: DedicatedWorkerGlobalScope & { loadPyodide: typeof LoadPyodide };

/** The page -> worker messages. */
export type ToWorker =
  | { type: 'boot'; interrupt: Int32Array | null }
  | { type: 'run'; job: Job };

export interface Job {
  session: string;
  code: string;
  stdin: string;
  files: RunFile[];
  check: Check | null;
}

/** The worker -> page messages. */
export type FromWorker =
  | { type: 'booted'; python: string; pyodide: string; isolated: boolean; boot_ms: number }
  | { type: 'boot-failed'; error: string }
  | { type: 'done'; out: HarnessOut }
  | { type: 'crashed'; error: string };

/** What harness.handle returns. */
export interface HarnessOut {
  stdout: string;
  stderr: string;
  status: 'ok' | 'error' | 'interrupted';
  results: { name: string; pass: boolean; detail: string }[];
  session_new: boolean;
  truncated: boolean;
  segments: { x1: number; y1: number; x2: number; y2: number; color: string; width: number }[];
}

const LIB = '/home/pyodide/py4kids-runner';
let handle: ((request: string) => string) | null = null;

// Captured before any student code runs: `seal` removes `postMessage` from the global scope.
const postToPage = self.postMessage.bind(self);

function post(message: FromWorker): void {
  postToPage(message);
}

/** Every global that can make a request, start a script or reach another context. */
const SEALED = [
  'fetch', 'fetchLater', 'XMLHttpRequest', 'importScripts', 'EventSource', 'WebSocket', 'WebSocketStream',
  'WebTransport', 'Worker', 'SharedWorker', 'BroadcastChannel', 'caches', 'indexedDB', 'postMessage',
];
const SEALED_NAVIGATOR = ['serviceWorker', 'sendBeacon'];

/** Delete `names` from `target` and every object on its prototype chain; true when none is left. */
function strip(target: object, names: string[]): boolean {
  for (let o: object | null = target; o; o = Object.getPrototypeOf(o)) {
    for (const name of names) {
      if (Object.prototype.hasOwnProperty.call(o, name)) Reflect.deleteProperty(o, name);
    }
  }
  return names.every((name) => !(name in target));
}

/**
 * [sol] plan 104 content review: student Python reaches this scope through Pyodide's `js`
 * module, so once Pyodide and the harness have loaded (nothing more is fetched: the page sends
 * code, stdin and files inside each job) every way to make a request, load a script or post a
 * message is deleted from the global scope, its prototypes and the navigator. `eval` is already
 * blocked by the runner's CSP (no 'unsafe-eval'), so a deleted constructor cannot be rebuilt.
 * Failing closed: a browser where a name cannot be removed does not boot.
 */
function seal(): void {
  if (!strip(self, SEALED) || !strip(self.navigator, SEALED_NAVIGATOR)) {
    throw new Error('the runner could not remove network access from Python');
  }
}

async function boot(interrupt: Int32Array | null): Promise<void> {
  const started = performance.now();
  try {
    self.importScripts(`${PYODIDE_INDEX}pyodide.js`);
    const pyodide: PyodideInterface = await self.loadPyodide({
      indexURL: PYODIDE_INDEX,
      // The harness captures the student's streams; anything Pyodide itself prints is dropped.
      stdout: () => {},
      stderr: () => {},
    });
    if (pyodide.version !== PYODIDE_VERSION) throw new Error(`Pyodide ${pyodide.version}, expected ${PYODIDE_VERSION}`);
    if (interrupt) pyodide.setInterruptBuffer(interrupt);
    pyodide.FS.mkdirTree(LIB);
    pyodide.FS.writeFile(`${LIB}/harness.py`, HARNESS);
    pyodide.FS.writeFile(`${LIB}/fake_turtle.py`, FAKE_TURTLE);
    // Import the harness, then take its directory off sys.path (a student's own module named
    // `harness` must not be shadowed by it).
    const python = pyodide.runPython(
      `import sys\nsys.path.insert(0, ${JSON.stringify(LIB)})\nimport harness\nsys.path.remove(${JSON.stringify(LIB)})\nsys.version`,
    ) as string;
    const fn = pyodide.pyimport('harness').handle as (request: string) => string;
    handle = (request) => fn(request);
    seal();
    post({
      type: 'booted',
      python,
      pyodide: pyodide.version,
      isolated: self.crossOriginIsolated,
      boot_ms: performance.now() - started,
    });
  } catch (error) {
    post({ type: 'boot-failed', error: String(error) });
  }
}

function run(job: Job): void {
  if (!handle) {
    post({ type: 'crashed', error: 'Python is not booted' });
    return;
  }
  try {
    post({ type: 'done', out: JSON.parse(handle(JSON.stringify(job))) as HarnessOut });
  } catch (error) {
    // A KeyboardInterrupt that escaped the harness, or an internal error.
    const text = String(error);
    if (/KeyboardInterrupt/.test(text)) {
      post({
        type: 'done',
        out: { stdout: '', stderr: 'KeyboardInterrupt\n', status: 'interrupted', results: [], session_new: false, truncated: false, segments: [] },
      });
    } else {
      post({ type: 'crashed', error: text.slice(0, 2000) });
    }
  }
}

self.onmessage = (event: MessageEvent<ToWorker>) => {
  const message = event.data;
  if (message?.type === 'boot') void boot(message.interrupt);
  else if (message?.type === 'run') run(message.job);
};

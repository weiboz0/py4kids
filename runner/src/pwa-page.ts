/**
 * The runner page's side of the offline runner (plan 105 Phase B): the update check and service
 * worker registration, the release it reports, cleanup, `precache` forwarding and the runner's
 * step of the update handshake. Imported by main.ts.
 *
 * - **Update check:** one `GET /release.json` (`cache: "no-store"`, never answered by the worker)
 *   per page load; on success the worker is registered as `/sw.js?r=<release_id>` (a new id is a
 *   new script URL, so the browser installs the new worker, which then waits). On failure
 *   (offline) the current registration stays, silently.
 * - **This page's release** is the release of the worker that controlled it at load, else the one
 *   `/release.json` named; the worker asks it (`which-release`) before deleting old caches.
 */
import { releaseOfScript, STEP_TIMEOUT_MS, workerScriptUrl } from './offline';

const sw: ServiceWorkerContainer | undefined = 'serviceWorker' in navigator ? navigator.serviceWorker : undefined;

/** The release of the worker that served this page, captured at load. */
const loadedUnder = releaseOfScript(sw?.controller?.scriptURL);
let pageRelease: string | null = loadedUnder;

let checked: Promise<string | null> | null = null;
/** The update check (once per page): the release `/release.json` names, or null (offline). */
export function releaseChecked(): Promise<string | null> {
  checked ??= fetchRelease();
  return checked;
}

async function fetchRelease(): Promise<string | null> {
  try {
    const response = await fetch('/release.json', { cache: 'no-store', credentials: 'same-origin' });
    if (!response.ok) return null;
    const id = (await response.json()) as { release_id?: unknown };
    return typeof id.release_id === 'string' && /^[0-9a-f]{64}$/.test(id.release_id) ? id.release_id : null;
  } catch {
    return null; // offline: keep the current registration, no error, no banner
  }
}

/** Register the worker for the server's release and keep this page's release current. */
export async function startPwa(): Promise<void> {
  if (!sw) return;
  sw.addEventListener('message', (event: MessageEvent<{ type?: unknown }>) => {
    if (event.data?.type === 'which-release') event.ports[0]?.postMessage({ release_id: pageRelease });
  });
  const id = await releaseChecked();
  pageRelease ??= id;
  if (!id) return;
  try {
    await sw.register(workerScriptUrl(id), { scope: '/', updateViaCache: 'none' });
  } catch {
    return; // service workers unavailable (blocked, private mode): the runner works online
  }
  // A page of the current release asks its worker to delete the other releases' caches; again a
  // little later, since a page of the old release may still be closing (it blocks cleanup).
  if (loadedUnder && loadedUnder === id) for (const ms of CLEANUP_AFTER_MS) setTimeout(requestCleanup, ms);
}

/** When a page of the current release asks for cleanup (ms after load). */
const CLEANUP_AFTER_MS = [0, 3000, 15000];

/** Ask the controlling worker (of this page's own release) to delete old releases' caches. */
export function requestCleanup(): void {
  const controller = sw?.controller;
  if (controller && pageRelease && releaseOfScript(controller.scriptURL) === pageRelease) controller.postMessage({ type: 'cleanup' });
}

/** The active worker's release, or null. */
export async function activeRelease(): Promise<string | null> {
  if (!sw) return null;
  const reg = await sw.getRegistration('/');
  return releaseOfScript(reg?.active?.scriptURL);
}

/**
 * Forward a `precache` to the active worker. Resolves `{ ok, bytes }`; progress is reported as
 * the worker caches files.
 */
export async function precache(
  message: { book: string; content_hash: string; files: string[]; release_id: string },
  onProgress: (bytes: number, total: number) => void,
): Promise<{ ok: boolean; bytes: number }> {
  if (!sw) return { ok: false, bytes: 0 };
  const reg = await withTimeout(sw.ready, STEP_TIMEOUT_MS).catch(() => null);
  const active = reg?.active;
  if (!active) return { ok: false, bytes: 0 };
  return new Promise((resolve) => {
    const channel = new MessageChannel();
    channel.port1.onmessage = (event: MessageEvent<{ type: string; ok?: boolean; bytes?: number; total?: number }>) => {
      const data = event.data;
      if (data.type === 'progress') onProgress(data.bytes ?? 0, data.total ?? 0);
      else if (data.type === 'done') {
        channel.port1.close();
        resolve({ ok: data.ok === true, bytes: data.bytes ?? 0 });
      }
    };
    active.postMessage({ type: 'precache', ...message }, [channel.port2]);
  });
}

/** `navigator.storage.persist()` on the runner origin (informational: the site's result counts). */
export async function persist(): Promise<boolean> {
  try {
    return (await navigator.storage?.persist?.()) === true;
  } catch {
    return false;
  }
}

function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('timeout')), ms);
    promise.then(
      (v) => {
        clearTimeout(timer);
        resolve(v);
      },
      (e: unknown) => {
        clearTimeout(timer);
        reject(e instanceof Error ? e : new Error(String(e)));
      },
    );
  });
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/**
 * The update handshake's step 2 (plan 105): make the worker for `releaseId` control this page.
 * If it already does, done at once (the step is idempotent). Otherwise wait for it to finish
 * installing, tell it to `skipWaiting`, and wait for this page's `controllerchange` (or, for a
 * page no worker controlled, for it to become the active worker). Resolves true when done, false
 * when it did not happen within the step timeout.
 */
export async function activate(releaseId: string, timeoutMs = STEP_TIMEOUT_MS): Promise<boolean> {
  if (!sw) return false;
  const deadline = Date.now() + timeoutMs;
  const controls = () => releaseOfScript(sw.controller?.scriptURL) === releaseId;
  while (Date.now() < deadline) {
    if (controls()) return true;
    const reg = await sw.getRegistration('/');
    if (!sw.controller && releaseOfScript(reg?.active?.scriptURL) === releaseId) return true;
    const waiting = reg?.waiting;
    if (waiting && releaseOfScript(waiting.scriptURL) === releaseId) {
      const changed = new Promise<void>((resolve) => sw.addEventListener('controllerchange', () => resolve(), { once: true }));
      waiting.postMessage({ type: 'skip-waiting' });
      await Promise.race([changed, sleep(Math.max(0, deadline - Date.now()))]);
      continue;
    }
    // Still installing (or this page's own update check has not registered it yet).
    await sleep(100);
  }
  return controls();
}

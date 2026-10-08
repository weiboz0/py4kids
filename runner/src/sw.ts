/**
 * The runner origin's service worker (design 012 D10; plan 105 Phase B), hand-written: no Workbox,
 * no CDN. Registered by the runner page as `/sw.js?r=<release_id>` (its own release, from
 * `/release.json`); the script is byte-identical across releases unless this code changes.
 *
 * - **Caches** (runner/src/offline.ts): `shell-<release_id>` (the page and its content-hashed
 *   assets, `worker-<hash>.js` included), `pyodide-<dir>` (the versioned Pyodide runtime, shared by
 *   every book) and `book-<book>-<content_hash>` (a book's runner-origin files; none today).
 * - **First use:** shell and Pyodide responses are cached as the runner fetches them (no request
 *   of its own); `precache` fetches whatever is still missing, then the book's files, and writes
 *   the confirmed record last. With a confirmed book on this origin, a newly installing release
 *   also completes its shell and Pyodide before it can activate, so an update never strands a
 *   downloaded book.
 * - **Serving:** an exact URL from any retained cache (every asset URL is release-specific, so an
 *   exact match is the right file whoever asks, the Python workers included), cloned with the
 *   COOP/COEP/CORP headers set, so `crossOriginIsolated` holds offline. The page itself (a
 *   navigation) comes from the current shell first. `/release.json` and `/sw.js` are never
 *   intercepted (network only).
 * - **Activation is page-mediated:** no `skipWaiting` on install; the page sends `skip-waiting`
 *   during the update handshake. `activate` deletes nothing; `cleanup` (from a page of this
 *   release) deletes other releases' shell and Pyodide caches once no client runs another release.
 *   On start, the active worker sweeps `book-*` caches without a confirmed record.
 * - **Privacy:** it requests nothing but this origin's own release files and the files a precache
 *   names; no push, sync or analytics.
 */
/// <reference lib="webworker" />
import { allRecords, putRecord } from './offline-store';
import {
  bookCacheName,
  chunks,
  cleanupPlan,
  normaliseNavigation,
  parseCacheName,
  pyodideCacheName,
  releaseOfScript,
  replacedBookCaches,
  RUNNER_ISOLATION,
  shellCacheName,
  sweepPlan,
  withIsolation,
  type OfflineRecord,
} from './offline';

declare const self: ServiceWorkerGlobalScope;

/** This worker's release (its script URL's `?r=`). */
const RELEASE = releaseOfScript(self.location.href) ?? '';
/** Where install stores this release's description inside its own shell cache (never served). */
const RELEASE_KEY = '/__py4kids-sw/release.json';
const CONCURRENCY = 6;
const ASK_TIMEOUT_MS = 2000;

interface RunnerReleaseInfo {
  release_id: string;
  shell: { files: { url: string; bytes: number }[]; bytes: number };
  pyodide: { dir: string; cache: string; files: { url: string; bytes: number }[]; bytes: number };
}

let info: Promise<RunnerReleaseInfo> | null = null;
function releaseInfo(): Promise<RunnerReleaseInfo> {
  info ??= (async () => {
    const stored = await (await caches.open(shellCacheName(RELEASE))).match(RELEASE_KEY);
    if (!stored) throw new Error('runner service worker: release description missing');
    return (await stored.json()) as RunnerReleaseInfo;
  })();
  info.catch(() => (info = null));
  return info;
}

// --- records -----------------------------------------------------------------------------------

let records: OfflineRecord[] = [];
async function loadRecords(): Promise<OfflineRecord[]> {
  try {
    records = await allRecords();
  } catch {
    records = [];
  }
  return records;
}

/** Is this the active worker (not one installing or waiting)? */
function isActive(): boolean {
  const me = (self as unknown as { serviceWorker?: ServiceWorker }).serviceWorker;
  return me ? me.state === 'activated' || me.state === 'activating' : self.registration.active?.scriptURL === self.location.href;
}

/** On start, the active worker deletes `book-*` caches no confirmed record names. */
async function sweep(): Promise<void> {
  if (!isActive()) return;
  const recs = await loadRecords();
  for (const name of sweepPlan(await caches.keys(), recs)) await caches.delete(name);
}
const started = sweep().catch(() => {});

// --- caching helpers ---------------------------------------------------------------------------

/** Fetch every missing URL into `cacheName`, `CONCURRENCY` at a time; `onBytes` counts each file. */
async function ensure(cacheName: string, files: { url: string; bytes: number }[], onBytes: (n: number) => void): Promise<void> {
  const cache = await caches.open(cacheName);
  for (const group of chunks(files, CONCURRENCY)) {
    await Promise.all(
      group.map(async ({ url, bytes }) => {
        if (await cache.match(url)) {
          onBytes(bytes);
          return;
        }
        const response = await fetch(url, { cache: 'no-cache', credentials: 'same-origin' });
        if (!response.ok || response.redirected) throw new Error(`${url}: HTTP ${response.status}`);
        await cache.put(url, response);
        onBytes(bytes);
      }),
    );
  }
}

async function complete(cacheName: string, files: { url: string }[]): Promise<boolean> {
  if (!(await caches.has(cacheName))) return files.length === 0;
  const cache = await caches.open(cacheName);
  for (const { url } of files) if (!(await cache.match(url))) return false;
  return true;
}

// --- lifecycle ---------------------------------------------------------------------------------

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      if (!RELEASE) throw new Error('runner service worker: registered without ?r=<release_id>');
      // The release's own description (network only, never cached for serving).
      const response = await fetch('/release.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`release.json: HTTP ${response.status}`);
      const described = (await response.json()) as RunnerReleaseInfo;
      // The server moved on since this page registered: refuse; the next page load registers the newer one.
      if (described.release_id !== RELEASE) throw new Error('release.json names another release');
      const cache = await caches.open(shellCacheName(RELEASE));
      await cache.put(RELEASE_KEY, new Response(JSON.stringify(described), { headers: { 'Content-Type': 'application/json' } }));
      // A downloaded book must survive the update: complete this release's files before it can activate.
      if ((await loadRecords()).length > 0) {
        await ensure(shellCacheName(RELEASE), described.shell.files, () => {});
        await ensure(described.pyodide.cache, described.pyodide.files, () => {});
      }
      // No skipWaiting: activation is page-mediated (the update handshake).
    })(),
  );
});

// `activate` deletes no cache (plan 105): cleanup and the sweep are the only deletion paths.

// --- fetch -------------------------------------------------------------------------------------

/** Exact-URL lookup across the retained caches: current shell, other shells, Pyodide, confirmed books. */
async function lookup(request: Request | string): Promise<Response | undefined> {
  const names = await caches.keys();
  const confirmed = new Set(records.map((r) => bookCacheName(r.book, r.content_hash)));
  const ordered = [
    shellCacheName(RELEASE),
    ...names.filter((n) => n !== shellCacheName(RELEASE) && parseCacheName(n)?.kind === 'shell'),
    ...names.filter((n) => parseCacheName(n)?.kind === 'pyodide'),
    ...names.filter((n) => confirmed.has(n)),
  ];
  for (const name of ordered) {
    if (!names.includes(name)) continue;
    const hit = await (await caches.open(name)).match(request, { ignoreVary: true });
    if (hit) return hit;
  }
  return undefined;
}

/** The cache a fetched URL belongs to on first use, if any: this release's shell or a Pyodide folder. */
async function homeOf(path: string): Promise<string | null> {
  const pyodide = /^\/pyodide\/([^/]+)\//.exec(path);
  if (pyodide) return pyodideCacheName(pyodide[1]!);
  try {
    const described = await releaseInfo();
    if (described.shell.files.some((f) => f.url === path)) return shellCacheName(RELEASE);
  } catch {
    // Not installed yet: cache nothing.
  }
  return null;
}

async function fromNetwork(request: Request, path: string): Promise<Response> {
  const response = await fetch(request);
  if (response.ok && response.type === 'basic' && !response.redirected) {
    const home = await homeOf(path);
    if (home) {
      const copy = response.clone();
      // Cache on first use; a failure to store never fails the request.
      void caches.open(home).then((c) => c.put(path, copy)).catch(() => {});
    }
  }
  return response;
}

async function respond(request: Request, url: URL): Promise<Response> {
  await started;
  if (request.mode === 'navigate') {
    const key = normaliseNavigation(url);
    const current = await (await caches.open(shellCacheName(RELEASE))).match(key);
    if (current) return withIsolation(current, RUNNER_ISOLATION);
    try {
      return await fromNetwork(request, key);
    } catch (error) {
      const any = await lookup(key);
      if (any) return withIsolation(any, RUNNER_ISOLATION);
      throw error;
    }
  }
  const hit = await lookup(request);
  if (hit) return withIsolation(hit, RUNNER_ISOLATION);
  return fromNetwork(request, url.pathname);
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  // Network only, never answered from a cache: the update check and the worker script.
  if (url.pathname === '/release.json' || url.pathname === '/sw.js') return;
  event.respondWith(respond(request, url));
});

// --- messages from this origin's pages ---------------------------------------------------------

interface PrecacheMessage {
  type: 'precache';
  book: string;
  content_hash: string;
  files: string[];
  release_id: string;
}

async function precache(message: PrecacheMessage, port: MessagePort): Promise<void> {
  await started;
  try {
    if (message.release_id !== RELEASE || !isActive()) {
      port.postMessage({ type: 'done', ok: false, bytes: 0, error: 'release' });
      return;
    }
    const described = await releaseInfo();
    const bookFiles = message.files.map((url) => ({ url, bytes: 0 }));
    const total = described.shell.bytes + described.pyodide.bytes;
    let done = 0;
    let last = 0;
    const onBytes = (n: number) => {
      done += n;
      const now = Date.now();
      if (now - last > 200) {
        last = now;
        port.postMessage({ type: 'progress', bytes: done, total });
      }
    };
    await ensure(shellCacheName(RELEASE), described.shell.files, onBytes);
    await ensure(described.pyodide.cache, described.pyodide.files, onBytes);
    const bookCache = bookCacheName(message.book, message.content_hash);
    if (bookFiles.length > 0) await ensure(bookCache, bookFiles, onBytes);
    // The record is written last: confirmation, not cache existence.
    const record: OfflineRecord = {
      book: message.book,
      content_hash: message.content_hash,
      release_id: RELEASE,
      bytes: done,
      confirmed_at: new Date().toISOString(),
    };
    await putRecord(record);
    await loadRecords();
    for (const name of replacedBookCaches(await caches.keys(), record)) await caches.delete(name);
    port.postMessage({ type: 'done', ok: true, bytes: done });
  } catch (error) {
    port.postMessage({ type: 'done', ok: false, bytes: 0, error: String(error).slice(0, 300) });
  }
}

/** Ask a window client which release it runs (`null` if it does not answer in time). */
function askRelease(client: Client): Promise<string | null> {
  return new Promise((resolve) => {
    const channel = new MessageChannel();
    const timer = setTimeout(() => resolve(null), ASK_TIMEOUT_MS);
    channel.port1.onmessage = (event: MessageEvent<{ release_id?: unknown }>) => {
      clearTimeout(timer);
      const r = event.data?.release_id;
      resolve(typeof r === 'string' ? r : null);
    };
    client.postMessage({ type: 'which-release' }, [channel.port2]);
  });
}

async function cleanup(port: MessagePort | undefined): Promise<void> {
  await started;
  let deleted: string[] = [];
  try {
    const described = await releaseInfo();
    const clients = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    const releases = await Promise.all(clients.map(askRelease));
    const shellComplete =
      (await complete(shellCacheName(RELEASE), described.shell.files)) && (await complete(described.pyodide.cache, described.pyodide.files));
    deleted = cleanupPlan(await caches.keys(), { release_id: RELEASE, pyodideCache: described.pyodide.cache }, releases, shellComplete);
    for (const name of deleted) await caches.delete(name);
  } catch {
    deleted = [];
  }
  port?.postMessage({ type: 'cleaned', deleted });
}

self.addEventListener('message', (event) => {
  const data = event.data as { type?: unknown } | null;
  if (!data || typeof data !== 'object' || !(event.source instanceof Client)) return;
  const port = event.ports[0];
  switch (data.type) {
    case 'skip-waiting':
      // The update handshake (the page decides; plan 105): only a waiting worker acts on it.
      event.waitUntil(self.skipWaiting());
      return;
    case 'precache':
      if (port) event.waitUntil(precache(data as PrecacheMessage, port));
      return;
    case 'cleanup':
      event.waitUntil(cleanup(port));
      return;
    case 'release':
      port?.postMessage({ type: 'release', release_id: RELEASE });
      return;
    default:
      return;
  }
});

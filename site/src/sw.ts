/**
 * The site origin's service worker (design 012 D10; plan 105 Phase A), hand-written: no Workbox, no
 * CDN. Built to dist/sw.js by scripts/pwa-build.ts and registered by every page as
 * `/sw.js?r=<release_id>` (from `/release.json`); its bytes change only when this code does.
 *
 * - **Caches** (runner/src/offline.ts): `shell-<release_id>` (the site pages, `_astro/*`, the
 *   content-hashed root assets, icons and web manifest; pages also cached on demand as they are
 *   visited) and `book-<book>-<content_hash>` (a downloaded book: every file in its build-time
 *   manifest, `_offline/<book>.<hash>.json`, which is kept in the same cache).
 * - **Download this book** (a `download` message with a port): fetch what this release's shell
 *   is missing, then the book's files in chunks into `book-<book>-<content_hash>` (progress on the
 *   port), and write the confirmed record last. A book whose content hash is unchanged is only
 *   verified (every listed URL is in its cache) and re-stamped with this release, never refetched.
 *   A changed hash downloads into a new cache; the old one is deleted only after confirmation.
 * - **Serving:** navigations are normalised (`/x`, `/x/index.html` -> `/x/`) and served from the
 *   book's confirmed cache or this release's shell, else the network (cached on demand), else any
 *   retained copy, else the offline page. Every other URL is served by exact match from any
 *   retained cache (asset URLs are release-specific), else the network. Responses from a cache
 *   are cloned with COOP/COEP set. `/release.json`, `/sw.js` and `/_offline/*` are never
 *   intercepted (network only).
 * - **Activation is page-mediated:** no `skipWaiting` on install (the page sends `skip-waiting`
 *   in the update handshake); `activate` deletes nothing; `cleanup` deletes other releases' shell
 *   caches once no window runs another release; the active worker sweeps unconfirmed `book-*`
 *   caches on start.
 * - **Privacy:** it requests only this origin's release files and the files a download names.
 */
/// <reference lib="webworker" />
import { allRecords, putRecord } from '../../runner/src/offline-store';
import {
  bookCacheName,
  bookOfPath,
  chunks,
  cleanupPlan,
  normaliseNavigation,
  parseCacheName,
  releaseOfScript,
  replacedBookCaches,
  shellCacheName,
  SITE_ISOLATION,
  sweepPlan,
  withIsolation,
  type OfflineRecord,
} from '../../runner/src/offline';

declare const self: ServiceWorkerGlobalScope;

/** Build-time (scripts/pwa-build.ts): true only in a PY4KIDS_TEST_HOOKS=1 build. */
declare const __PY4KIDS_TEST_HOOKS__: boolean;
const TEST_HOOKS = typeof __PY4KIDS_TEST_HOOKS__ !== 'undefined' && __PY4KIDS_TEST_HOOKS__;

const RELEASE = releaseOfScript(self.location.href) ?? '';
const RELEASE_KEY = '/__py4kids-sw/release.json';
const OFFLINE_PAGE = '/offline/';
const CONCURRENCY = 6;
const ASK_TIMEOUT_MS = 2000;

interface FileEntry {
  url: string;
  bytes: number;
}
interface BookSummary {
  content_hash: string;
  bytes: number;
  count: number;
  manifest: string;
}
interface SiteReleaseInfo {
  release_id: string;
  shell: { files: FileEntry[]; bytes: number };
  books: Record<string, BookSummary>;
  runner: { bytes: number };
}
interface BookManifest {
  book: string;
  content_hash: string;
  bytes: number;
  count: number;
  files: FileEntry[];
}

let info: Promise<SiteReleaseInfo> | null = null;
function releaseInfo(): Promise<SiteReleaseInfo> {
  info ??= (async () => {
    const stored = await (await caches.open(shellCacheName(RELEASE))).match(RELEASE_KEY);
    if (!stored) throw new Error('site service worker: release description missing');
    return (await stored.json()) as SiteReleaseInfo;
  })();
  info.catch(() => (info = null));
  return info;
}

// --- records and the start-up sweep ----------------------------------------------------------

let records: OfflineRecord[] = [];
async function loadRecords(): Promise<OfflineRecord[]> {
  try {
    records = await allRecords();
  } catch {
    records = [];
  }
  return records;
}

function isActive(): boolean {
  const me = (self as unknown as { serviceWorker?: ServiceWorker }).serviceWorker;
  return me ? me.state === 'activated' || me.state === 'activating' : self.registration.active?.scriptURL === self.location.href;
}

async function sweep(): Promise<void> {
  if (!isActive()) {
    await loadRecords();
    return;
  }
  const recs = await loadRecords();
  for (const name of sweepPlan(await caches.keys(), recs)) await caches.delete(name);
}
const started = sweep().catch(() => {});

// --- caching helpers -----------------------------------------------------------------------------

async function ensure(cacheName: string, files: FileEntry[], onFile: (f: FileEntry) => void, delayMs = 0): Promise<void> {
  const cache = await caches.open(cacheName);
  for (const group of chunks(files, CONCURRENCY)) {
    // Test builds only: a pause before each chunk, so a test can stop the servers mid-download.
    if (delayMs > 0) await new Promise((r) => setTimeout(r, delayMs));
    await Promise.all(
      group.map(async (file) => {
        if (await cache.match(file.url)) {
          onFile(file);
          return;
        }
        const response = await fetch(file.url, { cache: 'no-cache', credentials: 'same-origin' });
        if (!response.ok || response.redirected) throw new Error(`${file.url}: HTTP ${response.status}`);
        await cache.put(file.url, response);
        onFile(file);
      }),
    );
  }
}

async function missing(cacheName: string, files: FileEntry[]): Promise<FileEntry[]> {
  const cache = await caches.open(cacheName);
  const out: FileEntry[] = [];
  for (const f of files) if (!(await cache.match(f.url))) out.push(f);
  return out;
}

// --- lifecycle -----------------------------------------------------------------------------------

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      if (!RELEASE) throw new Error('site service worker: registered without ?r=<release_id>');
      const response = await fetch('/release.json', { cache: 'no-store' });
      if (!response.ok) throw new Error(`release.json: HTTP ${response.status}`);
      const described = (await response.json()) as SiteReleaseInfo;
      if (described.release_id !== RELEASE) throw new Error('release.json names another release');
      const cache = await caches.open(shellCacheName(RELEASE));
      await cache.put(RELEASE_KEY, new Response(JSON.stringify(described), { headers: { 'Content-Type': 'application/json' } }));
      // With a downloaded book on this device, complete this release's shell before it can
      // activate (its books are re-confirmed by the pages after the update).
      if ((await loadRecords()).length > 0) await ensure(shellCacheName(RELEASE), described.shell.files, () => {});
    })(),
  );
});

// `activate` deletes no cache (plan 105).

// --- fetch ---------------------------------------------------------------------------------------

function confirmedCaches(): string[] {
  return records.map((r) => bookCacheName(r.book, r.content_hash));
}

/** Exact-URL lookup: confirmed books, then this release's shell, then other retained shells. */
async function lookup(request: Request | string, ignoreSearch = false): Promise<Response | undefined> {
  const names = await caches.keys();
  const ordered = [
    ...confirmedCaches(),
    shellCacheName(RELEASE),
    ...names.filter((n) => n !== shellCacheName(RELEASE) && parseCacheName(n)?.kind === 'shell'),
  ];
  for (const name of ordered) {
    if (!names.includes(name)) continue;
    const hit = await (await caches.open(name)).match(request, { ignoreVary: true, ignoreSearch });
    if (hit) return hit;
  }
  return undefined;
}

async function shellHas(path: string): Promise<boolean> {
  try {
    return (await releaseInfo()).shell.files.some((f) => f.url === path);
  } catch {
    return false;
  }
}

async function navigate(request: Request, url: URL): Promise<Response> {
  const key = normaliseNavigation(url);
  const book = bookOfPath(key, records.map((r) => r.book));
  if (book) {
    const record = records.find((r) => r.book === book)!;
    const hit = await (await caches.open(bookCacheName(record.book, record.content_hash))).match(key);
    if (hit) return withIsolation(hit, SITE_ISOLATION);
  }
  const shell = await (await caches.open(shellCacheName(RELEASE))).match(key);
  if (shell) return withIsolation(shell, SITE_ISOLATION);
  try {
    const response = await fetch(request);
    if (response.ok && response.type === 'basic' && !response.redirected && (response.headers.get('Content-Type') ?? '').startsWith('text/html')) {
      // Pages are cached on demand, under this release.
      const copy = response.clone();
      void caches.open(shellCacheName(RELEASE)).then((c) => c.put(key, copy)).catch(() => {});
    }
    return response;
  } catch (error) {
    const any = (await lookup(key)) ?? (await lookup(OFFLINE_PAGE));
    if (any) return withIsolation(any, SITE_ISOLATION);
    throw error;
  }
}

async function asset(request: Request, url: URL): Promise<Response> {
  // Pagefind adds a cache-busting `?ts=` to its own (content-hashed) files.
  const hit = await lookup(request, url.pathname.startsWith('/pagefind/'));
  if (hit) return withIsolation(hit, SITE_ISOLATION);
  const response = await fetch(request);
  if (response.ok && response.type === 'basic' && !response.redirected && url.search === '' && (await shellHas(url.pathname))) {
    const copy = response.clone();
    void caches.open(shellCacheName(RELEASE)).then((c) => c.put(url.pathname, copy)).catch(() => {});
  }
  return response;
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  // Network only: the update check, the worker script and the download manifests.
  if (url.pathname === '/release.json' || url.pathname === '/sw.js' || url.pathname.startsWith('/_offline/')) return;
  event.respondWith(started.then(() => (request.mode === 'navigate' ? navigate(request, url) : asset(request, url))));
});

// --- download this book --------------------------------------------------------------------------

async function bookManifest(summary: BookSummary, cacheName: string): Promise<BookManifest> {
  const kept = await (await caches.open(cacheName)).match(summary.manifest);
  if (kept) return (await kept.json()) as BookManifest;
  const response = await fetch(summary.manifest, { cache: 'no-cache', credentials: 'same-origin' });
  if (!response.ok) throw new Error(`${summary.manifest}: HTTP ${response.status}`);
  const manifest = (await response.clone().json()) as BookManifest;
  if (manifest.content_hash !== summary.content_hash) throw new Error('the manifest names another content hash');
  await (await caches.open(cacheName)).put(summary.manifest, response);
  return manifest;
}

async function download(book: string, port: MessagePort, delayMs: number): Promise<void> {
  await started;
  try {
    if (!isActive()) throw new Error('not the active worker');
    const described = await releaseInfo();
    const summary = described.books[book];
    if (!summary) throw new Error(`no book ${book} in this release`);
    const cacheName = bookCacheName(book, summary.content_hash);
    const previous = records.find((r) => r.book === book);
    const shellMissing = await missing(shellCacheName(RELEASE), described.shell.files);
    const total = summary.bytes + shellMissing.reduce((n, f) => n + f.bytes, 0);
    let done = 0;
    let files = 0;
    let last = 0;
    const tick = (f: FileEntry, force = false) => {
      done += f.bytes;
      files++;
      const now = Date.now();
      if (force || now - last > 150) {
        last = now;
        port.postMessage({ type: 'progress', bytes: done, total, files });
      }
    };
    await ensure(shellCacheName(RELEASE), shellMissing, tick);
    const manifest = await bookManifest(summary, cacheName);
    if (previous && previous.content_hash === summary.content_hash) {
      // Unchanged content: verify every listed URL is present, then re-stamp. Nothing is refetched
      // unless a file has gone missing.
      const absent = await missing(cacheName, manifest.files);
      for (const f of manifest.files) if (!absent.includes(f)) tick(f);
      await ensure(cacheName, absent, tick, delayMs);
    } else {
      await ensure(cacheName, manifest.files, tick, delayMs);
    }
    tick({ url: '', bytes: 0 }, true);
    const record: OfflineRecord = {
      book,
      content_hash: summary.content_hash,
      release_id: RELEASE,
      bytes: summary.bytes,
      confirmed_at: new Date().toISOString(),
    };
    await putRecord(record);
    await loadRecords();
    // Only now may the book's previous cache go.
    for (const name of replacedBookCaches(await caches.keys(), record)) await caches.delete(name);
    port.postMessage({ type: 'done', ok: true, content_hash: summary.content_hash, release_id: RELEASE, bytes: done });
  } catch (error) {
    port.postMessage({ type: 'done', ok: false, error: String(error).slice(0, 300) });
  }
}

// --- cleanup and the rest of the messages ----------------------------------------------------------

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
    const complete = (await missing(shellCacheName(RELEASE), described.shell.files)).length === 0;
    deleted = cleanupPlan(await caches.keys(), { release_id: RELEASE }, releases, complete);
    for (const name of deleted) await caches.delete(name);
  } catch {
    deleted = [];
  }
  port?.postMessage({ type: 'cleaned', deleted });
}

async function status(port: MessagePort): Promise<void> {
  await started;
  try {
    const described = await releaseInfo();
    port.postMessage({ type: 'status', release_id: RELEASE, books: described.books, runner: described.runner });
  } catch {
    port.postMessage({ type: 'status', release_id: RELEASE, books: {}, runner: { bytes: 0 } });
  }
}

self.addEventListener('message', (event) => {
  const data = event.data as { type?: unknown; book?: unknown } | null;
  if (!data || typeof data !== 'object' || !(event.source instanceof Client)) return;
  const port = event.ports[0];
  switch (data.type) {
    case 'skip-waiting':
      event.waitUntil(self.skipWaiting());
      return;
    case 'download': {
      const delay = (data as { delay_ms?: unknown }).delay_ms;
      const delayMs = TEST_HOOKS && typeof delay === 'number' ? Math.min(Math.max(delay, 0), 10_000) : 0;
      if (port && typeof data.book === 'string') event.waitUntil(download(data.book, port, delayMs));
      return;
    }
    case 'cleanup':
      event.waitUntil(cleanup(port));
      return;
    case 'status':
      if (port) event.waitUntil(status(port));
      return;
    case 'client-count':
      if (port) {
        event.waitUntil(
          self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((all) => port.postMessage({ type: 'client-count', count: all.length })),
        );
      }
      return;
    default:
      return;
  }
});

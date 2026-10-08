/**
 * The offline rules both origins' service workers and pages share (plan 105 Global constraints
 * "Release identity and updates"): cache names, the confirmed-record rule, the sweep and cleanup
 * decisions, the release a worker script URL names, and navigation normalisation. Pure functions,
 * unit tested in runner/test/offline.test.ts; the site imports this file as it imports envelope.ts.
 *
 * - **Cache names**, three kinds per origin: `shell-<release_id>` (the app shell),
 *   `pyodide-<versioned dir>` (the runtime, shared by every book and release that uses that
 *   folder) and `book-<book>-<content_hash>` (a downloaded book).
 * - **Confirmation is a record, not cache existence.** Each origin stores one
 *   `{book, content_hash, release_id}` record per book, written only after every file of the book
 *   is in `book-<book>-<content_hash>`. On worker start, a `book-*` cache that no record names is
 *   deleted (`sweepPlan`): an interrupted download leaves nothing behind, and a confirmed one is
 *   never deleted before its replacement is confirmed.
 * - **No cache is deleted in `activate`.** `cleanupPlan` is the only path that deletes `shell-*`
 *   and `pyodide-*` caches: from a page of the current release, and only when no client still runs
 *   another release (every window client reports its release; one that does not answer blocks).
 * - **Immutable URLs** (every asset URL is content-hashed or versioned) are served by exact match
 *   from any retained cache, whoever asks (dedicated workers included).
 */

export const SHELL = 'shell-';
export const PYODIDE = 'pyodide-';
export const BOOK = 'book-';

const HEX64 = /^[0-9a-f]{64}$/;

export const shellCacheName = (releaseId: string): string => `${SHELL}${releaseId}`;
export const pyodideCacheName = (dir: string): string => `${PYODIDE}${dir}`;
export const bookCacheName = (book: string, contentHash: string): string => `${BOOK}${book}-${contentHash}`;

export type CacheKind =
  | { kind: 'shell'; release_id: string }
  | { kind: 'pyodide'; dir: string }
  | { kind: 'book'; book: string; content_hash: string };

/** What a cache name is, or null for a cache these rules do not own. */
export function parseCacheName(name: string): CacheKind | null {
  if (name.startsWith(SHELL)) {
    const id = name.slice(SHELL.length);
    return HEX64.test(id) ? { kind: 'shell', release_id: id } : null;
  }
  if (name.startsWith(PYODIDE)) {
    const dir = name.slice(PYODIDE.length);
    return /^[0-9A-Za-z._-]+$/.test(dir) ? { kind: 'pyodide', dir } : null;
  }
  const book = /^book-([a-z0-9][a-z0-9-]*)-([0-9a-f]{64})$/.exec(name);
  return book ? { kind: 'book', book: book[1]!, content_hash: book[2]! } : null;
}

/** A confirmed download of one book on one origin. */
export interface OfflineRecord {
  book: string;
  content_hash: string;
  release_id: string;
  /** Bytes the book's cache holds (the book's own files). */
  bytes: number;
  /** When it was confirmed (ISO). */
  confirmed_at: string;
  /** Site only: the release the runner confirmed the same book for (its `precached` reply). */
  runner_release_id?: string;
}

/** True when `value` is a well-formed record. */
export function isRecord(value: unknown): value is OfflineRecord {
  if (typeof value !== 'object' || value === null) return false;
  const r = value as Record<string, unknown>;
  return (
    typeof r.book === 'string' &&
    typeof r.content_hash === 'string' &&
    HEX64.test(r.content_hash) &&
    typeof r.release_id === 'string' &&
    HEX64.test(r.release_id) &&
    typeof r.bytes === 'number' &&
    typeof r.confirmed_at === 'string' &&
    (r.runner_release_id === undefined || (typeof r.runner_release_id === 'string' && HEX64.test(r.runner_release_id)))
  );
}

/** The `book-*` caches no confirmed record names: delete them (on worker start). */
export function sweepPlan(cacheNames: string[], records: OfflineRecord[]): string[] {
  const confirmed = new Set(records.map((r) => bookCacheName(r.book, r.content_hash)));
  return cacheNames.filter((name) => parseCacheName(name)?.kind === 'book' && !confirmed.has(name));
}

/** After a book's new cache is confirmed: its other `book-<book>-*` caches, to delete. */
export function replacedBookCaches(cacheNames: string[], record: Pick<OfflineRecord, 'book' | 'content_hash'>): string[] {
  const keep = bookCacheName(record.book, record.content_hash);
  return cacheNames.filter((name) => {
    const c = parseCacheName(name);
    return c?.kind === 'book' && c.book === record.book && name !== keep;
  });
}

/**
 * Cleanup (run on request from a page of the current release): the `shell-*` and `pyodide-*`
 * caches of other releases, but only when every client reported the current release
 * (`null`: a client that did not answer, which blocks cleanup), and the current shell is
 * complete (so nothing still needed is deleted). `book-*` caches follow the record rule instead.
 */
export function cleanupPlan(
  cacheNames: string[],
  current: { release_id: string; pyodideCache?: string | undefined },
  clientReleases: (string | null)[],
  currentShellComplete: boolean,
): string[] {
  if (!currentShellComplete) return [];
  if (clientReleases.some((r) => r !== current.release_id)) return [];
  return cacheNames.filter((name) => {
    const c = parseCacheName(name);
    if (c?.kind === 'shell') return c.release_id !== current.release_id;
    if (c?.kind === 'pyodide') return current.pyodideCache !== undefined && name !== current.pyodideCache;
    return false;
  });
}

/** The release a worker script URL names (`/sw.js?r=<release_id>`), or null. */
export function releaseOfScript(scriptUrl: string | undefined | null): string | null {
  if (!scriptUrl) return null;
  try {
    const r = new URL(scriptUrl, 'http://x').searchParams.get('r');
    return r && HEX64.test(r) ? r : null;
  } catch {
    return null;
  }
}

/** The worker script URL for a release. */
export const workerScriptUrl = (releaseId: string): string => `/sw.js?r=${releaseId}`;

/**
 * The cache key of a navigation: the path with `index.html` dropped and a trailing slash added to
 * an extensionless last segment, without query or fragment. (Cloudflare Pages redirects
 * `/x/index.html` and `/x` to `/x/`, so the trailing-slash URL is what is fetched and cached.)
 */
export function normaliseNavigation(url: URL | string): string {
  const u = typeof url === 'string' ? new URL(url, 'http://x') : url;
  let path = u.pathname;
  if (path.endsWith('/index.html')) path = path.slice(0, -'index.html'.length);
  else if (!path.endsWith('/') && !/\.[A-Za-z0-9]+$/.test(path.slice(path.lastIndexOf('/') + 1))) path = `${path}/`;
  return path;
}

/** The book a site path belongs to (its first segment, if it is one of `books`), else null. */
export function bookOfPath(pathname: string, books: Iterable<string>): string | null {
  const first = pathname.split('/')[1] ?? '';
  for (const b of books) if (b === first) return b;
  return null;
}

/**
 * A book's offline status on the site, from its site record and the active release:
 * - `available`: both origins confirmed the book for the active release (the site record's
 *   `release_id` and `runner_release_id` are both the active release);
 * - `updating`: a confirmed download from another release, or the runner's confirmation is
 *   missing, while a re-download runs;
 * - `none`: never downloaded.
 */
export type BookStatus = 'none' | 'updating' | 'available';
export function bookStatus(record: OfflineRecord | null | undefined, activeRelease: string | null): BookStatus {
  if (!record) return 'none';
  if (activeRelease && record.release_id === activeRelease && record.runner_release_id === activeRelease) return 'available';
  // Offline with no way to learn the active release: what both origins last confirmed stands.
  if (!activeRelease && record.runner_release_id === record.release_id) return 'available';
  return 'updating';
}

/** Isolation headers each origin re-asserts on a response served from its caches. */
export const SITE_ISOLATION: Record<string, string> = {
  'Cross-Origin-Opener-Policy': 'same-origin',
  'Cross-Origin-Embedder-Policy': 'require-corp',
};
export const RUNNER_ISOLATION: Record<string, string> = {
  ...SITE_ISOLATION,
  'Cross-Origin-Resource-Policy': 'cross-origin',
};

/**
 * A cached response as served: cloned, not rebuilt (`new Response(body, response)` keeps the
 * status and every stored header, `Content-Type: application/wasm` included, which
 * `WebAssembly.instantiateStreaming` needs), with the isolation headers set on the clone, so
 * `crossOriginIsolated` holds offline.
 */
export function withIsolation(response: Response, headers: Record<string, string>): Response {
  const out = new Response(response.body, response);
  for (const [name, value] of Object.entries(headers)) out.headers.set(name, value);
  return out;
}

/** Split `items` into chunks of `size`. */
export function chunks<T>(items: T[], size: number): T[][] {
  const out: T[][] = [];
  for (let i = 0; i < items.length; i += size) out.push(items.slice(i, i + size));
  return out;
}

/** The update handshake's per-step timeout (plan 105: 10 s). */
export const STEP_TIMEOUT_MS = 10_000;

/**
 * The shared offline rules (src/offline.ts; plan 105 "Release identity and updates"): cache names,
 * the confirmed-record rule, sweep and cleanup decisions, worker script releases, navigation
 * normalisation and the cloned-not-rebuilt cached responses.
 */
import { describe, expect, it } from 'vitest';
import {
  bookCacheName,
  bookOfPath,
  bookStatus,
  chunks,
  cleanupAllowed,
  cleanupPlan,
  isRecord,
  normaliseNavigation,
  parseCacheName,
  pyodideCacheName,
  releaseOfScript,
  replacedBookCaches,
  RUNNER_ISOLATION,
  shellCacheName,
  STEP_TIMEOUT_MS,
  sweepPlan,
  withIsolation,
  workerScriptUrl,
  type OfflineRecord,
} from '../src/offline';

const A = 'a'.repeat(64);
const B = 'b'.repeat(64);
const H1 = '1'.repeat(64);
const H2 = '2'.repeat(64);

const record = (book: string, content_hash: string, release_id: string, extra: Partial<OfflineRecord> = {}): OfflineRecord => ({
  book,
  content_hash,
  release_id,
  bytes: 10,
  confirmed_at: '2026-10-08T00:00:00.000Z',
  ...extra,
});

describe('cache names', () => {
  it('names the three kinds and parses them back', () => {
    expect(shellCacheName(A)).toBe(`shell-${A}`);
    expect(pyodideCacheName('0.27.8')).toBe('pyodide-0.27.8');
    expect(bookCacheName('python-projects', H1)).toBe(`book-python-projects-${H1}`);
    expect(parseCacheName(shellCacheName(A))).toEqual({ kind: 'shell', release_id: A });
    expect(parseCacheName('pyodide-0.27.8')).toEqual({ kind: 'pyodide', dir: '0.27.8' });
    // A book id with hyphens: the content hash is the last 64 hex digits.
    expect(parseCacheName(bookCacheName('usaco-bronze', H2))).toEqual({ kind: 'book', book: 'usaco-bronze', content_hash: H2 });
  });
  it('owns nothing else', () => {
    for (const name of ['shell-xyz', 'book-acsl-123', 'pyodide-', 'workbox-precache', 'other', `book--${H1}`]) expect(parseCacheName(name), name).toBeNull();
  });
});

describe('the confirmed-record rule', () => {
  it('sweeps every book cache that no record names (an interrupted download), and nothing else', () => {
    const names = [shellCacheName(A), 'pyodide-0.27.8', bookCacheName('acsl', H1), bookCacheName('acsl', H2), bookCacheName('python-projects', H1), 'unrelated'];
    expect(sweepPlan(names, [record('acsl', H1, A)])).toEqual([bookCacheName('acsl', H2), bookCacheName('python-projects', H1)]);
    expect(sweepPlan(names, [])).toEqual([bookCacheName('acsl', H1), bookCacheName('acsl', H2), bookCacheName('python-projects', H1)]);
  });
  it("deletes a book's old cache only after its new one is confirmed", () => {
    const names = [bookCacheName('acsl', H1), bookCacheName('acsl', H2), bookCacheName('python-projects', H1)];
    expect(replacedBookCaches(names, { book: 'acsl', content_hash: H2 })).toEqual([bookCacheName('acsl', H1)]);
    // Unchanged hash (verify and re-stamp): nothing to delete.
    expect(replacedBookCaches([bookCacheName('acsl', H1)], { book: 'acsl', content_hash: H1 })).toEqual([]);
  });
  it('says "available offline" only when both origins confirmed the active release', () => {
    expect(bookStatus(null, A)).toBe('none');
    expect(bookStatus(record('acsl', H1, A), A)).toBe('updating'); // the runner has not confirmed
    expect(bookStatus(record('acsl', H1, A, { runner_release_id: B }), A)).toBe('updating');
    expect(bookStatus(record('acsl', H1, A, { runner_release_id: A }), A)).toBe('available');
    expect(bookStatus(record('acsl', H1, A, { runner_release_id: A }), B)).toBe('updating'); // after an update
    expect(bookStatus(record('acsl', H1, A, { runner_release_id: A }), null)).toBe('available'); // offline
  });
  it('validates records', () => {
    expect(isRecord(record('acsl', H1, A))).toBe(true);
    expect(isRecord({ ...record('acsl', H1, A), release_id: 'x' })).toBe(false);
    expect(isRecord({ ...record('acsl', H1, A), runner_release_id: 'x' })).toBe(false);
    expect(isRecord(null)).toBe(false);
  });
});

describe('cleanup', () => {
  const names = [shellCacheName(A), shellCacheName(B), 'pyodide-0.27.8', 'pyodide-0.27.8-b', bookCacheName('acsl', H1)];
  it("deletes the other releases' shell and Pyodide caches once every client runs the current release", () => {
    expect(cleanupPlan(names, { release_id: B, pyodideCache: 'pyodide-0.27.8-b' }, [B, B], true)).toEqual([shellCacheName(A), 'pyodide-0.27.8']);
    // The site has no Pyodide cache to keep: it never deletes one.
    expect(cleanupPlan(names, { release_id: B }, [B], true)).toEqual([shellCacheName(A)]);
  });
  it('deletes nothing while a client still runs another release, or does not answer', () => {
    expect(cleanupPlan(names, { release_id: B }, [B, A], true)).toEqual([]);
    expect(cleanupPlan(names, { release_id: B }, [B, null], true)).toEqual([]);
  });
  it("deletes nothing while the current release's shell is incomplete", () => {
    expect(cleanupPlan(names, { release_id: B }, [B], false)).toEqual([]);
  });
  it('may clean up with an incomplete shell only when this origin holds no downloaded book', () => {
    // A visitor who never downloads a book never completes a shell: without this, every old
    // release's shell would be kept for ever.
    expect(cleanupAllowed(false, 0)).toBe(true);
    expect(cleanupAllowed(false, 1)).toBe(false);
    expect(cleanupAllowed(true, 3)).toBe(true);
    expect(cleanupPlan(names, { release_id: B }, [B], cleanupAllowed(false, 0))).toEqual([shellCacheName(A)]);
    expect(cleanupPlan(names, { release_id: B }, [B], cleanupAllowed(false, 2))).toEqual([]);
  });
  it('never deletes a book cache', () => {
    expect(cleanupPlan(names, { release_id: B, pyodideCache: 'pyodide-0.27.8-b' }, [], true)).not.toContain(bookCacheName('acsl', H1));
  });
});

describe('worker scripts, navigations and paths', () => {
  it('reads the release from a worker script URL', () => {
    expect(workerScriptUrl(A)).toBe(`/sw.js?r=${A}`);
    expect(releaseOfScript(`http://127.0.0.1:4691/sw.js?r=${A}`)).toBe(A);
    expect(releaseOfScript('/sw.js')).toBeNull();
    expect(releaseOfScript('/sw.js?r=nope')).toBeNull();
    expect(releaseOfScript(undefined)).toBeNull();
  });
  it('normalises navigations to the trailing-slash URL', () => {
    expect(normaliseNavigation('http://x/acsl/unit-01/')).toBe('/acsl/unit-01/');
    expect(normaliseNavigation('http://x/acsl/unit-01/index.html')).toBe('/acsl/unit-01/');
    expect(normaliseNavigation('http://x/acsl/unit-01')).toBe('/acsl/unit-01/');
    expect(normaliseNavigation('http://x/acsl/unit-01/?q=1#top')).toBe('/acsl/unit-01/');
    expect(normaliseNavigation('http://x/')).toBe('/');
    expect(normaliseNavigation('http://x/index.html')).toBe('/');
    expect(normaliseNavigation('http://x/acsl/cards/deck.json')).toBe('/acsl/cards/deck.json');
  });
  it('finds the book of a path', () => {
    expect(bookOfPath('/acsl/unit-01/', ['acsl', 'python-projects'])).toBe('acsl');
    expect(bookOfPath('/acsl-extra/', ['acsl'])).toBeNull();
    expect(bookOfPath('/', ['acsl'])).toBeNull();
  });
  it('chunks and times steps', () => {
    expect(chunks([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]]);
    expect(STEP_TIMEOUT_MS).toBe(10_000);
  });
});

describe('cached responses keep their headers', () => {
  it('clones, not rebuilds: Content-Type survives and the isolation headers are set', async () => {
    const cached = new Response(new Uint8Array([0, 97, 115, 109]), {
      status: 200,
      headers: { 'Content-Type': 'application/wasm', 'Content-Security-Policy': "default-src 'none'" },
    });
    const out = withIsolation(cached, RUNNER_ISOLATION);
    expect(out.status).toBe(200);
    expect(out.headers.get('content-type')).toBe('application/wasm');
    expect(out.headers.get('content-security-policy')).toBe("default-src 'none'");
    expect(out.headers.get('cross-origin-opener-policy')).toBe('same-origin');
    expect(out.headers.get('cross-origin-embedder-policy')).toBe('require-corp');
    expect(out.headers.get('cross-origin-resource-policy')).toBe('cross-origin');
    expect([...new Uint8Array(await out.arrayBuffer())]).toEqual([0, 97, 115, 109]);
  });
});

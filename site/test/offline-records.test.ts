/**
 * The confirmed-download records (runner/src/offline-store.ts; plan 105 "Confirmation is a record,
 * not cache existence") on IndexedDB through fake-indexeddb: a record is what the sweep keeps, a
 * malformed one confirms nothing, and the site record carries the runner's confirmation.
 */
import { IDBFactory } from 'fake-indexeddb';
import { beforeEach, describe, expect, it } from 'vitest';
import { allRecords, deleteRecord, getRecord, putRecord } from '../../runner/src/offline-store';
import { bookCacheName, bookStatus, sweepPlan, type OfflineRecord } from '../../runner/src/offline';

const A = 'a'.repeat(64);
const H = '1'.repeat(64);
const rec = (book: string, extra: Partial<OfflineRecord> = {}): OfflineRecord => ({
  book,
  content_hash: H,
  release_id: A,
  bytes: 5,
  confirmed_at: new Date(0).toISOString(),
  ...extra,
});

beforeEach(() => {
  (globalThis as { indexedDB: IDBFactory }).indexedDB = new IDBFactory();
});

describe('offline records', () => {
  it('stores one record per book, replacing it on a new confirmation', async () => {
    expect(await allRecords()).toEqual([]);
    await putRecord(rec('acsl'));
    await putRecord(rec('acsl', { runner_release_id: A }));
    await putRecord(rec('python-projects'));
    expect((await allRecords()).map((r) => r.book).sort()).toEqual(['acsl', 'python-projects']);
    expect((await getRecord('acsl'))?.runner_release_id).toBe(A);
    await deleteRecord('acsl');
    expect(await getRecord('acsl')).toBeNull();
  });

  it('refuses to write a malformed record, and ignores one found in the store', async () => {
    await expect(putRecord({ ...rec('acsl'), release_id: 'nope' })).rejects.toThrow();
    await putRecord(rec('acsl'));
    const db = await new Promise<IDBDatabase>((resolve) => {
      const r = indexedDB.open('py4kids-offline', 1);
      r.onsuccess = () => resolve(r.result);
    });
    await new Promise<void>((resolve) => {
      const tx = db.transaction('books', 'readwrite');
      tx.objectStore('books').put({ book: 'usaco-bronze', content_hash: 'x' });
      tx.oncomplete = () => resolve();
    });
    db.close();
    expect((await allRecords()).map((r) => r.book)).toEqual(['acsl']);
    expect(await getRecord('usaco-bronze')).toBeNull();
  });

  it('keeps exactly the confirmed caches when the worker sweeps, and reports the book status', async () => {
    await putRecord(rec('acsl', { runner_release_id: A }));
    const names = [bookCacheName('acsl', H), bookCacheName('python-projects', H)];
    expect(sweepPlan(names, await allRecords())).toEqual([bookCacheName('python-projects', H)]);
    expect(bookStatus(await getRecord('acsl'), A)).toBe('available');
    expect(bookStatus(await getRecord('python-projects'), A)).toBe('none');
  });
});

/**
 * The confirmed-download records (plan 105 "Confirmation is a record, not cache existence"), in an
 * IndexedDB database of their own on each origin (`py4kids-offline`, store `books`, one record per
 * book keyed by `book`). Kept apart from the site's progress database so the progress store's
 * versions never depend on the offline code. Pages and service workers of the same origin share it.
 */
import { isRecord, type OfflineRecord } from './offline';

export const OFFLINE_DB = 'py4kids-offline';
const STORE = 'books';

function open(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(OFFLINE_DB, 1);
    request.onupgradeneeded = () => {
      if (!request.result.objectStoreNames.contains(STORE)) request.result.createObjectStore(STORE, { keyPath: 'book' });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error('indexedDB.open failed'));
    request.onblocked = () => reject(new Error('indexedDB.open blocked'));
  });
}

function run<T>(mode: IDBTransactionMode, body: (store: IDBObjectStore) => IDBRequest<T>): Promise<T> {
  return open().then(
    (db) =>
      new Promise<T>((resolve, reject) => {
        const tx = db.transaction(STORE, mode);
        const request = body(tx.objectStore(STORE));
        tx.oncomplete = () => {
          db.close();
          resolve(request.result);
        };
        tx.onerror = tx.onabort = () => {
          db.close();
          reject(tx.error ?? new Error('transaction failed'));
        };
      }),
  );
}

/** Every well-formed record (a malformed one is ignored, and so confirms nothing). */
export async function allRecords(): Promise<OfflineRecord[]> {
  const rows = await run('readonly', (s) => s.getAll());
  return (rows as unknown[]).filter(isRecord);
}

export async function getRecord(book: string): Promise<OfflineRecord | null> {
  const row: unknown = await run('readonly', (s) => s.get(book));
  return isRecord(row) ? row : null;
}

/** Write (replace) a book's record: called only once every file of the book is cached. */
export async function putRecord(record: OfflineRecord): Promise<void> {
  if (!isRecord(record)) throw new Error('not an offline record');
  await run('readwrite', (s) => s.put(record));
}

export async function deleteRecord(book: string): Promise<void> {
  await run('readwrite', (s) => s.delete(book));
}

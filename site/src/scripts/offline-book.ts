/**
 * "Use this book offline" on a book page (plan 105 Phase A; markup in
 * src/components/OfflineBook.astro). Shows the size first (the book's files, plus Python once),
 * then on "Download this book" asks for persistent storage inside the click, downloads through
 * both origins' service workers with a progress bar, and says "Available offline" only when the
 * site and the runner both confirmed the book for the same release: the runner's own record is
 * asked for through the runner iframe ("Checking…" until it answers), never assumed from the
 * site's record. A runner whose record has gone (the browser cleared its storage) is said so, with
 * "Download again". A book downloaded under an older release reads "Updating…" and is downloaded
 * again (unchanged files are only verified). A download that stops making progress says so, with
 * "Try again".
 */
import { bookState, downloadBook, offlineSupported, requestPersistence, type BookState, type DownloadProgress } from '../lib/pwa-client';

const root = document.querySelector<HTMLElement>('[data-offline-book]');
if (root) void start(root);

const mb = (bytes: number) => `${(bytes / 1_000_000).toFixed(bytes < 10_000_000 ? 1 : 0)} MB`;

/** What the panel says in each state (students read these). */
const MESSAGES = {
  checking: 'Checking that this book is ready to use offline…',
  available: 'Available offline.',
  updating: 'Updating…',
  none: 'Not downloaded yet.',
  'runner-missing':
    'Python is no longer saved on this device, so code will not run offline. Download the book again.',
  unverified: 'Could not check that Python is saved for this book, so code may not run offline. Connect to the internet and download it again.',
  stalled: 'The download stopped. Try again.',
  failed: 'The download did not finish. Check the connection and try again.',
} as const;

async function start(root: HTMLElement): Promise<void> {
  const book = root.dataset.offlineBook!;
  const status = root.querySelector<HTMLElement>('[data-offline-status]')!;
  const size = root.querySelector<HTMLElement>('[data-offline-size]')!;
  const button = root.querySelector<HTMLButtonElement>('[data-offline-download]')!;
  const progress = root.querySelector<HTMLProgressElement>('[data-offline-progress]')!;
  const persist = root.querySelector<HTMLElement>('[data-offline-persist]')!;
  status.textContent = 'Checking…';
  if (!offlineSupported()) {
    status.textContent = 'This browser cannot keep books offline.';
    return;
  }
  // The runner connection is loaded only when needed (it is not part of every page's script).
  const connect = () => import('./run-support').then((m) => m.runnerConnection());

  const offer = (label: string) => {
    button.textContent = label;
    button.hidden = false;
  };

  const render = (state: BookState) => {
    root.dataset.status = state.status;
    if (state.summary) {
      size.textContent = `Download size: ${mb(state.summary.bytes)} for this book (${state.summary.count} files), plus ${mb(state.runnerBytes)} for Python, stored once for every book.`;
      size.hidden = false;
    }
    status.textContent = MESSAGES[state.status];
    button.hidden = true;
    if (state.status === 'none' && state.summary) offer('Download this book');
    else if ((state.status === 'runner-missing' || state.status === 'unverified') && state.summary) offer('Download again');
  };

  /** The book's state, with the runner's own record checked once the site's says "available". */
  const check = async (): Promise<BookState> => {
    const first = await bookState(book);
    if (first.status !== 'available') return first;
    root.dataset.status = 'checking';
    status.textContent = MESSAGES.checking;
    return bookState(book, connect);
  };

  const run = async (persisted: Promise<boolean> | null) => {
    button.hidden = true;
    progress.hidden = false;
    progress.value = 0;
    const onProgress = (p: DownloadProgress) => {
      const total = p.siteTotal + p.runnerTotal;
      progress.max = Math.max(1, total);
      progress.value = Math.min(total, p.siteBytes + p.runnerBytes);
    };
    const result = await downloadBook(book, connect, onProgress);
    progress.hidden = true;
    if (persisted) {
      const site = await persisted;
      persist.textContent =
        `Storage on this device: ${site ? 'kept until you remove it' : 'the browser may clear it when space runs low'}` +
        (result.runnerPersisted === null ? '.' : `; Python's storage: ${result.runnerPersisted ? 'kept' : 'may be cleared'}.`);
      persist.hidden = false;
    }
    if (!result.ok) {
      // The details go to the console only; the student gets a plain sentence and a retry.
      if (result.error) console.warn(`py4kids: the download of ${book} did not finish:`, result.error);
      root.dataset.status = result.stalled ? 'stalled' : 'failed';
      status.textContent = result.stalled ? MESSAGES.stalled : MESSAGES.failed;
      offer('Try again');
      return;
    }
    render(await check());
  };

  button.addEventListener('click', () => {
    // Inside the gesture: Firefox prompts for persistent storage only from a user action.
    const persisted = requestPersistence();
    void run(persisted);
  });

  const state = await check();
  render(state);
  // Downloaded under an older release: download it again for this one, in the background.
  if (state.status === 'updating' && navigator.onLine) await run(null);
}

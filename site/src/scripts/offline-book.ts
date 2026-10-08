/**
 * "Use this book offline" on a book page (plan 105 Phase A; markup in
 * src/components/OfflineBook.astro). Shows the size first (the book's files, plus Python once),
 * then on "Download this book" asks for persistent storage inside the click, downloads through
 * both origins' service workers with a progress bar, and says "Available offline" only when the
 * site and the runner both confirmed the book for the same release. A book downloaded under an
 * older release reads "Updating…" and is downloaded again (unchanged files are only verified).
 */
import { bookState, downloadBook, offlineSupported, requestPersistence, type BookState, type DownloadProgress } from '../lib/pwa-client';

const root = document.querySelector<HTMLElement>('[data-offline-book]');
if (root) void start(root);

const mb = (bytes: number) => `${(bytes / 1_000_000).toFixed(bytes < 10_000_000 ? 1 : 0)} MB`;

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

  const render = (state: BookState) => {
    root.dataset.status = state.status;
    if (state.summary) {
      size.textContent = `Download size: ${mb(state.summary.bytes)} for this book (${state.summary.count} files), plus ${mb(state.runnerBytes)} for Python, stored once for every book.`;
      size.hidden = false;
    }
    if (state.status === 'available') {
      status.textContent = 'Available offline.';
      button.hidden = true;
    } else if (state.status === 'updating') {
      status.textContent = 'Updating…';
      button.hidden = true;
    } else {
      status.textContent = 'Not downloaded yet.';
      button.hidden = !state.summary;
    }
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
      status.textContent = `The download did not finish: ${result.error ?? 'try again'}.`;
      button.hidden = false;
      button.textContent = 'Try again';
      return;
    }
    render(await bookState(book));
  };

  button.addEventListener('click', () => {
    // Inside the gesture: Firefox prompts for persistent storage only from a user action.
    const persisted = requestPersistence();
    void run(persisted);
  });

  const state = await bookState(book);
  render(state);
  // Downloaded under an older release: download it again for this one, in the background.
  if (state.status === 'updating' && navigator.onLine) await run(null);
}

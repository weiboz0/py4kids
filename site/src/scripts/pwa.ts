/**
 * The installable, offline site on every page (plan 105 Phase A; markup in
 * src/components/PwaIsland.astro):
 * - registers the service worker for the server's release (src/lib/pwa-client.ts);
 * - "you are offline" while the browser reports no network;
 * - "a new version is available — reload" when a newer worker is waiting, which runs the
 *   page-mediated update handshake (only when this is the site's only window);
 * - the install prompt, when the browser offers one;
 * - re-downloads this page's book in the background when it was downloaded under an older
 *   release ("updating" until both origins confirm it again).
 */
import { applyUpdate, bookState, downloadBook, offlineSupported, pendingUpdate, startPwa } from '../lib/pwa-client';

interface InstallPrompt extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<unknown>;
}

const root = document.querySelector<HTMLElement>('[data-pwa]');
if (root) start(root);

function start(root: HTMLElement): void {
  const offline = root.querySelector<HTMLElement>('[data-pwa-offline]')!;
  const update = root.querySelector<HTMLElement>('[data-pwa-update]')!;
  const updateText = root.querySelector<HTMLElement>('[data-pwa-update-text]')!;
  const accept = root.querySelector<HTMLButtonElement>('[data-pwa-update-accept]')!;
  const install = root.querySelector<HTMLElement>('[data-pwa-install]')!;
  const installButton = root.querySelector<HTMLButtonElement>('[data-pwa-install-button]')!;

  // Offline notice.
  const syncOnline = () => {
    offline.hidden = navigator.onLine;
  };
  addEventListener('online', syncOnline);
  addEventListener('offline', syncOnline);
  syncOnline();

  // Install prompt (browsers that offer one; nothing is shown otherwise).
  let deferred: InstallPrompt | null = null;
  addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    deferred = event as InstallPrompt;
    install.hidden = false;
  });
  installButton.addEventListener('click', () => {
    const prompt = deferred;
    deferred = null;
    install.hidden = true;
    if (prompt) void prompt.prompt().catch(() => {});
  });
  root.querySelector<HTMLButtonElement>('[data-pwa-install-dismiss]')!.addEventListener('click', () => {
    deferred = null;
    install.hidden = true;
  });
  addEventListener('appinstalled', () => {
    install.hidden = true;
  });

  if (!offlineSupported()) return;
  // The runner connection is loaded only when needed (it is not part of every page's script).
  const connect = () => import('./run-support').then((m) => m.runnerConnection());

  // Updates: a waiting worker of a newer release.
  const showUpdate = async () => {
    if (!(await pendingUpdate())) return;
    updateText.textContent = 'A new version of py4kids is available.';
    accept.disabled = false;
    update.hidden = false;
  };
  accept.addEventListener('click', () => {
    accept.disabled = true;
    void applyUpdate(connect, (message) => {
      updateText.textContent = message;
    }).then((outcome) => {
      if (outcome !== 'reloading') accept.disabled = false;
    });
  });

  void startPwa().then(async (reg) => {
    if (!reg) return;
    // (A blocked or failed registration leaves nothing to update or refresh.)
    const whenInstalled = (worker: ServiceWorker | null) =>
      worker?.addEventListener('statechange', () => {
        if (worker.state === 'installed') void showUpdate();
      });
    reg.addEventListener('updatefound', () => whenInstalled(reg.installing));
    // A worker already installing when this page loaded (its `updatefound` has fired) is offered too.
    whenInstalled(reg.installing);
    await showUpdate();
    await refreshBook(connect);
  });
}

/** This page's book, downloaded under an older release: download it again for this one. */
async function refreshBook(connect: () => Promise<import('../lib/runner-client').RunnerClient>): Promise<void> {
  const book = document.body.dataset.book;
  if (!book || document.querySelector('[data-offline-book]')) return; // the book page does it itself
  const state = await bookState(book);
  if (state.status !== 'updating' || !navigator.onLine) return;
  await downloadBook(book, connect, () => {});
}

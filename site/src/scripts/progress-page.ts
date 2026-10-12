/**
 * The progress island, on every page (plan 103 Phase D; contract in src/lib/dom-events.ts).
 * Nothing leaves the device: it only reads and writes the IndexedDB store.
 */

import { checklistOf, PROGRESS_IMPORTED_EVENT, SLIDE_EVENT, slideKey } from '../lib/dom-events';
import { onceUnsaved, recordChecklist, recordSlide, sharedProgress, type ProgressStore } from '../lib/progress';

const NOTICE_KEY = 'py4kids-unsaved-notice';

/** Once per visit when sessionStorage works; once per page otherwise. */
const remember = {
  get(): boolean {
    try {
      return sessionStorage.getItem(NOTICE_KEY) === '1';
    } catch {
      return false;
    }
  },
  set(): void {
    try {
      sessionStorage.setItem(NOTICE_KEY, '1');
    } catch {
      // Storage blocked too: the notice shows once on this page.
    }
  },
};

function showUnsavedNotice(): void {
  const main = document.getElementById('main');
  if (!main) return;
  const note = document.createElement('p');
  note.className = 'progress-notice';
  note.setAttribute('role', 'status');
  note.textContent =
    'This browser is not letting the site save your progress (a private window can do this). ' +
    'Everything still works, but cards, checklists and your place are forgotten when you leave.';
  main.prepend(note);
}

function warn(error: unknown): void {
  console.warn('py4kids progress:', error);
}

async function recordPosition(store: ProgressStore, href: string): Promise<void> {
  const { book, entry, entryTitle, resumeTitle } = document.body.dataset;
  if (!book || !entry) return;
  await store.setResume({ book, entry, href, title: resumeTitle ?? entryTitle ?? entry });
}

/**
 * Listens at once (the player may show its first slide before the store opens). A capturing
 * listener on `window` hears the event wherever it is dispatched (the player dispatches it on
 * `document`, without bubbling).
 */
function wireSlides(storeReady: Promise<ProgressStore>, contentHash: string): void {
  window.addEventListener(SLIDE_EVENT, (event) => {
    const key = slideKey((event as CustomEvent).detail);
    storeReady
      .then(async (store) => {
        if (key) await recordSlide(store, key, contentHash);
        // The player updates the URL hash around the event; read it once that has settled.
        await new Promise((resolve) => setTimeout(resolve, 0));
        await recordPosition(store, location.pathname + location.hash);
      })
      .catch(warn);
  }, { capture: true });
}

/**
 * Self-check checklists: restore each item's last saved boxes, and record every change. The change
 * listener is attached at once, before the store opens and the saved states load, so a box ticked
 * early is recorded (once the store is ready) and is not overwritten by the restore.
 */
function wireChecklists(storeReady: Promise<ProgressStore>, contentHash: string): void {
  const boxes = [...document.querySelectorAll<HTMLInputElement>('input[type="checkbox"][data-item-key]')];
  const keys = [...new Set(boxes.map((b) => b.dataset.itemKey!))];
  const touched = new Set<string>();
  document.addEventListener('change', (event) => {
    const box = event.target;
    if (!(box instanceof HTMLInputElement) || box.type !== 'checkbox' || !box.dataset.itemKey) return;
    const key = box.dataset.itemKey;
    touched.add(key);
    const list = checklistOf(document, key);
    storeReady.then((store) => recordChecklist(store, key, list, contentHash)).catch(warn);
  });
  storeReady
    .then(async (store) => {
      for (const key of keys) {
        const saved = (await store.latestEvent(key, 'self-check'))?.detail.checklist;
        if (touched.has(key)) continue;
        const mine = boxes.filter((b) => b.dataset.itemKey === key);
        if (saved && saved.length === mine.length) mine.forEach((box, i) => (box.checked = saved[i]!));
      }
    })
    .catch(warn);
}

async function fillResumeLinks(store: ProgressStore): Promise<void> {
  for (const holder of document.querySelectorAll<HTMLElement>('[data-resume-book]')) {
    const resume = await store.getResume(holder.dataset.resumeBook!);
    const link = holder.querySelector('a');
    if (!resume || !link || !resume.href.startsWith('/')) continue;
    link.href = resume.href;
    const title = holder.querySelector('[data-resume-title]');
    if (title) title.textContent = resume.title;
    holder.hidden = false;
  }
}

async function main(): Promise<void> {
  const storeReady = sharedProgress();
  const contentHash = document.body.dataset.contentHash;
  if (contentHash) wireSlides(storeReady, contentHash);
  if (contentHash) wireChecklists(storeReady, contentHash);
  const store = await storeReady;
  onceUnsaved(store, showUnsavedNotice, remember);
  if (document.body.dataset.entry) await recordPosition(store, location.pathname + location.hash);
  await fillResumeLinks(store);
  document.addEventListener(PROGRESS_IMPORTED_EVENT, () => {
    fillResumeLinks(store).catch(warn);
  });
}

main().catch(warn);

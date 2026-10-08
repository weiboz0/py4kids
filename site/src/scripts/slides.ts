/**
 * The slide player island (plan 103 D6). Enhances `/<book>/<entry>/slides/`, which without
 * script lists every slide in order:
 * - one slide at a time; ArrowRight / PageDown / Space go forward, ArrowLeft / PageUp go back,
 *   Home and End jump; a horizontal swipe also moves; Previous and Next buttons;
 * - the progress bar and "Slide n of N" follow; the slide number is the URL hash (`#3`), so a
 *   link or reload returns to the same slide;
 * - Escape returns to the reading view;
 * - each slide viewed dispatches `py4kids:slide` on `document` with
 *   `{book, entry, index, key, count}` (index is 0-based; key is the slide's first block key).
 *   The progress store (Phase D) listens for it; this module stores nothing itself.
 */

import { SLIDE_EVENT, type SlideEventDetail } from '../lib/dom-events';

const SWIPE_MIN_PX = 50;

function start(deck: HTMLElement): void {
  const slides = Array.from(deck.querySelectorAll<HTMLElement>('.slide'));
  if (slides.length === 0) return;
  const current = deck.querySelector<HTMLElement>('[data-deck-current]');
  const progress = deck.querySelector<HTMLProgressElement>('[data-deck-progress]');
  const prev = deck.querySelector<HTMLButtonElement>('[data-deck-prev]');
  const next = deck.querySelector<HTMLButtonElement>('[data-deck-next]');
  const { book = '', entry = '', reading = '../' } = deck.dataset;
  let index = -1;

  const fromHash = (): number => {
    const n = Number.parseInt(location.hash.replace(/^#(slide-)?/, ''), 10);
    return Number.isFinite(n) ? Math.min(Math.max(n, 1), slides.length) - 1 : 0;
  };

  const show = (to: number): void => {
    const target = Math.min(Math.max(to, 0), slides.length - 1);
    if (target === index) return;
    index = target;
    slides.forEach((slide, i) => {
      slide.hidden = i !== index;
    });
    if (current) current.textContent = String(index + 1);
    if (progress) progress.value = index + 1;
    if (prev) prev.disabled = index === 0;
    if (next) next.disabled = index === slides.length - 1;
    const hash = `#${index + 1}`;
    if (location.hash !== hash) history.replaceState(null, '', hash);
    const detail: SlideEventDetail = { book, entry, index, key: slides[index]!.dataset.key ?? '', count: slides.length };
    document.dispatchEvent(new CustomEvent<SlideEventDetail>(SLIDE_EVENT, { detail }));
  };

  deck.classList.add('is-live');
  show(fromHash());

  prev?.addEventListener('click', () => show(index - 1));
  next?.addEventListener('click', () => show(index + 1));
  window.addEventListener('hashchange', () => show(fromHash()));

  document.addEventListener('keydown', (event) => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return;
    const target = event.target as HTMLElement | null;
    if (target && (target.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))) return;
    const onButton = target?.tagName === 'BUTTON' || target?.tagName === 'A' || target?.tagName === 'SUMMARY';
    let to: number | null = null;
    switch (event.key) {
      case 'ArrowRight':
      case 'PageDown':
        to = index + 1;
        break;
      case ' ':
        if (onButton) return; // Space activates the focused control
        to = event.shiftKey ? index - 1 : index + 1;
        break;
      case 'ArrowLeft':
      case 'PageUp':
        to = index - 1;
        break;
      case 'Home':
        to = 0;
        break;
      case 'End':
        to = slides.length - 1;
        break;
      case 'Escape':
        event.preventDefault();
        location.assign(reading);
        return;
      default:
        return;
    }
    event.preventDefault();
    show(to);
  });

  let startX: number | null = null;
  let startY = 0;
  deck.addEventListener('pointerdown', (event) => {
    if (event.pointerType === 'mouse') return;
    startX = event.clientX;
    startY = event.clientY;
  }, { passive: true });
  deck.addEventListener('pointerup', (event) => {
    if (startX === null) return;
    const dx = event.clientX - startX;
    const dy = event.clientY - startY;
    startX = null;
    if (Math.abs(dx) >= SWIPE_MIN_PX && Math.abs(dx) > 2 * Math.abs(dy)) show(dx < 0 ? index + 1 : index - 1);
  }, { passive: true });
  deck.addEventListener('pointercancel', () => {
    startX = null;
  });
}

for (const deck of document.querySelectorAll<HTMLElement>('[data-deck]')) start(deck);

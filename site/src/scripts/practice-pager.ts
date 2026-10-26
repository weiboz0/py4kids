/**
 * The practice-page pager (plan 106): one item (step) at a time over the server-rendered page,
 * with Previous / Next and a grouped list of every item to jump to. Every step stays in the DOM and
 * is only hidden, so editors, checklists and results survive switching away and back; without
 * JavaScript (and for search and printing) every step shows.
 *
 * - Addressing: a step is shown by its item's anchor. A hash resolves to the step containing the
 *   element with that id (`getElementById(id)?.closest('[data-step]')`): the item anchor, its
 *   heading `#<anchor>-h` (Pagefind's sub-results) or any id inside the step. At load an empty or
 *   unknown hash shows the first step; later, an unresolvable hash (the skip link `#main`) leaves
 *   the current step shown.
 * - History: jump-list entries are real links (native fragment navigation pushes an entry and fires
 *   `hashchange`, which drives the view); Previous / Next replace the current entry.
 * - Focus: a control or list choice moves focus to the shown item's heading, which carries a
 *   visually hidden position ("4 of 12").
 * - Status: each list entry shows passed / tried, always read back from the progress store
 *   (src/lib/pager.ts `stepStatus`) on `py4kids:check` and `py4kids:checklist`, and "checking…"
 *   between `py4kids:check-start` and `py4kids:check`. A check that ends on a hidden item is
 *   announced by the page's polite live region.
 * - Every shown step dispatches `py4kids:step` (the progress island records the resume position).
 */

import {
  CHECK_EVENT,
  CHECK_START_EVENT,
  CHECKLIST_EVENT,
  notify,
  STEP_EVENT,
  type CheckEventDetail,
  type CheckStartDetail,
  type ChecklistEventDetail,
  type StepEventDetail,
} from '../lib/dom-events';
import { announcement, hashId, neighbours, positionText, STATUS_TEXT, stepForHash, stepStatus, type StepStatus } from '../lib/pager';
import { sharedProgress } from '../lib/progress';

interface Step {
  el: HTMLElement;
  section: HTMLElement;
  heading: HTMLElement;
  anchor: string;
  label: string;
  key: string;
  selfCheck: boolean;
  link: HTMLAnchorElement | null;
  status: HTMLElement | null;
  checking: boolean;
  state: StepStatus;
}

/** Wide screens: the list is an always-open side column. */
const WIDE = '(min-width: 62rem)';
/** An intro this short (one block) stays open on later steps (checkpoint rules stay visible). */
const SHORT_INTRO = 400;

function warn(error: unknown): void {
  console.warn('py4kids pager:', error);
}

const layout = document.querySelector<HTMLElement>('[data-practice-layout]');
const stepEls = [...document.querySelectorAll<HTMLElement>('[data-step]')];
if (layout && stepEls.length > 1) {
  try {
    start(layout, stepEls);
  } catch (error) {
    // Leave the page as rendered: every item shows.
    warn(error);
  }
}

function start(layout: HTMLElement, stepEls: HTMLElement[]): void {
  const nav = layout.querySelector<HTMLElement>('[data-pager-nav]');
  const list = layout.querySelector<HTMLDetailsElement>('[data-pager-list]');
  const controls = layout.querySelector<HTMLElement>('[data-pager-controls]');
  const prev = layout.querySelector<HTMLButtonElement>('[data-pager-prev]');
  const next = layout.querySelector<HTMLButtonElement>('[data-pager-next]');
  const live = layout.querySelector<HTMLElement>('[data-pager-live]');
  if (!nav || !list || !controls || !prev || !next || !live) return;
  const intro = layout.querySelector<HTMLElement>('[data-practice-intro]');
  const outro = layout.querySelector<HTMLElement>('[data-practice-outro]');
  const main = layout.querySelector<HTMLElement>('.practice-main') ?? layout;

  const steps: Step[] = stepEls.map((el) => {
    const section = el.querySelector<HTMLElement>('section.practice-item')!;
    const heading = section.querySelector<HTMLElement>('h2')!;
    const anchor = el.dataset.anchor!;
    const link = nav.querySelector<HTMLAnchorElement>(`a[data-jump="${CSS.escape(anchor)}"]`);
    return {
      el,
      section,
      heading,
      anchor,
      label: el.dataset.label ?? anchor,
      key: section.dataset.itemKey ?? '',
      selfCheck: section.dataset.checkKind === 'self-check',
      link,
      status: link?.querySelector<HTMLElement>('[data-jump-status]') ?? null,
      checking: false,
      state: 'none',
    };
  });
  const byKey = new Map(steps.map((s) => [s.key, s]));
  const byEl = new Map(steps.map((s) => [s.el, s]));
  const stepOf = (id: string): Step | null => {
    const found = document.getElementById(id)?.closest<HTMLElement>('[data-step]');
    return found ? (byEl.get(found) ?? null) : null;
  };
  let current = 0;

  // The intro: above the first item; on later items, inside "About these exercises".
  let introDetails: HTMLDetailsElement | null = null;
  if (intro) {
    introDetails = document.createElement('details');
    introDetails.className = 'intro-details';
    const summary = document.createElement('summary');
    summary.textContent = 'About these exercises';
    introDetails.append(summary);
    introDetails.open = intro.children.length <= 1 && (intro.textContent ?? '').trim().length <= SHORT_INTRO;
    introDetails.hidden = true;
    intro.after(introDetails);
  }
  const placeIntro = (index: number) => {
    if (!intro || !introDetails) return;
    if (index === 0) {
      if (intro.parentElement === introDetails) introDetails.before(intro);
      introDetails.hidden = true;
    } else {
      if (intro.parentElement !== introDetails) introDetails.append(intro);
      introDetails.hidden = false;
    }
  };

  // The position in each heading ("4 of 12"), added once the check island has read the headings
  // (it names each editor after its heading's text).
  let positioned = false;
  const addPositions = () => {
    if (positioned) return;
    positioned = true;
    steps.forEach((step, i) => {
      const pos = document.createElement('span');
      pos.className = 'visually-hidden step-pos';
      pos.textContent = positionText(i, steps.length);
      step.heading.append(' ', pos);
    });
  };
  if (document.body.dataset.checksReady !== undefined) addPositions();
  else {
    const watch = new MutationObserver(() => {
      if (document.body.dataset.checksReady === undefined) return;
      watch.disconnect();
      addPositions();
    });
    watch.observe(document.body, { attributes: true, attributeFilter: ['data-checks-ready'] });
  }

  for (const step of steps) step.heading.tabIndex = -1;

  // The list: always open on wide screens (a side column), a collapsed <details> on narrow ones.
  const wide = window.matchMedia(WIDE);
  list.open = wide.matches;
  wide.addEventListener('change', () => {
    list.open = wide.matches;
  });

  const label = (button: HTMLButtonElement, word: string, target: number | null) => {
    button.textContent = target === null ? word : `${word}: ${steps[target]!.label}`;
    button.disabled = target === null;
  };

  const inView = (el: HTMLElement) => {
    const r = el.getBoundingClientRect();
    return r.top >= 0 && r.bottom <= window.innerHeight;
  };

  /**
   * The one show function: from the controls, the list, Back / Forward and load. `focus` moves
   * focus to the item heading (a control or list choice); `target` is an element inside the step
   * to scroll to (focus stays); `scroll` brings the step into view.
   */
  const show = (index: number, options: { focus?: boolean; target?: HTMLElement | null; scroll?: boolean } = {}) => {
    current = index;
    steps.forEach((step, i) => {
      step.el.hidden = i !== index;
      if (i === index) step.link?.setAttribute('aria-current', 'step');
      else step.link?.removeAttribute('aria-current');
    });
    placeIntro(index);
    if (outro) outro.hidden = index !== steps.length - 1;
    const { prev: p, next: n } = neighbours(index, steps.length);
    label(prev, 'Previous', p);
    label(next, 'Next', n);
    notify<StepEventDetail>(STEP_EVENT, { href: location.pathname + location.hash });

    const step = steps[index]!;
    if (options.target) options.target.scrollIntoView({ block: 'start' });
    else if (options.scroll || options.focus) main.scrollIntoView({ block: 'start' });
    if (options.focus) {
      addPositions();
      step.heading.focus({ preventScroll: true });
      if (!inView(step.heading)) step.heading.scrollIntoView({ block: 'nearest' });
    }
  };

  /** The element a hash names, and whether it is the step itself (its item or heading). */
  const hashTarget = (step: Step): HTMLElement | null => {
    const el = document.getElementById(hashId(location.hash));
    return el && el !== step.section && el !== step.heading ? el : null;
  };

  // Previous / Next replace the current history entry, then show (replaceState fires no hashchange).
  const go = (target: number | null) => {
    if (target === null) return;
    history.replaceState(history.state, '', `#${steps[target]!.anchor}`);
    show(target, { focus: true });
  };
  prev.addEventListener('click', () => go(neighbours(current, steps.length).prev));
  next.addEventListener('click', () => go(neighbours(current, steps.length).next));

  // List choices are links: the browser pushes the entry and fires hashchange.
  let focusOnHashchange = false;
  nav.addEventListener('click', (event) => {
    const link = (event.target as Element | null)?.closest<HTMLAnchorElement>('a[data-jump]');
    if (!link || event.defaultPrevented) return;
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (!wide.matches) list.open = false;
    if (link.hash === location.hash) {
      // The same hash: no navigation and no hashchange, so show it here.
      event.preventDefault();
      const index = steps.findIndex((s) => s.link === link);
      if (index >= 0) show(index, { focus: true });
      return;
    }
    focusOnHashchange = true;
  });

  window.addEventListener('hashchange', () => {
    const focus = focusOnHashchange;
    focusOnHashchange = false;
    const step = stepOf(hashId(location.hash));
    if (!step) return; // not a step: the current one stays, the browser jumps normally
    const index = stepForHash(location.hash, steps, stepOf, { atLoad: false, current });
    show(index, { focus, target: hashTarget(step), scroll: true });
  });

  // Status: read back from the store; "checking…" while a check runs.
  const storeReady = sharedProgress();
  const render = (step: Step) => {
    if (!step.status) return;
    const which = step.checking ? 'checking' : step.state;
    const text = STATUS_TEXT[which];
    step.status.dataset.state = which;
    if (!text) return step.status.replaceChildren();
    const glyph = document.createElement('span');
    glyph.className = 'jump-glyph';
    glyph.setAttribute('aria-hidden', 'true');
    glyph.textContent = text.glyph;
    const hidden = document.createElement('span');
    hidden.className = 'visually-hidden';
    hidden.textContent = text.text;
    step.status.replaceChildren(glyph, hidden);
  };
  const refresh = async (step: Step) => {
    try {
      const store = await storeReady;
      step.state = stepStatus(await store.events(step.key), step.selfCheck);
    } catch (error) {
      warn(error);
    }
    render(step);
  };
  const say = (text: string) => {
    live.textContent = '';
    // A fresh node each time, so a repeated message is still announced.
    requestAnimationFrame(() => {
      live.textContent = text;
    });
  };

  document.addEventListener(CHECK_START_EVENT, (event) => {
    const step = byKey.get((event as CustomEvent<CheckStartDetail>).detail?.key ?? '');
    if (!step) return;
    step.checking = true;
    render(step);
  });
  document.addEventListener(CHECK_EVENT, (event) => {
    const detail = (event as CustomEvent<CheckEventDetail>).detail;
    const step = byKey.get(detail?.key ?? '');
    if (!step) return;
    step.checking = false;
    render(step);
    void refresh(step);
    if (steps[current] !== step) say(announcement(step.label, detail.result, detail.saved !== false));
  });
  document.addEventListener(CHECKLIST_EVENT, (event) => {
    const step = byKey.get((event as CustomEvent<ChecklistEventDetail>).detail?.key ?? '');
    if (step) void refresh(step);
  });

  // Print shows every step (pager.css); the intro's <details> opens for it.
  let introWasOpen = false;
  window.addEventListener('beforeprint', () => {
    if (!introDetails) return;
    introWasOpen = introDetails.open;
    introDetails.open = true;
  });
  window.addEventListener('afterprint', () => {
    if (introDetails) introDetails.open = introWasOpen;
  });

  // Enable: the chrome shows, one step at a time.
  layout.classList.add('is-paged');
  nav.hidden = false;
  controls.hidden = false;
  const first = stepForHash(location.hash, steps, stepOf, { atLoad: true, current: 0 });
  const resolved = stepOf(hashId(location.hash));
  show(first);
  // The browser scrolled to the hash in the full page; scroll again now that one step shows.
  if (resolved) {
    const target = hashTarget(resolved);
    (target ?? resolved.el).scrollIntoView({ block: 'start' });
  }
  layout.dataset.pagerReady = '';
  void Promise.all(steps.map(refresh)).then(() => {
    layout.dataset.statusesReady = '';
  });
}

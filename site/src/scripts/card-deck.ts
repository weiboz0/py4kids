/**
 * The card deck island, `/<book>/cards/` (plan 103 "Mastery map and cards (D8)").
 * - predict `typed`: type what the code prints; compared with `normalise`, case-sensitive.
 * - predict `flip`: reveal the output, then grade yourself ("Got it" / "Not yet").
 * - concept `choice`: pick the term for a definition (options in a stable, key-seeded order).
 * - concept `flip`: reveal the definition, then grade yourself.
 * Prelude cards show the prelude code above the card's code. Each answer updates the card's
 * Leitner box and writes a `card` event, on this device only.
 */

import type { DeckCard, DeckProjection } from '../lib/cards';
import { deckQueue, gradeChoice, gradeTyped, reportHref, type Queue } from '../lib/deck';
import type { CardState } from '../lib/leitner';
import { recordCardReview, sharedProgress, type ProgressStore } from '../lib/progress';

const root = document.querySelector<HTMLElement>('[data-deck]');

function el<K extends keyof HTMLElementTagNameMap>(tag: K, className?: string, text?: string): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function codeBlock(code: string, label: string): HTMLElement {
  const pre = el('pre', 'card-code');
  pre.setAttribute('aria-label', label);
  pre.tabIndex = 0;
  pre.append(el('code', undefined, code));
  return pre;
}

function button(text: string, className = 'button'): HTMLButtonElement {
  const b = el('button', className, text);
  b.type = 'button';
  return b;
}

class Deck {
  private queue: Queue = { cards: [], due: 0, fresh: 0, later: 0 };
  private position = 0;
  private shownAt = 0;

  constructor(
    private readonly host: HTMLElement,
    private readonly deck: DeckProjection,
    private readonly store: ProgressStore,
    private readonly states: Map<string, CardState>,
    private readonly contentHash: string,
    private readonly counts: HTMLElement,
    private readonly unit: HTMLSelectElement,
  ) {
    unit.addEventListener('change', () => this.restart());
  }

  restart(): void {
    this.queue = deckQueue(this.deck.cards, this.states, this.unit.value);
    this.position = 0;
    this.counts.textContent = `${this.queue.due} due, ${this.queue.fresh} new, ${this.queue.later} not due yet`;
    this.show(false);
  }

  private show(focus: boolean): void {
    this.host.replaceChildren();
    const card = this.queue.cards[this.position];
    if (!card) {
      this.finished();
      return;
    }
    this.shownAt = performance.now();
    const article = el('article', 'card');
    const heading = el('h2', 'card-heading', `Card ${this.position + 1} of ${this.queue.cards.length}`);
    heading.tabIndex = -1;
    const status = this.position < this.queue.due ? 'due' : this.position < this.queue.due + this.queue.fresh ? 'new' : 'not due yet';
    article.append(heading, el('p', 'card-status', `${this.unitTitle(card.unit)} · ${status}`));
    const body = el('div', 'card-body');
    article.append(body);
    if (card.kind === 'predict') this.predict(card, body);
    else if (card.mode === 'choice') this.choice(card, body);
    else this.conceptFlip(card, body);
    const report = el('p', 'card-report');
    const link = el('a', undefined, 'For parents and teachers: report a problem');
    link.href = reportHref(card.key, this.contentHash);
    report.append(link);
    article.append(report);
    this.host.append(article);
    // After "Next card", focus the answer box or first choice; otherwise the heading.
    if (focus) (article.querySelector<HTMLElement>('.card-typed input, .card-option') ?? heading).focus();
  }

  private unitTitle(id: string): string {
    return this.deck.units.find((u) => u.id === id)?.title ?? id;
  }

  private finished(): void {
    const box = el('div', 'card');
    const heading = el('h2', 'card-heading', this.queue.cards.length ? 'You have been through every card' : 'No cards here');
    heading.tabIndex = -1;
    const again = button('Start again');
    again.addEventListener('click', () => this.restart());
    box.append(heading, el('p', undefined, 'Cards you missed come back first next time.'), again);
    this.host.append(box);
    heading.focus();
  }

  private feedback(parent: HTMLElement): HTMLElement {
    const live = el('p', 'card-feedback');
    live.setAttribute('role', 'status');
    parent.append(live);
    return live;
  }

  private async answer(card: DeckCard, correct: boolean, selfGrade?: 'got-it' | 'not-yet'): Promise<void> {
    try {
      const { state } = await recordCardReview(
        this.store,
        { key: card.key, book: this.deck.book },
        correct,
        { content_hash: this.contentHash, duration_ms: performance.now() - this.shownAt, ...(selfGrade ? { self_grade: selfGrade } : {}) },
      );
      this.states.set(card.key, state);
    } catch (error) {
      console.warn('py4kids cards:', error);
    }
  }

  private nextButton(parent: HTMLElement): void {
    const next = button('Next card', 'button button-primary');
    next.addEventListener('click', () => {
      this.position += 1;
      this.show(true);
    });
    parent.append(next);
    next.focus();
  }

  private selfGrade(card: DeckCard, parent: HTMLElement): void {
    const group = el('div', 'card-actions');
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', 'How did you do?');
    const gotIt = button('Got it', 'button button-primary');
    const notYet = button('Not yet');
    const grade = (g: 'got-it' | 'not-yet') => {
      gotIt.disabled = notYet.disabled = true;
      void this.answer(card, g === 'got-it', g).then(() => this.nextButton(parent));
    };
    gotIt.addEventListener('click', () => grade('got-it'));
    notYet.addEventListener('click', () => grade('not-yet'));
    group.append(gotIt, notYet);
    parent.append(group);
    gotIt.focus();
  }

  private outputBlock(output: string): HTMLElement {
    return output === '' ? el('p', 'card-output-none', '(It prints nothing.)') : codeBlock(output, 'Output');
  }

  private predict(card: Extract<DeckCard, { kind: 'predict' }>, body: HTMLElement): void {
    if (card.prelude.length > 0) {
      const prelude = el('div', 'card-prelude');
      prelude.append(el('p', 'card-label', 'This code runs first:'));
      for (const code of card.prelude) prelude.append(codeBlock(code, 'Code that runs first'));
      body.append(prelude);
    }
    body.append(el('p', 'card-label', card.prelude.length ? 'Then this runs. What does it print?' : 'What does this code print?'));
    body.append(codeBlock(card.code, 'Code'));
    if (card.mode === 'typed') {
      const form = el('form', 'card-typed');
      const id = `answer-${this.position}`;
      const label = el('label', undefined, 'It prints:');
      label.htmlFor = id;
      const input = el('input');
      input.id = id;
      input.type = 'text';
      input.autocomplete = 'off';
      input.spellcheck = false;
      input.setAttribute('autocapitalize', 'off');
      const check = el('button', 'button button-primary', 'Check');
      check.type = 'submit';
      form.append(label, input, check);
      body.append(form);
      const live = this.feedback(body);
      form.addEventListener('submit', (event) => {
        event.preventDefault();
        if (input.readOnly) return;
        input.readOnly = true;
        check.disabled = true;
        const correct = gradeTyped(input.value, card.output);
        live.textContent = correct ? 'Correct!' : 'Not quite. It prints:';
        if (!correct) body.append(this.outputBlock(card.output));
        void this.answer(card, correct).then(() => this.nextButton(body));
      });
    } else {
      const reveal = button('Show the output', 'button button-primary');
      reveal.addEventListener('click', () => {
        reveal.remove();
        body.append(el('p', 'card-label', 'It prints:'), this.outputBlock(card.output));
        this.selfGrade(card, body);
      });
      body.append(reveal);
    }
  }

  private choice(card: Extract<DeckCard, { kind: 'concept' }>, body: HTMLElement): void {
    body.append(el('p', 'card-label', 'Which term means this?'));
    const definition = el('blockquote', 'card-definition');
    definition.innerHTML = card.definition_html; // built and escaped at build time (cards.ts)
    body.append(definition);
    const group = el('div', 'card-options');
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', 'Choices');
    const options = card.options.map((option) => {
      const b = button(option, 'button card-option');
      group.append(b);
      return b;
    });
    body.append(group);
    const live = this.feedback(body);
    for (const b of options) {
      b.addEventListener('click', () => {
        for (const o of options) o.disabled = true;
        const correct = gradeChoice(b.textContent ?? '', card.term);
        b.classList.add(correct ? 'is-correct' : 'is-wrong');
        options.find((o) => o.textContent === card.term)?.classList.add('is-correct');
        live.textContent = correct ? 'Correct!' : `Not quite. The answer is “${card.term}”.`;
        void this.answer(card, correct).then(() => this.nextButton(body));
      });
    }
  }

  private conceptFlip(card: Extract<DeckCard, { kind: 'concept' }>, body: HTMLElement): void {
    body.append(el('p', 'card-label', 'What does this term mean?'), el('p', 'card-term', card.term));
    const reveal = button('Show the meaning', 'button button-primary');
    reveal.addEventListener('click', () => {
      reveal.remove();
      const definition = el('blockquote', 'card-definition');
      definition.innerHTML = card.definition_html; // built and escaped at build time (cards.ts)
      body.append(definition);
      this.selfGrade(card, body);
    });
    body.append(reveal);
  }
}

async function main(): Promise<void> {
  if (!root) return;
  const loading = root.querySelector<HTMLElement>('[data-deck-loading]')!;
  const bar = root.querySelector<HTMLElement>('[data-deck-bar]')!;
  const host = root.querySelector<HTMLElement>('[data-deck-card]')!;
  const counts = root.querySelector<HTMLElement>('[data-deck-counts]')!;
  const unit = root.querySelector<HTMLSelectElement>('[data-deck-unit]')!;
  loading.textContent = 'Loading cards…';
  const response = await fetch(new URL('deck.json', location.href));
  if (!response.ok) throw new Error(`deck.json: HTTP ${response.status}`);
  const deck = (await response.json()) as DeckProjection;
  const store = await sharedProgress();
  const states = await store.cards(deck.book);
  const deckView = new Deck(host, deck, store, states, document.body.dataset.contentHash ?? '', counts, unit);
  loading.hidden = true;
  bar.hidden = false;
  host.hidden = false;
  deckView.restart();
}

main().catch((error: unknown) => {
  console.warn('py4kids cards:', error);
  const loading = root?.querySelector<HTMLElement>('[data-deck-loading]');
  if (loading) loading.textContent = 'The cards could not be loaded. Try reloading the page.';
});

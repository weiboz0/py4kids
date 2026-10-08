/**
 * The check island on practice pages (plan 104 Phase B). Per item (`section.practice-item`, its
 * contract in the page's data attributes):
 *
 * - code items get the CodeMirror editor (src/scripts/editor.ts), Run, Check and Stop;
 * - typed items (`answer`, `predict`) get an answer box compared by salted hash on the device;
 * - Check fetches the item's check projection (`data-check-href`) and, for fixtures, each case's
 *   files, lazily; the sample case runs first and is the only one whose input and expected output
 *   are shown; hidden cases report pass/fail only; asserts report per assert, never their source;
 * - every Check writes a D11 `exercise` / `checkpoint` / `project` event with `detail.cases`, and
 *   the code or typed answer goes only to the on-device attempt store;
 * - an odd unit exercise (`data-answer-href`) shows its answer only after a genuine attempt.
 */

import { answerHash } from '../lib/normalise';
import {
  answerUnlocked,
  DEFAULT_BUDGET_MS,
  NO_ATTEMPT,
  outcomeOf,
  verdictText,
  type AttemptHistory,
  type CheckKind,
  type ClientAnswer,
  type ClientCheck,
  type ClientFormat,
  type EventKind,
  type FixturesCheck,
  type Outcome,
} from '../lib/check-model';
import { checklistOf } from '../lib/dom-events';
import { recordCheck, sharedProgress, type Attempt, type ProgressStore } from '../lib/progress';
import type { ResultReply, RunnerClient } from '../lib/runner-client';
import { mountEditor, tabInserts, textareaEditor, type CodeEditor } from './editor';
import {
  drawing,
  el,
  fetchJson,
  fetchRunFiles,
  fetchText,
  freshSession,
  isUnavailable,
  restartNote,
  runner,
  runnerBooted,
  runOutput,
  textBlock,
  unavailable,
} from './run-support';

type Case = { n: number; pass: boolean };

interface ItemContext {
  section: HTMLElement;
  key: string;
  label: string;
  kind: CheckKind;
  checkHref: string;
  answerHref: string | null;
  eventKind: EventKind;
  result: HTMLElement;
  editor: CodeEditor | null;
  history: AttemptHistory;
  revealed: boolean;
  busy: boolean;
  /** The run the Stop button interrupts. */
  current: { client: RunnerClient; id: string } | null;
  stopped: boolean;
}

const contentHash = document.body.dataset.contentHash ?? '';
const storeReady = sharedProgress();

function warn(error: unknown): void {
  console.warn('py4kids checks:', error);
}

async function withStore(action: (store: ProgressStore) => Promise<unknown>): Promise<void> {
  try {
    await action(await storeReady);
  } catch (error) {
    warn(error);
  }
}

// ---------------------------------------------------------------------------------------------
// Answer gating

function historyOf(attempts: Attempt[], checklistDone: boolean): AttemptHistory {
  return {
    checks: attempts.filter((a) => a.kind === 'check').length,
    answers: attempts.filter((a) => a.kind === 'answer').length,
    runs: attempts.filter((a) => a.kind === 'run').length,
    checklistDone,
  };
}

async function maybeReveal(ctx: ItemContext): Promise<void> {
  if (ctx.revealed || !ctx.answerHref) return;
  if (!answerUnlocked({ gated: true, kind: ctx.kind }, ctx.history)) return;
  ctx.revealed = true;
  const slot = ctx.section.querySelector<HTMLElement>('[data-answer-slot]');
  if (!slot) return;
  try {
    const answer = await fetchJson<ClientAnswer>(ctx.answerHref);
    if (answer.key !== ctx.key) throw new Error(`answer for ${answer.key}, not ${ctx.key}`);
    const heading = el('h3', 'answer-heading', 'Answer');
    const body = el('div', 'answer-body');
    // Built at build time by the site's own Markdown pipeline (no inline style or script).
    body.innerHTML = answer.html;
    for (const drawing of answer.figures) {
      const figure = el('figure', 'turtle');
      // The SVG is built at build time by turtleSvg (escaped attributes, no script).
      figure.innerHTML = drawing.svg;
      figure.append(el('figcaption', 'turtle-caption', drawing.caption));
      body.append(figure);
    }
    slot.replaceChildren(heading, body);
    slot.hidden = false;
  } catch (error) {
    ctx.revealed = false;
    warn(error);
  }
}

async function addAttempt(ctx: ItemContext, attempt: Omit<Attempt, 'attempt_id' | 'book' | 'timestamp' | 'item_key'>): Promise<void> {
  if (attempt.kind === 'check') ctx.history.checks++;
  else if (attempt.kind === 'answer') ctx.history.answers++;
  else ctx.history.runs++;
  await withStore((store) => store.addAttempt({ ...attempt, item_key: ctx.key }));
  await maybeReveal(ctx);
}

// ---------------------------------------------------------------------------------------------
// Busy state, Stop

function setBusy(ctx: ItemContext, busy: boolean): void {
  ctx.busy = busy;
  for (const button of ctx.section.querySelectorAll<HTMLButtonElement>('[data-run-item], [data-check-item], form[data-answer-form] button')) {
    button.disabled = busy;
  }
  const stop = ctx.section.querySelector<HTMLButtonElement>('[data-stop]');
  if (stop) {
    stop.hidden = !busy || ctx.kind === 'answer' || ctx.kind === 'predict';
    stop.disabled = false;
  }
  if (busy) ctx.stopped = false;
  else ctx.current = null;
}

function status(ctx: ItemContext, text: string): HTMLElement {
  const p = el('p', 'check-status', text);
  ctx.result.replaceChildren(p);
  return p;
}

async function startRun(
  ctx: ItemContext,
  client: RunnerClient,
  options: Parameters<RunnerClient['run']>[0],
): Promise<ResultReply> {
  const { id, result } = client.run(options);
  ctx.current = { client, id };
  try {
    return await result;
  } finally {
    ctx.current = null;
  }
}

function startingText(): string {
  return runnerBooted() ? 'Checking…' : 'Starting Python (the first run takes a few seconds)…';
}

function verdictLine(outcome: Outcome, passed: number, total: number): HTMLElement {
  const text =
    outcome === 'pass'
      ? total === 1
        ? 'Passed.'
        : `Passed: all ${total} checks.`
      : outcome === 'error'
        ? 'Nothing was checked.'
        : `Not yet: ${passed} of ${total} ${total === 1 ? 'check' : 'checks'} passed.`;
  return el('p', `verdict verdict-${outcome}`, text);
}

/** One verdict per row: "Test 2: failed (assertion failed)". */
function resultList(rows: { name: string; pass: boolean; detail: string }[]): HTMLElement {
  const list = el('ul', 'case-list');
  for (const row of rows) {
    const li = el('li', row.pass ? 'case case-pass' : 'case case-fail');
    li.textContent = `${row.name}: ${verdictText(row.pass, row.detail)}`;
    list.append(li);
  }
  return list;
}

/** A runner verdict's name, for a student. */
const displayName = (name: string) => name.replace(/^assert (\d+)$/, 'Test $1').replace(/^turtle: /, 'Turtle: ');

/** Why a run that did not finish normally produced no gradable output. */
const stoppedDetail = (status: string) => (status === 'timeout' ? 'the program ran out of time' : 'the program stopped with an error');

// ---------------------------------------------------------------------------------------------
// Check kinds

async function checkFixtures(ctx: ItemContext, check: FixturesCheck, client: RunnerClient, code: string): Promise<Case[]> {
  const files = await fetchRunFiles(check.files);
  const progress = el('p', 'check-status', '');
  const list = el('ol', 'case-list');
  const rows = new Map<number, HTMLElement>();
  let hiddenIndex = 0;
  const names = new Map<number, string>();
  for (const c of check.cases) {
    const name = c.sample ? `Sample case ${c.n}` : `Hidden case ${++hiddenIndex}`;
    names.set(c.n, name);
    const li = el('li', 'case case-waiting', `${name}: ${c.skipped ? 'skipped' : 'waiting'}`);
    if (c.skipped) {
      li.className = 'case case-skipped';
      li.textContent = `${name}: skipped (too slow to check in the browser; it is not counted)`;
    }
    li.dataset.case = String(c.n);
    rows.set(c.n, li);
    list.append(li);
  }
  ctx.result.replaceChildren(progress, list);
  const cases: Case[] = [];
  let index = 0;
  const runnable = check.cases.filter((c) => !c.skipped).length;
  for (const c of check.cases) {
    if (c.skipped) continue;
    const li = rows.get(c.n)!;
    const name = names.get(c.n)!;
    if (ctx.stopped) {
      li.className = 'case case-stopped';
      li.textContent = `${name}: not run (stopped)`;
      continue;
    }
    index++;
    progress.textContent = `Running case ${index} of ${runnable}${runnerBooted() ? '' : ' (starting Python)'}…`;
    li.className = 'case case-running';
    li.textContent = `${name}: running…`;
    const [input, expected] = await Promise.all([fetchText(c.input), fetchText(c.expected)]);
    const result = await startRun(ctx, client, {
      session: freshSession(),
      code,
      stdin: input,
      files,
      check: { kind: 'fixture', expected, match: check.match, turtle: check.turtle },
      budget_ms: check.budget_ms,
    });
    if (result.status === 'interrupted') {
      ctx.stopped = true;
      li.className = 'case case-stopped';
      li.textContent = `${name}: stopped`;
      continue;
    }
    const pass = result.results.length > 0 && result.results.every((r) => r.pass);
    const failed = result.results.find((r) => !r.pass);
    li.className = pass ? 'case case-pass' : 'case case-fail';
    li.textContent = `${name}: ${verdictText(pass, failed?.detail ?? '')}`;
    cases.push({ n: c.n, pass });
    if (c.sample) {
      // The sample's input and expected output are public (the statement shows them too).
      const reveal = el('div', 'sample-reveal');
      reveal.append(textBlock('Sample input', input, 'io-input'), textBlock('Expected output', expected, 'io-expected'));
      reveal.append(textBlock('Your output', result.stdout === '' ? '(nothing)' : result.stdout, 'io-output'));
      if (result.stderr !== '') reveal.append(textBlock('Error', result.stderr, 'io-error'));
      const svg = drawing(result.segments, `Your drawing for ${ctx.label}`);
      if (svg) reveal.append(svg);
      li.append(reveal);
    }
    const note = restartNote(result);
    if (note) li.append(el('span', 'run-note', ` ${note}`));
  }
  const skipped = check.cases.length - runnable;
  const stoppedCount = runnable - cases.length;
  const parts = [`${cases.filter((c) => c.pass).length} of ${cases.length} cases passed`];
  if (skipped > 0) parts.push(`${skipped} skipped`);
  if (stoppedCount > 0) parts.push(`${stoppedCount} not run (stopped)`);
  progress.textContent = `${parts.join(', ')}.`;
  ctx.result.prepend(verdictLine(outcomeOf(cases), cases.filter((c) => c.pass).length, cases.length));
  return cases;
}

async function checkProgram(ctx: ItemContext, check: ClientCheck, client: RunnerClient, code: string): Promise<Case[]> {
  if (check.kind !== 'asserts' && check.kind !== 'expected-output') return [];
  const files = await fetchRunFiles(check.files);
  const result = await startRun(ctx, client, {
    session: freshSession(),
    code,
    files,
    check:
      check.kind === 'asserts'
        ? { kind: 'asserts', asserts: check.asserts, turtle: check.turtle }
        : { kind: 'output', turtle: check.turtle },
    budget_ms: check.budget_ms,
  });
  if (result.status === 'interrupted') {
    ctx.result.replaceChildren(el('p', 'verdict verdict-error', 'Stopped before the check finished.'));
    return [];
  }
  const rows: { name: string; pass: boolean; detail: string }[] = [];
  if (check.kind === 'expected-output') {
    const typed = await answerHash(check.key, result.stdout, check.format);
    const pass = result.status === 'ok' && typed === check.hash;
    rows.push({ name: 'Output', pass, detail: result.status === 'ok' ? 'does not match the expected output' : stoppedDetail(result.status) });
  }
  for (const r of result.results) rows.push({ name: displayName(r.name), pass: r.pass, detail: r.detail });
  // [sol] plan 104 content review: a program that stops with an error never passes, even when
  // the asserts (still run, for feedback) pass on what it defined before the error.
  if (check.kind === 'asserts' && result.status !== 'ok') {
    const ran = result.results.some((r) => r.name.startsWith('assert '));
    const detail = result.status === 'timeout'
      ? `it ran out of time${ran ? '' : ' before the tests could run'}`
      : ran ? 'it stopped with an error (see the error below); fix it so the whole program runs' : 'it stopped with an error before the tests could run';
    rows.unshift({ name: 'Your code', pass: false, detail });
  }
  const cases = rows.map((row, i) => ({ n: i + 1, pass: row.pass }));
  const passed = cases.filter((c) => c.pass).length;
  const parts: HTMLElement[] = [verdictLine(outcomeOf(cases), passed, cases.length), resultList(rows)];
  parts.push(...runOutput(result, { drawingLabel: `Your drawing for ${ctx.label}` }));
  ctx.result.replaceChildren(...parts);
  return cases;
}

async function onCheck(ctx: ItemContext): Promise<void> {
  if (ctx.busy || !ctx.editor) return;
  setBusy(ctx, true);
  const started = performance.now();
  const code = ctx.editor.getValue();
  status(ctx, startingText());
  try {
    const [check, client] = await Promise.all([fetchJson<ClientCheck>(ctx.checkHref), runner()]);
    if (check.key !== ctx.key) throw new Error(`check for ${check.key}, not ${ctx.key}`);
    status(ctx, 'Checking…');
    const cases = check.kind === 'fixtures' ? await checkFixtures(ctx, check, client, code) : await checkProgram(ctx, check, client, code);
    if (cases.length === 0 && ctx.stopped) return;
    const outcome = outcomeOf(cases);
    await withStore((store) =>
      recordCheck(store, {
        item_key: ctx.key,
        kind: ctx.eventKind,
        result: outcome,
        cases,
        duration_ms: performance.now() - started,
        content_hash: contentHash,
      }),
    );
    await addAttempt(ctx, { kind: 'check', code, result: outcome });
  } catch (error) {
    if (isUnavailable(error)) unavailable(ctx.result);
    else {
      warn(error);
      status(ctx, 'Something went wrong while checking. Try again, or reload the page.');
    }
  } finally {
    setBusy(ctx, false);
  }
}

async function onRun(ctx: ItemContext): Promise<void> {
  if (ctx.busy || !ctx.editor) return;
  setBusy(ctx, true);
  const code = ctx.editor.getValue();
  status(ctx, runnerBooted() ? 'Running…' : 'Starting Python (the first run takes a few seconds)…');
  try {
    const [check, client] = await Promise.all([fetchJson<ClientCheck>(ctx.checkHref), runner()]);
    status(ctx, 'Running…');
    const files = 'files' in check ? await fetchRunFiles(check.files) : [];
    // A judged program reads the sample input.
    const sample = check.kind === 'fixtures' ? check.cases.find((c) => c.sample) : undefined;
    const stdin = sample ? await fetchText(sample.input) : '';
    const result = await startRun(ctx, client, {
      session: freshSession(),
      code,
      stdin,
      files,
      check: { kind: 'output', turtle: false },
      budget_ms: 'budget_ms' in check ? check.budget_ms : DEFAULT_BUDGET_MS,
    });
    const parts = runOutput(result, { drawingLabel: `Your drawing for ${ctx.label}` });
    if (sample) parts.unshift(el('p', 'run-note', 'Ran on the sample input.'));
    ctx.result.replaceChildren(...parts);
    await addAttempt(ctx, { kind: 'run', code, result: result.status === 'ok' ? 'done' : 'error' });
  } catch (error) {
    if (isUnavailable(error)) unavailable(ctx.result);
    else {
      warn(error);
      status(ctx, 'Something went wrong while running. Try again, or reload the page.');
    }
  } finally {
    setBusy(ctx, false);
  }
}

async function onAnswer(ctx: ItemContext, field: HTMLTextAreaElement): Promise<void> {
  if (ctx.busy) return;
  const typed = field.value;
  if (typed.trim() === '') {
    status(ctx, 'Type your answer first.');
    return;
  }
  setBusy(ctx, true);
  try {
    const check = await fetchJson<ClientCheck>(ctx.checkHref);
    if ((check.kind !== 'answer' && check.kind !== 'predict') || check.key !== ctx.key) throw new Error(`not a typed check: ${ctx.key}`);
    const pass = (await answerHash(check.key, typed, check.format as ClientFormat)) === check.hash;
    ctx.result.replaceChildren(
      el('p', `verdict verdict-${pass ? 'pass' : 'fail'}`, pass ? 'Correct.' : 'Not yet: that is not the expected answer.'),
    );
    const outcome = pass ? 'pass' : 'fail';
    await withStore((store) =>
      recordCheck(store, { item_key: ctx.key, kind: ctx.eventKind, result: outcome, cases: [{ n: 1, pass }], duration_ms: 0, content_hash: contentHash }),
    );
    await addAttempt(ctx, { kind: 'answer', answer: typed, result: outcome });
  } catch (error) {
    warn(error);
    status(ctx, 'Something went wrong while checking. Try again, or reload the page.');
  } finally {
    setBusy(ctx, false);
  }
}

function onStop(ctx: ItemContext): void {
  ctx.stopped = true;
  const stop = ctx.section.querySelector<HTMLButtonElement>('[data-stop]');
  if (stop) stop.disabled = true;
  if (ctx.current) ctx.current.client.interrupt(ctx.current.id);
}

// ---------------------------------------------------------------------------------------------
// Wiring

const nearObserver =
  'IntersectionObserver' in window
    ? new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) continue;
            nearObserver!.unobserve(entry.target);
            nearCallbacks.get(entry.target)?.();
            nearCallbacks.delete(entry.target);
          }
        },
        { rootMargin: '400px 0px' },
      )
    : null;
const nearCallbacks = new Map<Element, () => void>();

/** Run `action` once `target` comes within 400px of the viewport (or on focus, or at once). */
function whenNear(target: HTMLElement, action: () => void): void {
  let done = false;
  const once = () => {
    if (done) return;
    done = true;
    nearObserver?.unobserve(target);
    nearCallbacks.delete(target);
    action();
  };
  target.addEventListener('focus', once, { once: true });
  if (!nearObserver) return once();
  nearCallbacks.set(target, once);
  nearObserver.observe(target);
}

async function setup(section: HTMLElement, store: ProgressStore): Promise<void> {
  const key = section.dataset.itemKey!;
  const ctx: ItemContext = {
    section,
    key,
    label: section.querySelector('h2')?.textContent?.trim() ?? key,
    kind: section.dataset.checkKind as CheckKind,
    checkHref: section.dataset.checkHref!,
    answerHref: section.dataset.answerHref ?? null,
    eventKind: (section.dataset.eventKind ?? 'exercise') as EventKind,
    result: section.querySelector<HTMLElement>('[data-result]')!,
    editor: null,
    history: { ...NO_ATTEMPT },
    revealed: false,
    busy: false,
    current: null,
    stopped: false,
  };
  let attempts: Attempt[] = [];
  try {
    attempts = await store.attempts(key);
  } catch (error) {
    warn(error);
  }
  const lastChecklist = ctx.kind === 'self-check' ? (await store.latestEvent(key, 'self-check'))?.detail.checklist : undefined;
  ctx.history = historyOf(attempts, Boolean(lastChecklist && lastChecklist.length > 0 && lastChecklist.every(Boolean)));

  const code = section.querySelector<HTMLTextAreaElement>('textarea[data-code]');
  if (code) {
    const last = [...attempts].reverse().find((a) => a.code !== undefined);
    if (last?.code !== undefined) code.value = last.code;
    // Plain textarea first (usable at once), then CodeMirror once the editor is near the screen.
    ctx.editor = textareaEditor(code);
    const label = `Your code for ${ctx.label}`;
    whenNear(code, () =>
      void mountEditor(code, label).then((editor) => {
        if (editor.kind === 'codemirror') {
          // Keep what was typed in the plain field meanwhile.
          const hadFocus = document.activeElement === code;
          ctx.editor = editor;
          code.closest('[data-work]')?.setAttribute('data-editor-ready', '');
          if (hadFocus) editor.focus();
        }
      }),
    );
    section.querySelector('[data-run-item]')?.addEventListener('click', () => void onRun(ctx));
    section.querySelector('[data-check-item]')?.addEventListener('click', () => void onCheck(ctx));
    section.querySelector('[data-stop]')?.addEventListener('click', () => onStop(ctx));
  }

  const form = section.querySelector<HTMLFormElement>('form[data-answer-form]');
  const answer = form?.querySelector<HTMLTextAreaElement>('textarea[data-answer]');
  if (form && answer) {
    if (answer.dataset.exact !== undefined) tabInserts(answer, '\t');
    const last = [...attempts].reverse().find((a) => a.answer !== undefined);
    if (last?.answer !== undefined) answer.value = last.answer;
    form.addEventListener('submit', (event) => {
      event.preventDefault();
      void onAnswer(ctx, answer);
    });
  }

  if (ctx.kind === 'self-check') {
    section.addEventListener('change', (event) => {
      if (!(event.target instanceof HTMLInputElement) || event.target.type !== 'checkbox') return;
      const list = checklistOf(section, key);
      ctx.history.checklistDone = list.length > 0 && list.every(Boolean);
      void maybeReveal(ctx);
    });
  }
  await maybeReveal(ctx);
}

async function main(): Promise<void> {
  const sections = [...document.querySelectorAll<HTMLElement>('section.practice-item[data-check-href]')];
  if (sections.length === 0) return;
  const store = await storeReady;
  await Promise.all(sections.map((section) => setup(section, store).catch(warn)));
  document.body.dataset.checksReady = '';
}

main().catch(warn);

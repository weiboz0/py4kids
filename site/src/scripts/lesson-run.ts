/**
 * Run and Reset on a lesson's code (plan 104 Phase B; design 012 D6, the runnable reading view).
 *
 * Every runnable block (`[data-run]`, set by `renderBlock`) gets Run and Reset, and a block that
 * calls `input()` (`data-stdin`) gets an input box. Runs share one session per lesson (the entry
 * id), like the notebook's kernel: the first run of a block that needs earlier cells first replays
 * its prelude silently; Reset clears the session. If the runner restarts Python (a hang that
 * swallowed the interrupt), the session is gone, the page says so, and the next run replays the
 * prelude again. Each Run writes a `lesson-run` event (results only, never code).
 * The runner is connected on the first Run, never on page load.
 */

import type { LessonRun, RunBlock } from '../lib/check-model';
import { recordLessonRun, sharedProgress } from '../lib/progress';
import type { ResultReply, RunnerClient } from '../lib/runner-client';
import { el, fetchJson, fetchRunFiles, isUnavailable, runner, runnerBooted, runOutput, unavailable } from './run-support';

const contentHash = document.body.dataset.contentHash ?? '';
const article = document.querySelector<HTMLElement>('[data-run-href]');

function warn(error: unknown): void {
  console.warn('py4kids run:', error);
}

/** The blocks run in the lesson session since it was last new (cleared by Reset or a restart). */
const ran = new Set<string>();
let busy = false;

async function lesson(): Promise<LessonRun> {
  return fetchJson<LessonRun>(article!.dataset.runHref!);
}

async function runCode(client: RunnerClient, data: LessonRun, block: RunBlock, stdin: string): Promise<ResultReply> {
  const files = await fetchRunFiles(block.files);
  return client.run({ session: data.session, code: block.code, stdin, files, check: null, budget_ms: data.budget_ms }).result;
}


function setButtons(disabled: boolean): void {
  for (const button of document.querySelectorAll<HTMLButtonElement>('[data-lesson-run], [data-lesson-reset]')) button.disabled = disabled;
}

async function onRun(holder: HTMLElement, out: HTMLElement, stdinBox: HTMLTextAreaElement | null): Promise<void> {
  if (busy) return;
  busy = true;
  setButtons(true);
  const key = holder.dataset.key!;
  const started = performance.now();
  out.replaceChildren(el('p', 'check-status', runnerBooted() ? 'Running…' : 'Starting Python (the first run takes a few seconds)…'));
  try {
    const [data, client] = await Promise.all([lesson(), runner()]);
    const block = data.blocks[key];
    if (!block) throw new Error(`no run data for ${key}`);
    out.replaceChildren(el('p', 'check-status', 'Running…'));
    const stdin = stdinBox ? stdinBox.value : '';
    const notes: string[] = [];
    const hadState = ran.size > 0;
    let first: ResultReply | null = null;
    const exec = async (runKey: string, runBlock: RunBlock, input: string) => {
      const r = await runCode(client, data, runBlock, input);
      first ??= r;
      ran.add(runKey);
      if (r.interrupts === 'restart') ran.clear();
      return r;
    };
    /** Replay, silently, the prelude blocks this session has not run. */
    const replay = async () => {
      const missing = block.prelude.filter((k) => !ran.has(k) && data.blocks[k]);
      for (const k of missing) await exec(k, data.blocks[k]!, data.blocks[k]!.sample_input);
      return missing.length > 0;
    };
    if (await replay()) notes.push('First, the earlier code this example needs was run for you.');
    let result = await exec(key, block, stdin);
    if (hadState && (first as ResultReply | null)?.session_new) {
      // The session was lost (Python restarted): rebuild what this block needs and run it again.
      ran.clear();
      if (await replay()) {
        result = await exec(key, block, stdin);
        notes.push('Python had started fresh, so the earlier code this example needs was run again first.');
      }
    }
    const parts = runOutput(result, { drawingLabel: `Your drawing for this example` });
    if (result.interrupts === 'restart') parts.push(el('p', 'run-note', 'Everything this lesson ran before was cleared.'));
    out.replaceChildren(...notes.map((n) => el('p', 'run-note', n)), ...parts);
    const ok = result.status === 'ok';
    sharedProgress()
      .then((store) => recordLessonRun(store, key, ok, performance.now() - started, contentHash))
      .catch(warn);
  } catch (error) {
    if (isUnavailable(error)) unavailable(out, error);
    else {
      warn(error);
      out.replaceChildren(el('p', 'check-status', 'Something went wrong while running. Try again, or reload the page.'));
    }
  } finally {
    busy = false;
    setButtons(false);
  }
}

async function onReset(out: HTMLElement): Promise<void> {
  if (busy) return;
  busy = true;
  setButtons(true);
  out.replaceChildren(el('p', 'check-status', 'Resetting…'));
  try {
    const [data, client] = await Promise.all([lesson(), runner()]);
    await client.reset(data.session);
    ran.clear();
    for (const region of document.querySelectorAll<HTMLElement>('[data-run-output]')) region.replaceChildren();
    out.replaceChildren(el('p', 'run-note', 'Reset: Python starts fresh for this lesson.'));
  } catch (error) {
    if (isUnavailable(error)) unavailable(out, error);
    else warn(error);
  } finally {
    busy = false;
    setButtons(false);
  }
}

function wire(holder: HTMLElement, index: number): void {
  const controls = el('div', 'run-controls');
  let stdinBox: HTMLTextAreaElement | null = null;
  if (holder.dataset.stdin !== undefined) {
    const id = `run-stdin-${index}`;
    const label = el('label', 'work-label', 'Input for input() (one answer per line)');
    label.htmlFor = id;
    stdinBox = el('textarea', 'stdin-input');
    stdinBox.id = id;
    stdinBox.rows = 3;
    stdinBox.spellcheck = false;
    controls.append(label, stdinBox);
    // The sample input, when the lesson has one, fills the box.
    lesson()
      .then((data) => {
        const sample = data.blocks[holder.dataset.key!]?.sample_input ?? '';
        if (stdinBox && stdinBox.value === '' && sample !== '') stdinBox.value = sample;
      })
      .catch(warn);
  }
  const buttons = el('div', 'work-actions');
  const run = el('button', 'button button-primary', 'Run');
  run.type = 'button';
  run.dataset.lessonRun = '';
  const reset = el('button', 'button', 'Reset');
  reset.type = 'button';
  reset.dataset.lessonReset = '';
  reset.title = 'Clear everything this lesson’s runs have made';
  buttons.append(run, reset);
  controls.append(buttons);
  const out = el('div', 'run-output');
  out.dataset.runOutput = '';
  out.setAttribute('aria-live', 'polite');
  controls.append(out);
  holder.append(controls);
  run.addEventListener('click', () => void onRun(holder, out, stdinBox));
  reset.addEventListener('click', () => void onReset(out));
}

if (article) {
  [...article.querySelectorAll<HTMLElement>('[data-run][data-key]')].forEach(wire);
}

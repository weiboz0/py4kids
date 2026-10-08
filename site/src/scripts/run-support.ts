/**
 * What the run and check islands share (plan 104 Phase B): the page's one runner connection,
 * opened on the first Run or Check (never on page load), the lazy same-origin fetches, and the
 * output rendering. Nothing here sends anything anywhere but the runner iframe (by `postMessage`)
 * and this site's own origin (the projections and files).
 */

import { connectRunner, RunnerUnavailableError, type ResultReply, type RunFile, type RunnerClient } from '../lib/runner-client';
import type { ClientFile, Segment } from '../lib/check-model';
import { turtleSvg } from '../lib/turtle';

let connecting: Promise<RunnerClient> | null = null;
let booted = false;

/** Is Python already booted on this page? (The UI then says "Running…" and not "Starting…".) */
export const runnerBooted = () => booted;

/** The page's runner client, connected and booted; rejects with `RunnerUnavailableError`. */
export function runner(): Promise<RunnerClient> {
  connecting ??= (async () => {
    const holder = document.createElement('div');
    holder.className = 'runner-holder';
    holder.hidden = true;
    document.body.append(holder);
    const { client } = connectRunner(holder);
    await client.ping();
    booted = true;
    return client;
  })().catch((error: unknown) => {
    connecting = null;
    throw error instanceof Error ? error : new RunnerUnavailableError(String(error));
  });
  return connecting;
}

/** A fresh, unique session id for one check run (the envelope's id pattern). */
export function freshSession(): string {
  const bytes = crypto.getRandomValues(new Uint8Array(12));
  return `check-${[...bytes].map((b) => b.toString(16).padStart(2, '0')).join('')}`;
}

// ---------------------------------------------------------------------------------------------
// Fetching

const cache = new Map<string, Promise<unknown>>();

/** A same-origin JSON projection, fetched once per page. */
export function fetchJson<T>(url: string): Promise<T> {
  if (!url.startsWith('/') || url.startsWith('//')) return Promise.reject(new Error(`not a site path: ${url}`));
  let promise = cache.get(url) as Promise<T> | undefined;
  if (!promise) {
    promise = fetch(url, { credentials: 'same-origin' }).then((r) => {
      if (!r.ok) throw new Error(`${url}: ${r.status}`);
      return r.json() as Promise<T>;
    });
    promise.catch(() => cache.delete(url));
    cache.set(url, promise);
  }
  return promise;
}

async function fetchBytes(url: string): Promise<Uint8Array> {
  if (!url.startsWith('/') || url.startsWith('//')) throw new Error(`not a site path: ${url}`);
  const response = await fetch(url, { credentials: 'same-origin' });
  if (!response.ok) throw new Error(`${url}: ${response.status}`);
  return new Uint8Array(await response.arrayBuffer());
}

/** A same-origin text file (a fixture's input or expected output). */
export async function fetchText(url: string): Promise<string> {
  return new TextDecoder().decode(await fetchBytes(url));
}

/** A file to mount: UTF-8 text as is, anything else base64. */
export async function fetchRunFile(file: ClientFile): Promise<RunFile> {
  const bytes = await fetchBytes(file.url);
  try {
    return { path: file.path, data: new TextDecoder('utf-8', { fatal: true }).decode(bytes), encoding: 'utf-8' };
  } catch {
    let binary = '';
    for (const b of bytes) binary += String.fromCharCode(b);
    return { path: file.path, data: btoa(binary), encoding: 'base64' };
  }
}

export const fetchRunFiles = (files: ClientFile[]): Promise<RunFile[]> => Promise.all(files.map(fetchRunFile));

// ---------------------------------------------------------------------------------------------
// Output

export function el<K extends keyof HTMLElementTagNameMap>(tag: K, className?: string, text?: string): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

/** A labelled `<pre>` block of program text (stdout, stderr, input). */
export function textBlock(label: string, text: string, className = ''): HTMLElement {
  const box = el('div', `io ${className}`.trim());
  box.append(el('p', 'io-label', label));
  const pre = el('pre', 'output-text');
  pre.append(el('code', undefined, text));
  box.append(pre);
  return box;
}

/** A turtle drawing from returned segments (no style attribute: an SVG string we built). */
export function drawing(segments: Segment[], label: string): HTMLElement | null {
  if (segments.length === 0) return null;
  const figure = el('figure', 'turtle');
  figure.innerHTML = turtleSvg(segments, label);
  return figure;
}

/** The "Python restarted" note when a run cost a worker restart. */
export function restartNote(result: ResultReply): string | null {
  if (result.interrupts !== 'restart') return null;
  const seconds = Math.max(1, Math.round(result.timing.restart_ms / 1000));
  return `Python had to restart to stop your program (about ${seconds} s).`;
}

/** What a run's stdout, stderr and status say, as output blocks. */
export function runOutput(result: ResultReply, options: { drawingLabel: string }): HTMLElement[] {
  const out: HTMLElement[] = [];
  if (result.stdout !== '') out.push(textBlock('Output', result.stdout, 'io-output'));
  if (result.stderr !== '') out.push(textBlock(result.status === 'timeout' ? 'Stopped' : 'Error', result.stderr, 'io-error'));
  if (result.stdout === '' && result.stderr === '' && result.status === 'ok' && result.segments.length === 0) {
    out.push(el('p', 'run-note', 'Your program ran and printed nothing.'));
  }
  if (result.status === 'interrupted') out.push(el('p', 'run-note', 'Stopped.'));
  if (result.truncated) out.push(el('p', 'run-note', 'The output was long, so only the start is shown.'));
  const note = restartNote(result);
  if (note) out.push(el('p', 'run-note', note));
  const svg = drawing(result.segments, options.drawingLabel);
  if (svg) out.push(svg);
  return out;
}

/** The "Python is unavailable" message, with a reload button. */
export function unavailable(region: HTMLElement): void {
  region.replaceChildren();
  const box = el('div', 'runner-unavailable');
  box.setAttribute('role', 'alert');
  box.append(el('p', undefined, 'Python is not available right now, so this cannot run. Reloading the page usually fixes it.'));
  const reload = el('button', 'button', 'Reload the page');
  reload.type = 'button';
  reload.addEventListener('click', () => location.reload());
  box.append(reload);
  region.append(box);
}

export const isUnavailable = (error: unknown) => error instanceof RunnerUnavailableError;

/**
 * Driving the real runner from a real site page (plan 104 Phases A and D). The site's client
 * (src/lib/runner-client.ts) is bundled with esbuild and evaluated in a site page (Playwright's
 * evaluate is not subject to the page's CSP), so the tests drive the real client, the real
 * iframe on the runner origin and the real Pyodide workers.
 */
import { build } from 'esbuild';
import { join } from 'node:path';
import type { Frame, Page } from '@playwright/test';
import { BASE_URL, RUNNER_URL, SITE } from './env';
import type { ReadyReply, ResultReply, RunOptions } from '../../src/lib/runner-client';

let bundled: Promise<string> | null = null;

/** The client, bundled once per test worker. */
export function clientBundle(): Promise<string> {
  bundled ??= build({
    entryPoints: [join(SITE, 'src', 'lib', 'runner-client.ts')],
    bundle: true,
    format: 'iife',
    globalName: 'py4kidsRunnerClient',
    target: 'es2023',
    write: false,
    footer: { js: 'globalThis.py4kidsRunnerClient = py4kidsRunnerClient;' },
    define: {
      'import.meta.env.PY4KIDS_RUNNER_ORIGIN': JSON.stringify(RUNNER_URL),
      'import.meta.env.PY4KIDS_ORIGIN_PAIRS': JSON.stringify([{ site: BASE_URL, runner: RUNNER_URL }]),
    },
  }).then((out) => out.outputFiles[0]!.text);
  return bundled;
}

export interface Browserside {
  py4kidsRunnerClient: typeof import('../../src/lib/runner-client');
  runner: import('../../src/lib/runner-client').RunnerClient;
}

/** Load the client into the current page (no navigation). */
export async function loadClient(page: Page): Promise<void> {
  await page.evaluate(await clientBundle());
}

/** Open a site page, embed the runner with the real client, and wait for Python. */
export async function openRunner(page: Page, path = '/'): Promise<ReadyReply> {
  await page.goto(path);
  await loadClient(page);
  return page.evaluate(async () => {
    const w = window as unknown as Browserside;
    const { client } = w.py4kidsRunnerClient.connectRunner(document.body);
    w.runner = client;
    return client.ping();
  });
}

export function run(page: Page, options: RunOptions): Promise<ResultReply> {
  return page.evaluate((o) => (window as unknown as Browserside).runner.run(o).result, options);
}

export function runnerFrame(page: Page): Frame {
  const frame = page.frames().find((f) => f.url().startsWith(`${RUNNER_URL}/`));
  if (!frame) throw new Error('no runner frame');
  return frame;
}

export const workers = (page: Page) =>
  runnerFrame(page).evaluate(() => (globalThis as unknown as { py4kidsRunner: { workers(): number } }).py4kidsRunner.workers());

let checks = 0;
/** A fresh check session id (one per check, as the site's `freshSession`). */
export const fresh = () => `check-${Date.now()}-${++checks}`;

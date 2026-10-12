/**
 * Envelope versions across the real boundary (plan 105 "Version skew"): the runner speaks version 2
 * and still serves version N−1 (plan 104's envelope, without `v`), answering each request in its
 * own version, which keeps a site page of the previous release working while the update handshake
 * has activated only the runner. A request newer than the runner gets `version-mismatch`, so a
 * newer page asks for a reload.
 */
import { expect, test } from '@playwright/test';
import { RUNNER_URL } from './helpers/env';
import { openRunner } from './helpers/runner';

test('the runner answers a version-1 envelope in version 1, version 2 in version 2, and a newer one with version-mismatch', async ({ page }) => {
  await openRunner(page, '/');
  const replies = await page.evaluate(async (runner) => {
    const iframe = document.querySelector<HTMLIFrameElement>('iframe')!;
    const got: Record<string, unknown>[] = [];
    window.addEventListener('message', (e: MessageEvent) => {
      if (e.origin === runner && e.source === iframe.contentWindow) got.push(e.data as Record<string, unknown>);
    });
    const send = (m: object) => iframe.contentWindow!.postMessage(m, runner);
    send({ type: 'ping', id: 'v1-ping' });
    send({ type: 'run', id: 'v1-run', session: 'v1-session', code: 'print(6 * 7)', stdin: '', files: [], check: null, budget_ms: 5000 });
    send({ v: 2, type: 'ping', id: 'v2-ping' });
    send({ v: 3, type: 'ping', id: 'v3-ping' });
    const deadline = Date.now() + 60_000;
    while (got.length < 4 && Date.now() < deadline) await new Promise((r) => setTimeout(r, 100));
    return got;
  }, RUNNER_URL);
  const byId = new Map(replies.map((r) => [r.id as string, r]));
  expect(byId.get('v1-ping')).toMatchObject({ type: 'ready', isolated: true });
  expect(byId.get('v1-ping')).not.toHaveProperty('v');
  expect(byId.get('v1-run')).toMatchObject({ type: 'result', stdout: '42\n', status: 'ok' });
  expect(byId.get('v1-run')).not.toHaveProperty('v');
  expect(byId.get('v2-ping')).toMatchObject({ v: 2, type: 'ready' });
  expect(byId.get('v3-ping')).toEqual({ type: 'version-mismatch', id: 'v3-ping', supported: [1, 2] });
});

/**
 * The request recorder catches what it must (plan 103 Phase F): a deliberately leaky page fails
 * the no-network assertions. The leaks run with the CSP bypassed, since the CSP alone would stop
 * a cross-origin load before any request was made, and this proves the RECORDING, the layer that
 * would still see a leak the CSP allowed (a same-origin query string, a beacon, a worker fetch).
 */
import { assertNoNetwork, expect, test } from './helpers/net';
import { BASE_URL } from './helpers/env';

test.use({ bypassCSP: true });

const run = async (fn: () => void | Promise<void>) => {
  try {
    await fn();
  } catch (error) {
    return String(error);
  }
  return '';
};

test('a clean page passes, and each kind of leak fails the no-network assertions', async ({ page, recorder }) => {
  await page.goto('/');
  expect(await run(() => assertNoNetwork(recorder, ['zq9secret']))).toBe('');

  const clean = recorder.requests.length;
  const leak = async (code: string, expected: RegExp) => {
    recorder.requests.splice(clean);
    await page.evaluate(code);
    await expect.poll(() => recorder.requests.length, { message: code }).toBeGreaterThan(clean);
    const failure = await run(() => assertNoNetwork(recorder, ['zq9secret']));
    expect(failure, code).toMatch(expected);
  };

  // Another origin (the same server under another host name is another origin).
  const other = BASE_URL.replace('127.0.0.1', 'localhost');
  await leak(`fetch('${other}/').catch(() => {})`, /another origin/);
  // A typed sentinel in a same-origin query string, and in a header.
  await leak(`fetch('/?q=zq9secret')`, /query string|zq9secret/);
  await leak(`fetch('/', { headers: { 'x-answer': 'zq9secret' } })`, /zq9secret/);
  // A beacon (a POST with a body), and a POST from fetch.
  await leak(`navigator.sendBeacon('/', 'zq9secret')`, /method|body|beacon/);
  await leak(`fetch('/', { method: 'POST', body: 'x' }).catch(() => {})`, /method|body/);
  // A path that is not in dist/.
  await leak(`fetch('/not-a-file.json').catch(() => {})`, /not a file in dist/);
  // A request made from inside a worker is recorded at the context level too. (The worker's own
  // blob: script load is recorded as well; it is set aside so the worker's fetch alone must fail.)
  recorder.requests.splice(clean);
  await page.evaluate(`new Worker(URL.createObjectURL(new Blob(["fetch(self.location.origin + '/?w=zq9secret')"], { type: 'text/javascript' })))`);
  await expect.poll(() => recorder.requests.some((r) => r.url.endsWith('/?w=zq9secret'))).toBe(true);
  const fromWorker = recorder.requests.filter((r) => r.url.endsWith('/?w=zq9secret'));
  recorder.requests.splice(clean, Infinity, ...fromWorker);
  expect(await run(() => assertNoNetwork(recorder, ['zq9secret']))).toMatch(/query string|zq9secret/);
});

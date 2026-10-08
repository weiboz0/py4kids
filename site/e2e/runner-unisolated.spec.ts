/**
 * The runner without cross-origin isolation (plan 104 Phase D, "Interrupt path proven"): with no
 * SharedArrayBuffer the runner stops a hang by terminating and restarting the worker, and every
 * result says `interrupts: "restart"`. The site page is served without COOP/COEP through
 * `page.route`, so the page, and the runner inside it, are not cross-origin isolated.
 */
import { expect, test } from '@playwright/test';
import { BASE_URL, chromiumPath } from './helpers/env';
import { fresh, openRunner, run, runnerFrame, workers } from './helpers/runner';

// A page served through `page.route` has no remote address, so Chromium's Local Network Access
// checks would block its iframe to the local runner origin; this test turns those checks off.
test.use({ launchOptions: { executablePath: chromiumPath(), args: ['--disable-features=LocalNetworkAccessChecks'] } });
test('§3 interrupt, isolation disabled: without cross-origin isolation a hang is stopped by restarting the worker', async ({ page }) => {
  // Serve the site page without COOP/COEP: the page, and so the runner inside it, is not
  // cross-origin isolated, so there is no SharedArrayBuffer and the runner must restart.
  await page.route(`${BASE_URL}/`, async (route) => {
    const response = await route.fetch();
    const headers = Object.fromEntries(
      Object.entries(response.headers()).filter(([k]) => !['cross-origin-opener-policy', 'cross-origin-embedder-policy'].includes(k)),
    );
    await route.fulfill({ response, headers });
  });
  const ready = await openRunner(page);
  expect(ready.isolated).toBe(false);
  expect(await page.evaluate(() => self.crossOriginIsolated)).toBe(false);
  expect(await runnerFrame(page).evaluate(() => self.crossOriginIsolated)).toBe(false);
  await run(page, { session: 'u07', code: 'kept = 7' });
  const start = Date.now();
  const hang = await run(page, { session: 'u07', code: 'while True:\n    pass', budget_ms: 1000 });
  const elapsed = Date.now() - start;
  expect(hang).toMatchObject({ status: 'timeout', interrupts: 'restart' });
  expect(hang.stderr).toContain('time limit');
  // budget + 1 s grace (the runner restarts at once here, without waiting for it) + slack
  expect(elapsed).toBeLessThan(1000 + 1000 + 1500);
  const after = await run(page, { session: 'u07', code: 'print("kept" in dir())' });
  expect(after).toMatchObject({ status: 'ok', stdout: 'False\n', session_new: true, interrupts: 'sab' });
  // A check hang is a failed case, the same way.
  const fixture = await run(page, {
    session: fresh(),
    code: 'while True:\n    pass',
    check: { kind: 'fixture', expected: '1\n', match: 'token', turtle: false },
    budget_ms: 500,
  });
  expect(fixture).toMatchObject({ status: 'timeout', interrupts: 'restart', results: [{ name: 'case', pass: false, detail: 'time limit' }] });
  expect(await workers(page)).toBeLessThanOrEqual(3);
});


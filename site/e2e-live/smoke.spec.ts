/**
 * Plan 105 Phase F smoke test against the deployed origins: headers and isolation, a lesson run,
 * an expected-output check, a fixtures check, the offline download, and the alias redirect.
 */
import { expect, test } from '@playwright/test';
import { BASE_URL, RUNNER_URL } from '../e2e/helpers/env';
import { findItem, fixturePairs, lookupProgram } from '../e2e/helpers/content';
import { check, open, setCode } from '../e2e/helpers/practice';

test('the deployed site: isolation, a lesson run, two checks, an offline download, the alias', async ({ page, request }) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));

  for (const url of [`${BASE_URL}/`, `${RUNNER_URL}/`]) {
    const h = (await page.goto(url))!.headers();
    expect(h['cross-origin-opener-policy'], url).toBe('same-origin');
    expect(h['cross-origin-embedder-policy'], url).toBe('require-corp');
    expect(h['content-security-policy'], url).toBeTruthy();
  }

  await page.goto('/python-projects/');
  expect(await page.evaluate(() => crossOriginIsolated)).toBe(true);
  await page.evaluate(async () => void (await navigator.serviceWorker.ready));

  // A lesson Run.
  await page.goto('/python-projects/unit-03-turtle-art-studio/');
  const holder = page.locator('[data-run]').first();
  await holder.scrollIntoViewIfNeeded();
  await holder.locator('[data-lesson-run]').click();
  await expect(holder.locator('[data-lesson-run]')).toBeEnabled({ timeout: 120_000 });

  // An expected-output check (a real tab passes).
  const output = findItem((f) => f.item.key === 'python-concepts/unit-01-output-and-variables/exercises/u01e14a', 'u01e14a');
  let item = await open(page, output);
  await setCode(page, item, '# Print the poem.\npoem = "Sun comes up\\nBirds sing\\n\\tThe end"\nprint(poem)\n');
  expect(await check(item)).toBe('Passed.');

  // A fixtures check (usaco), every case in a fresh Python worker.
  const fixtures = findItem((f) => f.book === 'usaco-bronze' && f.item.check.kind === 'fixtures' && f.item.check.cases.length >= 2, 'a usaco item');
  item = await open(page, fixtures);
  await setCode(page, item, lookupProgram(Object.fromEntries(fixturePairs(fixtures).map((c) => [c.input, c.output]))));
  expect(await check(item)).toMatch(/^Passed/);

  // "Download this book" until both origins confirm it.
  await page.goto('/python-projects/');
  const book = page.locator('[data-offline-book]');
  await book.locator('[data-offline-download]').click();
  await expect(book.locator('[data-offline-status]')).toContainText('Available offline', { timeout: 240_000 });

  // The alias.
  const alias = await request.get('https://py4kids.futurespark.cc/python-projects/', { maxRedirects: 0 });
  expect(alias.status()).toBe(301);
  expect(alias.headers()['location']).toBe(`${BASE_URL}/python-projects/`);

  expect(errors.filter((e) => !/release\.json/.test(e))).toEqual([]);
});

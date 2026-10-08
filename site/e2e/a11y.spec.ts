/**
 * Accessibility (plan 103 Phase F): axe on every page template, in the light and the dark
 * colour scheme, after the page's islands have run, plus acsl unit 08's math lesson (its MathML
 * must be in the accessibility tree). Zero serious or critical violations; minor and moderate
 * ones are printed.
 */
import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';
import { settle, TEMPLATES } from './helpers/site';

for (const scheme of ['light', 'dark'] as const) {
  test.describe(`axe, ${scheme}`, () => {
    test.use({ colorScheme: scheme });
    for (const [name, path] of Object.entries(TEMPLATES)) {
      test(`${name} (${path})`, async ({ page }) => {
        await page.goto(path);
        await settle(page);
        if (path === '/search/') {
          await page.locator('[data-search-input]').fill('loop');
          await page.locator('[data-search-results] .search-result').first().waitFor();
        }
        const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice']).analyze();
        const blocking = results.violations.filter((v) => v.impact === 'serious' || v.impact === 'critical');
        const describe = (v: (typeof results.violations)[number]) =>
          `${v.impact} ${v.id}: ${v.help} — ${v.nodes.length} node(s): ${v.nodes.slice(0, 3).map((n) => n.target.join(' ')).join(' | ')}`;
        const other = results.violations.filter((v) => !blocking.includes(v));
        if (other.length) console.log(`${name} (${scheme}) minor/moderate:\n  ${other.map(describe).join('\n  ')}`);
        expect(blocking.map(describe)).toEqual([]);
        expect(results.passes.length).toBeGreaterThan(0);
      });
    }
  });
}

test('the math lesson exposes its MathML to the accessibility tree', async ({ page }) => {
  await page.goto('/acsl/unit-08-boolean-algebra/');
  const math = page.locator('article.lesson math');
  expect(await math.count()).toBeGreaterThan(0);
  // Chromium maps <math> to the "math" role; the snapshot must carry it with its content.
  const snapshot = await page.locator('article.lesson').ariaSnapshot();
  expect(snapshot).toMatch(/- math/);
  // The overline (NOT A) is MathML, not an image or a styled span.
  expect(await page.locator('article.lesson math mover, article.lesson math menclose').count()).toBeGreaterThan(0);
});

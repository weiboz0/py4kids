/**
 * The installable site's UI, with service workers on (plan 105 Phase E "Accessibility and
 * performance"; Phase C, the book pages' link to the export controls):
 * - **Installability**, as Chromium itself judges it: Lighthouse 13 no longer has the PWA category
 *   (its `installable-manifest` audit was removed in Lighthouse 12), so the test asks Chromium the
 *   question that audit asked, through the DevTools protocol (`Page.getInstallabilityErrors`,
 *   `Page.getAppManifest`), on the catalog, a book page and a lesson: no installability error,
 *   the parsed manifest without errors, and a service worker controlling the page (with a
 *   page without a manifest as the control). Lighthouse's own budgets (performance,
 *   accessibility, best practices) cover the book page with its download panel in
 *   e2e/lighthouse.spec.ts.
 * - **axe** (WCAG 2.2 A and AA, as e2e/a11y.spec.ts) on the new UI in both colour schemes: the
 *   download panel before, during and after a download (size, button, progress bar, status,
 *   storage results), the offline notice, the install notice, and the export and import controls
 *   with their status message. (The update notice is checked in its own states by update.spec.ts.)
 * - The book page's "Export my progress" is a link to the catalog's export controls.
 * - The offline recorder itself: a request that escapes the caches offline fails the contract.
 */
import { mkdtempSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { chromium, type Page } from '@playwright/test';
import { BASE_URL, fullChromiumPath, SITE } from '../e2e/helpers/env';
import { axe, assertOfflineContract, downloadBook, HOOKS, NetLog } from './helpers';
import { expect, test } from './servers';

const BOOK = 'python-projects';
const LESSON = '/python-projects/unit-03-turtle-art-studio/';

async function installability(page: Page): Promise<{ errors: { errorId: string }[]; manifestErrors: unknown[]; url: string }> {
  const cdp = await page.context().newCDPSession(page);
  try {
    const { installabilityErrors } = (await cdp.send('Page.getInstallabilityErrors')) as { installabilityErrors: { errorId: string }[] };
    const manifest = (await cdp.send('Page.getAppManifest', {})) as { url: string; errors: unknown[] };
    return { errors: installabilityErrors, manifestErrors: manifest.errors, url: manifest.url };
  } finally {
    await cdp.detach();
  }
}

// Chromium's installability check needs the full browser (the headless shell answers nothing) and
// a profile that is not incognito (a Playwright context is: "in-incognito"), so this test runs
// in a persistent context of the full Chromium Lighthouse uses.
test('installable, as Chromium judges it: no installability error and a valid manifest on the catalog, a book page and a lesson', async ({ servers: _ }) => {
  const profile = mkdtempSync(join(SITE, 'node_modules', '.cache', 'py4kids-install-'));
  const context = await chromium.launchPersistentContext(profile, { executablePath: fullChromiumPath(), serviceWorkers: 'allow', baseURL: BASE_URL });
  try {
    const page = context.pages()[0] ?? (await context.newPage());
    // The control: a document with no manifest is reported as not installable.
    await page.goto('/release.json');
    expect((await installability(page)).errors.map((e) => e.errorId)).toContain('no-manifest');
    // The first visit installs the worker; the pages after it are controlled by it.
    await page.goto('/');
    await page.evaluate(async () => navigator.serviceWorker.ready);
    for (const path of ['/', `/${BOOK}/`, LESSON]) {
      await page.goto(path);
      await expect.poll(() => page.evaluate(() => navigator.serviceWorker.controller !== null), { timeout: 15_000 }).toBe(true);
      const result = await installability(page);
      expect(result.url, path).toMatch(/\/manifest\.[0-9a-f]{10}\.webmanifest$/);
      expect(result.manifestErrors, `${path}: manifest errors`).toEqual([]);
      expect(result.errors, `${path}: installability errors`).toEqual([]);
    }
  } finally {
    await context.close();
    rmSync(profile, { recursive: true, force: true });
  }
});

for (const scheme of ['light', 'dark'] as const) {
  test.describe(`axe on the new UI, ${scheme}`, () => {
    test.use({ colorScheme: scheme });

    test('the download panel before and after a download; the offline and install notices', async ({ page, context, servers: _ }) => {
      await page.goto(`/${BOOK}/`);
      const panel = page.locator('[data-offline-book]');
      await expect(panel.locator('[data-offline-status]')).toHaveText('Not downloaded yet.', { timeout: 30_000 });
      await expect(panel.locator('[data-offline-size]')).toBeVisible();
      await axe(page, 'the download panel, not downloaded', '[data-offline-book]');
      await panel.getByRole('button', { name: 'Download this book' }).click();
      await expect(panel.locator('[data-offline-status]')).toHaveText('Available offline.', { timeout: 180_000 });
      await expect(panel.locator('[data-offline-persist]')).toBeVisible();
      await axe(page, 'the download panel, available offline');

      // The offline notice (the browser reports no network).
      await context.setOffline(true);
      await expect(page.locator('[data-pwa-offline]')).toBeVisible();
      await axe(page, 'the offline notice', '[data-pwa]');
      await context.setOffline(false);
      await expect(page.locator('[data-pwa-offline]')).toBeHidden();

      // The install notice, as the browser's own install prompt event shows it.
      await page.evaluate(() => {
        const event = new Event('beforeinstallprompt', { cancelable: true }) as Event & { prompt(): Promise<void>; userChoice: Promise<unknown> };
        event.prompt = () => Promise.resolve();
        event.userChoice = Promise.resolve({ outcome: 'dismissed' });
        dispatchEvent(event);
      });
      const install = page.locator('[data-pwa-install]');
      await expect(install).toBeVisible();
      await expect(install.getByRole('button', { name: 'Install' })).toBeVisible();
      await axe(page, 'the install notice', '[data-pwa]');
      await install.getByRole('button', { name: 'Not now' }).click();
      await expect(install).toBeHidden();
    });

    test('the download panel during a download (progress bar)', { tag: '@hooks' }, async ({ page, servers: _ }) => {
      test.skip(!HOOKS, 'needs a build with PY4KIDS_TEST_HOOKS=1 (the download delay)');
      await page.goto(`/${BOOK}/`);
      const panel = page.locator('[data-offline-book]');
      await expect(panel.locator('[data-offline-status]')).toHaveText('Not downloaded yet.', { timeout: 30_000 });
      await page.evaluate(() => {
        (window as unknown as { __py4kidsPwaTest: { downloadDelayMs: number } }).__py4kidsPwaTest.downloadDelayMs = 300;
      });
      await panel.getByRole('button', { name: 'Download this book' }).click();
      const bar = panel.locator('[data-offline-progress]');
      await expect.poll(async () => Number(await bar.getAttribute('value')), { timeout: 60_000 }).toBeGreaterThan(0);
      await expect(bar).toBeVisible();
      await expect(bar).toHaveAccessibleName('Download progress');
      await axe(page, 'the download panel, downloading', '[data-offline-book]');
    });

    test('the export and import controls, and their status message', async ({ page, servers: _ }) => {
      await page.goto('/');
      const transfer = page.locator('[data-transfer]');
      await expect(transfer.getByRole('button', { name: 'Export my progress' })).toBeVisible();
      await axe(page, 'the export and import controls', '[data-transfer]');
      // A malformed file: the status message says so.
      await transfer.locator('[data-transfer-import]').setInputFiles({ name: 'not-progress.json', mimeType: 'application/json', buffer: Buffer.from('{"nope": true}') });
      await expect(transfer.locator('[data-transfer-status]')).toContainText('not a py4kids progress file');
      await axe(page, 'the export and import controls with a status message', '[data-transfer]');
    });
  });
}

test('the book page\'s "Export my progress" is a link to the catalog\'s export controls', async ({ page, servers: _ }) => {
  await page.goto(`/${BOOK}/`);
  const link = page.locator('[data-offline-book]').getByRole('link', { name: /Export my progress/ });
  await expect(link).toHaveAttribute('href', '/#your-progress');
  await expect(link).toHaveAccessibleName('“Export my progress” on the home page');
  // By keyboard: focus the link and follow it.
  await link.focus();
  await expect(link).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL('/#your-progress');
  const section = page.locator('#your-progress');
  await expect(section).toBeInViewport();
  await expect(section.getByRole('button', { name: 'Export my progress' })).toBeVisible();
  await expect(section).toHaveAttribute('aria-labelledby', 'transfer-heading');
});

test('the offline recorder catches a request that escapes the caches (servers stopped)', async ({ page, context, servers }) => {
  await downloadBook(page, BOOK);
  await servers.stop();
  const log = new NetLog(context);
  await page.reload();
  await expect(page.locator('h1')).toBeVisible();
  await log.settle();
  expect(() => assertOfflineContract(log)).not.toThrow();
  // A file that is in no cache: the site's worker tries the network for it.
  await page.evaluate(() => fetch('/not-in-any-cache.json').catch(() => null));
  await log.settle();
  expect(() => assertOfflineContract(log)).toThrow(/requests a service worker made offline/);
  // A second update check in the same document load.
  log.reset();
  await page.evaluate(() => fetch(location.pathname).catch(() => null));
  await page.evaluate(() => fetch('/release.json', { cache: 'no-store' }).catch(() => null));
  await page.evaluate(() => fetch('/release.json', { cache: 'no-store' }).catch(() => null));
  await log.settle();
  expect(() => assertOfflineContract(log)).toThrow(/more than one update check/);
  // A console error.
  log.reset();
  await page.evaluate(() => fetch(location.pathname).catch(() => null));
  await page.evaluate(() => console.error('zq9 an error'));
  await log.settle();
  expect(() => assertOfflineContract(log)).toThrow(/console errors/);
});

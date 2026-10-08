// The installable, offline site's browser tests (plan 105 Phases A and B). Unlike the main config
// (playwright.config.ts), the tests start and STOP the two servers themselves
// (e2e-pwa/servers.ts): offline is proven by stopping both servers, because a service worker's
// fetches escape page-level offline emulation. The servers listen at the origins the build baked
// in, so this suite runs alone, after the main suite (`pnpm e2e` runs them in turn). It runs twice:
// on dist/ (`pnpm e2e:pwa`; the hook tests skip), and with `--grep @hooks` on the test-hooks build
// in build/site-hooks/ (`pnpm e2e:pwa-hooks`, which builds it first: scripts/hooks-build.ts).
import { defineConfig } from '@playwright/test';
import { BASE_URL, chromiumPath } from './e2e/helpers/env';

export default defineConfig({
  testDir: 'e2e-pwa',
  testMatch: '*.spec.ts',
  fullyParallel: false,
  forbidOnly: true,
  retries: 0,
  workers: 1,
  timeout: 240_000,
  reporter: [['list']],
  outputDir: 'node_modules/.cache/playwright-pwa-results',
  use: {
    baseURL: BASE_URL,
    browserName: 'chromium',
    launchOptions: { executablePath: chromiumPath() },
    serviceWorkers: 'allow',
    trace: 'off',
  },
});

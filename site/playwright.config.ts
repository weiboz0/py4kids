// The browser tests of the built site (plan 103 Phase F): end-to-end journeys, axe, Lighthouse,
// the no-network proofs and the header checks. They run against site/dist/ served by
// scripts/serve.mjs (which applies dist/_headers), with the runner (runner/dist/) on its own
// origin, so build both first: bash scripts/build-site.sh.
import { defineConfig } from '@playwright/test';
import { BASE_URL, PORT, RUNNER_DIST, RUNNER_PORT, RUNNER_URL, chromiumPath } from './e2e/helpers/env';

export default defineConfig({
  testDir: 'e2e',
  fullyParallel: true,
  forbidOnly: true,
  retries: 0,
  workers: 4,
  timeout: 120_000,
  reporter: [['list']],
  outputDir: 'node_modules/.cache/playwright-results',
  use: {
    baseURL: BASE_URL,
    browserName: 'chromium',
    launchOptions: { executablePath: chromiumPath() },
    // These suites were written for pages without a service worker; the installable, offline site
    // (plan 105) has its own suite with workers on and servers it can stop (playwright.pwa.config.ts).
    serviceWorkers: 'block',
    trace: 'off',
  },
  projects: [
    { name: 'site', testMatch: '*.spec.ts', testIgnore: ['lighthouse.spec.ts', 'solvers.spec.ts'] },
    // The no-network and request-recording proofs again with the service workers ACTIVE on both
    // origins (plan 105 Phase E): the recorder sees the workers' own requests too (context level),
    // and each must still be a body-less GET for a file of the release.
    {
      name: 'site-sw',
      testMatch: ['journey.spec.ts', 'recorder.spec.ts', 'isolation.spec.ts', 'progress-io.spec.ts'],
      grep: /no network|no-network|cannot make a request|export, clear storage, import/,
      use: { serviceWorkers: 'allow' },
    },
    // Lighthouse runs last and alone (its performance score is sensitive to CPU contention).
    { name: 'lighthouse', testMatch: 'lighthouse.spec.ts', dependencies: ['site', 'site-sw'], fullyParallel: false },
    // Reference-solver parity (plan 104 Phase D), slow and run on its own: `pnpm e2e:solvers`.
    { name: 'solvers-setup', testMatch: 'solvers.setup.ts' },
    { name: 'solvers', testMatch: 'solvers.spec.ts', dependencies: ['solvers-setup'] },
  ],
  // The site and the Python runner (plan 104) on their two origins, each with its own _headers.
  webServer: [
    {
      command: `node scripts/serve.mjs --port ${PORT} --host ${new URL(BASE_URL).hostname}`,
      url: `${BASE_URL}/`,
      reuseExistingServer: false,
      stdout: 'ignore',
      stderr: 'pipe',
    },
    {
      command: `node scripts/serve.mjs --root ${JSON.stringify(RUNNER_DIST)} --port ${RUNNER_PORT} --host ${new URL(RUNNER_URL).hostname}`,
      url: `${RUNNER_URL}/`,
      reuseExistingServer: false,
      stdout: 'ignore',
      stderr: 'pipe',
    },
  ],
});

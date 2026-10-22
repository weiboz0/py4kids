/**
 * Live smoke test of a deployed release (plan 105 Phase F): `pnpm e2e:live` with PY4KIDS_TARGET=production.
 * Runs against the real origins in deploy/origins.json "production"; never part of ci-local.
 */
import { defineConfig } from '@playwright/test';
import { BASE_URL, chromiumPath } from './e2e/helpers/env';

export default defineConfig({
  testDir: 'e2e-live',
  timeout: 300_000,
  retries: 0,
  workers: 1,
  reporter: [['list']],
  use: { baseURL: BASE_URL, launchOptions: { executablePath: chromiumPath(), args: ['--disable-ipv6', ...(process.env.PY4KIDS_LIVE_CHROMIUM_ARGS ? [process.env.PY4KIDS_LIVE_CHROMIUM_ARGS] : [])] }, serviceWorkers: 'allow' },
});

/** Where the browser tests find the site, the runner and a Chromium (plans 103 Phase F, 104). */
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { chromium } from '@playwright/test';

export const SITE = join(import.meta.dirname, '..', '..');
export const DIST = join(SITE, 'dist');
export const RUNNER_DIST = join(SITE, '..', 'runner', 'dist');

// Both origins come from runner/origins.json (or PY4KIDS_SITE_ORIGIN / PY4KIDS_RUNNER_ORIGIN): the
// runner's build bakes the site origin in (frame-ancestors, the parent it accepts) and the site's
// build bakes the runner origin in (frame-src), so the test servers listen exactly there.
const origins = JSON.parse(readFileSync(join(SITE, '..', 'runner', 'origins.json'), 'utf-8')) as { site: string; runner: string };
export const BASE_URL = process.env.PY4KIDS_SITE_ORIGIN ?? origins.site;
export const RUNNER_URL = process.env.PY4KIDS_RUNNER_ORIGIN ?? origins.runner;
export const PORT = Number(new URL(BASE_URL).port);
export const RUNNER_PORT = Number(new URL(RUNNER_URL).port);

const SYSTEM = ['/usr/bin/chromium', '/usr/bin/chromium-browser', '/usr/bin/google-chrome', '/usr/bin/google-chrome-stable'];

/**
 * Playwright's own Chromium when it is downloaded (`pnpm -C site exec playwright install
 * chromium`), else a system Chromium (scripts/site-env.sh `site_chromium` accepts either).
 * `undefined` lets Playwright launch its own headless shell.
 */
export function chromiumPath(): string | undefined {
  if (process.env.PY4KIDS_CHROMIUM) return process.env.PY4KIDS_CHROMIUM;
  if (existsSync(chromium.executablePath())) return undefined;
  return SYSTEM.find((p) => existsSync(p));
}

/** A full Chromium for Lighthouse (it launches its own browser through chrome-launcher). */
export function fullChromiumPath(): string {
  if (process.env.PY4KIDS_CHROMIUM) return process.env.PY4KIDS_CHROMIUM;
  const own = chromium.executablePath();
  if (existsSync(own)) return own;
  const system = SYSTEM.find((p) => existsSync(p));
  if (!system) throw new Error('no Chromium found for Lighthouse');
  return system;
}

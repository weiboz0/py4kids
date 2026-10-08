/** Where the browser tests find the site and a Chromium (plan 103 Phase F). */
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { chromium } from '@playwright/test';

export const PORT = Number(process.env.PY4KIDS_E2E_PORT ?? 4391);
export const BASE_URL = `http://127.0.0.1:${PORT}`;
export const SITE = join(import.meta.dirname, '..', '..');
export const DIST = join(SITE, 'dist');

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

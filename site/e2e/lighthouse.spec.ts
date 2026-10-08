/**
 * Lighthouse budgets (plan 103 Phase F): on the catalog, a book page (plan 105: its download
 * panel), a lesson and the card deck, with the default (mobile, simulated throttling)
 * configuration in headless Chromium against the built site served locally: performance >= 0.9,
 * accessibility >= 0.95, best practices >= 0.95.
 * This project runs after every other one (playwright.config.ts), one page at a time, so CPU
 * contention from parallel tests does not skew the performance score.
 */
import { createServer } from 'node:net';
import { chromium, expect, test } from '@playwright/test';
import lighthouse from 'lighthouse';
import { BASE_URL, fullChromiumPath } from './helpers/env';

const PAGES: Record<string, string> = {
  catalog: '/',
  // The book page carries the download panel (plan 105 Phase E).
  'book page': '/python-projects/',
  lesson: '/python-projects/unit-03-turtle-art-studio/',
  'card deck': '/python-projects/cards/',
};

const BUDGET = { performance: 0.9, accessibility: 0.95, 'best-practices': 0.95 } as const;

/** A free local TCP port for Chromium's DevTools endpoint. */
function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      server.close(() => resolve(typeof address === 'object' && address ? address.port : 0));
    });
  });
}

/**
 * One Lighthouse run of `url` in a fresh headless Chromium. A run whose trace recording failed
 * (`NO_NAVSTART`: "Something went wrong with recording the trace over your page load. Please run
 * Lighthouse again.") says nothing about the page, and is run again, up to twice; it happens
 * intermittently here with the site's service worker blocked too.
 */
async function audit(url: string) {
  for (let attempt = 1; ; attempt += 1) {
    const lhr = await auditOnce(url);
    if (lhr.runtimeError?.code === 'NO_NAVSTART' && attempt < 3) {
      console.log(`Lighthouse ${url}: trace recording failed (NO_NAVSTART), run again (attempt ${attempt + 1})`);
      continue;
    }
    expect(lhr.runtimeError, 'Lighthouse runtime error').toBeUndefined();
    return lhr;
  }
}

async function auditOnce(url: string) {
  const port = await freePort();
  const browser = await chromium.launch({
    executablePath: fullChromiumPath(),
    args: [`--remote-debugging-port=${port}`, '--remote-debugging-address=127.0.0.1'],
  });
  try {
    const result = await lighthouse(url, { port, output: 'json', logLevel: 'error', onlyCategories: Object.keys(BUDGET) });
    expect(result, 'Lighthouse returned a result').toBeDefined();
    return result!.lhr;
  } finally {
    await browser.close();
  }
}

/**
 * Lighthouse's own guidance for a stable performance score is the median of several runs: one
 * run varies with the machine's load (here mostly layout time, which font fallback across the
 * host's installed fonts dominates). Each page is audited RUNS times and the run with the median
 * performance score is judged, on every category.
 */
const RUNS = 3;

for (const [name, path] of Object.entries(PAGES)) {
  test(`Lighthouse: ${name} (${path})`, async () => {
    test.setTimeout(300_000);
    const runs = [];
    for (let i = 0; i < RUNS; i += 1) runs.push(await audit(`${BASE_URL}${path}`));
    runs.sort((a, b) => (a.categories.performance?.score ?? 0) - (b.categories.performance?.score ?? 0));
    const lhr = runs[Math.floor(RUNS / 2)]!;
    const scores = Object.fromEntries(Object.keys(BUDGET).map((id) => [id, lhr.categories[id]?.score ?? 0]));
    const perfRuns = runs.map((r) => r.categories.performance?.score);
    console.log(`Lighthouse ${name} (${path}): median run ${JSON.stringify(scores)}; performance runs ${JSON.stringify(perfRuns)}`);
    for (const [id, min] of Object.entries(BUDGET)) {
      const failing = lhr.categories[id]!.auditRefs
        .map((ref) => lhr.audits[ref.id]!)
        .filter((a) => a.score !== null && a.score < 1 && a.scoreDisplayMode !== 'informative' && a.scoreDisplayMode !== 'manual')
        .map((a) => `${a.id} (${a.score})`);
      expect(scores[id], `${id} on ${path}; audits below 1: ${failing.join(', ')}`).toBeGreaterThanOrEqual(min);
    }
    // Accessibility and best practices do not vary between runs: every run must meet them.
    for (const run of runs) {
      expect(run.categories.accessibility?.score ?? 0).toBeGreaterThanOrEqual(BUDGET.accessibility);
      expect(run.categories['best-practices']?.score ?? 0).toBeGreaterThanOrEqual(BUDGET['best-practices']);
    }
  });
}

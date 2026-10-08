/**
 * Response headers and the strict CSP (plan 103 Phase F, D9). The test server applies
 * dist/_headers with the Cloudflare Pages semantics (scripts/serve.mjs; test/serve.test.ts), so:
 * - every HTML response carries the CSP and the other headers, exactly;
 * - every template, /search/ with a real search (Pagefind's WebAssembly), acsl unit 08's math
 *   lesson and the acsl reference page raise zero `securitypolicyviolation` events, and no
 *   element carries a `style` attribute after the page's scripts have run;
 * - a deliberately injected inline script and inline style ARE reported (the listener works).
 */
import { readdirSync } from 'node:fs';
import { join, relative, sep } from 'node:path';
import { expect, test, type BrowserContext, type Page } from '@playwright/test';
import { CSP, parseHeaders } from '../test/helpers/headers';
import { BASE_URL, DIST } from './helpers/env';
import { search, settle, TEMPLATES } from './helpers/site';
import { readFileSync } from 'node:fs';

interface Violation {
  directive: string;
  blocked: string;
  source: string;
  sample: string;
  page: string;
}

/** Record every CSP violation of the context's pages (events and console reports alike). */
async function watchCsp(context: BrowserContext): Promise<{ violations: Violation[]; console: string[] }> {
  const violations: Violation[] = [];
  const consoleReports: string[] = [];
  await context.exposeBinding('__py4kidsCsp', ({ page }, v: Omit<Violation, 'page'>) => {
    violations.push({ ...v, page: page.url() });
  });
  await context.addInitScript(() => {
    const report = (e: SecurityPolicyViolationEvent) =>
      (window as unknown as { __py4kidsCsp(v: object): void }).__py4kidsCsp({
        directive: e.violatedDirective,
        blocked: e.blockedURI,
        source: `${e.sourceFile}:${e.lineNumber}`,
        sample: e.sample,
      });
    document.addEventListener('securitypolicyviolation', report, true);
  });
  const watch = (page: Page) => {
    page.on('console', (msg) => {
      if (/Content Security Policy|Refused to/i.test(msg.text())) consoleReports.push(`${page.url()}: ${msg.text()}`);
    });
    page.on('worker', (worker) =>
      worker.on('console', (msg) => {
        if (/Content Security Policy|Refused to/i.test(msg.text())) consoleReports.push(`worker ${worker.url()}: ${msg.text()}`);
      }),
    );
  };
  context.pages().forEach(watch);
  context.on('page', watch);
  return { violations, console: consoleReports };
}

function htmlFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((d) =>
    d.isDirectory() ? htmlFiles(join(dir, d.name)) : d.name.endsWith('.html') ? [join(dir, d.name)] : [],
  );
}

test('every HTML page is served with the CSP and the other _headers headers', async ({ request }) => {
  const expected = parseHeaders(readFileSync(join(DIST, '_headers'), 'utf-8')).get('/*')!;
  expect(expected.get('content-security-policy')).toBe(CSP);
  expect([...expected.keys()].sort()).toEqual([
    'content-security-policy',
    'cross-origin-embedder-policy',
    'cross-origin-opener-policy',
    'permissions-policy',
    'referrer-policy',
    'x-content-type-options',
  ]);
  const pages = htmlFiles(DIST).map((f) => `/${relative(DIST, f).split(sep).join('/')}`.replace(/index\.html$/, ''));
  expect(pages.length).toBeGreaterThan(200);
  const failures: string[] = [];
  for (let i = 0; i < pages.length; i += 50) {
    await Promise.all(
      pages.slice(i, i + 50).map(async (path) => {
        const response = await request.head(path);
        if (response.status() !== 200) failures.push(`${path}: HTTP ${response.status()}`);
        const headers = response.headers();
        if (!headers['content-type']?.startsWith('text/html')) failures.push(`${path}: content-type ${headers['content-type']}`);
        for (const [name, value] of expected) if (headers[name] !== value) failures.push(`${path}: ${name} = ${headers[name]}`);
      }),
    );
  }
  expect(failures).toEqual([]);
  // The other files carry them too (Pagefind's worker runs under the same CSP).
  for (const path of ['/pagefind/pagefind.js', '/pagefind/pagefind-worker.js', '/code.css', '/scripts/theme.js']) {
    const response = await request.head(path);
    expect(response.status(), path).toBe(200);
    expect(response.headers()['content-security-policy'], path).toBe(CSP);
  }
  // _headers itself is never served.
  expect((await request.get('/_headers')).status()).toBe(404);
});

const PAGES: Record<string, string> = { ...TEMPLATES, 'acsl reference': '/acsl/reference/', 'acsl unit 08 slides': '/acsl/unit-08-boolean-algebra/slides/' };

for (const [name, path] of Object.entries(PAGES)) {
  test(`zero CSP violations and no style attribute: ${name} (${path})`, async ({ context, page }) => {
    const csp = await watchCsp(context);
    const response = await page.goto(path);
    expect(response?.headers()['content-security-policy']).toBe(CSP);
    await settle(page);
    if (path === '/search/') {
      await search(page, 'variable');
      await expect(page.locator('[data-search-results] .search-result').first()).toBeVisible();
    }
    if (path.endsWith('/slides/')) {
      await page.keyboard.press('ArrowRight');
      await page.keyboard.press('End');
    }
    if (path.endsWith('/cards/')) {
      const card = page.locator('[data-deck-card] article.card');
      const reveal = card.getByRole('button', { name: /Show the (output|meaning)/ });
      if (await reveal.count()) await reveal.click();
      else if (await card.locator('.card-option').count()) await card.locator('.card-option').first().click();
      else {
        await card.locator('.card-typed input').fill('x');
        await card.locator('.card-typed button[type="submit"]').click();
      }
    }
    await page.waitForLoadState('load');
    // Violation events are queued as tasks: give any late one time to arrive.
    await page.waitForTimeout(300);
    expect(await page.locator('[style]').evaluateAll((els) => els.map((e) => e.outerHTML.slice(0, 120)))).toEqual([]);
    expect(csp.violations).toEqual([]);
    expect(csp.console).toEqual([]);
  });
}

test('the CSP listener reports a deliberately injected inline script and inline style', async ({ context, page }) => {
  const csp = await watchCsp(context);
  await page.goto('/');
  const ran = await page.evaluate(() => {
    const w = window as unknown as { __inlineRan?: boolean };
    const script = document.createElement('script');
    script.textContent = 'window.__inlineRan = true;';
    document.body.append(script);
    const style = document.createElement('style');
    style.textContent = 'body { outline: 1px solid red; }';
    document.head.append(style);
    return w.__inlineRan === true;
  });
  expect(ran, 'the inline script must not run').toBe(false);
  await expect.poll(() => csp.violations.map((v) => v.directive).sort()).toEqual(['script-src-elem', 'style-src-elem']);
  expect(csp.violations.every((v) => v.blocked === 'inline')).toBe(true);
  expect(new URL(csp.violations[0]!.page).origin).toBe(new URL(BASE_URL).origin);
});

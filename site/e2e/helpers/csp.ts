/** Record every CSP violation of a browser context's pages (plan 103 Phase F; shared with plan 104). */
import type { BrowserContext, Page } from '@playwright/test';

export interface Violation {
  directive: string;
  blocked: string;
  source: string;
  sample: string;
  page: string;
}

/** Record every CSP violation of the context's pages (events and console reports alike). */
export async function watchCsp(context: BrowserContext): Promise<{ violations: Violation[]; console: string[] }> {
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

/**
 * "Report a problem" (plan 103, Pages): one prefilled GitHub new-issue link for lessons, items
 * and cards, carrying only the item key and the bundle content hash. A plain link: no script,
 * nothing sent until the adult submits. Dependency-free so the card island can import it.
 */

export const ISSUES_URL = 'https://github.com/weiboz0/py4kids/issues/new';
export const REPORT_LABEL = 'For parents and teachers: report a problem';

export function reportHref(key: string, contentHash: string): string {
  const title = `Problem report: ${key}`;
  const body = `Item: ${key}\nContent: ${contentHash}\n\nWhat is wrong:\n`;
  return `${ISSUES_URL}?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`;
}

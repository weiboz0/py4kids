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

/** Where adults raise problems and questions (plan 103: contact is GitHub issues, no email). */
export const ISSUES_LIST_URL = 'https://github.com/weiboz0/py4kids/issues';
/** The course content license (LICENSE.md): CC BY-NC-SA 4.0, attribution "py4kids". */
export const LICENSE_URL = 'https://creativecommons.org/licenses/by-nc-sa/4.0/';
export const LICENSE_NAME = 'CC BY-NC-SA 4.0';

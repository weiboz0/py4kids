/** Driving the practice page's check islands (plan 104 Phases B and D). */
import { expect, type Locator, type Page, type Route } from '@playwright/test';
import type { ClientCheck } from '../../src/lib/check-model';
import { answerHash, type NormaliseOptions } from '../../src/lib/normalise';
import { findItem, type Found } from './content';

export const section = (page: Page, found: Found) => page.locator(`section.practice-item[data-item-key="${found.item.key}"]`);

export async function open(page: Page, found: Found): Promise<Locator> {
  await page.goto(found.page);
  await page.locator('body[data-checks-ready]').waitFor({ state: 'attached' });
  const item = section(page, found);
  await item.scrollIntoViewIfNeeded();
  return item;
}

/** Replace the editor's text (CodeMirror, in its shadow root) with `code`. */
export async function setCode(page: Page, item: Locator, code: string): Promise<void> {
  await item.locator('[data-work][data-editor-ready]').waitFor();
  await item.locator('.cm-content').click();
  await page.keyboard.press('ControlOrMeta+a');
  await page.keyboard.press('Delete');
  await page.keyboard.insertText(code);
}

/** Press Check and wait for the verdict (the buttons come back when the check ends). */
export async function check(item: Locator, timeout = 90_000): Promise<string> {
  await item.locator('[data-check-item]').click();
  await expect(item.locator('[data-check-item]')).toBeDisabled();
  await expect(item.locator('[data-check-item]')).toBeEnabled({ timeout });
  return (await item.locator('[data-result] .verdict').first().textContent()) ?? '';
}

export const caseRows = (item: Locator) => item.locator('[data-result] .case-list > li').evaluateAll((lis) => lis.map((li) => li.firstChild?.textContent ?? ''));

/** Serve a changed copy of an item's check projection. */
export async function patchCheck(page: Page, found: Found, change: (check: ClientCheck) => Promise<ClientCheck> | ClientCheck): Promise<void> {
  await page.route(`**${found.page}check/*.json`, async (route: Route) => {
    const response = await route.fetch();
    const check = (await response.json()) as ClientCheck;
    if (check.key !== found.item.key) return route.fulfill({ response });
    await route.fulfill({ response, json: await change(check) });
  });
}


/**
 * A turtle-checked item. Plan 102 (rule 1) made every real turtle item a self-check, so none is
 * checked automatically; an expected-output item's projection is served with `turtle: true` and the
 * hash of an empty output (a turtle program prints nothing), and the turtle rule runs as for a real one.
 */
export async function turtleItem(page: Page): Promise<Found> {
  const found = findItem(
    (f) => f.item.check.kind === 'expected-output' && !f.item.check.turtle && f.item.files.length === 0,
    'an expected-output item to serve as a turtle item',
  );
  const format = (found.item.check as { answer_format: NormaliseOptions }).answer_format;
  const hash = await answerHash(found.item.key, '', { case: format.case });
  await patchCheck(page, found, (c) => ({ ...c, turtle: true, hash }) as ClientCheck);
  return found;
}

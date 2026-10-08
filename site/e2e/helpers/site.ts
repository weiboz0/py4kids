/** Shared knowledge of the built site for the browser tests (plan 103 Phase F). */
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import type { Page } from '@playwright/test';
import { DIST } from './env';

export interface BookPlan {
  /** The entry whose lesson the journey reads. */
  lesson: string;
  /** The lesson draws turtle figures (an inline SVG per drawing). */
  turtle: boolean;
  /** The lesson's practice page carries self-check checklists. */
  selfCheck: boolean;
}

/**
 * Every `site: true` book and the entry its journey reads. The python books read their turtle
 * unit (figures and checklists); usaco-bronze reads its first unit; acsl reads unit 08, the
 * MathML lesson. The contest books have no self-check items (their exercises are judged), which
 * the journey asserts rather than skips silently.
 */
export const BOOKS: Record<string, BookPlan> = {
  'python-projects': { lesson: 'unit-03-turtle-art-studio', turtle: true, selfCheck: true },
  'python-concepts': { lesson: 'unit-06-turtle-geometry', turtle: true, selfCheck: true },
  'usaco-bronze': { lesson: 'unit-01-reading-the-input', turtle: false, selfCheck: false },
  acsl: { lesson: 'unit-08-boolean-algebra', turtle: false, selfCheck: false },
};

export interface DeckCard {
  key: string;
  kind: 'predict' | 'concept';
  mode: 'typed' | 'flip' | 'choice';
  unit: string;
}

export function deckOf(book: string): DeckCard[] {
  return (JSON.parse(readFileSync(join(DIST, book, 'cards', 'deck.json'), 'utf-8')) as { cards: DeckCard[] }).cards;
}

/** One page per template (plus the math lesson), for axe and the CSP checks. */
export const TEMPLATES: Record<string, string> = {
  catalog: '/',
  book: '/python-projects/',
  lesson: '/python-projects/unit-03-turtle-art-studio/',
  'lesson (checkpoint)': '/python-projects/checkpoint-01-first-steps/',
  'lesson (project)': '/python-projects/project-01-arcade-night/',
  practice: '/python-projects/unit-03-turtle-art-studio/practice/',
  'practice (judged)': '/usaco-bronze/unit-01-reading-the-input/practice/',
  slides: '/python-projects/unit-03-turtle-art-studio/slides/',
  cards: '/python-projects/cards/',
  glossary: '/acsl/glossary/',
  reference: '/acsl/reference/',
  search: '/search/',
  about: '/about/',
  privacy: '/privacy/',
  terms: '/terms/',
  'math lesson (acsl unit 08)': '/acsl/unit-08-boolean-algebra/',
};

/** Wait until the page's own islands have run: the card deck, search and the slide player. */
export async function settle(page: Page): Promise<void> {
  const path = new URL(page.url()).pathname;
  if (path.endsWith('/cards/')) await page.locator('[data-deck-card] .card').first().waitFor();
  if (path === '/search/') await page.locator('[data-search-form]').waitFor();
  if (path.endsWith('/slides/')) await page.locator('.deck.is-live').waitFor();
}

/** Run a search on /search/ and wait for its result count. */
export async function search(page: Page, term: string, bookTitle?: string): Promise<void> {
  await page.locator('[data-search-form]').waitFor();
  if (bookTitle) await page.locator('[data-search-book]').selectOption({ label: bookTitle });
  await page.locator('[data-search-input]').fill(term);
  await page.locator('[data-search-status]').filter({ hasText: /match/ }).waitFor();
}

/** Everything in the `py4kids` IndexedDB database, by store. */
export async function stores(page: Page): Promise<Record<string, Record<string, unknown>[]>> {
  return page.evaluate(
    () =>
      new Promise((resolve, reject) => {
        const open = indexedDB.open('py4kids');
        open.onerror = () => reject(open.error);
        open.onsuccess = () => {
          const db = open.result;
          const names = [...db.objectStoreNames];
          const tx = db.transaction(names, 'readonly');
          const out: Record<string, Record<string, unknown>[]> = {};
          for (const name of names) {
            const req = tx.objectStore(name).getAll();
            req.onsuccess = () => (out[name] = req.result as Record<string, unknown>[]);
          }
          tx.oncomplete = () => {
            db.close();
            resolve(out);
          };
          tx.onerror = () => reject(tx.error);
        };
      }),
  );
}

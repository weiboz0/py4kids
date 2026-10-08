/**
 * Lesson blocks by key, shared by the card deck (`cards.ts`, build time) and the mastery map
 * (`mastery.ts`, which a client island imports). Kept dependency-free so the island never pulls
 * the build-time Markdown pipeline (Shiki, KaTeX) into the browser bundle.
 */

import type { LoadedBook } from './bundle';
import type { Block } from './types';

/** Every lesson block of the book by key (predict cards and preludes reference them). */
export function blocksByKey(book: LoadedBook): Map<string, Block> {
  const map = new Map<string, Block>();
  for (const { data } of book.entries) for (const block of data.lesson?.blocks ?? []) map.set(block.key, block);
  return map;
}

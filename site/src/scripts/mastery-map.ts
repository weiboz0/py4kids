/**
 * The mastery map island (plan 103 "Mastery map and cards (D8)"): fills each concept's
 * percentage from `/<book>/mastery.json` and the on-device card boxes (1/k weighting, box >= 3).
 */

import { conceptMastery, type MasteryProjection } from '../lib/mastery';
import { sharedProgress } from '../lib/progress';

async function main(): Promise<void> {
  const section = document.querySelector<HTMLElement>('[data-mastery]');
  const book = section?.dataset.book;
  if (!section || !book) return;
  const response = await fetch(`/${book}/mastery.json`);
  if (!response.ok) throw new Error(`mastery.json: HTTP ${response.status}`);
  const projection = (await response.json()) as MasteryProjection;
  const store = await sharedProgress();
  const mastery = conceptMastery(projection, await store.cards(book));
  for (const row of section.querySelectorAll<HTMLElement>('[data-concept]')) {
    const share = mastery.get(row.dataset.concept!);
    if (share === undefined) continue;
    const pct = Math.round(share * 100);
    const bar = row.querySelector<HTMLProgressElement>('[data-mastery-bar]');
    const text = row.querySelector<HTMLElement>('[data-mastery-pct]');
    if (bar) bar.value = pct;
    if (text) text.textContent = `${pct}%`;
  }
}

main().catch((error: unknown) => console.warn('py4kids mastery:', error));

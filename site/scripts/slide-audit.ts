/**
 * The slide audit (plan 103 D6): `pnpm -C site slide-audit`.
 *
 * For every site bundle under site/content (or $PY4KIDS_SITE_CONTENT) it builds the slides with
 * the player's own rules (src/lib/slides.ts) and reports, per book:
 * - every indivisible unit over max_unit_words, every table over max_table_rows and every code
 *   slide over max_code_lines (failures, unless the block key is in `<book>/site.yaml`
 *   `slides.allow` with a reason);
 * - every unit between max_words and max_unit_words, and the notice-only slide count (reported,
 *   never failing).
 * A stale `slides.allow` key (one that matches no oversized unit) also fails.
 * Exit status: 0 when every book passes, 1 otherwise.
 */
import { loadBooks, repoRoot } from '../src/lib/bundle.ts';
import { auditLoadedBook, auditPasses, formatAudit } from '../src/lib/slide-config.ts';

const repo = repoRoot();
let failed = false;
for (const book of loadBooks()) {
  const { audit, config } = auditLoadedBook(repo, book);
  for (const line of formatAudit(audit, config)) console.log(line);
  if (!auditPasses(audit)) failed = true;
}
if (failed) {
  console.error(
    'slide-audit: FAIL (split the block with a slide-break tag, or list its key with a reason in <book>/site.yaml slides.allow)',
  );
  process.exit(1);
}
console.log('slide-audit: OK');

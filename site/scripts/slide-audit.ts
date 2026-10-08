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
 * A stale `slides.allow` key (one that matches no oversized unit) also fails. On the default
 * content directory, every `site: true` book in books.yaml must have a bundle, or the audit
 * fails. The last line names every audited book with its slide count.
 * Exit status: 0 when every book passes, 1 otherwise.
 */
import { CONTENT_ENV, loadBooks, repoRoot } from '../src/lib/bundle.ts';
import { runAudit, siteBookIds } from '../src/lib/slide-config.ts';

const repo = repoRoot();
const expected = process.env[CONTENT_ENV] ? undefined : siteBookIds(repo);
const run = runAudit(repo, loadBooks(), expected);
for (const line of run.lines) console.log(line);
if (!run.passed) {
  console.error(
    'slide-audit: FAIL (split the block with a slide-break tag, or list its key with a reason in <book>/site.yaml slides.allow)',
  );
  process.exit(1);
}

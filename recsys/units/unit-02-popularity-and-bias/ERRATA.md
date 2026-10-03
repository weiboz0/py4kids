# Errata — Unit 2: Popularity and weighted baselines

## 2026-10-03 — recsys-004 generator regeneration

Plan recsys-004 redesigned the synthetic interaction generator (taste-aware exposure:
exposure proportional to `popularity^alpha * exp(beta * z-scored affinity)`). The positive
rate rose (~0.23 -> ~0.33), so more readers are scored and the measured figures changed.
`catalog.csv.gz` and `cold_partitions.json` are byte-identical to before.

Updated figures (verified on the committed seed, k=10, cold readers excluded):

- Scored readers: **500** (was 368). `solutions.ipynb` Exercise 3 assert updated to
  `readers_scored == 500`; all "368 readers" prose updated in `lesson.ipynb`,
  `teacher-notes.md`, and `projects/bookrec/milestones/unit-02-popularity.ipynb`.
- Popularity hit@10 ~0.11 vs random floor ~0.012 (still roughly 9x the floor); prose
  updated from the old ~0.12 / ~0.014.
- Popularity catalog coverage ~0.008 (about 16 of 2000 books), was ~0.007 / 14 of 2000;
  random coverage ~0.92 (was ~0.84); head-share 1.0 (unchanged).

### Quality-vs-floor correction (the substantive content fix)

The old narrative claimed the positive-rate "quality" ranking scores **below** the random
floor (~0.005 vs ~0.014). Under the taste-aware generator that is no longer true and, per
plan recsys-004 implementation note 3, the quality-vs-floor relationship is **seed-dependent**
(sometimes just above, sometimes just below the floor). The corrected lesson makes the robust
point instead:

- Ranking by positive **rate** ignores BOTH popularity AND the reader, so it lands **far below
  popularity** — on this seed ~0.016 (hit@10), only ~1.3x the random floor and roughly 7x below
  the count path's ~0.11.
- The assert `quality_hit < random_board.hit_rate_at_k` was **dropped** (not seed-robust) and
  replaced with `quality_hit < 0.5 * pop_board.hit_rate_at_k` (quality loses badly to popularity).
- The popularity-bias-in-the-metric lesson is preserved, but the holdout is now described as
  popularity-**weighted** (taste-aware exposure), not popularity-**only**.

Affected cells: `lesson.ipynb` sections 2-3 and the coverage figures; `solutions.ipynb`
Exercises 5-6; `exercises.ipynb` Exercise 5 statement; the Unit-2 milestone prose; `teacher-notes.md`.

Re-verified unchanged-in-direction: `tests/test_unit02.py` value-pinned contracts
(popularity hit@10 > 0.05 and > 5x random; coverage < 0.05 and < 0.1x random; head-share == 1.0)
all still pass on the regenerated data.

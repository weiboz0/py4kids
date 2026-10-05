# Plan recsys-008 — Unit 6: Evaluation deepened + Blend v1 + Checkpoint A (end of Part 1)

**Design:** `docs/designs/011-recsys-book.md` (§5 blend architecture, §8 row 6, §9 budgets). **Book:** `recsys`
(Book 3). **Autopilot** per AGENTS.md. Sixth and final **Part-1** unit, on the Units 1–5 substrate (random/popularity/
lexical/item-item-CF/MF paths + the taste-aware generator). Closes Part 1 with the **first blended system** and the
book's **first checkpoint**. Scope confirmed by the user (2026-10-05): **one plan** covering the U6 unit AND
Checkpoint A.

## Scope
**Unit 6** (`recsys/units/unit-06-evaluation-and-blending/`) + **Checkpoint A**
(`recsys/checkpoints/checkpoint-01-part-1/`). Teaches **evaluation deepened** (ranking metrics beyond hit@k — NDCG,
precision@k; the ratings-RMSE-vs-ranking contrast; **beyond-accuracy** coverage/diversity/novelty; the **cold-start**
framing as a cross-unit thread → U9/U13; **path ablations**) and the **first blended recommender** — calibrate +
weight-blend the Part-1 paths (`blend.blend`) and order with the classical ranker (`rank.rank`), measured on `val`.
**Checkpoint A** is the Part-1 assessment: it **unseals the `test` holdout** (sealed since U1) for a one-time honest
final score, checkpoint-**strict** (no borrowed tools), assessing only U1–U6 concepts. No PyTorch/neural (Part 2). No
generator change.

## Why this works on the data (empirical, MEASURED — [fable] round 1; Phase B re-confirms on the shipped code)
Part-1 paths on committed `val` (seed 0, k=10, 60 cold readers excluded, 500 readers): popularity 0.108 (coverage
0.008), lexical 0.158 (0.278), item-item CF 0.252 (0.490), **MF 0.276 (0.074)**. **PINNED blend config (binding):
per-path retrieval pool = 30**, weights **{popularity 0.25, lexical 0.5, item-item 1.0, MF 1.0}**, `blend.blend`
(calibrated weighted union) → `rank.rank(exclude=seen)`. Measured blend: **hit@10 ~0.306 (≥ MF 0.276) and catalog
coverage ~0.33 (≫ MF's 0.074)**. So the honest, data-grounded thesis: **a calibrated, sensibly-weighted blend beats
the best single path AND covers 4–5× more of the catalog.**

Two measured facts bind the lesson (NOT a free choice of framing — pool/weights are PINNED above so the subagent
cannot tune them on `val`, which is the anti-lesson the unit teaches):
- **Pool size matters:** equal-weight blend swings 0.242 (pool 10, < MF) → 0.280 (pool 30) → 0.298 (pool 50). We pin
  pool = 30.
- **Popularity has NEGATIVE marginal value:** leave-one-out (pool 30) — **−popularity 0.306 (↑)**, −lexical 0.254,
  −item-item 0.244, −MF 0.246. Dropping popularity *raises* hit@10 at every pool, because min-max calibration gives
  every path's top item score 1.0, so a reader-independent popularity path ties its head books with every reader's
  true top pick. The lesson/teacher-notes MUST teach this: "every path contributes" is FALSE here; a path earns its
  place by reader-dependence, and a weak/flat path can *tie* strong paths at the top once calibrated. (This is also
  why the pinned weights down-weight popularity to 0.25 rather than dropping it — it still adds head coverage.)

Phase-B assertions bind to the PINNED config with a tolerance (e.g. `blend_hit >= mf_hit - 0.01` AND
`blend_coverage >= 3 * mf_coverage` AND the signed leave-one-out table reproduced). Reviewers re-verify against the
shipped scoreboard, not a scratch script.

## Buildout
Whole-book `lessons` total becomes **18.5** (U1–U6 at 3 each = 18, plus Checkpoint A at **0.5** — checkpoints DO
count, per `tools/curriculum.py lesson_budget_findings`, and every coverage entry incl. a checkpoint requires a
positive `lessons`; usaco-bronze/python-projects use `0.5`) < 30 → `buildout: true` retained. (Crosses ≥30 around
U8–U10; a later plan removes it.)

## Audience & retained laws
Advanced baseline (design 011). Retained in full: project-first; taught-before-assessed; student notebooks (exercises
AND the checkpoint) carry NO solutions/outputs; solutions + milestone run clean (fixed seeds); teacher-notes;
from-scratch→reveal-the-library; a stretch exercise per unit. **Checkpoint is STRICT** (design 004 borrowed-tool
relaxation does NOT apply to checkpoints): everything the checkpoint assesses must be taught in U1–U6. CPU-light
(numpy + `bookrec`; no torch/faiss) routed `--group recsys`; within the per-notebook exec budget (design §9).

## Concepts introduced (3) — `concepts.yaml`
- `ranking-metrics` — rank-position-aware offline metrics beyond hit-rate/recall: **precision@k** and **NDCG@k**
  (gain discounted by log rank); the ratings-**RMSE**-vs-ranking contrast (why a ranking metric, not RMSE, for
  top-k). `kind: technique`, `category: techniques`.
- `beyond-accuracy` — **coverage / diversity / novelty**: a recommender is more than hit@k — catalog coverage,
  intra-list diversity (1 − mean pairwise similarity), and novelty (mean self-information −log₂ popularity).
  `kind: technique`, `category: techniques`.
- `score-blending` — combining multiple retrieval paths into one pool: per-path **calibration** to a common scale,
  **weighted** union, provenance, ordering with the classical ranker, and **path ablations** (leave-one-path-out).
  Includes the **calibration pitfall**: min-max calibration maps every path's top candidate to 1.0, so a weak or
  reader-independent path can *tie* strong paths at the top of the pool — the mechanism behind the measured
  "dropping popularity raises hit@10" ablation. `kind: technique`, `category: techniques`.
All three globally unique (confirm 0 hits across `*/curriculum/concepts.yaml` in Phase A). **`cold-start` is a strictly
UNASSESSED preview** in U6: a short prose mention in the lesson only — NO exercise drills it and the strict checkpoint
does NOT assess it (that would violate taught-before-assessed, since it is registered + taught + assessed in U9). The
lesson MAY concretely show the 60 `cold_readers` (for whom MF/CF/lexical return `[]` while popularity does not) as a
graceful-degradation demo — but that is **score-blending/robustness** content (a taught U6 concept), not a cold-start
assessment, and earns no cold-start credit.

### Coverage-map entries
- `unit-06-evaluation-and-blending`, `kind: unit`, `title: "Evaluation deepened and the first blend"`, `lessons: 3`,
  `introduces: [ranking-metrics, beyond-accuracy, score-blending]`,
  `requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, popularity-ranking,
  popularity-bias, item-item-cf, matrix-factorization, latent-factors]`,
  `practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, popularity-bias]`.
- `checkpoint-01-part-1`, `kind: checkpoint`, `title: "Checkpoint A — the Part-1 recommender"`, **`lessons: 0.5`**
  (required + counted), listed AFTER the unit entry (so `checkpoint_findings` sees U6's introductions),
  `requires: [...all Part-1 introduced ids...]`,
  `practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, popularity-ranking,
  bayesian-shrinkage, popularity-bias, bag-of-words, tf-idf, bm25, item-item-cf, knn-similarity, implicit-feedback,
  matrix-factorization, latent-factors, gradient-descent, ranking-metrics, beyond-accuracy, score-blending]`.
  (Phase A confirms `practices ∩ introduces = ∅` for each entry; the checkpoint introduces nothing. No `project`
  entry → the capstone rule stays inert until U14. Closes under buildout.)

## Phases

### Phase A — registry + syllabus
- `concepts.yaml`: add the 3 ids. `coverage-map.yaml`: add the unit + checkpoint entries (buildout comment →
  "eighteen"). `baseline.yaml`: declare any new `x.name(...)` methods the authored cells use (confirm against cells;
  e.g. `blend`, `rank`, `ndcg_at_k`, `precision_at_k`, `intra_list_diversity`, `novelty`, numpy idioms).
- `unit-06-evaluation-and-blending/manifest.yaml`; `checkpoint-01-part-1/manifest.yaml` (`kind: checkpoint`,
  `lessons: 0.5`, `blueprint_version: 1`, `provenance: original`, matching the coverage entry);
  `syllabus.md` — add TWO real table rows in map order: the U6 arc row `| 6 | \`unit-06-evaluation-and-blending\` |
  unit | 3 | <hook> |` AND a checkpoint row `| — | \`checkpoint-01-part-1\` | checkpoint | 0.5 | <blurb> |` placed
  AFTER the U6 row (`tools/curriculum.py syllabus_findings` requires a real row for EVERY map entry in order — a prose
  note fails coverage-check, match the existing table's column shape); rebuild PDF.
- `baseline.yaml`: the checkpoint/solution call `run_validation_scoreboard(..., split="test")` is a MODULE function,
  not an `x.name(...)` attribute call, so `split=` needs NO `library_methods` entry; confirm no spurious add. Only add
  genuinely new attribute-call methods (e.g. `precision_at_k`/`ndcg_at_k`/`intra_list_diversity`/`novelty` if called
  as `bookrec.X(...)` vs module fns — confirm against the authored cells).
**Verify:** manifest/prereq/coverage (incl. `syllabus_findings`) green for both entries; buildout holds (18.5<30);
concepts unique.

### Phase B — `bookrec` evaluation/diversity extensions + blend measurement (Opus subagent; numpy-only)
Dispatch an **Opus subagent**. STUDY `evaluate.py` (`hit_rate_at_k`/`recall_at_k`/`mean_hit_rate_at_k`),
`diversity.py` (`catalog_coverage`/`head_share`), `blend.py` (`blend`), `rank.py` (`rank`), `scoreboard.py`,
`protocol.py`. ADD (additively; preserve existing signatures):
- `evaluate.py`: `precision_at_k(recommendations, relevant, k)` and `ndcg_at_k(recommendations, relevant, k)`
  (binary-gain DCG/IDCG, log₂ rank discount; defined/0-safe when `relevant` is empty). Pure, deterministic.
- `diversity.py`: `intra_list_diversity(recommendations, similarity)` (1 − mean pairwise similarity over the top-k;
  similarity from a supplied item–item function/matrix) and `novelty(recommendations, popularity)` (mean
  self-information −log₂ p̂(item), p̂ from train counts). Pure, deterministic, 0-safe.
- `scoreboard.py`: **additively** generalize `run_validation_scoreboard` to take a **`split=` param** (default
  `"val"`; `"test"` permitted — same cold-reader exclusion applies to both) and extend `ScoreboardResult` with
  **precision@k / NDCG@k** fields (keep hit/recall; existing callers unaffected). This is the single piece
  Checkpoint A needs to score `test` once.
- A **blended-scoreboard** helper/test that fits popularity+lexical+CF+MF, retrieves **per-path pool = 30** candidates
  each, `blend.blend(..., weights={popularity:0.25, lexical:0.5, item-item:1.0, mf:1.0})` → `rank.rank(exclude=seen)`,
  and computes hit@10 + coverage at the **PINNED config** (above). Compute the **leave-one-path-out ablation table
  WITH SIGN** (must reproduce −popularity ↑) and coverage/diversity for blend vs the best single path.
- Tests (routed): the new metrics against hand-checkable fixtures (NDCG of a known ranking; precision; a 2-item
  diversity; novelty monotonic in rarity); blend determinism; assertions bound to the measured PINNED-config numbers:
  `blend_hit >= mf_hit - 0.01` (≈0.306 vs 0.276), `blend_coverage >= 3 * mf_coverage` (≈0.33 vs 0.074), and the
  signed leave-one-out (`drop_popularity_hit > full_blend_hit`). Keep per-path fits at their pinned configs; budget.
- **Test-holdout hygiene guard** (also enforced in Phase H): a scan asserting no Unit-6 lesson/exercises/solutions/
  milestone notebook source filters `split == "test"` (or passes `split="test"`) — ONLY
  `checkpoints/checkpoint-01-part-1/solutions.ipynb` may. Keeps "`test` sealed since U1" true for everything but the
  one unsealing.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, numpy-only; **report the
measured blend hit@10 + coverage + the signed ablation table so the lesson/checkpoint numbers are bound to the shipped
code (not [fable]'s scratch script); ALSO report the `test`-split reader count after cold exclusion (≈593 w/ positives,
2339 rows) so Checkpoint A's "how val and test differ" discussion has a concrete number.**

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "we have five paths and a scoreboard — but *which* recommender is actually best, and best at *what*?". Arc:
(1) **ranking metrics**: hit@k/recall@k only see presence; precision@k and **NDCG** reward putting the right book
high; the RMSE-vs-ranking contrast (why not RMSE for implicit top-k). (2) **beyond-accuracy**: coverage/diversity/
novelty — two paths with equal hit@k can serve very different catalogs (tie back to U2 popularity bias; U4's
818 unreachable items; MF's low 0.074 coverage). (3) **blend v1** at the PINNED config: calibrate each path to a
common scale, weighted-union with `blend.blend`, order with `rank.rank(exclude=seen)`; measure on `val` — blend
~0.306 ≥ MF 0.276 AND coverage ~0.33 ≫ 0.074. The **leave-one-path-out ablation** delivers the headline insight:
**dropping popularity RAISES hit@10** — teach why (min-max calibration ties a reader-independent path's head books
with every reader's top pick), so "every path helps" is false and a path earns its place by reader-dependence. Show
the 60 `cold_readers` concretely (personalized paths return `[]`, popularity/blend still serve them) as a
**graceful-degradation / robustness** demo — a score-blending benefit. Close with a SHORT **unassessed** prose
pointer to the broader **cold-start** problem (a brand-new book no path has signal for → taught in U9, system ethics
in U13) — no exercise, no assessment here. ASCII only; reuse `bookrec`; ≤ budget fits.
**Verify:** `exec-lessons` clean (budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds), ≥3
non-vacuous asserts. Drill: compute precision@k/NDCG@k by hand then via `bookrec`; coverage/diversity/novelty of a
path's recs; calibrate+blend the paths at the pinned config and read the blended scoreboard honestly (NOT "blend
always wins"); the leave-one-path-out ablation + interpret the −popularity ↑ result. Stretch e.g.: sweep the
per-path pool size (≤4 fits/cell budget) and show hit@10 swings; construct two recommenders with equal hit@k but
different coverage/diversity; reproduce the calibration pitfall (a flat path tying strong paths at the top).
**Taught-before-assessed: do NOT drill cold-start (it is only an unassessed preview here) and do NOT touch the `test`
split.** Seeded.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-06-evaluation-and-blending.ipynb` — fixed-seed demo: fit all Part-1 paths,
build the **blended recommender**, show the `val` scoreboard (hit@10 + precision@10 + NDCG@10 + coverage + diversity)
for each path AND the blend, plus the leave-one-path-out ablation table, with the honest Phase-B framing. Passes
`milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget.

### Phase F — Checkpoint A (Opus subagent for STATEMENT; SEPARATE fresh Opus subagent for SOLUTION)
`recsys/checkpoints/checkpoint-01-part-1/{checkpoint.ipynb, solutions.ipynb, teacher-notes.md, manifest.yaml}`.
The **Part-1 assessment**, checkpoint-**STRICT** (no borrowed tools; assess ONLY U1–U6 taught concepts — NOT
cold-start). `checkpoint.ipynb` has **6–8 `## Question N` headings** (not `## Exercise`; `tools/notebooks.py` checkpoint
structure), NO solutions/outputs, ASCII, first cell non-empty markdown.
**The `test`-holdout unseal, operationally explicit (freeze-then-score):** earlier questions have the student assemble
and tune the Part-1 recommender **on `val`** (choose paths, blend weights at the pinned-style pool, read the deepened
metrics) and FREEZE every decision; then ONE final question loads `test` and runs a SINGLE aggregate evaluation
(`run_validation_scoreboard(..., split="test")` or the taught metric fns) with NO return to selection. Questions cover:
building/selecting paths, precision@k/NDCG@k, coverage/diversity interpretation, the ablation reading, and the
one-time `test` score + honest interpretation (how val vs test differ; why you evaluate test once).
`solutions.ipynb` (SEPARATE fresh Opus session) runs clean (fixed seeds, ≥3 non-vacuous asserts), and is the ONLY
Unit-6/Checkpoint notebook permitted to touch `split="test"`. `manifest.yaml` `kind: checkpoint`, `lessons: 0.5`, the
Part-1 `requires`/`practices`. `teacher-notes.md` MUST include a **`## Grading`** heading (checkpoint teacher-notes
contract) with a rubric + common mistakes (test-set hygiene: evaluate `test` ONCE, never tune against it).
**Verify:** `hygiene`/`structure` (6–8 `## Question N`)/`cell-lint`/`noexec` on `checkpoint.ipynb`;
`exec-solutions`/`concept-scan` on the solution; `manifest-check`/`prereq-check`/`coverage-check` accept the checkpoint
entry; checkpoint-strict (no borrowed-tool markers); `## Grading` present in teacher-notes.

### Phase G — teacher-notes.md (unit; inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises assigned), `## Common mistakes` (reading
hit@k as the only metric; test-set leakage/tuning on the holdout; assuming a blend always beats the best path AND
assuming "every path contributes" — the measured −popularity ↑ ablation refutes both; the **calibration pitfall** —
min-max blending lets a weak/flat path TIE strong paths at the top of the pool; equating coverage with accuracy;
leaving the per-path pool at k (too small — pool 30 needed)), `## Discussion prompts` (when does blending help, and
why did popularity hurt? what does NDCG reward that hit@k ignores? which reader is each path best for? what is
cold-start and why can't a Part-1 blend solve it → U9?), `## Differentiation`.

### Phase H — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–6 + Checkpoint A + the Unit-6 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (18.5). Run the **test-holdout hygiene scan** (Phase B) —
only `checkpoints/checkpoint-01-part-1/solutions.ipynb` may reference `split="test"`. Confirm exec stays within the
whole-book CI budget.

## Out of scope
No PyTorch/neural (two-tower = U8; learned reranker = U11); no ANN/FAISS (U10); no `cold-start` CONCEPT id (framed as
a thread here, registered/taught in U9); no generator change; no `projects/project-*` map entry (capstone = U14); no
buildout removal; no Checkpoint B (U13).

## Verification phase declared
Phase H is this plan's named verification phase. Units/checkpoint ship with it.

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE.** Registry closes: the unit's `requires` are all introduced by U1–U5; the unit `practices`
(retrieve-then-rank/offline-evaluation/top-k-ranking-metrics/popularity-bias) keep `practices ∩ introduces = ∅`; and
the **checkpoint's `practices` provides the practice home for U6's three new concepts** (ranking-metrics/
beyond-accuracy/score-blending) — which is precisely why bundling U6 + Checkpoint A in one plan is the right call
(a split would leave the new concepts without a practice home inside recsys-008's own coverage-check). Checkpoint
introduces nothing (`practices ∩ introduces = ∅` trivially); no `project` entry → capstone rule inert; buildout holds
(18<30, checkpoints excluded from the lesson budget). Phase B is **additive** (ndcg/precision → evaluate.py,
diversity/novelty → diversity.py; blend.py/rank.py already exist) with no signature collisions. The Blend-v1 accuracy
claim is **conditional and measured-first** (the hard-won discipline from U3/U5/U7) with an honest coverage/robustness
fallback. Checkpoint A is strict, unseals `test` once (no tuning), assesses only U1–U6. Named Phase H present;
project-first hook; ≥6/≥2-stretch/≥3-asserts; teacher-notes. `cold-start` framed as a thread, registered in U9 where
taught. No [self] blockers.

**[sol] — REJECT** (3 Must + 1 Should; all verified correct against the tooling):
1. `[OPEN]` **Must** — checkpoints DO require a positive `lessons` value (`tools/curriculum.py` schema fails
   `lessons <= 0`) and `lesson_budget_findings` **sums every entry incl. checkpoints** (usaco-bronze uses
   `lessons: 0.5`). So "no `lessons`; checkpoints do not count" cannot pass Phase H. → Fix: Checkpoint A gets
   `lessons: 0.5` in both coverage-map + manifest; whole-book total = 18 + 0.5 = **18.5 < 30** (buildout holds).
2. `[OPEN]` **Must** — the empirical fallback is under-specified: "within noise"/"real margin"/`tol` undefined; the
   `<MF` branch assumes weights recover parity; no branch for "neither parity NOR a coverage/diversity win"; and it
   risks selecting AND evaluating weights on the same `val`. → Fix: prespecify the comparison + a concrete tolerance
   (and/or a bootstrap/paired-SE uncertainty note), forbid tuning+scoring weights on the same observations without
   qualification, and give a COMPLETE decision table binding the headline/assertions to every possible outcome
   (incl. "blend wins nothing on hit@k here → it is the extensible substrate the U11 learned reranker improves, and
   its value today is coverage/robustness").
3. `[OPEN]` **Must** — `cold-start` can't be both "assessed" and "unregistered": the plan has U6 teach it, an exercise
   practice it, AND the STRICT checkpoint assess a reflection on it, while deferring its concept id to U9 — a
   taught-before-assessed violation. → Fix (chosen): keep cold-start as a strictly **unassessed preview** — a prose
   mention in the lesson ONLY; REMOVE the cold-start exercise (Phase D) and the checkpoint cold-start reflection
   (Phase F). It is registered + taught + assessed in U9.
4. `[OPEN]` **Should** — make the `test` unseal operationally explicit: freeze the chosen paths/weights/ALL decisions
   on `val` BEFORE loading `test`, then one aggregate `test` evaluation with no return to selection. The existing
   `scoreboard.run_validation_scoreboard` is val-only. → Fix: Phase B generalizes the scoreboard to take a split (or
   adds a test variant) so the checkpoint can score `test` once; Phase F spells out the freeze-then-score protocol.

**[fable] — APPROVE WITH NITS** (2 Must + 4 Should + 2 Nice; **measured the blend on the shipped data**, seed 0,
k=10, 500 val readers). Singles: pop 0.108 (cov 0.008), lexical 0.158 (0.278), item-item CF 0.252 (0.490), MF 0.276
(0.074). Equal-weight blend of all four: pool 10 → 0.242/cov 0.343; **pool 30 → 0.280/0.271**; pool 50 → 0.298/0.214.
Leave-one-out (pool 30): **−popularity 0.306 (↑)**, −lexical 0.254, −item-item 0.244, −MF 0.246 (dropping popularity
RAISES hit@10 at every pool). Weighted {pop .25, lex .5, CF 1, MF 1} pool 30 → **0.306 / cov 0.333**.
1. `[OPEN]` **Must** (= [sol]#1) — checkpoint needs `lessons: 0.5` (coverage-map + manifest); `lesson_budget_findings`
   silently returns `[]` (disables buildout accounting) if any entry lacks numeric `lessons`. Total → 18.5 < 30.
2. `[OPEN]` **Must** — **PIN the blend config before measuring + record it in the plan**: per-path pool size (pin
   **30**; result swings 0.242→0.298 across pool 10→50), weights (down-weight popularity), `rank(exclude=seen)`; bind
   the Phase-B assertions to that pinned config. Report the leave-one-out table WITH SIGN; the lesson/teacher-notes
   MUST state the measured fact that **dropping popularity raises hit@10** (the honest story: a reader-independent
   path adds only head coverage and costs accuracy once min-max-calibrated to [0,1]). Without pinning, the subagent
   could reach any framing by tuning pool/weights on `val` — the exact anti-lesson.
3. `[OPEN]` **Should** (= [sol]#4) — `run_validation_scoreboard` hardcodes `split=="val"` + carries only hit/recall.
   Either (a) add a `split=` param (default "val") + precision/NDCG fields, additively, OR (b) have the checkpoint
   student write the test-eval loop from taught pieces. Pick one so Phase-F doesn't improvise a leaky loop. (test:
   593 readers w/ positives, 2339 rows — confirm cold readers excluded there too.)
4. `[OPEN]` **Should** — Phase F checkpoint CI contracts: **6–8 `## Question N` headings** (not `## Exercise`) +
   **`## Grading`** in the checkpoint teacher-notes (`tools/notebooks.py` CHECKPOINT_NOTES_HEADINGS). Name both.
5. `[OPEN]` **Should** — `score-blending` definition must name the **calibration pitfall**: min-max makes every path's
   top item 1.0, so a weak/flat path ties strong paths at the top (the mechanism behind the ablation). Flip the
   common-mistake from "un-calibrated letting one dominate" to "calibrated blending letting a WEAK path tie".
6. `[OPEN]` **Should** — add a cheap **test-holdout hygiene guard** (Phase B/H scan): no U6 lesson/exercise/solution/
   milestone notebook source may filter `split == "test"`; only the checkpoint solution may. Keeps "sealed since U1" true.
7. `[CONFIRMED]` **Nice** — cold-start-as-thread is honest (design §8 U6→U9→U13); the 60 `cold_readers` (MF/CF/lexical
   return `[]`, popularity doesn't) are a FREE graceful-degradation demo for the ablation — no concept id needed.
8. `[CONFIRMED]` **Nice** — registry closure checks out (requires ⊆ U1–U5; practices∩introduces=∅ both entries;
   checkpoint entry must be listed AFTER the unit entry for `checkpoint_findings`); Phase H named; blend reuses
   `blend.blend`/`rank.rank` with no signature change.

### Plan-review outcome (round 1): **NOT consensus — [sol] REJECT (3 Must) + [fable] APPROVE WITH NITS + [self] APPROVE.** [fable]'s measurement RESOLVES the empirical risk: framing #2 holds under a PINNED config (pool 30, popularity down-weighted → ~0.306 ≥ MF, coverage ~0.33 ≫ 0.074), with the drop-popularity ablation as the honest headline. Fold all → **v2** (concrete pinned config replaces the 3-branch conditional; checkpoint `lessons: 0.5`; cold-start unassessed; split-aware scoreboard; checkpoint `## Question`/`## Grading` contracts; calibration-pitfall framing; test-hygiene guard), then round-2 re-review.

### Round 2 (on v2)

**v2 changelog** (folds [sol] 3 Must + 1 Should and [fable] 2 Must + 4 Should): (a) checkpoint `lessons: 0.5` in
coverage-map + manifest; buildout total 18.5<30; checkpoints DO count [sol#1/fable#1]; (b) "Why this works" replaced
with the MEASURED result + a **PINNED** blend config (pool 30, weights {pop .25, lex .5, CF 1, MF 1} → ~0.306 ≥ MF,
coverage ~0.33); Phase-B assertions bound to it; the −popularity↑ ablation is the taught headline [fable#2/sol#2];
(c) cold-start demoted to a strictly **unassessed** lesson preview — removed from exercises (Phase D) and the
checkpoint (Phase F); the 60-cold-reader graceful-degradation demo reframed as score-blending/robustness [sol#3];
(d) Phase B additively adds `split=`+precision/NDCG to the scoreboard so the checkpoint scores `test` once
[sol#4/fable#3]; (e) Phase F names the 6–8 `## Question N` + `## Grading` contracts and the freeze-then-score test
protocol [fable#4]; (f) `score-blending` concept + common-mistakes name the calibration pitfall [fable#5]; (g)
test-holdout hygiene scan added to Phase B/H [fable#6]; (h) cold-start-thread + registry closure confirmed
[fable#7/#8].

**[self] — APPROVE (round 2).** All six Must folded and internally consistent; the empirical thesis is now pinned and
data-bound (not a free framing choice); checkpoint registration matches the tooling (`lessons: 0.5`, counted);
cold-start is unassessed; the scoreboard extension is additive; checkpoint CI contracts (`## Question`/`## Grading`)
named; test-hygiene guarded. No [self] blockers.

**[sol] — APPROVE (round 2).** All three round-1 Must + the Should confirmed resolved; no new blocker.

**[fable] — APPROVE WITH NITS (round 2).** All 8 round-1 findings resolved (verified against the tooling line-by-line);
registry closure + checkpoint-after-unit ordering re-confirmed. New nits, folded as v2.1:
1. `[FIXED]` **Should** — Phase A must add a real syllabus TABLE row for the checkpoint (not a prose note);
   `syllabus_findings` requires a row per map entry in order. → Phase A now specifies both rows.
2. `[FIXED]` **Nice** — `split=` is a module-fn kwarg, no `baseline.yaml` `library_methods` entry needed. → Phase A
   note added.
3. `[FIXED]` **Nice** — Phase B should report the `test`-split reader count after cold exclusion (≈593/2339). → added.

### Plan-review gate outcome: **CONSENSUS — [self] APPROVE · [sol] APPROVE · [fable] APPROVE WITH NITS; no open Must.**
3-way roster (GLM removed). v2 is data-grounded (pinned blend config measured ~0.306 ≥ MF, coverage ~0.33; the
−popularity↑ ablation is the taught headline). Proceed to the build (Phase A → H).

## Content Review

### Round 1 — [fable] (2026-10-05)
- **Verdict**: APPROVE WITH NITS (no Must Fix). Blind-solved Ex1/Ex2/Ex7 + checkpoint Q1/Q7 and re-measured
  (blend 0.306/0.333, test 0.306/0.338/500, ablation −pop +0.002, pinned-weight sweep 0.278/0.306/0.316); honest
  framing, freeze-then-score, strict-checkpoint, test-hygiene, project-first all verified.
1. `[OPEN]` **Should** — exercises.ipynb (intro / `POOL`/`WEIGHTS` comments / Ex6 prose+`pool_explanation`) + the same
  solutions cells frame **val-selection itself** as the sin ("pinned so you never tune it on val — the anti-lesson"),
  contradicting the book protocol (val IS the selection split; Unit 1 + Checkpoint A Q5 + milestone all say "choose on
  val, test stays sealed"). Realign to lesson cell 12's precise version: val is for selection, but don't report the
  val-MAX of a sweep as expected performance (selecting+reporting on the same split biases it), and never touch test.
2. `[OPEN]` **Should** — lesson.ipynb cells 0 & 11 say item-item reaches "nearly/almost 5x more books"; 0.49/0.0745 =
  **6.6×** (solutions correctly say 6.6×). Fix to "~6.6×".
3. `[OPEN]` **Nice** — checkpoint intro (both notebooks) says "five retrieval paths" but Q2 fits/blends FOUR (random
  floor absent). Say "four signal paths (plus the random floor)".
4. `[OPEN]` **Nice** — checkpoint intro "build and tune a calibrated blend" vs Q5 pre-filling the config → "adopt the
  Unit-6 configuration, measure on val, and freeze it".
5. `[OPEN]` **Nice** — Ex6: coverage FALLS as pool grows (0.379→0.333→0.3075) — a stronger measured reason to pin 30;
  add a clause.
6. `[OPEN]` **Nice** — `assert blend_hit >= mf_hit - 0.01` (Ex4 + checkpoint Q5) is slack vs its "at least the best
  single path" message; the adjacent strict `blend_beats_best_single` already enforces it — drop the −0.01 or reword.

### Round 1 — [sol] (2026-10-05)
- **Verdict**: REJECT (4 Must + 2 Should). One REJECT blocks.
1. `[FIXED]` **Must** — `evaluate.py` precision/NDCG gave duplicate rec-ids repeated credit (`ndcg_at_k([1,1],{1},2)`
   = 1.63 > 1). → `_ranked_ids` now de-dups stably (no-op on real unique recs; fixes range-safety) + regression test
   `test_ranking_metrics_are_range_safe_on_duplicate_ids` (6 metric tests pass, ruff clean).
2. `[OPEN]` **Must** — checkpoint Q6 + the `## Grading` rubric assess cold-reader robustness while teacher-notes say
   "no cold-start assessment". → Resolve: Q6 grades the ablation (popularity ≈0 marginal accuracy) + the calibration
   pitfall (both taught); the cold-reader/robustness point becomes GIVEN context, not a graded requirement; and the
   teacher-notes clarify that the cold-START problem (new items/features → U9) is unassessed, distinct from the
   score-blending robustness U6 teaches.
3. `[OPEN]` **Must** (= [fable]#1) — "tuning on val is the cardinal sin" contradicts the book protocol + Checkpoint A
   ("choose on val, freeze, score test once"). → Reframe everywhere: val IS the selection split; the discipline is
   not reporting the val-MAX of a sweep as expected performance, and keeping `test` sealed for one read.
4. `[OPEN]` **Must** — "popularity retained for head coverage" is FALSE: dropping popularity RAISES coverage
   (0.333→0.354). → Fix everywhere: popularity adds neither accuracy (≈0) nor coverage; it is kept ONLY for
   cold-reader robustness. Separate the claims in prose + the milestone + the checkpoint.
5. `[OPEN]` **Should** (= [fable]#2) — item-item vs MF coverage is **6.6×** (0.49/0.0745), not "nearly 5×"; 4.5× is
   blend-vs-MF. → Fix lesson cells.
6. `[OPEN]` **Should** — "a path earns its place by being reader-dependent" overgeneralizes; the MEASURED
   leave-one-out improvement is what establishes contribution (reader-dependence explains popularity's weakness but
   isn't sufficient). → Reword lesson/exercises/checkpoint.

### Content-gate round 1 outcome: **NOT consensus — [sol] REJECT (4 Must) + [fable] APPROVE WITH NITS + [self] (pending).**
Must#1 fixed in code. Must#2/#3/#4 + Should#5/#6 + [fable]'s 6 nits are prose reframes across the 5 notebooks +
checkpoint teacher-notes — folding with a single canonical framing (val = selection split; popularity kept only for
cold-reader robustness, not coverage/accuracy; contribution = measured marginal value; cold-START unassessed vs
score-blending robustness taught). Then re-run ci-local + re-review [sol].

### Round 1 — [self] (2026-10-05)
- **Verdict**: APPROVE WITH NITS → all resolved. Project-first, from-scratch→reveal, structure (7 exercises + 7
  checkpoint Questions), taught-before-assessed (cold-start unassessed), strict checkpoint + freeze-then-score +
  test-holdout hygiene, honest framing all hold. The [sol]/[fable] findings are folded (below).

### Resolution (commits fdb5921 + 0635b8d) — every finding `[FIXED]`:
- **[sol]#1** metric dedup — `_ranked_ids` stable de-dup + regression test (range-safe on dup ids; no-op on real recs).
- **[sol]#2 / cold-case** — checkpoint Q6 grades ablation + calibration pitfall only; cold-reader robustness is
  explicit "given context, not graded"; teacher-notes split cold-START (U9, unassessed) from taught robustness.
- **[sol]#3 = [fable]#1 / val-selection** — reframed across lesson/exercises/solutions/milestone/checkpoint: `val` is
  the selection split; the discipline is not reporting the val-sweep max + keeping `test` sealed.
- **[sol]#4 / popularity-coverage** — corrected everywhere: popularity adds neither accuracy nor coverage (dropping it
  raises coverage 0.333→0.354); kept only for cold-reader robustness.
- **[sol]#5 = [fable]#2 / 6.6×** — item-item-vs-MF coverage fixed to ~6.6× (4.5× left only for blend-vs-MF).
- **[sol]#6 / reader-dependence** — contribution established by measured leave-one-out, not the label.
- **[fable]#3** checkpoint "four signal paths (+ random floor)"; **#4** "adopt/measure/freeze" not "tune"; **#5** Ex6
  coverage-falls clause; **#6** tightened slack assert to `>= mf_hit`.
All re-verified GREEN (hygiene/structure/cell-lint/noexec/concept-scan/exec-lessons/exec-solutions/milestone-check +
18 tests incl. the test-holdout guard); measured numbers unchanged.

### Content-gate round 2: re-running full `ci-local.sh` + re-reviewing **[sol]** (sole rejecter) on the fixes; [fable] + [self] already APPROVE/APPROVE-WITH-NITS, all nits folded.

<!-- appended pre-PR -->

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->

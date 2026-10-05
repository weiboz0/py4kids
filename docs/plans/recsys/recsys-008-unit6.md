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

## Why this works on the data (empirical, binding — MUST be measured in Phase B before the lesson claims anything)
The Part-1 paths on the committed `val` (seed 0, k=10, 60 cold readers excluded, 500 readers): random 0.012,
popularity 0.108, lexical 0.158, item-item CF 0.252, MF 0.276. **The unit's thesis is that a calibrated blend of
complementary paths is at least as good as the best single path AND better on beyond-accuracy (coverage/diversity).**
Phase B MUST measure the blended path's `val` hit@10 and bind the lesson to the result, in this order of preference:
1. **If blend hit@10 ≥ MF (best single) + a real margin** → the lesson's headline is "blending helps accuracy too".
2. **If blend ≈ MF within noise** (the likely honest outcome — MF already captures most of the signal) → headline is
   **"blending trades a little top-line accuracy for robustness and coverage"**: the blend matches the best path on
   hit@k while improving **catalog coverage / diversity** and degrading gracefully when a path is cold (the ablation
   story). This is the honest, generator-agnostic framing (mirrors the U3 lexical / U5 "on par" discipline).
3. **If blend < MF** → do NOT ship a blend that loses; instead teach calibration/weighting as the *mechanism*, show
   which weights recover parity, and frame blend v1 as the extensible substrate Part 2's learned reranker (U11)
   improves. Record the measured numbers either way.
Reviewers MUST empirically verify the chosen framing against a scratch measurement (not assert it).

## Buildout
Whole-book `lessons` total becomes **18** (U1–U6, 3 each) < 30 → `buildout: true` retained. (Crosses ≥30 around
U8–U10; a later plan removes it.) Checkpoints do not count toward the lesson budget.

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
  **weighted** union, provenance, and ordering with the classical ranker; **path ablations** (leave-one-path-out).
  `kind: technique`, `category: techniques`.
All three globally unique (confirm 0 hits across `*/curriculum/concepts.yaml` in Phase A). (`cold-start` is framed in
the lesson/teacher-notes as a cross-unit THREAD and named in prose, but is **introduced** as a registered concept in
U9 where it is actually taught/practiced — U6 only motivates it, so it earns no U6 concept id; confirm this is the
honest call at the gate.)

### Coverage-map entries
- `unit-06-evaluation-and-blending`, `kind: unit`, `title: "Evaluation deepened and the first blend"`, `lessons: 3`,
  `introduces: [ranking-metrics, beyond-accuracy, score-blending]`,
  `requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics, popularity-ranking,
  popularity-bias, item-item-cf, matrix-factorization, latent-factors]`,
  `practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, popularity-bias]`.
- `checkpoint-01-part-1`, `kind: checkpoint`, `title: "Checkpoint A — the Part-1 recommender"`, (no `lessons`),
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
- `unit-06-evaluation-and-blending/manifest.yaml`; `checkpoint-01-part-1/manifest.yaml` (`kind: checkpoint`);
  `syllabus.md` arc row `| 6 | ... |` + note Checkpoint A; rebuild PDF.
**Verify:** manifest/prereq/coverage checks green for both entries; buildout holds (18<30); concepts unique.

### Phase B — `bookrec` evaluation/diversity extensions + blend measurement (Opus subagent; numpy-only)
Dispatch an **Opus subagent**. STUDY `evaluate.py` (`hit_rate_at_k`/`recall_at_k`/`mean_hit_rate_at_k`),
`diversity.py` (`catalog_coverage`/`head_share`), `blend.py` (`blend`), `rank.py` (`rank`), `scoreboard.py`,
`protocol.py`. ADD (additively; preserve existing signatures):
- `evaluate.py`: `precision_at_k(recommendations, relevant, k)` and `ndcg_at_k(recommendations, relevant, k)`
  (binary-gain DCG/IDCG, log₂ rank discount; defined/0-safe when `relevant` is empty). Pure, deterministic.
- `diversity.py`: `intra_list_diversity(recommendations, similarity)` (1 − mean pairwise similarity over the top-k;
  similarity from a supplied item–item function/matrix) and `novelty(recommendations, popularity)` (mean
  self-information −log₂ p̂(item), p̂ from train counts). Pure, deterministic, 0-safe.
- A thin **blended-scoreboard** helper or test that fits popularity+lexical+CF+MF, retrieves per path for each val
  reader, `blend.blend(...)`s (calibrated, weighted) and `rank.rank(...)`s, and computes hit@10 — the Phase-B
  measurement that decides the "Why this works" framing. Also compute a **leave-one-path-out ablation** table and
  coverage/diversity for blend vs the best single path.
- Tests (routed): the new metrics against hand-checkable fixtures (NDCG of a known ranking; precision; a 2-item
  diversity; novelty monotonic in rarity); blend determinism; the blended-path hit@10 + the ablation numbers recorded
  as assertions bound to whichever framing Phase B establishes (e.g. `blend_hit >= mf_hit - tol` AND
  `blend_coverage >= mf_coverage`). Keep fits at the pinned per-path configs; stay within the exec budget.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/ -q` green, deterministic, numpy-only; **report the
measured blend hit@10, the ablation table, and coverage/diversity so the lesson/checkpoint framing is bound to data.**

### Phase C — lesson.ipynb (Opus subagent; project-first)
Hook: "we have five paths and a scoreboard — but *which* recommender is actually best, and best at *what*?". Arc:
(1) **ranking metrics**: hit@k/recall@k only see presence; precision@k and **NDCG** reward putting the right book
high; the RMSE-vs-ranking contrast (why not RMSE for implicit top-k). (2) **beyond-accuracy**: coverage/diversity/
novelty — two paths with equal hit@k can serve very different catalogs (tie back to U2 popularity bias; U4's
818 unreachable items). (3) **blend v1**: calibrate each path to a common scale, weighted-union with `blend.blend`,
order with `rank.rank`; measure on `val` and tell the **honest** story Phase B established; a **leave-one-path-out
ablation** shows each path's marginal contribution; the **cold-start thread** (a new book/reader no path covers yet →
U9/U13). ASCII only; `rank(exclude=seen)`; reuse `bookrec`; ≤ budget fits.
**Verify:** `exec-lessons` clean (budget); non-empty markdown first cell; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
≥6 `## Exercise N`; ≥2 `stretch`; exercises NO solutions/outputs; solutions mirror all, clean (fixed seeds), ≥3
non-vacuous asserts. Drill: compute precision@k/NDCG@k by hand then via `bookrec`; coverage/diversity/novelty of a
path's recs; calibrate+blend two or more paths and read the blended scoreboard honestly (NOT "blend always wins");
a leave-one-out ablation. Stretch e.g.: tune blend weights (≤4 fits/cell budget); construct two recommenders with
equal hit@k but different coverage/diversity; the cold-start case a blend still misses. Taught-before-assessed; seeded.
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec`; `exec-solutions` clean (budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-06-evaluation-and-blending.ipynb` — fixed-seed demo: fit all Part-1 paths,
build the **blended recommender**, show the `val` scoreboard (hit@10 + precision@10 + NDCG@10 + coverage + diversity)
for each path AND the blend, plus the leave-one-path-out ablation table, with the honest Phase-B framing. Passes
`milestone-check` + `exec-solutions` + `concept-scan`; ≤ budget.

### Phase F — Checkpoint A (Opus subagent for STATEMENT; SEPARATE fresh Opus subagent for SOLUTION)
`recsys/checkpoints/checkpoint-01-part-1/{checkpoint.ipynb, solutions.ipynb, teacher-notes.md, manifest.yaml}`.
The **Part-1 assessment**, checkpoint-**STRICT** (no borrowed tools; assess only U1–U6 taught concepts). It **unseals
the `test` holdout** for a one-time honest final score: the student assembles the Part-1 recommender (choose/blend
paths), evaluates it on `test` with the deepened metrics, and interprets the result (which path/blend, coverage, a
cold-start reflection). `checkpoint.ipynb` carries NO solutions/outputs; `solutions.ipynb` runs clean (fixed seeds,
≥3 non-vacuous asserts) and is authored by a SEPARATE fresh Opus session. `manifest.yaml` `kind: checkpoint` with the
Part-1 `requires`/`practices`. Teacher-notes: grading guidance + a rubric + common mistakes (test-set hygiene: you
evaluate on `test` ONCE; no tuning against it).
**Verify:** `hygiene`/`structure`/`cell-lint`/`noexec` on `checkpoint.ipynb`; `exec-solutions`/`concept-scan` on the
solution; `manifest-check`/`prereq-check`/`coverage-check` accept the checkpoint entry; checkpoint-strict (no
borrowed-tool markers).

### Phase G — teacher-notes.md (unit; inline)
`## Goals`, `## Pacing` (60–90 min / 2–3 sittings, hook first, all exercises assigned), `## Common mistakes` (reading
hit@k as the only metric; test-set leakage/tuning; assuming a blend always beats the best path; equating coverage with
accuracy; un-calibrated blending letting one path dominate), `## Discussion prompts` (when does blending help? what
does NDCG reward that hit@k ignores? which reader is each path best for? cold-start → U9), `## Differentiation`.

### Phase H — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–6 + Checkpoint A + the Unit-6 milestone AND
`bash scripts/pre-merge-guard.sh --pr` OK. buildout holds (18). Confirm exec stays within the whole-book CI budget.

## Out of scope
No PyTorch/neural (two-tower = U8; learned reranker = U11); no ANN/FAISS (U10); no `cold-start` CONCEPT id (framed as
a thread here, registered/taught in U9); no generator change; no `projects/project-*` map entry (capstone = U14); no
buildout removal; no Checkpoint B (U13).

## Verification phase declared
Phase H is this plan's named verification phase. Units/checkpoint ship with it.

## Plan Review

<!-- round 1 appended -->

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->

# Plan recsys-016 — Unit 13: Evaluating the whole system (ethics & beyond-accuracy) + Checkpoint B

**Design:** `docs/designs/011-recsys-book.md`:
- §8 row 13: "Evaluating the whole system; **ethics & beyond-accuracy**: exposure/popularity bias, feedback loops,
  filter bubbles, fairness, offline-metric limits; per-path ablations → System-wide eval; **Checkpoint B**".
- §8 threads: the cold-start thread runs U6 → U9 → **U13**; the ethics thread.
- §6: U13/U14 score the sequence path **on the session log only**.
- §7 determinism; §9 budgets.

**Book:** `recsys` (Book 3). **Autopilot**; the standing goal is "complete the recsys book with autopilot". Like
recsys-008 (U6 + Checkpoint A), this is **one plan** for the unit **and** the Part-2 checkpoint.

**Prerequisite noted (recsys-015):** the book-wide exec time (about 38 min loaded, before U12; about 44 min after)
already exceeds the design §9 "≤ ~15 CI-minute" *target*. A **book-wide exec-budget slice is required before U14**.
It will cache fits under `assets/` with a regeneration check, or amend the target, with user review. It is out of
scope here, but this plan must **not** make the overrun materially worse. U13 + Checkpoint B use only cheap and
already-measured fits (see Budget).

## Scope
**Unit 13** (`recsys/units/unit-13-whole-system-ethics/`). It teaches three things on the main log, using the paths
built in U2–U10:
1. **Feedback loops.** A recommender retrained on what it recommended concentrates exposure ("rich get richer"). A
   self-contained multi-round **simulation**:
   - simulated readers take a top-k recommendation with a fixed probability;
   - the accepted reads are appended to the train log, and the path is refit;
   - after each round, measure catalog coverage, head-share, the exposure Gini and accuracy.
   Compare a popularity loop with an item-item CF loop, then add one **mitigation** (an exploration slot, or a
   popularity-penalised re-rank) and show what it buys and costs.
2. **Exposure fairness.** Who gets recommended? Measure the distribution of exposure across **books and authors**
   (Gini coefficient of exposure, long-tail share) for each path and for the Part-1 / U10 blends. Then show the
   accuracy ↔ exposure-fairness **trade-off curve** of a popularity-penalty re-rank (a Pareto readout, not a single
   winner).
3. **Filter bubbles.** For each reader, measure the **genre spread** of the recommendations (genre entropy, or
   intra-list diversity from U6) against the reader's own history. Then measure narrowing across the feedback-loop
   rounds.

It also covers **offline-metric limits** (prose plus one measurement: offline hit@k rewards what the logging policy
already exposed, so popularity bias inflates offline scores). The **cold-start thread closes here**: a per-path
readout on the cold partitions (cold items via the U9 feature tower, versus every warm-only path, which scores 0 on
cold items).

**Checkpoint B** (`recsys/checkpoints/checkpoint-02-part-2/`, `lessons: 0.5`) is the Part-2 assessment. It is
checkpoint-**strict** (no borrowed tools; it assesses only taught concepts) and is the book's **second authorized
`test` unseal**: freeze on `val`, then score once on `test`. It assesses a **lean subset** of U7–U13 (see Phase F).
No sequence-path test unseal on the session log is required. A Part-2 sequence question is scored on the session
log's **val** only, unless the plan gate decides otherwise.

## Budget (binding; probe-measured at the plan gate)
- **Fits allowed in U13 notebooks:** numpy/cheap paths (popularity, lexical, item-item, MF ~15 s, semantic
  embeddings) plus at most **one** two-tower fit (~15 s). For the cold-start readout, **one** feature-tower fit
  (~20–27 s) in the lesson and milestone only. **No** reranker, SASRec or ANN index builds in U13.
- **Feedback-loop simulation:** numpy only (popularity + item-item CF refits are sub-second). The rounds and
  readers are sized by the probe so that the whole simulation takes ≤ 30 s per notebook.
- **Checkpoint B solutions:** at most one MF (~15 s) and one two-tower (~15 s); hybrid, if used, reuses the two-tower
  vectors. The probe measures this, and each notebook ≤ 2.5 min.
- **Routed pytest delta:** ≤ +60 s.
- Phase B reports the per-notebook exec time and the U13 + Checkpoint B delta against the recorded ~44 min.

## Gate (pinned by the plan-gate probe; re-measured in Phase B on shipped code)
Main log, val, k = 10, committed seed:
- **(a) feedback loop concentrates:** after R rounds, the item-item CF loop's catalog coverage falls, or its exposure
  Gini rises, by a pinned margin versus round 0, and the popularity loop is already near its floor.
- **(b) mitigation helps exposure at a measured accuracy cost:** with the mitigation, the loop's coverage or Gini at
  round R is better than without it, by a pinned margin. The hit@10 cost is recorded (not hidden).
- **(c) fairness trade-off is real:** the popularity-penalty re-rank traces a monotone curve. A higher penalty lowers
  the exposure Gini and changes hit@10. Record at least 3 points.
- **(d) recorded:** genre-spread narrowing across rounds; per-path Gini/head-share table; the cold-start readout;
  the offline-metric-limit measurement.
Determinism: the simulation is seeded, and two runs give identical round metrics (`allclose`).

## Audience and retained laws
Advanced baseline. Retained in full:
- project-first;
- taught-before-assessed;
- student notebooks carry no solutions or outputs;
- solutions and milestone run clean;
- teacher-notes;
- from-scratch → reveal (Gini by hand → `bookrec` helper; simulation loop by hand → `bookrec` helper);
- stretch exercises;
- the checkpoint is strict.

The ethics framing is **measured and non-preachy**. Every claim is backed by a number on our data, and the
discussion prompts present trade-offs, not verdicts.

## Concepts introduced (3) — `concepts.yaml`
- `feedback-loops` — "Feedback loops: a recommender retrained on its own exposures (simulation)".
- `exposure-fairness` — "Exposure fairness across items/authors (Gini of exposure, long-tail share, trade-off
  curves)".
- `filter-bubbles` — "Filter bubbles: narrowing of recommended genre spread vs a reader's history".
All are `kind: technique`, `category: techniques`, and globally unique (0 hits today; re-confirm in Phase A).

### Coverage-map entries
**`unit-13-whole-system-ethics`** (`kind: unit`, `title: "Evaluating the whole system: ethics and beyond-accuracy"`,
`lessons: 3`):
- `introduces: [feedback-loops, exposure-fairness, filter-bubbles]`.
- `requires: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, popularity-ranking, popularity-bias,
  item-item-cf, implicit-feedback, ranking-metrics, beyond-accuracy, score-blending, two-tower, feature-towers,
  item-cold-start]`.
- `practices: [offline-evaluation, top-k-ranking-metrics, popularity-bias, item-item-cf, beyond-accuracy,
  score-blending, item-cold-start]`.

**`checkpoint-02-part-2`** (`kind: checkpoint`, `title: "Checkpoint B — the Part-2 recommender"`, `lessons: 0.5`,
listed after U13):
- `introduces: []`.
- `requires`/`practices` (the Phase F subset, all taught in U1–U13): `[retrieve-then-rank, offline-evaluation,
  top-k-ranking-metrics, beyond-accuracy, score-blending, word-embeddings, document-embeddings, embedding-retrieval,
  two-tower, bpr-loss, neural-training, item-cold-start, hybrid-retrieval, sequential-recommendation,
  item-transitions, feedback-loops, exposure-fairness, filter-bubbles]`.

Whole-book lessons go from 36.5 to 40.

## Phases

### Phase A — registry + syllabus (inline)
- Add the 3 concepts and the 2 coverage entries.
- Add the 2 manifests.
- Add the syllabus rows: the U13 row, and a checkpoint row `| — | checkpoint-02-part-2 | checkpoint | 0.5 | … |`.
- `baseline.yaml`: only the idioms actually called.
- **Test-unseal guard:** extend the `test_unit06` split-guard pattern into the new `test_unit13.py`. Only
  `checkpoint-02-part-2/{checkpoint,solutions}.ipynb` may contain `split="test"`. Its roots are U13, Checkpoint B and
  the U13 milestone.
**Verify:** manifest/prereq/coverage/checkpoint/syllabus checks are green; the lesson total is 40.

### Phase B — `bookrec` ethics helpers (Opus subagent; numpy only, torch-free)
New `bookrec/fairness.py`:
- `exposure_gini(recommendations_by_reader, catalog_ids) -> float`;
- `author_exposure_gini(…, catalog)`;
- `long_tail_share(…, head_ids)`;
- `genre_entropy(items, catalog)` and a per-reader `genre_spread_vs_history`;
- `popularity_penalized(path, penalty, counts)`: a thin re-ranking wrapper path (name `"pop-penalized"`, version
  `"1"`);
- `simulate_feedback_loop(path_factory, rows, *, rounds, k, accept_prob, seed, mitigation=None) -> list[RoundMetrics]`.
  It is pure numpy and seeded. Each round it appends simulated train positives (new rows tagged `split="train"`) and
  refits through `path_factory`. It never touches val/test rows, and val/test stay the evaluation target for the
  accuracy column. The mitigation is an exploration slot (one random warm, unseen item in the top-k) or a
  popularity penalty.

Tests (`tests/test_unit13.py`, ≤ +60 s):
- Gini edge cases (uniform → 0; a single item → (n−1)/n);
- determinism of the simulation;
- val/test rows are never modified;
- the mitigation path really changes exposure;
- gates (a)–(c) on the CI-generated main log (skip if absent);
- the test-unseal guard.

**Report:** the round-by-round table for both loops, with and without mitigation; the Pareto points; per-path
Gini/head-share; the cold-start readout; timings.

### Phase C — lesson.ipynb (Opus subagent; project-first)
**Hook:** "Your recommender scores 0.36 hit@10. Who is it *good for*, which books does it never show, and what happens
when readers start reading what it suggests?" The lesson works through these steps:
1. **Whole-system scoreboard.** Hit@10 *and* coverage / head-share / Gini for the Part-1 blend, the two-tower and
   the U10 hybrid (reusing measured paths; cheap fits only).
2. **Exposure fairness.** Gini by hand, then the reveal; the author-level Gini; the popularity-penalty trade-off
   curve.
3. **Feedback loops.** One round of simulation by hand, then `simulate_feedback_loop`; watch coverage fall and the
   Gini rise; then the mitigation.
4. **Filter bubbles.** Genre spread vs history, and narrowing across rounds.
5. **Offline-metric limits and the cold-start thread.** Offline hit@k is computed on data the logging policy
   exposed, so popularity bias inflates it (one measurement). Cold items: warm-only paths score 0; the feature tower
   is the only learned path that serves them (U9).
6. **Bridge:** Checkpoint B, then U14 (the capstone).
**Verify:** `exec-lessons` clean; `concept-scan` clean.

### Phase D — exercises + solutions (separate fresh Opus subagents)
- At least 6 exercises, and at least 2 `stretch`.
- Drill: compute the Gini by hand and with the helper; author-level exposure; a 3-point penalty curve; run a short
  feedback loop and read it; genre spread; the cold-item readout.
- Stretch: a different mitigation (calibrated genre re-rank); a two-sided (reader-group) fairness slice; a longer
  loop.
- Exercises have no outputs; solutions run clean and contain at least 3 asserts.

### Phase E — milestone (Opus subagent)
`recsys/projects/bookrec/milestones/unit-13-whole-system-ethics.ipynb`:
- the whole-system readout;
- the feedback loop with and without mitigation, asserting gates (a) and (b);
- the trade-off curve, asserting gate (c);
- the cold-start readout.
It is shipped **cleared**, and contains no `split="test"`.

### Phase F — Checkpoint B (statement Opus subagent; solutions in a separate fresh Opus subagent)
`checkpoint-02-part-2/{checkpoint.ipynb, solutions.ipynb, teacher-notes.md, manifest.yaml}`. It uses Checkpoint A's
"freeze, then score" structure. Questions, all on the main log unless marked:
1. **Semantic retrieval:** `SemanticEmbeddingRetrievalPath` on val.
2. **The two-tower:** fit one with BPR (one fit), and score it on val.
3. **Hybrid retrieval:** the U10 BM25 + dense hybrid on val. It reuses the two-tower or semantic vectors, with no
   new fit.
4. **Cold start:** the cold-item readout. If a feature-tower fit is needed, it is the only extra fit, and the probe
   decides.
5. **Sequence (session log, val only):** last-k CF vs item-item, and the transition path vs its shuffled control.
6. **Ethics:** the exposure Gini and long-tail share of the Part-2 blend; one short feedback-loop run with the
   mitigation.
7. **Build the Part-2 blend on val, then FREEZE it.** It is assembled from paths fit above (no new fits). Run a
   leave-one-path-out ablation.
8. **Unseal `test` once:** the frozen blend on the main-log `test`, giving hit@10 + coverage + Gini. Compare honestly
   with val and with Checkpoint A's test score, and explain the differences.

The checkpoint statement has no outputs. The solutions run clean, within budget, with fixed seeds. The teacher notes
include grading guidance (as Checkpoint A's do).

### Phase G — teacher-notes for U13 (inline)
- Goals.
- Pacing.
- Common mistakes:
  - treating one fairness metric as "the" fairness;
  - comparing Gini across different catalog sizes;
  - forgetting that offline metrics inherit the logging policy's bias;
  - a feedback loop that leaks val into the train log;
  - preaching instead of measuring.
- Discussion prompts (trade-offs; who decides the penalty?).
- Differentiation.
- Provenance.

### Phase H — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` must be ALL GREEN, and `pre-merge-guard --pr` must be OK. Confirm:
- the test split is touched only by the Checkpoint B notebooks (guard test);
- determinism;
- the budget delta is reported;
- the lesson total is 40.

## Out of scope
- The capstone (U14).
- The book-wide exec-budget slice (required before U14).
- New retrieval models.
- Generator changes.
- Reranker or SASRec fits in U13 or Checkpoint B.
- A session-log `test` unseal (the sequence question uses val), unless the gate decides otherwise.
- GPU.

## Verification phase declared
Phase H is this plan's named verification phase.

## Plan Review

## Content Review

## Post-Execution Report

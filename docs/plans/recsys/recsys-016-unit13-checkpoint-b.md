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
2. **Exposure fairness.** These are *descriptive exposure-inequality proxies*, not a complete fairness judgment.
   The author Gini is reported alongside each author's **catalog share**, because unequal exposure partly reflects
   unequal numbers of books. Who gets recommended? Measure the distribution of exposure across **books and authors**
   (Gini coefficient of exposure, long-tail share) for each path and for the Part-1 / U10 blends. Then show the
   accuracy ↔ exposure-fairness **trade-off curve** of a popularity-penalty re-rank (a Pareto readout, not a single
   winner).
3. **Filter bubbles.** For each reader, measure the **genre spread** of the recommendations (genre entropy, or
   intra-list diversity from U6) against the reader's own history. Then measure narrowing across the feedback-loop
   rounds.

It also covers **offline-metric limits**: offline scores *reflect the logging policy*. Val positives are 44% head
books, and the head-target hit is at least 5× the tail-target hit for the collaborative paths. It is a descriptive
measurement, not a causal claim about inflation. The **cold-start thread closes here**: a per-path
readout on the cold partitions.
Warm-only **collaborative** paths (popularity, item-item, MF, two-tower) surface 0 zero-train items. The feature
tower is the only *learned/collaborative* path that serves cold items. Lexical and semantic, which are content paths,
surface even more of them.

**Checkpoint B** (`recsys/checkpoints/checkpoint-02-part-2/`, `lessons: 0.5`) is the Part-2 assessment. It is
checkpoint-**strict** (no borrowed tools; it assesses only taught concepts) and is the book's **second authorized
`test` unseal**: freeze on `val`, then score once on `test`. It assesses a **lean subset** of U3–U13 (mostly U7–U13) (see Phase F).
No sequence-path test unseal on the session log is required. A Part-2 sequence question is scored on the session
log's **val** only, unless the plan gate decides otherwise.

## Probe evidence (plan-gate r1, [fable]; main log, committed seed, k = 10, val cohort of 500 readers; load ≈ 14)
| Path | hit@10 | coverage | head-share | item Gini | author Gini | genre H (bits) |
|---|---|---|---|---|---|---|
| popularity | 0.108 | 0.008 | 1.000 | 0.995 | 0.970 | 2.14 |
| lexical | 0.158 | 0.278 | 0.268 | 0.888 | 0.600 | 0.30 |
| semantic | 0.102 | 0.355 | 0.109 | 0.857 | 0.573 | 1.93 |
| item-item | 0.252 | 0.490 | 0.491 | 0.773 | 0.474 | 1.64 |
| MF | 0.276 | 0.075 | 0.994 | 0.972 | 0.843 | 1.38 |
| two-tower | 0.340 | 0.177 | 0.900 | 0.929 | 0.687 | 0.68 |
| feature-tower | 0.298 | 0.307 | 0.638 | 0.877 | 0.609 | 0.35 |
| U10 hybrid | 0.362 | 0.192 | 0.862 | 0.922 | 0.677 | 0.51 |
| U6 blend | 0.306 | 0.333 | 0.793 | 0.908 | 0.694 | 1.39 |

The story: **the most accurate paths are the most concentrated**, and item-item is the least concentrated
collaborative path. The Gini is computed over the **full catalog** (zeros included), so every path shares the same N.

## Feedback-loop simulation — pinned semantics (v2)
`simulate_feedback_loop(path_factory, rows, *, cohort, rounds=6, k=10, accept_prob=0.3, seed, mitigation=None)`.
This is a *stylized exposure-to-consumption loop*: readers take what they are shown with a fixed probability. It is
**not** a realistic preference model, and the lesson says so.
- **Cohort:** the 500-reader val cohort (readers with an unseen val positive, not cold), fixed for all rounds.
- **Each round:**
  1. Fit `path_factory()` on the **augmented train log**: original train rows plus the simulated rows so far.
  2. For each cohort reader, retrieve the top-k, excluding the reader's *augmented* seen set.
  3. With probability `accept_prob`, the reader reads **one** item, chosen **uniformly at random from the top-k**.
     The item must be unseen, and must **not** be in the reader's val/test positives (the **leakage guard**: we
     never let the simulation hand the model a held-out answer).
  4. Append that item as a train row (`label=1`), with a timestamp after the reader's last. There is at most one new
     row per reader per round, and no duplicates.
- **Readouts per round:**
  - coverage, head-share (head frozen at round 0), item Gini and genre entropy of the round's top-k lists;
  - **clean hit@10**: the refit path scored on the **original val** relevance with the **original train seen set**.
    This is not the grown set; otherwise the accuracy readout changes for a bookkeeping reason.
- **Mitigation (primary): an exploration slot.** Slot 10 is replaced by a seeded random unseen warm item. The
  penalty re-rank (λ = 0.3, pool 50) is reported as a second mitigation.
- **Why the guard matters (measured):** without it, clean hit *rises* from 0.252 to 0.27–0.29, because simulated
  readers "accept" their own val books. This is a leak, and it is taught as a common mistake.
- **Measured** (500 readers, p = 0.3, R = 6, 3 seeds, guarded):
  - item-item coverage 0.490 → 0.354–0.358;
  - Gini 0.773 → 0.826–0.832;
  - clean hit 0.252 → 0.090–0.114 (self-training teaches CF the *recommender*, not the readers);
  - genre H 1.64 → a minimum of 1.14–1.22 (rounds 3–4) → partial rebound;
  - popularity loop: Gini ≥ 0.9879 and coverage ≤ 0.020 throughout;
  - exploration slot at R: coverage +0.062 to +0.074 and Gini −0.017 to −0.020;
  - penalty 0.3: Gini −0.035 to −0.040.
- **Time:** about 13–15 s per loop loaded, so 3 loops take about 45 s.

## Gates (v2: numeric, pinned now from the probe; Phase B re-measures on shipped code, and a miss means stop, amend and re-gate, with no re-tuning)
All are measured on the main log, at the committed seed, through the shipped helpers, and asserted in the CI-executed
milestone and/or `test_unit13.py`:
- **(a) The loop concentrates** (item-item, p = 0.3, R = 6, the exact config above):
  - `coverage_R ≤ coverage_0 − 0.08` **and** `gini_R ≥ gini_0 + 0.03`;
  - the popularity loop has `gini ≥ 0.98` and `coverage ≤ 0.03` in every round.
- **(b) The exploration slot partially restores exposure** at round R versus the unmitigated loop:
  `coverage ≥ loop_cov_R + 0.04` **and** `gini ≤ loop_gini_R − 0.01`. (v2.2 loosened this from −0.015 *before*
  implementation: one seed cleared −0.015 by only 0.0017. The measured range is −0.017 to −0.020.) The accuracy cost is **reported,
  not asserted**, as two signed deltas:
  - `cost_0 = clean_hit_0(mitigated) − clean_hit_0(loop)`, measured 0.000 on all 3 guarded seeds;
  - `cost_R = clean_hit_R(mitigated) − clean_hit_R(loop)`.
- **(c) The fairness trade-off curve.** The predeclared grid is λ ∈ {0, 0.1, 0.3, 0.5, 1.0}, pool 50, with
  `score' = minmax(score) − λ · log1p(count)/log1p(max count)`. On item-item **and** on the U6 blend:
  - the Gini is **strictly decreasing** over the grid;
  - hit@10 is **non-increasing**;
  - signed hit deltas are recorded.
  Anchors (± 0.003 hit / ± 0.005 Gini): item-item λ = 0.3 → 0.224 / 0.747; U6 blend λ = 0.3 → 0.290 / 0.858.
  Coverage is **not** gated, because it is non-monotone (item-item peaks at λ = 0.5).
- **(d) Recorded, with light gates:**
  - **Filter bubble:** `min(H_1..H_4) ≤ H_0 − 0.3` bits; report the rebound.
  - **Offline-metric limit:** val positives are 44.1% head items (head = top 10% by train count). Gate:
    `head_target_hit ≥ 5 × tail_target_hit` for item-item, MF, two-tower and the U6 blend (tail hit may be 0,
    e.g. MF; the test tolerates that).
  - **Cold readout:** popularity, item-item, MF and two-tower surface exactly 0 zero-train items; the feature tower
    surfaces > 0.
- **Determinism:** two seeded loop runs are `allclose` on every round column.
- **Leakage test:** the augmented log contains no (reader, item) pair from that reader's val/test positives. A
  **recording `path_factory` mutant** proves that no original val/test row ever reaches `fit` or the acceptance step.

## Budget (v2: binding ceilings, loaded; the reduce-or-stop rule follows recsys-015)
Fit inventory (loaded times: MF ≈ 22 s, two-tower ≈ 26 s, feature tower ≈ 35 s):

| Notebook | Fits | Simulation | Ceiling |
|---|---|---|---|
| U13 lesson | MF, two-tower, feature tower (cold readout) | 3 loops ≈ 45 s | ≤ 3.5 min |
| U13 solutions | two-tower | ≤ 2 loops | ≤ 2.5 min |
| U13 milestone | MF, two-tower, feature tower | 3 loops | ≤ 3.5 min |
| CP-B solutions | two-tower (**no** feature tower) | 2 short loops (R = 3) | ≤ 3.5 min |

- **Total added ≤ 13 min loaded of notebook exec** (the routed-pytest ≤ +60 s is separate). That is about +30% on the ~44 min book. It is recorded, and the book-wide slice
  before U14 owns the overall fix.
- **If a ceiling is exceeded:**
  1. drop the lesson's feature-tower fit (cite the milestone-asserted cold readout);
  2. cut the simulation to 300 readers (re-measure the gates, and re-gate if any changes);
  3. stop and amend.
- **Routed pytest ≤ +60 s:** the gate tests use 1 loop config and the Gini helpers.

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
  item-cold-start, hybrid-retrieval]`.
- `practices: [offline-evaluation, top-k-ranking-metrics, popularity-bias, item-item-cf, beyond-accuracy,
  score-blending, item-cold-start]`.

**`checkpoint-02-part-2`** (`kind: checkpoint`, `title: "Checkpoint B — the Part-2 recommender"`, `lessons: 0.5`,
listed after U13):
- `introduces: []`.
- `requires`/`practices` (the Phase F subset, all taught in U1–U13): `[retrieve-then-rank, offline-evaluation,
  top-k-ranking-metrics, beyond-accuracy, score-blending, word-embeddings, document-embeddings, embedding-retrieval,
  two-tower, bpr-loss, neural-training, item-cold-start, hybrid-retrieval, sequential-recommendation,
  item-transitions, feedback-loops, exposure-fairness, filter-bubbles, bm25, item-item-cf]`.
  v2.1 adds `bm25` (lexical, used in Q3/Q4/Q7) and `item-item-cf` (Q4/Q5/Q7). `filter-bubbles` is assessed by Q6's
  genre-spread readout.

Whole-book lessons go from 36.5 to 40.

## Phases

### Phase A — registry + syllabus (inline)
- Add the 3 concepts and the 2 coverage entries.
- Add the 2 manifests.
- Add the syllabus rows: the U13 row, and a checkpoint row `| — | checkpoint-02-part-2 | checkpoint | 0.5 | … |`.
- `baseline.yaml`: only the idioms actually called.
- **Test-unseal guard (v2), in `test_unit13.py`:**
  - **Globally**, across *all* recsys notebooks (**code cells only**: the U10–U12 milestones mention
    `split="test"` in markdown), the scoped pattern is `test_unit06`'s regex
    `split\s*={1,2}\s*['"]test['"]` (a `split=` keyword or a `split ==` filter). It may match only in
    `checkpoint-01-part-1/{checkpoint,solutions}.ipynb` and `checkpoint-02-part-2/{checkpoint,solutions}.ipynb`.
    U1's temporal-split diagnostic `("min", "test")` is not a split filter or a scoring call, so it stays unaffected
    and is explicitly allowed.
  - **"Once" is proved structurally** (an AST check of `checkpoint-02-part-2/solutions.ipynb`). The keyword literal
    `split="test"` occurs in **exactly one** `ast.Call` across the notebook's code cells. That call is a **top-level
    statement** of its cell: not inside a `for`/`while`/`def`/`lambda`/comprehension, so it executes exactly once
    when the notebook runs top to bottom. Its cell comes **after** the cell carrying the `# FREEZE` marker.
  - Any **indirect** split selection is rejected: a name bound to `"test"`, `"test"` in an f-string, or a `**kwargs`
    split.
  - The statement notebook carries the call only as a markdown or TODO-stub comment, not as executable code.
  - The test also asserts that the CP-A guard in `test_unit06` still passes (so it is not weakened).
**Verify:** manifest/prereq/coverage/checkpoint/syllabus checks are green; the lesson total is 40.

### Phase B — `bookrec` ethics helpers (Opus subagent; numpy only, torch-free)
New `bookrec/fairness.py`:
- `exposure_gini(recommendations_by_reader, catalog_ids) -> float`;
- `author_exposure_gini(…, catalog)`;
- `long_tail_share(…, head_ids)`;
- `genre_entropy(items, catalog)` and a per-reader `genre_spread_vs_history`;
- `popularity_penalized(path, penalty, counts)`: a thin re-ranking wrapper path (name `"pop-penalized"`, version
  `"1"`);
- `simulate_feedback_loop(path_factory, rows, *, cohort, rounds=6, k=10, accept_prob=0.3, seed, mitigation=None) ->
  list[RoundMetrics]` (the pinned semantics above are authoritative).
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
   the U10 hybrid (reusing measured paths; bounded, probe-measured fits per the Budget table).
2. **Exposure fairness.** Gini by hand, then the reveal; the author-level Gini; the popularity-penalty trade-off
   curve.
3. **Feedback loops.** One round of simulation by hand, then `simulate_feedback_loop`; watch coverage fall and the
   Gini rise; then the mitigation.
4. **Filter bubbles.** Genre spread vs history, and narrowing across rounds.
5. **Offline-metric limits and the cold-start thread.** Offline scores reflect the logging policy: val
   positives are 44% head books, and the head-target hit is at least 5× the tail-target hit for the collaborative
   paths (a measured association, not a causal claim). Cold items: warm-only paths score 0; the feature tower
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
0. **Setup:** fit item-item (U4) and lexical/BM25 (U3) on the main log. Both are sub-second; the reason is given in
   the statement, with no new concept.
1. **Semantic retrieval:** `SemanticEmbeddingRetrievalPath` on val.
2. **The two-tower:** fit one with BPR (one fit), and score it on val.
3. **Hybrid retrieval:** the U10 BM25 + dense hybrid on val. It reuses the two-tower or semantic vectors, with no
   new fit.
4. **Cold start** (v2: pinned, **no feature-tower fit**): count the zero-train items each path surfaces, and the
   hit on cold-target val readers. This uses the paths already fit (semantic, lexical, item-item, two-tower), so the
   assessed concept is `item-cold-start` only. The finding: content paths serve cold items, and warm-only
   collaborative paths surface 0.
5. **Sequence (session log, val only):** last-k CF vs item-item, and the transition path vs its shuffled control.
6. **Ethics:**
   - the exposure Gini and long-tail share of the Part-2 blend;
   - a **genre-spread vs history** readout (filter bubbles);
   - two short feedback-loop runs (R = 3), with and without the mitigation (≈ one full loop of time).
7. **Build the Part-2 blend on val, then FREEZE it** (v2: pinned members). The members are an equal-weight
   {item-item, two-tower, semantic, lexical} blend at pool 30, from paths fit above (no new fits); then a
   leave-one-path-out ablation over those 4. **Honesty:** the plan-gate probe measured this exact blend at **hit 0.298 /
   coverage 0.383**. It loses to its own two-tower member (0.340) and to the hybrid (0.362), and dropping either
   content path *raises* the hit (leave-one-out: −item-item 0.246, −two-tower 0.198, −semantic 0.310, −lexical
   0.312). Q7 and Q8 are framed as a **hit ↔ coverage trade**: coverage is 0.383, against 0.177 for the two-tower
   and 0.192 for the hybrid. Students must compare the frozen blend with the best single path, and must not assume
   the blend wins. The hybrid is reported as a single path (it already contains the two-tower; collinear members
   make the leave-one-out readout odd).
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

### Round 2 (plan v2 @ 11eea1c)
- **[self]** APPROVE WITH NITS. I concur with [sol] on the manifest/question mismatch.
- **[sol]** REJECT.
  - B2, B4 and N6 RESOLVED.
  - B1 open (gate (b) hit cost undefined). → v2.1 defines two signed deltas, `cost_0` and `cost_R`, reported and not
    asserted.
  - B3 open, on two counts. → v2.1 fixes both:
    - The global guard would have flagged U1's `("min","test")` diagnostic. → The guard is scoped to the
      `test_unit06` regex (`split=` / `split ==` only), with U1 explicitly allowed.
    - Literal counting does not prove a single runtime call. → An AST structural proof: exactly one `Call` with the
      keyword, at the top level of its cell, after `# FREEZE`; indirect selection rejected.
  - B5 open (Phase C still said "inflates"). → Reworded as a measured association.
  - New BLOCKER: the checkpoint manifest did not match the questions. → v2.1 adds `bm25` and `item-item-cf`, a Q0
    setup that fits the lexical and item-item paths, and Q6 a genre-spread readout for `filter-bubbles`.
  - NITs:
    - `cohort` added to the Phase B signature;
    - "cheap fits only" → "bounded, probe-measured fits";
    - the 13 min total is notebook exec only, with pytest separate.
- **[fable]** APPROVE WITH NITS. The r1 MUST-FIX and N1–N7 are RESOLVED, and every gate passed on 3 seeds in a
  re-probe. Nits, folded as v2.2:
  1. Q7: the measured pinned-blend numbers (0.298 / coverage 0.383, plus leave-one-out), framed as a hit ↔
     coverage trade.
  2. The guard checks code cells only.
  3. Q6 runs two R = 3 loops, which now matches the budget row.
  4. "U3–U13 subset".
  5. The prose numbers are corrected to the guarded probe, and the gate (b) Gini margin is loosened to −0.01
     pre-implementation.
  6. A sentence-break typo.

### Round 1 (plan v1 @ 2774c6c)
- **[self]** APPROVE WITH NITS. The registry closes; the lesson total is 40.
- **[sol]** REJECT.
  - B1: the gates were not pinned. → v2 records the full probe recipe and pins numeric, directional thresholds:
    - one primary concentration metric (coverage plus Gini);
    - a numeric mitigation improvement;
    - a predeclared λ grid with strictly decreasing Gini and non-increasing hit;
    - pool 50 over-retrieval.
  - B2: the feedback-loop semantics were unspecified. → v2 pins:
    - a fixed cohort, uniform-over-top-k acceptance, at most one unseen item per reader per round, and the
      timestamp/duplicate policy;
    - the augmented seen set;
    - a leakage guard excluding val/test positives;
    - a clean-hit readout on the original context;
    - a recording-path mutant test;
    - a "stylized loop" disclaimer.
  - B3: checkpoint strictness was conditional, and "once" was unprovable. → v2 pins Q4 with no feature-tower fit
    (`item-cold-start` only) and adds a global test-literal allowlist (CP-A, CP-B), exactly one executable test call
    after `# FREEZE`, and indirect selection rejected.
  - B4: there was no budget acceptance criterion. → v2 adds a fit inventory, per-notebook ceilings, a total
    ceiling ≤ 13 min, and the reduce-or-stop order.
  - B5: the causal offline-bias claim. → Softened to "scores reflect the logging policy", with a head/tail
    measurement gate (≥ 5×).
  - N6: fairness proxies. → Labelled descriptive; author catalog share reported alongside.
- **[fable]** APPROVE WITH NITS (with a probe).
  - MUST-FIX: the loop leaked val into the train log, so hit rose. → The leakage guard and the clean-hit definition
    are pinned, with a test.
  - N1: add `hybrid-retrieval` to the requires list. → done.
  - N2: cold-start wording. → "learned/collaborative" kept; content paths surface more cold items.
  - N3: coverage is non-monotone in λ. → Not gated.
  - N4: genre narrowing is transient. → The minimum-over-rounds is gated, and the rebound taught.
  - N5: the Part-2 blend may lose to the hybrid. → Blend members pinned, plus an honesty clause.
  - N6: loaded fit times. → Used in the budget.
  - N7: the Gini is over the full catalog. → Stated.

## Content Review

## Post-Execution Report

# Plan recsys-015 — Unit 12: Sequence-aware retrieval (what you read *last* matters)

**Design:** `docs/designs/011-recsys-book.md`:
- §8 row 12: "Sequence-aware (tiny capped SASRec-style self-attention over reading history), scored on the
  **session log** (§6) → Path: session/sequence".
- §6 "Session log for U12" (amended v5): the separate seeded `sessions.csv.gz` + `series.csv.gz`; SASRec is a
  measured **near-tie**, not the winner; the cheap order-aware paths carry the lift.
- §7: torch, CPU-deterministic, tolerance/rank-based (§184) determinism; the SASRec ceiling is 1 block, dim ≤ 32,
  seq-len ≤ 50.
- §9: 120 s/cell cap; exec runs lesson + solutions + milestone; a ≤ ~15 CI-minute whole-book exec target.

**Book:** `recsys` (Book 3). **Autopilot** per AGENTS.md; the user's standing goal is "complete the recsys book with
autopilot". This is the sixth Part-2 unit. It is built on the **recsys-014 session log** (PR #148), whose measured
facts and binding constraints this plan inherits verbatim (recsys-014 post-execution report, "Binding constraints
handed to recsys-015").

## Scope
**Unit 12** (`recsys/units/unit-12-sequence-aware/`). It teaches three things:
1. **Sequential recommendation.** A reader's history is a *sequence*, not a bag. The next read depends on the
   *recent* reads (series next-volumes, an author streak, a genre mood). Last-k recency: query with the last k
   books instead of all of them.
2. **Item transitions.** A first-order "what do people read *right after* X" model, learned from consecutive train
   pairs: the Markov-chain view. An order-shuffled control *proves* that order, not the item set, carries the lift.
3. **Self-attention over history.** A tiny SASRec-style causal self-attention model in PyTorch. It learns order
   (it beats its own shuffled-history copy by +0.040, 3.8 paired SE). But at the unit's fast recipe it **trails**
   plain item-item CF by about 0.06 on the committed seed (−0.057 ± 0.012). The recsys-014 V1 held-out near-tie is
   cited as *that* recipe's result, not this unit's. This is the honest readout, like U11's.

It ships three `bookrec` paths, a loader-backed ordered-history contract, and a Unit-12 milestone. Everything is
scored with the unchanged `run_validation_scoreboard` **on `sessions.csv.gz`**. Every U12 number is labelled "on the
session log" and is not comparable to the main-log numbers of U2–U11 (design §6).

## Inherited facts (recsys-014; committed seed 20260930, val, k = 10, cohort = val − train non-empty)
| Reference (numpy harness) | hit@10 |
|---|---|
| popularity | 0.113 |
| bag item-item CF (all train) | 0.480 |
| last-3 CF | **0.550** (+0.070) |
| last-5 transition, ordered / order-shuffled | **0.510 / 0.343** (1.48×) |
| next-in-series events (n = 654): last-5 transition / bag CF | 0.500 / 0.301 (1.66×) |
| SASRec R3-V1 (≈ 5 min/fit), ordered / shuffled | 0.434 / 0.380; vs bag −0.046 (**just outside the 0.04 near-tie margin on this seed**; within it on held-out seeds 2–4) |

**Binding constraints (verbatim from recsys-014):**
1. "Near-tie" is the held-out claim. On the committed seed students run, SASRec is −0.046 behind bag CF, and U12
   must report that number as it is. (If U12 uses a faster recipe, it reports *that recipe's* measured gap. It
   never borrows the held-out claim for a recipe that was not gated on held-out seeds.)
2. SASRec takes about 5 min per fit at V1, so U12's notebooks need cached or seeded short fits within budget.
3. The lift comes from **last-k CF** and the **transition** path; the order evidence is the shuffled-control drop.
4. `series.csv.gz` is for diagnostics only, not a model input.
5. Ordered history is loaded through `bookrec.load_train_sequences`; scoring uses `run_validation_scoreboard` on
   `sessions.csv.gz`.

## Frozen SASRec recipe and budget (v2: pinned from the plan-gate probe; binding)
**Recipe D, frozen before implementation:**
- architecture (V1): 1 block, 1 head, dim 32, max_len 50, learned positions, causal mask, tied output embedding,
  per-position next-item full-softmax CE;
- training: **30 epochs, batch 128, lr 2e-3**, dropout 0.2, weight decay 0, init std 0.02, Adam, seed 0, the full
  reader set;
- determinism: single-thread and deterministic.

Probe measurements at the committed seed, through the real `run_validation_scoreboard`, under machine load 4–5:

| Recipe | Ordered | Shuffled | Ordered − shuffled (paired SE) | Gap to bag | Fit time |
|---|---|---|---|---|---|
| D (frozen) | 0.4228 | 0.3827 | +0.040 (0.0105) | −0.057 (0.012) | 42–48 s |
| B: 20 / 256 / 3e-3 | — | — | +0.017 (fails G4a) | — | — |
| A: 30 / 256 / 3e-3 | — | — | +0.031 | — | — |
| C: 40 / 256 / 3e-3 | — | — | +0.035 | — | — |

An unloaded machine should be faster, but that is an estimate, not a measurement. Two seeded fits gave bit-exact weights and identical top-10 lists
for all 1,419 readers.

**No re-tuning.** If the shipped code at recipe D misses gate (c), Phase B **stops**, the plan is amended, and the
plan-review gate re-runs. No other recipe may be substituted silently.

**Where the gate (c) number is enforced: the milestone notebook (CI-executed), at the shipped recipe.** Two full
recipe-D fits (about 85–95 s) cannot fit the routed pytest budget. So the milestone notebook *asserts* gate (c) on
the frozen recipe at the committed seed. CI runs that notebook through `exec-solutions`, so the shipped recipe is
gated in CI. `test_unit12.py` adds reduced-config **contract** tests (determinism, round-trip, shuffle semantics,
numpy/torch fidelity). These are additional checks; they never substitute for the gate.

**Exec budget:**
- **Fits per notebook:** the lesson does 2 SASRec fits (ordered + shuffled); the milestone does 2 (the gate); the
  solutions do **1** (ordered only, reusing the lesson-measured shuffled number as a stated constant is NOT allowed —
  any shuffled comparison in the solutions uses the numpy transition control instead). That is 5 fits ≈ 3.5–4 min.
- **Cell layout:** each fit in its own cell, ≤ 90 s.
- **Per-notebook time:** about 2.5 min for the lesson and the milestone, and about 1.5 min for the solutions.
- **Measurement:** Phase B measures the **current pre-U12 whole-book exec time** (`exec-lessons` + `exec-solutions`
  for recsys) and reports U12's delta against the ≤ ~15 CI-minute target. If the total exceeds the target, the
  reduction order is (1) drop the lesson's shuffled SASRec fit and use the numpy transition control there. This
  fallback **amends** the lesson contract (Phase C step 4) and the fit inventory (to 4 fits), and is recorded in the
  post-execution report. The milestone keeps both fits, so gate (c) is unaffected. Then (2) stop and amend.
- **Routed pytest delta:** ≤ +60 s (numpy gates plus reduced-config SASRec contracts).

## Gate (measured by the probe; the thresholds are re-pinned in Phase B from the shipped code, with headroom)
On `sessions.csv.gz`, val, k = 10, committed seed, through `run_validation_scoreboard`:
- **(a) recency lift:** `last_k_cf.hit ≥ item_item.hit + 0.03`. The harness measured +0.070; the bookrec
  `ItemItemRetrievalPath` baseline is re-measured.
- **(b) order evidence:** `transition.hit ≥ 1.3 × transition_shuffled.hit` and `≥ +0.10`.
- **(c) SASRec learns order (milestone-asserted at frozen recipe D):** `sasrec.hit − sasrec_shuffled.hit ≥ 0.02`
  **and** `≥ 2 × paired SE`. The paired SE is over per-reader hits (probe: +0.040, SE 0.0105). If this fails, stop,
  amend and re-gate (no re-tuning).
- **(d) recorded, not gated:**
  - SASRec vs item-item CF (the honest gap; probe −0.057 ± 0.012; **not** a near-tie at this recipe);
  - next-item hit@10;
  - coverage per path;
  - the next-in-series diagnostic (from `series.csv.gz`, diagnostics only);
  - fit times.

Probe values for gates (a) and (b), on the real scoreboard:
- (a) distinct last-3 − item-item = **+0.071** (SE 0.0136; hit 0.5511);
- (b) transition last-5 0.5159 vs shuffled 0.3326, which is **1.55×, +0.183**.
Item-item on the session rows reproduces the harness bag number exactly (0.4799).

Phase B pins (a) at ≥ +0.03, and (b) at ≥ 1.3× and ≥ +0.10, re-measured on the shipped code.

Determinism: two seeded SASRec fits give an identical top-k ranking and `allclose` weights (§184); never exact-float
or array_equal on ids. Numpy paths are deterministic by construction.

## Audience and retained laws
Advanced baseline (design 011). Retained in full:
- project-first;
- taught-before-assessed (the three new concepts are introduced and practised here);
- student notebooks carry NO solutions and NO outputs;
- solutions and the milestone run clean (fixed seeds, deterministic torch);
- teacher-notes;
- from-scratch → reveal (numpy last-k / transition built by hand → the `bookrec` paths; a hand-written causal mask
  and attention → the `SasrecRetrievalPath`);
- a stretch exercise.
It runs CPU-deterministic, routed through `--group recsys`, within budget.

## Concepts introduced (3) — `concepts.yaml`
- `sequential-recommendation` — "Sequential (next-item) recommendation from an ordered history; recency / last-k".
  `kind: technique`, `category: techniques`.
- `item-transitions` — "First-order item transition (Markov) model learned from consecutive reads".
  `kind: technique`, `category: techniques`.
- `self-attention` — "Causal self-attention over reading history (SASRec-style)". `kind: technique`,
  `category: techniques`.
All three must be globally unique across `*/curriculum/concepts.yaml`; re-confirm in Phase A and rename if needed.

### Coverage-map entry
`unit-12-sequence-aware`, `kind: unit`, `title: "Sequence-aware retrieval"`, `lessons: 3`,
`introduces: [sequential-recommendation, item-transitions, self-attention]`.

`requires: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, beyond-accuracy, implicit-feedback,
item-item-cf, knn-similarity, embedding-retrieval, two-tower, neural-training]`.

`practices: [retrieve-then-rank, offline-evaluation, top-k-ranking-metrics, beyond-accuracy, implicit-feedback,
item-item-cf, embedding-retrieval, neural-training]`.

Why each required concept is needed:
- `item-item-cf` / `knn-similarity` (U4): the bag baseline and the last-k query reuse them.
- `embedding-retrieval` (U7): SASRec scores items against learned item embeddings.
- `two-tower` / `neural-training` (U8): the torch training idioms and the dot-product scoring head.
- `implicit-feedback` (U4): positives-only sequences.
- `beyond-accuracy` (U6): the coverage readout.

`practices ∩ introduces = ∅`. There is no `project` entry. Whole-book lessons go from 33.5 to 36.5, within
[30, 60].

## Phases

### Phase A — registry + syllabus (inline)
- `concepts.yaml`: add the 3 ids.
- `coverage-map.yaml`: add the Unit-12 entry.
- `baseline.yaml`: declare **only** the `x.name(...)` idioms the authored cells actually call. These are the new
  bookrec paths and loader, plus any new torch idioms (e.g. `MultiheadAttention`/`triu`/`masked_fill`/`softmax`/
  `LayerNorm`/`Dropout` if used). Trim unused names at the Phase G concept-scan.
- `recsys/units/unit-12-sequence-aware/manifest.yaml`.
- `syllabus.md`: add the row `| 12 | unit-12-sequence-aware | unit | 3 | <hook> |`.
**Verify:** manifest/prereq/coverage/syllabus are green; the lesson budget is 36.5 ∈ [30, 60].

### Phase B — `bookrec` sequence paths (Opus subagent)
Add `bookrec/sequence.py`, with numpy paths that are torch-free.

**Ordered-history contract (v2; it resolves the loader hand-off).**
- `bookrec/sessions.py` gains one shared helper, `ordered_train_histories(rows) -> dict[int, list[int]]`.
  `load_train_sequences(path)` is refactored to call it, so there is **one** ordering implementation: train
  positives only, ordered by `(timestamp, row order)`, ties broken by row order.
- Every sequence path's `fit(rows, catalog=None)` calls that helper. **Row contract:** rows must carry `timestamp`,
  in addition to the U4 keys `reader_id, item_id, split, label`; `fit` raises if it is missing. A test asserts that
  `fit(rows)`'s stored histories equal `load_train_sequences(path)` exactly.
- The stored histories (after any `shuffle_seed` permutation) are **persisted in `artifact()` and restored by
  `load()`**, so a shuffled control's *query* history survives a round-trip.
- `retrieve(query=reader_id, context, k)` uses the stored history and **never** `context["seen"]` for the query
  (`seen` is only the exclusion set). It returns `[]` for an unknown reader, and only positive-score items (the U4
  coverage-ceiling convention).

**Evaluation helpers (v2; they add no change to `run_validation_scoreboard`).**
- `bookrec.scoreboard.reader_hits(path, interactions_path, *, catalog_ids, k, split="val") -> dict[int, float]`
  returns per-reader hit@k on exactly the scoreboard cohort. A test asserts its mean equals
  `run_validation_scoreboard(...).hit_rate_at_k`. It powers the paired SE.
- `bookrec.sessions.first_unseen_val(path) -> dict[int, int]` returns each reader's time-ordered first val positive
  that is not in train, for next-item hit@10.
- Coverage uses the existing `run_blended_scoreboard({name: path}, ..., pool=k)`; the probe verified that a
  single-path blend reproduces hit@10 to 1e-9.
- All three names are declared in `baseline.yaml` if notebooks call them.
- **`LastKItemItemPath(k_last=3)`** (name `"last-k-item-item"`, version `"1"`, artifact `last-k-item-item-v1`):
  - the item-item cosine (reusing U4's construction), queried with the reader's **last `k_last` distinct** train
    positives (the most-recent occurrence of each item; 28% of train positives are re-reads);
  - `k_last=None` means all distinct items, and its top-k must **equal `ItemItemRetrievalPath`'s** (test);
  - probe: distinct last-5 0.5715 > last-3 0.5511. The default stays 3 as the lesson's starting point, and the
    exercise sweep reveals 5.
- **`TransitionRetrievalPath(k_last=5)`** (name `"transition"`, version `"1"`, artifact `transition-v1`): first-order transition counts `T[a, b]` over
  consecutive train positives; the score is the sum of the `T` rows over the last `k_last` items. It takes a
  `shuffle_seed: int | None` knob that permutes each reader's sequence before learning **and** querying. That is the
  order-shuffled control, exposed so the lesson can run the control with the same path.
- **`SasrecRetrievalPath`** (name `"sasrec"`, version `"1"`, artifact `sasrec-v1`; torch imported **lazily in `fit`
  only**; `retrieve`/`artifact`/`load` run torch-free on numpy weights):
  - architecture: 1 block, 1 head, dim 32, max_len 50, learned positions, causal mask, tied output embedding,
    per-position next-item full-softmax cross-entropy, init std 0.02, Adam;
  - recipe: frozen recipe D as the defaults, plus the same `shuffle_seed` control;
  - determinism: `torch.manual_seed` + `use_deterministic_algorithms(True)` + single thread, all saved and restored
    around `fit` (mirror `two_tower.py`);
  - `retrieve` runs a numpy forward pass of the last ≤ 50 items and scores every item by its dot product with the
    final hidden state.
- Export all three from `bookrec/__init__.py` with no eager torch. **Extend** the import-blocked subprocess test in
  `tests/test_unit07.py` to cover `sequence`.
- Tests, in the new `tests/test_unit12.py` (lean; budget ≤ +60 s):
  - gates (a)–(b) on the CI-generated `sessions.csv.gz` (skip if absent, like the data tests). Gate (c) is asserted
    in the milestone (see "Frozen SASRec recipe");
  - **shuffle and leakage mutants** (mutants 1–3 run against `LastKItemItemPath(k_last=3)` and
    `TransitionRetrievalPath` fixtures, never `k_last=None`, where mutant 3 is undetectable by design) (named negative tests, each built as a small monkeypatched or subclassed
    mutant on a hand-made sequence fixture where order is decisive; each must be *detected*):
    1. only learning shuffled, querying ordered;
    2. only querying shuffled, learning ordered;
    3. the query built from unordered `context["seen"]` instead of the stored history;
    4. a val/test event injected into the rows changes **neither** learned statistics **nor** stored query
       histories (the shipped path passes; a mutant that reads all splits is caught);
  - numpy/torch fidelity: right after `fit` on a reduced config, the numpy-forward top-k equals the torch-forward
    top-k for sampled readers (rank-based, §184);
  - `fit(rows)` history == `load_train_sequences(path)`; `reader_hits` mean == scoreboard hit;
    `LastKItemItemPath(k_last=None)` == `ItemItemRetrievalPath`;
  - determinism (reduced config: identical top-k + allclose);
  - empty/unknown-reader contract;
  - `fit→artifact→load` identical and torch-free;
  - val/test rows cannot change any fitted artifact (train-only);
  - the shuffle control really permutes, and is seed-deterministic;
  - registration names.
**Report:** every path's hit@10, next-item hit@10 and coverage on the session log (incl. the U4
`ItemItemRetrievalPath` and popularity baselines); the shuffled controls; SASRec's fast-recipe gap to bag; per-fit
times; and the per-notebook budget plan.

### Phase C — lesson.ipynb (Opus subagent; project-first)
**Hook:** "You just finished volume 2 of a series. Should the recommender care that you read it *last*? Our CF path
treats your history as a bag." The lesson works through these steps:
1. **New data.** Load the session log (`generated_dir()/"sessions.csv.gz"`) and say plainly that it has a different
   reader population and that numbers are not comparable to earlier units. Show one reader's ordered history with
   the series volumes visible (`series.csv.gz`, diagnostics only).
2. **The bag baseline.** U4 item-item CF on the session log, then recency: query with the last 3 books by hand
   (numpy) → the `LastKItemItemPath` reveal → +lift.
3. **Transitions.** Count consecutive pairs by hand → the `TransitionRetrievalPath` reveal. Then **the control**:
   shuffle each history and refit. The lift collapses, which proves *order* carries it.
4. **Self-attention.** Build a causal mask and one attention step by hand on a toy sequence (numpy) → the
   `SasrecRetrievalPath` reveal. Train it (the fast recipe) and its shuffled copy: it *learns order* (ordered >
   shuffled).
5. **The honest readout.** SASRec does not beat the simple paths here. At this recipe it **trails** item-item CF by
   its measured gap (about −0.06 on the committed seed); the recsys-014 near-tie belongs to its longer V1 recipe
   and its held-out seeds, so cite it only that way. Last-k CF and transition are the winners on this data. Explain why: the order effects are
   short-range and item-to-item, so a counting model captures them, while a tiny attention model at our size budget
   cannot use its extra flexibility.
**Bridge:** U13 evaluates the whole system (beyond accuracy, fairness, feedback loops) and Checkpoint B; U14 is the
capstone.
ASCII only. Score with `run_validation_scoreboard(path, sessions_path, ...)`. Respect the SASRec fit budget. A
non-empty markdown first cell.
**Verify:** `exec-lessons` clean and within budget; `concept-scan` clean.

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents)
- At least 6 `## Exercise N`, and at least 2 tagged `stretch`.
- Exercises have NO solutions or outputs. Solutions mirror every exercise, run clean, and include at least 3
  non-vacuous asserts.
- Drill:
  - a last-k sweep (k = 1, 3, 5, all) on the session log;
  - build a transition table by hand and check it against the path;
  - the shuffled control;
  - next-item vs any-item hit;
  - read SASRec ordered vs item-item from the solution's own single ordered fit (the ordered-vs-shuffled SASRec
    comparison is interpretive: a markdown answer that reads the lesson's table, with no numeric assert);
  - coverage per path.
- Stretch ideas: a second-order transition or a decayed-recency CF; a next-in-series diagnostic (series used only as
  an evaluation lens); a blend of last-k CF and transition.
- The solutions use their own **single ordered** fit (see Exec budget) or a reduced config; there is no other full
  fit.
**Verify:** hygiene/structure/cell-lint/noexec; `exec-solutions` clean (within budget); `concept-scan` clean.

### Phase E — milestone notebook (Opus subagent)
`recsys/projects/bookrec/milestones/unit-12-sequence-aware.ipynb`, a fixed-seed demo:
- fit and register the three sequence paths;
- the session-log val scoreboard vs item-item CF and popularity (hit@10 + coverage);
- the shuffled controls;
- one reader whose next series volume the transition path surfaces and the bag path misses.
It passes `milestone-check` + `exec-solutions` + `concept-scan`. It is shipped **cleared**, never with stored
outputs. There is no `split="test"`.

### Phase F — teacher-notes.md (inline)
- `## Goals`.
- `## Pacing` (2–3 sittings; hook first).
- `## Common mistakes`:
  - comparing session-log numbers to main-log numbers;
  - letting val/test rows into the transition counts (leakage);
  - claiming SASRec "wins" or "ties" (at this recipe it trails item-item CF by about 0.06; give the measured gap);
  - forgetting that the shuffled control must permute both the learning and the query sequences;
  - using the series table as a model feature (it is a diagnostic);
  - non-determinism.
- `## Discussion prompts`:
  - when would attention beat counting (longer-range patterns, more data, a bigger model)?
  - why is order evidence a *control*, not a raw number?
  - which real-world sequences have order effects?
- `## Differentiation`.

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` must be ALL GREEN, covering Units 1–12, Checkpoint A and the U12
milestone. `bash scripts/pre-merge-guard.sh --pr` must be OK. Confirm:
- CPU-determinism;
- no torch/faiss on the group-free path;
- lesson budget 36.5;
- the routed-suite delta is ≤ +60 s;
- the U12 exec time is reported against the whole-book exec target.

## Out of scope
- No change to the session-log generator or the main log; no new data.
- No ethics deepening or Checkpoint B (U13), and no capstone (U14).
- No sequence features in the U11 reranker.
- No GPU.
- SASRec beyond the §7 ceiling.

## Verification phase declared
Phase G is this plan's named verification phase.

## Plan Review

### Round 1 (plan v1 @ 05d700f)
- **[self]** APPROVE WITH NITS. The registry closes over U1, U4, U6, U7 and U8; budget 36.5.
- **[sol]** REJECT.
  - B1: gate (c) was a loophole (a post-hoc recipe, a reframe escape, a reduced-config substitute). → v2 freezes
    recipe D before implementation; (c) = ≥ 0.02 and ≥ 2 paired SE, asserted in the CI-executed milestone at the
    shipped recipe; failure means stop, amend and re-gate.
  - B2: the budget was not concrete. → v2 pins the recipe, fit time, cell layout, fits per notebook (2/2/1),
    per-notebook totals, a measured pre-U12 exec baseline plus the delta, and a reduction order.
  - B3: the ordered-history hand-off conflicted with the loader. → one shared `ordered_train_histories` helper (the
    loader refactored onto it); histories persisted in the artifact; a `fit == load_train_sequences` test;
    `first_unseen_val` for next-item hit.
  - B4: the shuffle and leakage tests lacked teeth. → four named mutant tests.
  - N5: artifact ids. → `{name}-v1` pinned for all three paths.
- **[fable]** APPROVE WITH NITS (with a probe).
  - N1: the honesty wording ("near-ties") must go, because the fast recipe trails by −0.057. → Scope 3, lesson
    step 5 and the teacher notes are reworded.
  - N2: gate (c) needs ≥ 2 SE and recipe D. → done.
  - N3: last-k must use distinct-most-recent items, and `k=None` must equal U4. → done.
  - N4: per-reader hits, next-item and coverage APIs. → `reader_hits`, `first_unseen_val`, and
    `run_blended_scoreboard` for coverage.
  - N5: the full (c) gate does not fit the pytest budget. → milestone-asserted.
  - N6: a numpy/torch fidelity test. → added.
  - N7: the row contract plus a shared ordering helper. → added.
  - The probe tables are folded into the "Frozen SASRec recipe" section and the gates.

### Round 2 (plan v2 @ f2036f9) — CONSENSUS
- **[self]** APPROVE.
- **[sol]** APPROVE WITH NITS.
  - B1–B4 and N5 RESOLVED. It verified that `exec-solutions` executes milestones in CI, so gate (c) is enforced at
    the shipped recipe.
  - NIT: the budget fallback conflicted with the lesson contract. → The fallback now explicitly amends the lesson
    contract and the fit inventory, and the milestone keeps both fits.
- **[fable]** APPROVE WITH NITS.
  - N1–N7 RESOLVED; the probe numbers match.
  - NIT A: the gate (b) floor was inconsistent. → Unified at +0.10.
  - NIT B: the unloaded-time figure was unsupported. → Now labelled an estimate.
  - NIT C: the Phase D SASRec drill conflicted with the budget. → It is now interpretive, with the solution's own
    single fit.
  - NIT D: (a) had a stale figure. → Distinct +0.071.
  - NIT E: mutant 3 is vacuous for `k_last=None`. → Mutants run on `k_last=3` and the transition fixtures.
**Gate result:** all three APPROVE / APPROVE WITH NITS, with no open blockers. Implementation may begin.

## Content Review

## Post-Execution Report

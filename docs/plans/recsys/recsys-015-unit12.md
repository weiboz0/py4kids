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
   (it beats its own shuffled-history copy) but, at the book's model ceiling, it only **near-ties** plain item-item
   CF. This is the honest readout, like U11's.

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

## Budget (binding; the probe measures it)
- The recsys routed pytest suite already takes **14 m 18 s** (recsys-014 Phase G). U12's new tests must be lean:
  **≤ +60 s routed-suite delta**. Any SASRec test uses a small config, or a deterministic contract check, not a
  full V1 fit.
- **Notebook SASRec recipe (the plan-gate probe picks it):** the shipped `SasrecRetrievalPath` defaults to a
  **fast recipe** whose single fit is **≤ 90 s** standalone, under the 120 s/cell cap. It stays within the §7
  ceiling (1 block, dim ≤ 32, seq-len ≤ 50). It achieves this with fewer epochs, a larger batch and a higher lr, or
  a reader subsample — whatever the probe shows is cheapest at an acceptable cost.
  - Each notebook (lesson, solutions, milestone) fits SASRec **at most twice** (ordered + shuffled), each in its
    own cell. Exercises add no third fit; reuse the fitted path.
  - Phase B reports the fast recipe's own committed-seed numbers: ordered, shuffled, bag, and the gap to bag. Those
    measured numbers are what the unit cites.
- Numpy paths (last-k CF, transition) fit in < 5 s.
- Phase B reports the per-notebook total exec time, and the aggregate added to the whole-book exec budget.

## Gate (measured by the probe; the thresholds are re-pinned in Phase B from the shipped code, with headroom)
On `sessions.csv.gz`, val, k = 10, committed seed, through `run_validation_scoreboard`:
- **(a) recency lift:** `last_k_cf.hit ≥ item_item.hit + 0.03`. The harness measured +0.070; the bookrec
  `ItemItemRetrievalPath` baseline is re-measured.
- **(b) order evidence:** `transition.hit ≥ 1.3 × transition_shuffled.hit` and `≥ +0.08`.
- **(c) SASRec learns order:** `sasrec.hit − sasrec_shuffled.hit ≥ +0.02` at the shipped fast recipe. If the fast
  recipe cannot clear this, the plan gate decides between a longer recipe or cache, and a reframe.
- **(d) recorded, not gated:** SASRec vs item-item CF (the honest gap); the next-item hit@10; coverage per path; the
  next-in-series diagnostic (from `series.csv.gz`, diagnostics only); and the fit times.

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
Add `bookrec/sequence.py`, with numpy paths that are torch-free. All paths `fit(interactions_rows, catalog=None)` read
**train positives only**, ordered by `(timestamp, row order)`, the same key as `load_train_sequences`. They store
each reader's ordered train history. `retrieve(query=reader_id, context, k)` uses that stored history, excludes
`context["seen"]`, returns `[]` for an unknown reader, and returns only positive-score items (the U4 coverage-ceiling
convention).
- **`LastKItemItemPath(k_last=3)`** (name `"last-k-item-item"`): the item-item cosine (reusing U4's construction),
  queried with the reader's last `k_last` train positives.
- **`TransitionRetrievalPath(k_last=5)`** (name `"transition"`): first-order transition counts `T[a, b]` over
  consecutive train positives; the score is the sum of the `T` rows over the last `k_last` items. It takes a
  `shuffle_seed: int | None` knob that permutes each reader's sequence before learning **and** querying. That is the
  order-shuffled control, exposed so the lesson can run the control with the same path.
- **`SasrecRetrievalPath`** (name `"sasrec"`, torch imported **lazily in `fit` only**; `retrieve`/`artifact`/`load`
  run torch-free on numpy weights):
  - architecture: 1 block, 1 head, dim 32, max_len 50, learned positions, causal mask, tied output embedding,
    per-position next-item full-softmax cross-entropy, init std 0.02, Adam;
  - recipe: the fast default chosen by the plan-gate probe, plus the same `shuffle_seed` control;
  - determinism: `torch.manual_seed` + `use_deterministic_algorithms(True)` + single thread, all saved and restored
    around `fit` (mirror `two_tower.py`);
  - `retrieve` runs a numpy forward pass of the last ≤ 50 items and scores every item by its dot product with the
    final hidden state.
- Export all three from `bookrec/__init__.py` with no eager torch. **Extend** the import-blocked subprocess test in
  `tests/test_unit07.py` to cover `sequence`.
- Tests, in the new `tests/test_unit12.py` (lean; budget ≤ +60 s):
  - gate (a)–(b) on the CI-generated `sessions.csv.gz` (skip if absent, like the data tests);
  - gate (c) on the shipped recipe, *if* it fits the budget; otherwise on a reduced config documented as a
    contract test, and the full number is measured in Phase B and asserted in the milestone;
  - determinism;
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
5. **The honest readout.** SASRec does not beat the simple paths here. Give its measured gap to item-item CF at
   this recipe, and say that last-k CF / transition are the winners on this data. Explain why: the order effects are
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
  - read SASRec ordered vs shuffled vs item-item;
  - coverage per path.
- Stretch ideas: a second-order transition or a decayed-recency CF; a next-in-series diagnostic (series used only as
  an evaluation lens); a blend of last-k CF and transition.
- Exercises **reuse** a fitted SASRec, or use a reduced config; there is no extra full fit (budget).
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
  - claiming SASRec "wins" (it does not here; give the measured gap);
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

## Content Review

## Post-Execution Report

# Plan recsys-002 — Unit 1: The recommendation problem, the catalog, and the evaluation scoreboard

**Design:** `docs/designs/011-recsys-book.md` (§2, §5, §8 Unit 1). **Book:** `recsys` (Book 3). **Autopilot** per
AGENTS.md. Ships the **first student unit** of Part 1 ("Foundational Recommenders") on top of the recsys-001
foundation substrate (the `bookrec` package + the seeded synthetic generators).

## Scope
**Unit 1 only** (`recsys/units/unit-01-...`). Unit 1 establishes the shared frame the whole book builds on:
the recommendation problem, the real-shaped (synthetic) **catalog**, the **retrieve-then-rank** architecture and the
`RetrievalPath` contract, **search/filter** over the catalog, and the **evaluation scoreboard** (a frozen holdout +
hit-rate@k / recall@k). It does NOT ship a learned/scored retrieval path — the first one (**popularity**) is Unit 2.

## Buildout stays (important correction)
recsys-001 said "recsys-002 removes `buildout`." That assumed recsys-002 landed the first *several* units. With
Unit-1-only scope, the whole-book `lessons` total is ~3 — far below the `lesson_budget` lower bound (30), which
`buildout` waives (`curriculum.py:345`). So **recsys-002 KEEPS `buildout: true`.** Buildout is removed by the later
Part-1 plan whose added unit(s) first bring the whole-book `lessons` total to ≥ 30 (and satisfy full
introduction/coverage) — not this plan. recsys-001's note is superseded accordingly.

## Audience & conventions (retained laws — design 011 §2)
Advanced audience (calc/linalg/prob-stats + numerical-Python), assumed baseline in `baseline.yaml`. Every retained
law applies: **project-first** (the lesson OPENS with the "build a book recommender" hook, not concept drill);
**taught-before-assessed** for what Unit 1 teaches; student notebooks carry **no solutions and no executed outputs**;
`solutions.ipynb` runs top-to-bottom clean with fixed seeds; **≥1 `stretch`** exercise; a `teacher-notes.md` with a
pacing plan. Dual **concept∥project tracks** and **from-scratch→reveal-the-library** (Unit 1: derive hit-rate@k /
recall@k by hand in NumPy, then reveal `bookrec.evaluate`). Unit 1 is **CPU-light** (pandas/NumPy + `bookrec`; no
torch/faiss), but its notebooks still run under the `recsys` dependency group via the existing `dependency_group`
routing (they import numpy/pandas/bookrec).

## Concepts introduced (refine at gate)
Added to `recsys/curriculum/concepts.yaml`; Unit 1 is their `introduces` home in `coverage-map.yaml` + the manifest.
`retrieve-then-rank` already exists (seed) and is **introduced here** (moves from declared-only to introduced).
Proposed Unit-1 concept set:
- `retrieve-then-rank` — the candidate-generation → blend → rank architecture (seed concept; introduced here).
- `catalog-representation` — books as items with attributes (title/authors/subjects/year); loading the slice.
- `attribute-search` — search/filter the catalog by text/attributes (the baseline "find books" operation; the
  first `RetrievalPath`-shaped operation, scored trivially).
- `offline-evaluation` — the frozen train/holdout split and why offline evaluation answers "did it help?".
- `hit-rate-at-k` — the hit-rate@k (and recall@k) ranking metric.

(5 concepts is a proposal; the gate may merge/trim — e.g. fold `attribute-search` scoring into `retrieve-then-rank`,
or split evaluation. All must be globally unique vs every registered book.)

## Phases

### Phase A — curriculum registry (concepts + coverage-map + manifest)
- Add the new concept ids to `recsys/curriculum/concepts.yaml` (kebab, globally unique; sensible `category`/`kind`).
- Add the Unit-1 entry to `recsys/curriculum/coverage-map.yaml` (`introduces` = the Unit-1 concepts; `requires` =
  any assumed-baseline ids used as given [these earn no credit]; `practices` = the introduced ids the exercises
  drill). `lessons: 3`.
- `recsys/units/unit-01-<slug>/manifest.yaml` mirroring the map entry (blueprint_version 1; provenance original).
**Verify:** `manifest-check` / `prereq-check` / `coverage-check` / `concept-scan` green for `recsys` (routed under
`--group recsys`); whole-book `lessons` total still < 30 so `buildout` holds.

### Phase B — lesson.ipynb (concept track; opens with the project hook)
Teacher-led notebook, project-first: open with the recommender goal and a concrete "what should I read next?"
problem, then teach — the catalog and item attributes (load via `bookrec.load_catalog` on the seeded synthetic
slice); the **retrieve-then-rank** architecture and the `RetrievalPath` contract (read/use `bookrec`, don't rebuild
it); **search/filter** as the first candidate operation; and the **evaluation scoreboard** — derive hit-rate@k and
recall@k **from scratch in NumPy**, then reveal `bookrec.evaluate.hit_rate_at_k`/`recall_at_k`. No real data.
**Verify:** `exec-lessons` runs clean under the group; hygiene (no stray solutions) as applicable to lessons.

### Phase C — exercises.ipynb + solutions.ipynb (dual-model dispatch)
Per the agent-dispatch table, STATEMENTS and SOLUTIONS are authored by SEPARATE fresh subagents (cross-model
verification lives in the gates). Exercises: core tasks drilling the Unit-1 concepts (load+inspect the catalog;
implement an attribute search/filter; build a frozen holdout; compute hit-rate@k/recall@k; wire a trivial path +
the scoreboard) + **≥1 `stretch`** (rendered "Challenge"). `exercises.ipynb` has NO solutions and NO executed
outputs. `solutions.ipynb` runs top-to-bottom clean with fixed seeds and reproduces stated answers.
**Verify:** `hygiene` (exercises: no solutions/outputs; ≥1 stretch tag), `exec-solutions` clean, blind-solvable at
the content gate.

### Phase D — project milestone (project track)
The growing recommender's Unit-1 milestone: a notebook/module step that loads the catalog, exposes search/filter,
and stands up the **evaluation scoreboard** (frozen holdout + hit-rate@k) against which later units' paths are
measured — using the `bookrec` substrate (register a trivial/identity path; blend/rank pass-through) so Unit 2's
popularity path slots in. (Any reusable code lands in the `bookrec`-adjacent project package, not scattered cells.)
**Verify:** runs under the group; deterministic (fixed seeds); no real data.

### Phase E — teacher-notes.md (active session inline — pedagogy)
Learning goals; a 2–3-sitting pacing plan (advanced audience); how to run the project hook; common mistakes
(e.g. evaluating on the training split; confusing hit-rate@k with precision); discussion prompts; differentiation.

### Phase F — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Unit 1 present (structure, manifest, prereq closure over
own graph + baseline + python-projects dependency baseline, coverage, **stretch presence**, notebook exec +
hygiene, concept-scan, PDF build incl. the Unit-1 handout, pre-merge-guard). `recsys` checks routed under
`--group recsys`; global `tests/` group-free. `buildout` still holds (lessons total < 30). No real-catalog data.

## Out of scope
No learned retrieval path (popularity = Unit 2); no later Part-1 topics (TF-IDF/BM25, CF, MF); no Part-2/neural; no
checkpoints yet (Checkpoint A lands at the end of Part 1); no `buildout` removal (deferred as above); no real data.

## Plan Review
_(4-way gate — [glm] skipped per standing plan-091 decision; pending)_

## Content Review
_(4-way, pre-PR — pending; reviewers blind-solve the exercises + review the lesson for project-first/engagement/
audience-appropriateness per the book's declared baseline; tooling-if-any gets code review.)_

## Post-Execution Report
_(pending)_

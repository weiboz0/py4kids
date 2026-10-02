# Plan recsys-003 — Unit 2: Popularity and weighted baselines

**Design:** `docs/designs/011-recsys-book.md` (§2, §5, §6 popularity-bias signal, §8 Unit 2). **Book:** `recsys`
(Book 3). **Autopilot** per AGENTS.md. Ships the **second student unit** of Part 1 on the recsys-001 substrate
(`bookrec` + the seeded generators) and on Unit 1's scoreboard. Unit 2 builds the **first learned/scored retrieval
path** and measures it against Unit 1's random floor.

## Scope
**Unit 2 only** (`recsys/units/unit-02-<slug>/`). Teaches the **popularity baseline** — the simplest path that
actually learns from data — and why a naive popularity count is a trap: **the weighted (Bayesian-shrinkage) estimate**
that stops a thinly-exposed book from outranking a genuinely popular one, and **popularity bias** (a popularity
recommender amplifies head items and starves the tail — measurable, and the motivation for the personalised paths in
U4+). The deliverable is a real `PopularityRetrievalPath` in `bookrec`, registered and **scored on Unit 1's
`val` scoreboard**, beating the random floor. No personalisation (that is neighbourhood CF, Unit 4). No real data.

## Buildout stays
recsys-003 **KEEPS `buildout: true`**: the whole-book `lessons` total becomes `6` (Unit 1's 3 + Unit 2's 3), still
far below the `lesson_budget` lower bound (30), which buildout waives (`curriculum.py:346`); introductions and
coverage are waived too, and `concept_minimum` is already met. Buildout is removed by the later Part-1/Part-2 plan
whose added unit(s) first bring the total to ≥30 — NOT this plan.

## Audience & retained laws (design 011 §2)
Advanced audience; assumed baseline in `baseline.yaml` (incl. `probability`, `expectation`, `statistics`,
`pandas-groupby`). Retained: **project-first** (lesson opens with the hook; `noexec-check` needs a non-empty markdown
first cell); **taught-before-assessed**; student notebooks have NO solutions / NO executed outputs
(`execution_count: null`); `solutions.ipynb` runs clean with fixed seeds; teacher notes; dual **concept∥project
tracks**; **from-scratch→reveal-the-library**. CPU-light (pandas/NumPy + `bookrec`; no torch/faiss) but routed under
`--group recsys` via the existing `dependency_group` routing.

## Concepts introduced (3) — added to `concepts.yaml`; Unit 2 is their `introduces` home
- `popularity-ranking` — rank catalog items by observed popularity (a count of positive **training**-split
  interactions per item); the first path that reads data. The retrieval score is the (smoothed) popularity, equal for
  every reader (not yet personalised). `kind: technique`.
- `bayesian-shrinkage` — the weighted / Bayesian-average estimate `score = (v·R + m·C)/(v + m)`: an item's own
  positive rate `R` over its exposure count `v`, shrunk toward the global positive rate `C` by a prior strength `m`.
  Taught from first principles (why a 3-of-3 book must not outrank a 9000-of-10000 book; `m` as pseudo-counts; the
  `v→∞` and `v→0` limits) — grounds the baseline math-concepts `probability`/`expectation`. `kind: technique`.
- `popularity-bias` — a popularity recommender concentrates exposure on already-popular (head) items and under-serves
  the long tail; **measured** here (catalog coverage / the share of recommendations drawn from the head) and named as
  the motivation for personalised paths (U4+) and the beyond-accuracy metrics of U13. `kind: technique`.

All three are **`kind: technique`** (so `concept_scan` never treats them as flaggable syntax) with valid categories,
and all three are globally unique vs every registered book (confirmed: 0 hits in any `*/curriculum/concepts.yaml`).

### Coverage-map entry (`requires`/`practices` now reference Unit 1)
`unit-02-<slug>`, `kind: unit`, `lessons: 3`,
`introduces: [popularity-ranking, bayesian-shrinkage, popularity-bias]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]` (all introduced by Unit 1
→ `prereq_findings` closes; verified non-fastforward policy checks both `requires` and `practices` against
`known_baseline ∪ earlier-introduces`),
`practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]` (Unit 2 genuinely
re-exercises all four: it builds a real scored path (retrieve-then-rank) that retrieves catalog items
(catalog-search) and scores it on the `val` scoreboard (offline-evaluation) with hit-rate@k/recall@k
(top-k-ranking-metrics)). `practices ∩ introduces(own) = ∅`; no assumed-baseline id is practised; no field has
duplicates (satisfies `practice_findings`). No `project` entry authored → the capstone rule
(`practice_findings:555-570`) does not fire.

## Phases

### Phase A — curriculum registry + syllabus (the CI-fidelity phase)
- `recsys/curriculum/concepts.yaml`: add `popularity-ranking`, `bayesian-shrinkage`, `popularity-bias` (kebab,
  globally unique, `kind: technique`, valid `category`).
- `recsys/curriculum/coverage-map.yaml`: add the Unit-2 entry exactly as specified above (map order after Unit 1).
- `recsys/curriculum/baseline.yaml`: **declare every new library method** Unit-2 notebooks call that is not already
  in `library_methods` (candidate set to confirm against the authored cells: `value_counts`, `Counter`, `get`,
  `items`, `argsort`, `clip`, `maximum`, `cumsum`, `astype`, `fillna`, `map`, `index`, `tolist`, `round` — authors
  add only the ones actually used; an undeclared library method FAILs `concept-scan`, so this is checked in Phase C/F).
- `recsys/units/unit-02-<slug>/manifest.yaml`: mirror the map entry (blueprint_version 1, provenance original;
  concept tags `introduces`/`requires`/`practices`).
- `recsys/syllabus.md`: add the "Arc at a glance" table row `| 2 | \`unit-02-<slug>\` | unit | 3 | <hook> |` (in map
  order; `syllabus_findings` requires one row per coverage entry, no stale rows); rebuild the syllabus PDF via
  `scripts/build-pdf.sh`.
**Verify:** `manifest`/`prereq`/`coverage`/`practice`/`concept-scan`/`structure`/`syllabus` green for `recsys`
(routed `--group recsys`); `practices ∩ introduces = ∅`; whole-book `lessons` total = 6 < 30 so buildout holds.

### Phase B — project milestone as `bookrec` code (`bookrec/popularity.py`; codex per the dispatch table)
Dispatch: **tooling/package code** to codex (`codex:codex-rescue`, GPT-5.6-sol), SEPARATE from the lesson/exercise
authoring. Promote the foundation's `_popularity_fixture.py` into a real, shipped path:
- `bookrec/popularity.py`: a `PopularityRetrievalPath(BaseRetrievalPath)` (name `"popularity"`, version `"1"`) whose
  `fit(interactions, catalog=None)` counts positive **train**-split interactions per catalog item and computes the
  **smoothed** popularity `score = (v·R + m·C)/(v + m)` per item (`v` = exposures, `R` = item positive rate,
  `C` = global positive rate, `m` = prior strength, a constructor parameter with a documented default); `retrieve`
  returns the top items by smoothed score, **reader-independent** (same ranking for every query) but honouring the
  `context["seen"]` exclusion and the `Candidate`/finite-score/stable-int/tie-break contract via `_finish`; `load`
  restores from a fitted artifact. Raise on a non-positive `m`, on an empty fit, and on non-finite scores (reuse the
  protocol guards). Export it from `bookrec/__init__.py` (`__all__`).
- A **popularity-bias measurement** helper (`bookrec/popularity.py` or `bookrec/diversity.py`): `catalog_coverage`
  (fraction of catalog items that appear in any reader's top-k) and a head-share metric, used by the lesson/exercises
  and tested. Keep it small and seed-free.
- Tests under `recsys/projects/bookrec/tests/` (routed recsys suite): the path beats the random floor on the seeded
  `val` scoreboard; smoothing orders a 3-of-3 item below a 9000-of-10000 item (and the reverse without smoothing);
  `m→0` recovers the raw positive-rate ranking and large `m` collapses toward the global order; coverage/head-share
  are in `[0,1]` and the popularity path's coverage is **lower** than the random path's (the measurable bias). Retire
  or re-point `_popularity_fixture.py` so there is one source of truth.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/tests/` green; deterministic (seeded); no real data;
the new path registers in a `PathRegistry` without artifact/name collision.

### Phase C — lesson.ipynb (concept track; Opus subagent; opens with the project hook)
Dispatch: an **Opus subagent** authors the lesson. Project-first: first cell is the markdown hook ("a brand-new
reader with no history — what do we recommend *before* we know anything about them?" → the popularity baseline, and
the honest question "is counting enough?"). Then, deriving from scratch before revealing `bookrec`:
1. **Count popularity** on the **train** split (never val/test); show the heavy-tailed distribution (the generator's
   §6 popularity-bias signal makes this real); rank by raw count; score it on Unit 1's `val` scoreboard — it beats
   the random floor (state the expected direction, show the number).
2. **Why raw counts/averages mislead** → derive the **weighted (Bayesian-shrinkage)** estimate from first principles
   (the `v·R + m·C` / `(v+m)` form; `m` as pseudo-counts; limits), by hand in NumPy, then reveal
   `PopularityRetrievalPath`; show the smoothed ranking changes which books surface and (if measurable on the seed)
   nudges the scoreboard.
3. **Popularity bias** — measure catalog coverage / head-share for the popularity path vs the random floor; name the
   bias and why personalisation (U4) and beyond-accuracy metrics (U13) are the answer. This is the bridge cell.
Diagrams use **ASCII** (no box-drawing glyphs — handout PDF `pdf_glyphs`). Use `rank(exclude=seen)` so already-read
books are not recommended. Reuse `bookrec` (don't rebuild the scoreboard/metrics).
**Verify:** `exec-lessons` clean under the group; non-empty markdown first cell (`noexec-check`); every `x.name(...)`
call's method is in `baseline.yaml library_methods` or a `def` in the notebook (`concept-scan`).

### Phase D — exercises.ipynb + solutions.ipynb (separate subagents; exact minima)
Dispatch: exercise **statements** and **solutions** by SEPARATE fresh subagents (cross-model check at the gate).
Hard minima: **≥6 `## Exercise N`** headings; **≥2 `stretch`-tagged cells** (tag both statement markdown and answer
cell; rendered "Challenge"); `exercises.ipynb` has NO solutions and NO outputs (`execution_count: null`);
`solutions.ipynb` mirrors every `## Exercise N`, runs top-to-bottom clean with fixed seeds, carries **≥3 non-vacuous
`assert` cells**. Exercises drill the Unit-2 concepts and re-exercise Unit-1's (compute popularity counts on train;
derive and apply the shrinkage estimate for given `(v,R,C,m)`; register `PopularityRetrievalPath` and read the `val`
scoreboard vs the random floor; measure catalog coverage / head-share). Stretch e.g.: show analytically that
raising `m` is a convex combination pulling every item toward `C` and predict the coverage change; derive the `m`
that makes two given items tie. Anything **assessed** must be taught in the lesson first (taught-before-assessed).
**Verify:** `hygiene`/`exercise-structure` (≥6 exercises, ≥2 stretch, no solutions/outputs); `exec-solutions` clean;
`concept-scan` clean; blind-solvable at the content gate.

### Phase E — teacher-notes.md (active session inline — pedagogy)
Exact headings: `## Goals`, `## Pacing` (2–3 sittings, advanced), `## Common mistakes` (counting on val/test;
forgetting to exclude `seen`; raw-count traps; mis-reading `m`; claiming popularity is "personalised"),
`## Discussion prompts`, `## Differentiation`. The popularity-bias caution lives in the LESSON, not only here.

### Phase F — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–2 present (structure, manifest, prereq over own
graph + baseline + python-projects dependency baseline, coverage, practice, **stretch presence**, exec + hygiene,
concept-scan, PDF handout, routed recsys pytest) AND `bash scripts/pre-merge-guard.sh --pr` OK (the PR-union guard;
ci-local runs the guard without `--pr`, so name it explicitly). `recsys` routed `--group recsys`; global `tests/`
group-free; `buildout` holds (lessons total 6).

## Out of scope
No personalisation (neighbourhood CF = Unit 4); no content/lexical retrieval (TF-IDF/BM25 = Unit 3); no MF/neural; no
`projects/project-*` registry entry (the growing project is represented by the `bookrec` package + the per-unit
lesson/exercise integration; the single `project-*` entry is reserved for the U14 capstone, so the capstone rule does
not fire mid-book — this supersedes recsys-002 Phase D's "first ≥2-unit plan" note; revisit if a reviewer prefers
per-part project entries); no checkpoint (Checkpoint A ends Part 1 at U6); no `buildout` removal (deferred); no
real-catalog data; no generator/schema change (the §6 popularity signal already exists).

## Verification phase declared
This plan ships a unit; Phase F is its named verification phase (per the plan-review gate requirement).

## Plan Review

### Round 1 (on v1)

<!-- verdicts appended here -->

## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->

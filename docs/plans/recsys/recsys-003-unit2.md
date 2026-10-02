# Plan recsys-003 — Unit 2: Popularity and weighted baselines (+ the milestone-notebook mechanism)

**Design:** `docs/designs/011-recsys-book.md` (§5, §6 popularity-bias signal, §8 Unit 2, §10 project packaging — **amended
here**). **Book:** `recsys` (Book 3). **Autopilot** per AGENTS.md. **v2** folds plan-review round 1 ([sol] REJECT +
[fable] REJECT — both "fixable in one revision; design sound"). Ships the **second student unit** of Part 1 on the
recsys-001/Unit-1 substrate, **and** inaugurates the project's **milestone-notebook mechanism** (the user-chosen
project architecture — see `## Project architecture decision`).

## Scope
**Unit 2** (`recsys/units/unit-02-popularity-and-bias/`) **plus** the milestone-notebook infrastructure it is the
first to use. Unit 2 builds the **first learned/scored retrieval path** and measures it honestly:
- **popularity (count) ranking** — the simplest path that reads data, and it really beats Unit 1's random floor;
- the **weighted (Bayesian-shrinkage) rating** — a *quality* estimate that re-ranks the catalog and, measured on the
  same `val` holdout, **scores near zero** — because the holdout's exposure is popularity-driven, so the offline
  metric itself encodes popularity bias (the unit's sharpest lesson);
- **popularity bias** — measured as catalog coverage / head-share: the scoreboard "winner" serves almost none of the
  catalog, motivating personalisation (U4) and beyond-accuracy metrics (U13).
No personalisation (neighbourhood CF = U4). No lexical/content retrieval (U3/U7). No real data; no generator change.

## Project architecture decision (resolves [sol] round-1 finding 2; user-authorised 2026-10-02)
The user chose: **the growing project is the `bookrec` package + per-unit milestone notebooks; the single
`projects/<id>/` registry entry is reserved for the U14 capstone.** Rationale: the tooling's capstone rule
(`practice_findings:555-570` — the last `project` map entry must have every concept practised by non-capstone
entries) makes a single `projects/` *map entry* CI-infeasible until the book is concept-complete, so it can only
exist at the end. Therefore:
- **Phase 0 amends Design 011 §10** to state this explicitly (milestone notebooks accumulate in the package across
  units; the one `projects/` registry entry is the capstone, authored at U14), replacing the prior "single
  `projects/` entry's manifest grows per unit" wording and superseding recsys-002 Phase D's "first ≥2-unit plan"
  placeholder. Design 011 is a design doc (NOT a governance file in the AGENTS.md hard-safeguard list), so this
  amendment is vetted by THIS plan's 4-way plan-review gate.
- **Phase 1 adds the tooling** so milestone notebooks are under the gate (today `content_dirs` discovers only
  `units/unit-*`, `checkpoints/checkpoint-*`, `projects/project-*`, so a notebook under `projects/bookrec/milestones/`
  is never executed or hygiene-checked — verified in `tools/notebooks.py:155-190`).
- Unit 1 is **grandfathered** (its milestone shipped as package code before this convention); the convention starts
  at Unit 2. A later optional pass may backfill a Unit-1 milestone notebook — NOT blocking here.

## Buildout stays
recsys-003 **KEEPS `buildout: true`**: the whole-book `lessons` total becomes `6` (Unit 1's 3 + Unit 2's 3), far
below the `lesson_budget` lower bound (30), which buildout waives (`curriculum.py:346`); introductions and coverage
are waived; `concept_minimum` is met. Buildout is removed by the later plan whose unit(s) first bring the total ≥30.

## Audience & retained laws (design 011 §2)
Advanced audience; assumed baseline in `baseline.yaml` (incl. `probability`, `expectation`, `statistics`,
`pandas-groupby`). Retained: **project-first** (lesson + milestone open with the hook; `noexec-check` needs a
non-empty markdown first cell); **taught-before-assessed** (the weighted-rating/~0-score result is shown in the
lesson before any exercise assesses it); student notebooks have NO solutions / NO executed outputs
(`execution_count: null`); `solutions.ipynb` + the milestone notebook run top-to-bottom clean with fixed seeds;
teacher notes; dual **concept∥project tracks**; **from-scratch→reveal-the-library**. CPU-light (pandas/NumPy +
`bookrec`; no torch/faiss) routed under `--group recsys`.

## Concepts introduced (3) — added to `concepts.yaml`; Unit 2 is their `introduces` home
- `popularity-ranking` — rank catalog items by observed popularity: a count of positive **train**-split interactions
  per item; reader-independent (not yet personalised). The shipped `PopularityRetrievalPath` ranks by this count.
  `kind: technique`, `category: techniques`.
- `bayesian-shrinkage` — the weighted / Bayesian-average quality estimate `score = (v·R + m·C)/(v + m)`: an item's
  own positive **rate** `R = positives/observed-train-rows`, its exposure `v`, the global positive rate `C`, and a
  prior strength `m` (pseudo-counts). Taught from first principles (why a 3-of-3 book must not be called better than a
  9000-of-10000 book; `m→0` recovers the raw rate `R`; `m→∞` sends every score to `C`, so the ranking **degenerates
  to an all-ties, id-ascending order** — NOT a "global order"). A *quality* ranking, distinct from popularity.
  `kind: technique`, `category: techniques`.
- `popularity-bias` — a popularity recommender concentrates exposure on head items and starves the tail; **measured**
  here via **catalog coverage** and **head-share** (defined precisely below); and the realisation that the `val`
  holdout is itself popularity-biased (exposure ∝ popularity), so a quality-first ranker scores near zero on it.
  `kind: technique`, `category: techniques`.

All three are globally unique vs every registered book (confirmed: 0 hits across `*/curriculum/concepts.yaml`).

### Coverage-map entry (`requires`/`practices` reference Unit 1; verified CI-green)
`unit-02-popularity-and-bias`, `kind: unit`, `lessons: 3`,
`introduces: [popularity-ranking, bayesian-shrinkage, popularity-bias]`,
`requires: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]`,
`practices: [retrieve-then-rank, catalog-search, offline-evaluation, top-k-ranking-metrics]`.
Both reviewers confirmed on a scratch copy that this entry yields `[]` from `prereq_findings` (non-fastforward →
checks `requires`+`practices` against baseline ∪ earlier-introduces; all four are Unit-1 introductions),
`practice_findings` (no own-overlap, no assumed-baseline practised, no dups; capstone rule does not fire — no
`project` map entry), `introduction_findings`, `lesson_budget_findings` (buildout, total 6<30), `coverage_findings`,
`map_schema_findings`, `syllabus_findings` (with the added row).

### Metric definitions (bind for code + lesson + exercises — fixes [sol]#3 / [fable]#3)
- **Head set** = the top **10%** of catalog items by **train** positive count (deterministic; ties broken by
  ascending `item_id` to reach exactly `ceil(0.10·N)` items).
- **Head-share** = fraction of recommendation **slots** (summed over every scored reader's top-k list) whose item is
  in the head set.
- **Catalog coverage** = fraction of **unique** catalog items that appear in at least one scored reader's top-k.
- All computed over the **train**-exposure head and the SAME scored-reader set as the scoreboard (cold readers
  excluded). Reference numbers to reproduce on the seed (k=10, 368 readers, cold excluded): random coverage 0.95 /
  head-share 0.047; popularity-count coverage 0.007 / head-share 1.0 → the "popularity coverage < random" direction
  is robust and is the tested assertion.

### Empirical scoreboard expectations (bind for tests + lesson prose — fixes [sol]#5 / [fable]#1)
Measured via `run_validation_scoreboard` on `recsys/data/generated/interactions.csv.gz`, k=10, cold excluded, 368
readers: **random hit@10 ≈ 0.0136; popularity-count hit@10 ≈ 0.1196 (~9× floor); weighted-rating (shrunk rate)
hit@10 ≈ 0 (m small) rising only toward ~0.03 at large m.** Root cause (`gen_interactions.py:150-160`): positive
probability has no popularity term while exposure ∝ popularity, so corr(exposure, rate) ≈ 0.006 but corr(exposure,
count) ≈ 0.906. The shipped path ranks by **count** (beats the floor); the weighted rating is taught as the quality
lens whose near-zero scoreboard is the popularity-bias-in-the-metric lesson. Authors RE-RUN these on the committed
seed and assert the **direction** (count ≫ random; weighted-rating ≪ count), not brittle exact values.

## Phases

### Phase 0 — Design 011 §10 amendment (active session inline; part of this plan's reviewed surface)
Edit `docs/designs/011-recsys-book.md §10` to the user-chosen architecture (above). Add a one-line entry to the
design's `## 14. Revision history`. No other design section changes. Reviewed by this plan's plan-review gate.
**Verify:** design renders; wording matches the Project-architecture decision; no stray edits elsewhere.

### Phase 1 — milestone-notebook tooling (Opus subagent; `tools/` per the dispatch table)
Dispatch: an **Opus subagent** (`Agent`, `model: opus`) extends `tools/notebooks.py` so milestone notebooks are
discovered and gated WITHOUT being a `project-*` map entry:
- a `milestone_dirs`/`milestone_notebooks(root, book)` helper globbing `<book_dir>/projects/*/milestones/*.ipynb`
  (so `recsys/projects/bookrec/milestones/*.ipynb` is found); fail-closed (absent dir → no notebooks, no error);
- include milestone notebooks in **`exec-solutions`** (run top-to-bottom clean with fixed seeds — they are
  demonstrations of the working system) and in **hygiene-check** (committed with cleared outputs +
  `execution_count: null`, like solutions); they are NOT student-facing exercises (no `exercise-structure`/`noexec`
  obligation) and NOT map entries (so `coverage`/`prereq`/capstone untouched);
- routed under the book's dependency group exactly as unit notebooks are.
- group-free tests in `tests/` (e.g. `tests/test_milestone_notebooks.py`): a milestone notebook under the glob is
  discovered + exec'd; a milestone notebook with stored outputs / non-null `execution_count` FAILs hygiene; absence
  of a `milestones/` dir is clean.
**Verify:** new `tests/` green (group-free); `exec-solutions`/`hygiene-check` pick up a milestone notebook; no
regression to existing unit/checkpoint/project discovery; `coverage-map`/capstone behaviour unchanged.

### Phase A — curriculum registry + syllabus (CI-fidelity)
- `recsys/curriculum/concepts.yaml`: add `popularity-ranking`, `bayesian-shrinkage`, `popularity-bias`
  (`kind: technique`, `category: techniques`, kebab, globally unique).
- `recsys/curriculum/coverage-map.yaml`: add the Unit-2 entry exactly as specified; **update the stale `:2-3`
  comment** ("three lessons" → the whole-book total is now six) (fixes [fable]#5).
- `recsys/curriculum/baseline.yaml`: **declare every new `x.name(...)` library method** Unit-2 notebooks call that is
  not already present (confirm against authored cells; `Counter(...)` is a Name call and NOT required — [fable]#6).
- `recsys/units/unit-02-popularity-and-bias/manifest.yaml`: mirror the map entry (blueprint_version 1, provenance
  original).
- `recsys/syllabus.md`: add the "Arc at a glance" row `| 2 | \`unit-02-popularity-and-bias\` | unit | 3 | <hook> |`
  (map order); rebuild the syllabus PDF via `scripts/build-pdf.sh`.
**Verify:** `manifest`/`prereq`/`coverage`/`practice`/`concept-scan`/`structure`/`syllabus` green for `recsys`;
`practices ∩ introduces = ∅`; buildout holds (total 6 < 30).

### Phase B — project milestone as `bookrec` code (Opus subagent; `tools/`-style package code)
Dispatch: an **Opus subagent** (`Agent`, `model: opus`) — SEPARATE from lesson/exercise authoring. Promote the
foundation's `_popularity_fixture.py` into real shipped code:
- `bookrec/popularity.py`: `PopularityRetrievalPath(BaseRetrievalPath)` (name `"popularity"`, version `"1"`).
  `fit(interactions, catalog=None)` takes a **pandas DataFrame (or iterable of rows) with columns
  `reader_id,item_id,split,label`** (per `gen_interactions.py:46 INTERACTION_COLUMNS`) and counts **only
  `split=="train"` AND `label==1`** rows per catalog item → the popularity **count** score; `retrieve` returns the
  top items by count, **reader-independent**, honouring `context["seen"]` exclusion and the
  `Candidate`/finite-score/stable-int/tie-break contract via `_finish`; `load` restores from a fitted artifact.
  Raise on an empty fit. (Fixes [fable]#2 — input type named; leakage enforced in code.)
- `bookrec/popularity.py` also exposes `weighted_rating(positives, exposures, *, m, global_rate=None)` computing the
  `(v·R + m·C)/(v+m)` **quality** estimate (vectorised), with a **documented default `m`** (chosen so the 3/3 vs
  9000/10000 reversal is exhibited on the fixture — e.g. `m` on the order of the median exposure; authors fix and
  document the value), the `m→0 ⇒ R` and `m→∞ ⇒ C` limits, and ties broken by ascending `item_id`.
- a **popularity-bias measurement** helper (`bookrec/diversity.py`): `catalog_coverage(recommendations, catalog_ids)`
  and `head_share(recommendations, head_ids)` per the Metric definitions above; small, seed-free.
- Export the new public names from `bookrec/__init__.py` (`__all__`). **Retire `_popularity_fixture.py`** and
  **rewrite** the tests that import it (`recsys/projects/bookrec/tests/test_bookrec.py:30-72,98-109` call
  `PopularityPath().fit([ints])` / `PopularityPath(version="2")` — update to the real `fit(DataFrame)` signature)
  (fixes [fable]#2).
- Tests under `recsys/projects/bookrec/tests/` (routed recsys suite): count path **beats the random floor** on the
  seeded `val` scoreboard (direction, not exact value), with `cold_readers` passed; a **leakage test** (val/test or
  `label==0` rows do not change fitted counts); `weighted_rating` reverses 3/3 vs 9000/10000 at the default `m`,
  `m→0 ⇒ R`, and **`m→∞ ⇒ all-C ties → id-ascending order**; coverage/head-share in `[0,1]` and the popularity path's
  coverage is **lower** than the random path's; the path registers in a `PathRegistry` with no name/artifact
  collision.
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/tests/` green; deterministic (seeded); no real data.

### Phase C — lesson.ipynb (concept track; Opus subagent; opens with the project hook)
Dispatch: an **Opus subagent** (`Agent`, `model: opus`). Project-first: first cell is the markdown hook ("a brand-new
reader with no history — what do we recommend *before* we know anything about them?"). Deriving from scratch before
revealing `bookrec`:
1. **Count popularity** on **train** only (never val/test); show the heavy-tailed distribution (§6 signal); rank by
   count; score on Unit 1's `val` scoreboard **passing `cold_readers=cold["cold_readers"]` from
   `cold_partitions.json`** (fixes [fable]#4) — it beats the random floor (state and show ≈0.12 vs ≈0.014).
2. **Is the most-read the best?** Derive the **weighted (Bayesian-shrinkage)** rating by hand (`(vR+mC)/(v+m)`;
   `m` pseudo-counts; the `m→0`/`m→∞` limits), reveal `weighted_rating`, re-rank → different books surface; then
   **honestly score the quality ranking on `val` → ≈0** and explain WHY: exposure in the holdout ∝ popularity, so the
   offline metric rewards recommending the already-popular — **popularity bias living in the metric.** (Taught here,
   so exercises may assess it.)
3. **Measure popularity bias** — coverage/head-share for the count path vs the random floor (0.007/1.0 vs 0.95/0.047);
   name the bias; bridge to personalisation (U4) and beyond-accuracy metrics (U13).
ASCII diagrams only (no box-drawing — handout PDF `pdf_glyphs`). Use `rank(exclude=seen)`. Reuse `bookrec`.
**Verify:** `exec-lessons` clean under the group; non-empty markdown first cell; every `x.name(...)` method declared
in `baseline.yaml library_methods` or a notebook `def` (`concept-scan`).

### Phase D — exercises.ipynb + solutions.ipynb (separate fresh Opus subagents; exact minima)
Dispatch: statements and solutions by **SEPARATE fresh Opus subagents** (`model: opus`) — cross-model check at the
gate. Hard minima: **≥6 `## Exercise N`**; **≥2 `stretch`-tagged cells** (tag statement + answer; rendered
"Challenge"); `exercises.ipynb` NO solutions / NO outputs (`execution_count: null`); `solutions.ipynb` mirrors every
`## Exercise N`, runs clean with fixed seeds, **≥3 non-vacuous `assert` cells**. Exercises drill Unit-2 concepts and
re-exercise Unit-1's (count positives on train; apply `weighted_rating` for given `(v,R,C,m)` and predict the
re-ranking; register `PopularityRetrievalPath` and read the `val` scoreboard vs the random floor with cold readers
excluded; measure coverage/head-share). Stretch e.g.: show `weighted_rating` is a convex combination pulling every
item toward `C` and predict the coverage change; find the `m` that makes two given items tie. Everything assessed is
taught in Phase C first.
**Verify:** `hygiene`/`exercise-structure` (≥6, ≥2 stretch, no solutions/outputs); `exec-solutions` clean;
`concept-scan` clean; blind-solvable at the content gate.

### Phase E — milestone notebook (Opus subagent; the Unit-2 contribution to the growing project)
Dispatch: an **Opus subagent** (`model: opus`) authors `recsys/projects/bookrec/milestones/unit-02-popularity.ipynb`
— a runnable demonstration (cleared outputs, `execution_count: null`, fixed seeds) that integrates the Unit-2
deliverable into the growing `bookrec` system end-to-end: construct + `fit` + register `PopularityRetrievalPath`,
score it on the `val` scoreboard vs the random floor (cold excluded), show the `weighted_rating` quality view and its
near-zero scoreboard, and report coverage/head-share. Opens with a one-line project-hook markdown cell.
**Verify:** discovered + executed by `exec-solutions` and passed by `hygiene-check` via the Phase-1 tooling; runs
clean under `--group recsys`.

### Phase F — teacher-notes.md (active session inline — pedagogy)
`recsys/units/unit-02-popularity-and-bias/teacher-notes.md`. Exact headings `## Goals`, `## Pacing`, `## Common
mistakes`, `## Discussion prompts`, `## Differentiation`. **`## Pacing` states the project hook and a 60–90-minute
allocation across 2–3 sittings** (fixes [sol]#6; AGENTS.md teacher-notes rule). Common mistakes: counting on
val/test; forgetting `cold_readers`/`exclude=seen`; reading the weighted-rating's low score as "quality is useless"
rather than "the metric is popularity-biased"; calling popularity "personalised".

### Phase G — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Units 1–2 + the Unit-2 milestone notebook + the new
tooling present (lint, group-free `tests/`, routed recsys pytest, structure/manifest/prereq/coverage/practice,
stretch, exec-lessons/exec-solutions incl. the milestone notebook, hygiene, concept-scan, PDF handout) AND
`bash scripts/pre-merge-guard.sh --pr` OK. `buildout` holds (lessons total 6).

## Out of scope
No personalisation (U4); no lexical/content retrieval (U3/U7); no MF/neural; no `projects/project-*` **map entry**
(the single registry entry is the U14 capstone — see Project-architecture decision); no Unit-1 milestone-notebook
backfill (grandfathered; optional later); no checkpoint (Checkpoint A ends Part 1 at U6); no `buildout` removal; no
real-catalog data; no generator change (the §6 popularity signal already exists).

## Verification phase declared
This plan ships a unit; Phase G is its named verification phase (per the plan-review gate requirement).

## Plan Review

### Round 1 (on v1)

**[self] — APPROVE WITH NITS.** Verified against `tools/curriculum.py`: (a) `prereq_findings:490-522` for a
non-fastforward book checks both `requires` and `practices` against `known_baseline ∪ earlier-introduces`; the four
Unit-1 ids are all introduced by Unit 1, so the Unit-2 entry closes. (b) `practice_findings:525-571` —
`practices ∩ introduces(own) = ∅` holds; no assumed-baseline id is practised; no field has dupes; the capstone rule
(555-570) needs `capstone_id is not None AND projects/<id>/.is_dir()`, and with no `project` map entry
`capstone_id = None`, so it cannot fire — deferral is sound. (c) `introduction_findings:374-387` — "introduced
twice" is always-on (each new id appears once; globally unique: 0 hits across all `*/curriculum/concepts.yaml`); the
"never introduced" branch is buildout-waived. (d) `lesson_budget_findings` lower bound is buildout-waived (total 6).
Nits (implementation-binding, not plan blockers):
1. `[FIXED v2]` **Should Fix** (Phase B/C). The Unit-1 content gate caught a degenerate `0.0/0.0` demo at an unlucky
   seed/k. Authors MUST empirically pick `k`/metric so the printed numbers show the intended direction. → v2 adds the
   measured Empirical scoreboard expectations + Metric definitions sections and binds direction-asserts.
2. `[FIXED v2]` **Should Fix** (Phase A). category for the three new ids. → v2 sets `category: techniques`.
3. `[FIXED v2]` **Nice to Have** (Phase A/C). declare new library methods; retire `_popularity_fixture.py`. → v2
   Phase A/B.

**[sol] — REJECT.** 1. `[FIXED v2]` **Must Fix** — replace `unit-02-<slug>` with a concrete id matching
`unit-[0-9]{2}-[a-z0-9-]+`. → `unit-02-popularity-and-bias` throughout. 2. `[FIXED v2]` **Must Fix** — project-entry
deferral contradicts Design §10 + the Unit-1 plan; resolve via a design amendment/tooling decision, not silently. →
`## Project architecture decision` (user-authorised) + Phase 0 (design §10 amendment) + Phase 1 (milestone-notebook
tooling). 3. `[FIXED v2]` **Must Fix** — define head-share precisely (head set, ties, slots vs unique). → Metric
definitions section. 4. `[FIXED v2]` **Must Fix** — Phase B/D dispatch is Opus subagent per the updated AGENTS.md
table, not Codex. → all authoring/tooling phases now dispatch Opus subagents; D keeps separate fresh statement/
solution sessions. 5. `[FIXED v2]` **Should Fix** — shrinkage: R = positives/observed-train-rows (sound); 3/3 vs
9000/10000 reversal depends on C and m; `m→∞ ⇒ all → C` (no "global order"). → concept text + Phase B tests specify
default `m`, convergence-to-C, and the all-ties/id-ascending degeneration. 6. `[FIXED v2]` **Should Fix** — teacher
notes require the project hook + 60–90-min pacing, not just "2–3 sittings". → Phase F.

**[fable] — REJECT** (empirically verified against the generated data). 1. `[FIXED v2]` **Must Fix** — shrunk-RATE
does NOT beat the floor; raw positive COUNT does (0.1196 vs 0.0136); shrinkage changes nothing when the count is
retained. → shipped path ranks by COUNT; weighted rating is the quality lens whose ~0 score is the taught
popularity-bias-in-the-metric moment; Empirical expectations section binds the numbers. 2. `[FIXED v2]` **Should
Fix** — name `fit()`'s input type + add a leakage test; retiring the fixture means rewriting its tests. → Phase B.
3. `[FIXED v2]` **Should Fix** — define the head cutoff. → Metric definitions (top 10% by train positive count).
4. `[FIXED v2]` **Should Fix** — name cold-reader exclusion. → Phase B/C/E pass `cold_readers`. 5. `[FIXED v2]`
**Nice to Have** — stale `coverage-map.yaml:2-3` comment. → Phase A. 6. `[FIXED v2]` **Nice to Have** — `Counter`
is a Name call, not required in `library_methods`. → Phase A note.

### Plan-review outcome (round 1): **NOT consensus** — [sol] REJECT + [fable] REJECT (both one-revision-fixable).
All findings folded into v2 above. Re-review as round 2 (4-way incl. [glm] per the updated AGENTS.md roster).

### Round 2 (on v2)

**[self] — APPROVE.** v2 folds all three round-1 reviewers' findings (every item tagged `[FIXED v2]`). The
load-bearing blocker ([fable]#1) is resolved by shipping the COUNT path (empirically beats the floor) and reframing
the shrinkage as the quality lens whose near-zero `val` score is the taught popularity-bias-in-the-metric lesson —
honest and better pedagogy, grounded in the measured numbers. The project-architecture fork is resolved by the
user's authorised choice, encoded as a reviewable Design §10 amendment (Phase 0) + minimal gate-coverage tooling
(Phase 1); the milestone notebook is thereby under `exec-solutions`/`hygiene`. Concrete slug, metric definitions,
cold-reader exclusion, `fit()` input + leakage test, default-`m`/limits, Opus dispatch, and teacher-notes pacing all
specified. No open [self] blockers.

<!-- [sol] / [glm] / [fable] appended here -->


## Content Review

<!-- appended pre-PR -->

## Post-Execution Report

<!-- appended before ship -->

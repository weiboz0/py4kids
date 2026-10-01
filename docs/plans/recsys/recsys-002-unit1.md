# Plan recsys-002 — Unit 1: The recommendation problem, the catalog, and the evaluation scoreboard

**Design:** `docs/designs/011-recsys-book.md` (§2, §5, §8 Unit 1). **Book:** `recsys` (Book 3). **Autopilot** per
AGENTS.md. **v2** folds plan-review round 1 ([sol] REJECT + [fable] REJECT — both "fixable in one revision; design
sound"). Ships the **first student unit** of Part 1 on the recsys-001 substrate (`bookrec` + the seeded generators).

## Scope
**Unit 1 only** (`recsys/units/unit-01-<slug>/`). Establishes the shared frame: the recommendation problem, the
synthetic **catalog**, the **retrieve-then-rank** architecture + the `RetrievalPath` contract, **search/filter**, and
the **evaluation scoreboard** (the generator's per-reader temporal `val` split + hit-rate@k / recall@k) — with a
**seeded random baseline path** so the scoreboard shows a real number. No learned path (popularity = Unit 2). **No
project-`*` entry** this plan (deferred — see Phase D). No real data.

## Buildout stays
recsys-002 **KEEPS `buildout: true`**: the whole-book `lessons` total is `3` (Unit 1 only), below the
`lesson_budget` lower bound (30), which buildout waives (`curriculum.py:346`); introductions are waived too, and
`concept_minimum=1` is already met. (Both reviewers confirmed a one-unit `lessons:3` map is CI-green under buildout
once the fixes below land.) Buildout is removed by the later Part-1 plan whose added unit(s) first bring the total
to ≥30 — NOT this plan. **Also fix the stale `recsys/curriculum/coverage-map.yaml:4-5` comment** that still says
recsys-002 removes buildout.

## Audience & retained laws (design 011 §2)
Advanced audience; assumed baseline in `baseline.yaml`. Retained: **project-first** (lesson opens with the hook;
`noexec-check` also needs a non-empty markdown first cell); **taught-before-assessed**; student notebooks have NO
solutions / NO executed outputs (`execution_count: null`); `solutions.ipynb` runs clean with fixed seeds; teacher
notes; dual **concept∥project tracks**; **from-scratch→reveal-the-library**. CPU-light (pandas/NumPy + `bookrec`; no
torch/faiss) but routed under `--group recsys` (notebooks import numpy/pandas/bookrec) via the existing
`dependency_group` routing.

## Concepts introduced (4) — added to `concepts.yaml`; Unit 1 is their `introduces` home
- `retrieve-then-rank` — candidate-generation → blend → rank architecture **and the `RetrievalPath` contract**
  (seed concept; **introduced here**; the protocol the student reads/implements is taught under this id).
- `catalog-search` — books as catalog items with the **real** generated schema (`item_id, title, author_id,
  genres, year`) + search/filter over them (merges the earlier thin catalog-representation + attribute-search;
  `pandas-dataframe` is already baseline).
- `offline-evaluation` — why offline eval answers "did it help?", the **per-reader temporal split** the generator
  emits (train/val/test), leakage, and keeping `test` sealed (for U6/Checkpoint A).
- `top-k-ranking-metrics` — **hit-rate@k and recall@k** (per-query vs aggregate-mean distinguished); U6 later adds
  precision@k/NDCG (this split avoids `introduction_findings` double-introduce — design §8 row 6 reconciled: U1
  owns hit@k+recall@k, U6 owns precision@k+NDCG).

All four are globally unique vs every registered book (confirmed by both reviewers). `requires`/`practices` for the
Unit-1 entry are **both `[]`** (it is the first entry — nothing earlier to require/practice; assumed-baseline ids
are used as given and earn no credit, never listed in `practices`). `requires` may list earlier-introduced ids only
once later units exist.

## Phases

### Phase A — curriculum registry + syllabus (the CI-fidelity phase)
- `recsys/curriculum/concepts.yaml`: add `catalog-search`, `offline-evaluation`, `top-k-ranking-metrics` (kebab,
  globally unique; `retrieve-then-rank` already present).
- `recsys/curriculum/coverage-map.yaml`: add the Unit-1 entry — `introduces: [retrieve-then-rank, catalog-search,
  offline-evaluation, top-k-ranking-metrics]`, **`requires: []`**, **`practices: []`**, `lessons: 3`. Update the
  stale buildout comment.
- `recsys/units/unit-01-<slug>/manifest.yaml`: mirror the map entry (blueprint_version 1, provenance original).
- `recsys/syllabus.md`: add the required entry **table row** `| \`unit-01-<slug>\` | unit | 3 |` (in map order, no
  stale rows — `syllabus_findings` requires one row per coverage entry); rebuild the syllabus PDF via `build-pdf.sh`.
**Verify:** `manifest`/`prereq`/`coverage`/`concept-scan`/`structure` green for `recsys` (routed `--group recsys`);
`practices ∩ introduces = ∅`; whole-book `lessons` total = 3 < 30 so buildout holds.

### Phase B — lesson.ipynb (concept track; Opus subagent; opens with the project hook)
Dispatch: an **Opus subagent** authors the lesson (per the agent-dispatch table). Project-first: first cell is the
markdown hook ("what should I read next?" → build a recommender). Then teach, deriving from scratch in NumPy before
revealing the library: the **catalog** via `bookrec.load_catalog` (returns `dict[int, Book]`; show the dict→DataFrame
view, the real `item_id/title/author_id/genres/year` schema) on the seeded synthetic slice; **search/filter**; the
**retrieve-then-rank** architecture + the `RetrievalPath` contract (use `bookrec`, don't rebuild it); the
**scoreboard** — use the generator's per-reader temporal **`val`** split (teach WHY temporal-per-reader avoids
leakage; keep `test` sealed), derive **hit-rate@k + recall@k** by hand, then reveal `bookrec.evaluate`; and a
**seeded random baseline `RetrievalPath`** whose expected hit-rate@k the student derives analytically (≈ k/N for one
relevant item) and confirms empirically — the floor Unit 2's popularity path must beat; use `rank(exclude=seen)` so
already-read books aren't recommended. Diagrams use **ASCII** (no box-drawing glyphs — handout PDF `pdf_glyphs`).
**Verify:** `exec-lessons` clean under the group; non-empty markdown first cell (`noexec-check`).

### Phase C — exercises.ipynb + solutions.ipynb (separate subagents; exact minima)
Dispatch: exercise **statements** and **solutions** by SEPARATE fresh Opus subagents (cross-model check at the gate).
Hard minima (encode for the authors): **≥6 `## Exercise N`** headings; **≥2 `stretch`-tagged cells** (tag both the
statement markdown and its answer cell; rendered "Challenge"); `exercises.ipynb` has NO solutions and NO outputs
(`execution_count: null`); `solutions.ipynb` mirrors every `## Exercise N` with code beneath, runs top-to-bottom
clean with fixed seeds, and carries **≥3 non-vacuous `assert` cells**. Exercises drill the Unit-1 concepts (load +
inspect the real-schema catalog; implement search/filter; use the temporal `val` split; compute hit-rate@k /
recall@k; register the seeded random path + read the scoreboard). Stretch e.g.: derive the random path's
expected-hit-rate@k and compare to the empirical value.
**Verify:** `hygiene`/`exercise-structure` (≥6 exercises, ≥2 stretch, no solutions/outputs); `exec-solutions` clean;
blind-solvable at the content gate.

### Phase D — project milestone as `bookrec` code (NO project-`*` entry this plan)
A standalone `project-*` entry is DEFERRED: the tooling treats the last `project` entry as the **capstone** and
would require every concept practiced by a non-capstone entry — impossible with one unit (`practices: []`). So the
Unit-1 milestone lands as **`bookrec` package code**: `bookrec/search.py` (attribute/text search over the catalog)
and `bookrec/scoreboard.py` (a frozen-`val`-split hit-rate@k runner), with **pytest under
`recsys/projects/bookrec/tests/`** (executed by ci-local step 2's routed recsys suite), and is **exercised** in
`lesson.ipynb`/`exercises.ipynb`. The first real `projects/project-01-<slug>/` brief entry is deferred to the first
plan with ≥2 units. (Design §10's "single projects/ entry grows per unit" collides with the 3–6 milestone-heading
cap over 14 units — flagged for that later plan to resolve as per-part project entries or a design amendment.)
**Verify:** `uv run --group recsys pytest recsys/projects/bookrec/tests/` green; deterministic (seeded); no real data.

### Phase E — teacher-notes.md (active session inline — pedagogy)
Exact headings: `## Goals`, `## Pacing` (2–3 sittings, advanced), `## Common mistakes`, `## Discussion prompts`,
`## Differentiation`. (The temporal-leakage warning lives in the LESSON, not just here.)

### Phase F — verification (named)
`TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN with Unit 1 present (structure, manifest, prereq over own
graph + baseline + python-projects dependency baseline, coverage, **stretch presence**, exec + hygiene,
concept-scan, PDF handout, routed recsys pytest) AND `bash scripts/pre-merge-guard.sh --pr` OK (the PR-union guard;
ci-local runs the guard without `--pr`, so name it explicitly). `recsys` routed `--group recsys`; global `tests/`
group-free; `buildout` holds (lessons total 3).

## Out of scope
No learned retrieval path (popularity = Unit 2); no TF-IDF/BM25/CF/MF; no Part-2/neural; no `projects/project-*`
entry (deferred to the first ≥2-unit plan); no checkpoint (Checkpoint A ends Part 1); no `buildout` removal
(deferred); no real-catalog data; no generator/schema migration (teach the real `item_id/title/author_id/genres/
year` schema as-is).

## Plan Review
4-way gate ([glm] skipped, standing plan-091 decision).
### Round 1 (on v1)
- **[self]:** APPROVE WITH NITS (concept grain).
- **[sol]:** REJECT — Must: practices must be `[]` + add syllabus table (#1); project milestone under-specified vs
  the project-entry tooling (#2); ≥6 exercises/≥2 stretch + Phase B must dispatch lesson authoring to an Opus
  subagent (#3); **catalog schema is `item_id/title/author_id/genres/year`, not title/authors/subjects/year** (#4);
  Phase F must name `pre-merge-guard --pr` + fix the stale coverage-map buildout comment (#6). Should: split
  hit-rate@k vs recall@k or use a broader metric concept (#5). Confirmed buildout + routing + global-uniqueness.
- **[fable]:** REJECT (fixable in one revision) — same practices=`[]`/syllabus (#1,#2); the **capstone rule** kills a
  single-unit + single-project plan → land the milestone as `bookrec` code+tests, defer `project-01` (#3); encode
  hygiene minima (#4); ship a **seeded random baseline path** w/ analytic expected hit-rate@k (#5); use the
  generator's **per-reader temporal split** (val now, test sealed) + teach leakage + `exclude=seen` (#6); reconcile
  recall@k double-introduce + fold catalog concepts (#7); name the data-access idiom (#8); ASCII diagram (#9);
  `load_catalog` returns dict not a frame (#10).
- **[glm]:** skipped.
- **Outcome:** NOT consensus (2 REJECT). **v2 folds every Must + Should above.** Round 2 pending.
### Round 2 (on v2)
- **[self]:** _(pending)_ · **[sol]:** _(pending)_ · **[fable]:** _(pending)_ · **[glm]:** skipped.

## Content Review
_(4-way, pre-PR — pending; reviewers blind-solve the exercises + review the lesson for project-first/engagement/
audience-appropriateness per the book's declared baseline; the `bookrec` code gets conventional code review.)_

## Post-Execution Report
_(pending)_

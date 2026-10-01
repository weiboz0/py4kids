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

All four are **`kind: technique`** (so `concept_scan` never treats them as flaggable syntax features) with a valid
`category` (`catalog-search` → `search`). All four are globally unique vs every registered book (confirmed). `requires`/`practices` for the
Unit-1 entry are **both `[]`** (it is the first entry — nothing earlier to require/practice; assumed-baseline ids
are used as given and earn no credit, never listed in `practices`). `requires` may list earlier-introduced ids only
once later units exist.

## Phases

### Phase 0 — tooling: assumed library methods for a `baseline.yaml` book (NEW — the round-2 blocker)
`concept_scan`'s legacy (map-v1) path (`_legacy_scan_findings`) emits `FAIL: untaught method <m>` for any
`x.<m>(...)` whose name is not in `TAUGHT_METHODS` and not a `def` in the entry; `known_baseline` widens only the
*concept* set, not methods. So a numpy/pandas/math/`bookrec` notebook cannot pass `concept-scan` (verified:
`read_csv`, `groupby`, `default_rng`, `comb` all flag). Encode design 011 §4's "assumed library API" as tooling:
- extend `recsys/curriculum/baseline.yaml` + its loader (`tools/books.py`) with an OPTIONAL assumed **library-method
  allowlist** — a `library_methods: [...]` list (plain method names, e.g. `read_csv, groupby, default_rng, comb,
  to_frame, ...`), validated **fail-closed** (absent = today's behavior);
- subtract it from the untaught-methods set in BOTH `tools/concept_scan.py` `_legacy_scan_findings` AND the v2 path
  (so it also serves future v2 books); keep `dependency_baseline`/`known_baseline` semantics intact.
- group-free tests in `tests/` (extend `tests/test_assumed_baseline.py` with a library-method scan fixture:
  declared methods pass, an UNdeclared library method still FAILs).
Dispatched as tooling (codex per the AGENTS.md table). Then `recsys/curriculum/baseline.yaml` declares exactly the
library methods Unit-1's notebooks use.
**Verify:** a representative Unit-1 cell passes `concept-scan` only with its methods declared; undeclared library
methods still FAIL; group-free `tests/` green.

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
- **[self]:** APPROVE (v2 folds every round-1 Must + Should).
- **[sol]:** APPROVE — all 6 round-1 findings RESOLVED (practices/syllabus; bookrec-code milestone avoiding the
  capstone rule; lesson Opus-dispatch + ≥6 exercises/≥2 stretch/≥3 asserts; real catalog schema; top-k-ranking-metrics
  split; pre-merge-guard --pr + buildout holds); no new findings.
- **[fable] (run 1, a9a640):** APPROVE WITH NITS — v2 resolves every round-1 Must; nits folded below. **Missed the
  concept-scan blocker.**
- **[fable] (run 2, independent, ace3d65):** **REJECT** — one new BLOCKER, empirically verified: for a **map-v1**
  book, `concept_scan._legacy_scan_findings` emits `FAIL: untaught method <m>` for every `x.m(...)` not in
  `TAUGHT_METHODS` and not a `def` in the entry, and `known_baseline` widens only the *concept* set, not methods.
  Confirmed by orchestrator probe: `pd.read_csv`, `df.groupby`, `np.random.default_rng`, `math.comb` all flag →
  Unit-1's numpy/pandas/bookrec notebooks cannot pass `ci-local` step 4. No tooling allows library methods for a
  baseline-declaring book. (recsys-001 was vacuously green — no notebooks.) This is design 011 §4's "assumed
  library API" with no tooling encoding yet.
- **[glm]:** skipped.

### Plan-review outcome (round 2): **NOT consensus — [fable] REJECT (concept-scan library-method blocker).**
Process correction: the orchestrator prematurely recorded a "[fable] APPROVE WITH NITS / CONSENSUS" line and
launched a Session-1 build before both [fable] runs returned; that was wrong — the build was **cancelled** and the
verdict record corrected. **v3 adds Phase 0 (tooling)** to encode assumed library methods for a `baseline.yaml`
book, folds the remaining nits, and goes back for a **round-3** re-review before any build. No implementation until
round-3 consensus.
### Round 3 (on v3 — adds Phase 0 tooling + folded nits)
- **[self]:** APPROVE (Phase 0 closes the blocker; nits folded).
- **[sol]:** APPROVE WITH NITS — Phase 0 is the right minimal fix (subtract the validated allowlist in BOTH the
  legacy and v2 untaught-attribute-call sets; `known_baseline` unchanged); no new blocker; v3 implementable to green
  ci-local. Two refinements folded: (a) `library_methods` is an allowlist of **attribute-call terminal names** (incl.
  module functions / qualified constructors — `read_csv`, `default_rng`, `comb`, `groupby`, `load_catalog`);
  malformed/non-identifier/duplicate entries → `BaselineConfigError`; test BOTH map-v1 AND map-v2 paths. (b) The
  random-baseline expectation is **`= k/N` exactly** for one relevant item (not ≈); empirical only approximates it.
- **[fable] (independent):** APPROVE WITH NITS — no new blocker; verified Phase 0 closes the blocker empirically
  under BOTH map versions (only the declared library methods are flagged, zero spurious concept findings); all
  round-2 nits folded; v3 implementable to green ci-local with buildout kept. Nits folded below.
- **[glm]:** skipped.

### Plan-review outcome: **CONSENSUS on v3** — [self] APPROVE · [sol] APPROVE WITH NITS · [fable] APPROVE WITH NITS · [glm] skipped
No open blockers. Gate CLOSED (3 rounds). Implementation proceeds: **Phase 0 first** (it makes the notebooks
CI-passable), then Phases A/D/B/C, then solutions (separate session), teacher-notes inline, verify, content gate.

### Phase 0 implementation specifics (folded [sol]+[fable] round-3 nits — binding)
- New accessor **`assumed_library_methods(root, book) -> set[str]`** in `tools/books.py`: the `library_methods`
  value is a list of unique **identifier strings**, validated **fail-closed** (non-list / non-string / non-identifier
  / duplicate → `BaselineConfigError`). `assumed_baseline()` stays **ids-only** (so `curriculum.py` consumers are
  untouched).
- The baseline.yaml exact-key check `set(data) != {"baseline_version","entries"}` (`tools/books.py:119`) must be
  widened to ADMIT the optional `library_methods` (keep it exact-set, just add the allowed optional key — do NOT
  loosen to "superset"), and the existing test expectation
  `tests/test_assumed_baseline.py` ("keys must be exactly ['baseline_version','entries']") must be UPDATED to match.
- Subtract `assumed_library_methods` from the untaught-methods set in BOTH scan paths — right after the legacy
  `methods -= defined_names` (`concept_scan.py:~1035`) and the v2 equivalents (`~1269`, `~1445`). It covers **every
  `x.name(...)` attribute-style call** (object methods AND module functions / constructors — `pd.DataFrame`,
  `bookrec.Candidate`, `np.mean`, `math.comb`, `read_csv`, `groupby`, `default_rng`, `hit_rate_at_k`, and `split`);
  bare from-import calls (`load_catalog(...)`, `rank(...)`) and non-call attribute access (`df.shape`, `.str`) are
  never flagged. Tests exercise BOTH map-v1 AND map-v2 (declared → pass; undeclared library method → still FAIL).
- `recsys/curriculum/baseline.yaml` groups `library_methods` by library with comments (for gate review).
- `bookrec.data.generated_dir()`: prefer **fail with a clear message** if the generated slice is absent (ci-local
  regenerates it in step 2 before exec) over fragile in-package regeneration (the `recsys/data/gen_*.py` are not a
  package); a subprocess regen is an acceptable alternative. Random-baseline expectation is **`= k/N`** (exact, r=1).

## Implementation notes (folded [fable] round-2 nits — binding on the authors)
- **Dispatch (settled):** content authoring goes to **`codex:codex-rescue` (GPT-5.6-sol)** per the AGENTS.md table
  (codex credits restored): lesson + exercise STATEMENTS in one fresh session; SOLUTIONS in a SEPARATE fresh
  session; the `bookrec` `search.py`/`scoreboard.py` + tests as tooling (codex); teacher-notes inline. (If codex is
  unavailable, substitute an Opus subagent in the real env — as recsys-001 did.) This supersedes the earlier
  "Opus subagent" wording in Phases B/C.
- **Data-access idiom:** notebooks execute with cwd = the unit dir, and the data is the gitignored
  `recsys/data/generated/{catalog,interactions}.csv.gz` (ci-local regenerates it in step 2, before step-3 exec).
  Add a single `bookrec` path helper (e.g. `bookrec.data.generated_dir()` resolving the repo `recsys/data/generated/`
  and regenerating deterministically if absent) so all three notebook authors use ONE idiom; the lesson tells
  students to run the generators first.
- **Random-baseline analytics (exact):** expected hit-rate@k over N unseen items with r val-positives is
  `1 − C(N−r,k)/C(N,k)` (≈ k/N only when r = 1 — state the condition). Exclude readers with zero val-positives and
  all cold readers (all-`test`) from the scoreboard mean (else the floor is biased low). The random path must sample
  k from the UNSEEN set inside `retrieve` (so `rank(exclude=seen)` doesn't drop it below k and break the
  empirical≈analytic check). Use `numpy.random.default_rng(seed)` (not stdlib `random`).
- **`bookrec` deps:** `recsys/projects/bookrec/pyproject.toml` currently declares only numpy and `catalog.py` is
  stdlib `csv`+`gzip`. If `search.py`/`scoreboard.py` use pandas, add `pandas` to bookrec's deps; otherwise stay
  stdlib.
- **Handout glyphs:** `build-pdf.sh` renders `exercises.ipynb` (and `syllabus.md`) as the handout, so the ASCII-only
  (no box-drawing) rule applies most to the EXERCISES notebook/syllabus (keep ASCII everywhere anyway).
- **`Book` schema coercion:** `Book` exposes only `item_id`/`title` as attributes; `author_id`/`genres`/`year` live
  as STRINGS in `Book.fields` (`genres` is `;`-joined, `year` is e.g. `"1987"`). The lesson's dict→DataFrame view
  must coerce types (split genres, int the year) — state it for the authors.
- **Library-method declaration:** every library/`bookrec` METHOD the notebooks call (`.read_csv`, `.groupby`,
  `.default_rng`, `.comb`, `.to_frame`, etc.) must be in Phase 0's `baseline.yaml library_methods` allowlist, or
  `concept-scan` fails — authors keep that list in sync with the cells they write.

## Content Review
Pre-PR gate on commit `35613b0` ([glm] skipped). Both externals blind-solved all 8 exercises (matched) and
code-reviewed the Phase-0 tooling + `bookrec` (both: fail-closed, correct).
### Round 1
- **[self]:** APPROVE WITH NITS — ci-local/guard green; content matches the consensus plan; deferred to the external
  blind-solves for independent correctness.
- **[sol]:** REJECT — M1 scoreboard relevance includes train-seen val-positives (unrecommendable → biases metrics;
  15/369 overlap, 1 reader zero recommendable) + the test misses it; M2 Exercise 5 assesses an undeclared data
  contract (positive=`label==1`, interaction columns, non-cold reader) never taught in the lesson; S3 Ex1
  `author_id` type ambiguity; S4 handout headings use em-dashes vs the ASCII rule.
- **[fable] (independent):** APPROVE WITH NITS — no wrong answers/leakage; strong Should: the real validation
  scoreboard renders **0.0/0.0** (seed 2026 unlucky; hit@10≈0.0085), making the lesson's climax + Exercise 8
  vacuous (CI green only because the solution asserts `readers>0`); = [sol] M1 (relevance⊄unseen); + title-placeholder
  clarity + polish (split-table order, temporal-invariant assert, Ex7 derivation, a non-zero-hit regression test).
- **Outcome:** NOT consensus ([sol] REJECT). Folding the union via codex (relevance−=seen + overlap/non-zero tests;
  non-zero demo floor + analytic expectation; teach the interaction schema/label/cold rule before Ex5; author_id
  clarity; placeholder-titles note; ASCII headings; polish) → re-verify ci-local → round-2 re-review.
### Round 2
- **[self]:** _(pending)_ · **[sol]:** _(pending)_ · **[fable]:** _(pending)_ · **[glm]:** skipped.

## Post-Execution Report
_(pending)_

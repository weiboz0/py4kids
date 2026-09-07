# Plan 007 — Project 01 Arcade Night Implementation Plan

**Goal:** Ship `project-01-arcade-night` — Term 2's milestone build where students combine functions, loops, conditionals, and randomness into their own mini-arcade — and establish the PROJECT pipeline (conventions + `tools/` checks) the year's second project (the capstone) will reuse.

**Architecture:** Projects are a new content KIND (like checkpoints were in plan 005): a multi-lesson guided BUILD, `introduces: []`, integrating prior concepts. New first-class conventions mirroring units/checkpoints (student-facing brief, a reference solution, map-equal manifest, teacher notes with a rubric) and `tools/` checks extended from unit+checkpoint to also cover projects. ONE map amendment rides along (gate round 1, sol #5) — the SAME systemic plan-002 under-specification fixed for unit-04 (plan 005) and checkpoint-02 (plan 006): project-01's `requires ∪ practices` omits `variable`, `arithmetic`, `int-type`, yet a running score and returned point values inherently need them; `practices` gains those three (variable from unit 01, arithmetic/int-type from unit 02; verified green). The redundant `random-module` in both `requires` and `practices` is harmless and stays as-is (no invariant inspects `requires ∩ practices`; verified) — not a "correction", just mirrored verbatim.

**Spec:** design 000 §1–§3 (`projects/` in the tree); `book1/curriculum/coverage-map.yaml` (binding); plan 004/005 conventions; plan 003/006 tooling; D-001, D-002.

## Global Constraints

- **Project conventions (binding on all Book 1 projects, new):**
  - Directory `book1/projects/<map-id>/` with `manifest.yaml`, `brief.ipynb`
    (student-facing), `solutions.ipynb` (reference build), `teacher-notes.md`.
  - `manifest.yaml`: unit schema with `kind: project`; `concepts` EQUAL the map entry
    (the map already sets `introduces: []`).
  - `brief.ipynb`: the build spec — markdown milestones + a requirements checklist +
    scaffolding/starter code cells the student extends; NO full solution, NO executed
    outputs; `input()` allowed. Uses only concepts in the entry's `requires ∪ practices`.
    Milestones are markdown headings matching `^## Milestone \d+` (3–6). NO stretch tag
    requirement — a project is differentiated by its "make it your own" extensions, stated
    in a `## Make it yours` markdown section, not by tagged cells.
  - `solutions.ipynb`: ONE complete reference game proving a compliant build exists from the
    taught concepts. Runs headless; the unit solution conventions verbatim (no `input()`,
    `import random` only + `random.seed(4)` — placed in the FIRST code cell ABOVE any `def`
    that uses random, since the seed-order check reads source position not call order
    (glm #1); no GUI, self-contained, ≥3 non-vacuous asserts, scaffolding note).
    **Headless reference design (binding, sol #1 / fable F1 / gate round-2) — the ONLY
    in-budget shape:** the solution contains NO `input()` anywhere. The interactive
    input-driven menu lives ONLY in the brief; the solution defines each game function to
    take the player's choice/guess as a PARAMETER (or be pure-random), returns points, and
    an EXECUTED driver (straight-line or `while`) calls those functions with fixed sample
    arguments, accumulates the score, and asserts outcomes. Do NOT script an input SEQUENCE
    with a list or string-indexing — neither is in project-01's `requires ∪ practices`
    (amended), so it is OUT OF THE CONCEPT BUDGET (not a claim about teaching order:
    `for-loop` is unit 03, `string-index` unit 06, lists unit 07 — the point is none is in
    THIS entry's union). Whether the solution "defines and calls the brief's required
    functions" is a REVIEWER duty (no mechanical check); the mechanical floor is only: ≥1
    `def`, headless execution, ≥3 non-vacuous asserts, the pattern/seed bans.
  - `teacher-notes.md`: the five unit headings PLUS `## Rubric` (milestone-by-milestone
    "what done looks like", the minimum bar vs. stretch, how to run the 2-lesson build and
    the class showcase, how to assess a student's OWN game not a fixed answer key).
- All plan-004 solution executable rules apply to `solutions.ipynb` (per-line pattern bans,
  seed ordering, non-vacuous asserts). Turtle is NOT in project-01's concepts, so no assets.
- Process (standing): no commits while a `[sol]` review is in flight; codex content-gate
  prompts name the in-process fallback and avoid bare CLI-flag-like tokens; turtle N/A here.

## Out of scope

Content plan → Phase D is the mandatory named verification phase. Out of scope: the capstone
(project 02) and units 06+ (later plans); PDF handouts for the project; auto-grading (D-002 —
projects are assessed manually against the rubric); any map edit BEYOND the project-01
practices amendment in Phase B; turtle anything.

## Phases

Dispatch per AGENTS.md: project tooling via codex; brief statements via codex; the reference
SOLUTION via a SEPARATE blind codex session (finished brief only); teacher/rubric notes
inline; manifest inline.

### Phase A — project support in tools (TDD, codex)

**Files:** `tools/notebooks.py`, `tools/checks.py`, `tools/cli.py`, `tests/test_tools.py`.
1. `project_dirs(root, book, ident=None)` mirroring `checkpoint_dirs` (fail-closed on missing
   book/projects dirs; empty `projects/` = N=0 pass — the real book's `projects/` holds only
   `.gitkeep`, so existing checks stay green).
2. Checks extended to the project scope:
   - layout (project file set: manifest/brief/solutions/teacher-notes);
   - manifest map-equality with `kind: project`;
   - brief hygiene (no solutions, no outputs in code cells; broken/starter snippets that
     shouldn't run ride in markdown fences, same as checkpoints). IMPLEMENTATION NOTE
     (fable F4): `hygiene_findings`'s kind→notebook map is currently BINARY (unit→exercises
     else checkpoint) — make it THREE-WAY so a project targets `brief.ipynb`, not
     checkpoint.ipynb;
   - milestone structure (`^## Milestone \d+` count 3–6, sequential 1..N; a `## Make it yours`
     section present); NO stretch check;
   - solutions structure: ≥3 non-vacuous asserts, pattern/seed bans, self-contained,
     executes headless — but NO milestone-mirror (projects aren't Q&A);
   - teacher-notes: the five unit headings PLUS `## Rubric` (six total);
   - the project prefix rule (existing project dirs = first K project map entries, in order);
   - cell-lint covers `brief.ipynb` + `solutions.ipynb` code cells.
   UNIT/CHECKPOINT-only checks (stretch, no-exec, turtle, question-count) do NOT apply to
   projects.
3. CLI `--unit <id>` selector extends to `project-*` ids (structure/hygiene/manifest/
   exec-solutions/cell-lint accept them; inapplicable checks exit 2), mirroring the plan-005
   checkpoint matrix.
4. One-fault fixtures for every NEW project rule (layout each file, manifest kind/equality,
   brief hygiene, milestone count both directions + sequence, missing `## Make it yours`,
   solutions assert-floor/bans/seed, `## Rubric` heading, project prefix gap+orphan,
   fail-closed missing-root/dir/target) AND the `--unit project-*` selector matrix cases
   (sol #2: a `project-*` id on a project-applicable check → scoped run; on an
   inapplicable check → exit 2; a missing project id → exit 1; a neither-prefix id →
   unit scope exit 1) from a generated valid project. Nothing broken committed. The
   fixture-factory baseline gains an empty `projects/` dir PLUS one valid project directory
   map-equal to the fixture map's EXISTING `project-02-grand-adventure` entry (sol #3 /
   fable F4 — no new fixture-map entry needed); this baseline change lands in the same
   change as `content_dirs` enumerating projects, or `test_generated_baseline_passes_each_check`
   breaks. Parity: all existing unit + checkpoint checks and their tests unchanged; no new
   check NAMES (projects reuse the extended checks, so the registry/6-step pins stay green).
- **Acceptance:** `uv run pytest -q` green (new fixtures pass; existing unchanged);
  `ci-local.sh` ALL GREEN with the project checks live.

### Phase B — map amendment + manifest

1. **Map amendment (inline):** append `variable, arithmetic, int-type` to
   `project-01-arcade-night.practices` (sol #5; verified green against every curriculum
   invariant). Apply surgically to keep a clean diff (do NOT round-trip the whole file
   through a YAML dumper — it reflows every entry). Nothing else in the map changes.
2. **Manifest (inline, lands with content):**
   `book1/projects/project-01-arcade-night/manifest.yaml`, map-equal to the AMENDED entry
   (`kind: project`, `introduces: []`, requires/practices verbatim incl. the redundant
   `random-module`). Lands in the same commit as the complete directory.
- **Acceptance:** amendment green with `ci-local` before content; manifest passes
  `manifest-check` in the project scope.

### Phase C — project-01-arcade-night content

Blueprint (requires def-function/parameters/return-value/while-loop/if-statement/random-module;
AMENDED practices print/input/f-string/accumulator/logical-ops/loop-counter/elif-else/
break-statement/comparison/scope/import-statement/variable/arithmetic/int-type):
- Hook: ARCADE NIGHT — build a mini-arcade of 2–3 games the class plays on each other's.
- brief.ipynb, 3–6 milestones (~2 lessons): M1 a menu loop (`while` + input choice + `break`
  to quit); M2 game one as a FUNCTION returning points (a guess/luck game using
  `random.randint`); M3 game two as another function (a quick quiz or higher-lower using
  logical-ops/elif); M4 a running total across games (accumulator + f-string scoreboard,
  loop-counter for rounds played); a `## Make it yours` section (add a third game, a
  high-score message, a difficulty toggle). A requirements checklist ("your arcade must:
  use at least two game functions that RETURN points, keep a total score, let the player
  quit"). Starter scaffold cells with `input()` are fine (student-facing).
- solutions.ipynb: proves the arcade LOGIC works headlessly. It contains NO `input()`
  ANYWHERE (glm/sol round-2 blocker: the no-input scan is a source scan over every code cell,
  so even an unexecuted menu `def` with `input()` in its body fails — the interactive menu
  belongs only in the brief). Instead the solution defines the two parameterized game
  functions (each takes the player's guess/choice as an argument, returns points, uses
  `random.randint` seeded in the first cell) and an EXECUTED driver — a straight-line or
  `while` sequence that CALLS the game functions with fixed sample arguments, accumulates the
  score, and asserts the final score and each function's returned points. This mirrors how
  unit-02's guessing-game solution replaces `input()` with assigned sample values.
- Teacher notes + `## Rubric`: minimum bar (two returning game functions + a working total +
  a quit path) vs. stretch (a third game, high-score, difficulty); how to run the 2-lesson
  build (design → build → showcase), how to grade a student's OWN arcade against the rubric,
  differentiation, the class-showcase logistics. PACING CUT (glm #2 / fable F7): the `## Pacing`
  section pins the minimum bar to END OF LESSON 1 (menu + one returning game + a total),
  with the second game, `## Make it yours` extensions, and the showcase in lesson 2 — so a
  mixed-ability class always finishes a playable arcade.

### Phase D — Verification (NAMED, mandatory)

Mechanical: full pytest green (incl. new project one-fault fixtures); `ci-local.sh` ALL GREEN
(project checks in steps 3–4); the reference solution executes with non-vacuous asserts;
manifest map-equal.
Reviewer duties (explicit — several conventions are reviewer-only, no mechanical check,
fable F6): run the brief's requirements checklist LINE-BY-LINE against the reference
solution (glm #3), confirming it defines AND exercises the required functions; the reference
arcade uses only the AMENDED requires ∪ practices concepts — NO lists/dicts/classes/
string-methods/for-loops-as-scripting (the trap of F1); it is non-vacuous and buildable by a
student who finished unit 05; the brief's milestones are achievable in 2 lessons with the
min bar reachable by end of lesson 1; the rubric is usable to assess DIFFERENT student
arcades (not a fixed key); hook-first; `## Make it yours` gives real, taught-concept-only
extensions; age-appropriateness.

**Acceptance criteria:** the project directory is complete; `uv run pytest -q` green;
ci-local ALL GREEN; content gate 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE — project pipeline mirrors the shipped checkpoint pattern; conventions and tooling extension enumerated; named verification present.

### Review 2 — [glm] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (no blockers; confirmed fixture map already has project-02 entry, redundant random harmless, no list smuggled)
1. `[FIXED]` Seed-before-def source-order trap — pin seed in the first cell above any random-using def.
2. `[FIXED]` 2-lesson pacing tight — encode a min-bar-by-lesson-1 cut.
3. `[FIXED]` "Solution defines+calls required functions" has no proxy — assign it as an explicit Phase-D checklist reviewer duty.

### Review 3 — [fable] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (deep trace; redundant-random and closure mechanically confirmed)
1. `[FIXED]` (F1, should-fix) Headless reference-solution under-specified and collides with the no-list/no-for budget — pin the parameterized design (game funcs take choice as parameter, assert via direct calls, menu defined-not-executed; list/for/string-index forbidden as scripting).
2. `[FIXED]` (F2) Phase E→D text bug.
3. `[FIXED]` (F4) `hygiene_findings` binary kind→notebook map must go three-way for brief.ipynb; fixture baseline ties to content_dirs change.
4. `[NOTED]` (F6/F7) some conventions reviewer-only (stated in Phase D); pacing ambitious (cut added).

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT
1. `[FIXED]` (Major) "Solution defines+calls required functions" not mechanically specified — clarified as reviewer-only; mechanical floor stated.
2. `[FIXED]` (Major) `project-*` selector matrix absent from the one-fault inventory — added.
3. `[FIXED]` (Nit) Name the fixture project — `project-02-grand-adventure` (already in fixture map).
4. `[FIXED]` (Nit) "Correction" wording misleading — reworded (now a real amendment + a verbatim-mirror note).
5. `[FIXED]` (Blocker) requires ∪ practices omits variable/arithmetic/int-type the score needs — map amendment adds them to practices (verified green).
6. `[FIXED]` (Nit) Phase E→D in out-of-scope.

### Revision 2 (2026-09-06)
All round-1 findings applied; the project-01 substrate amendment verified green in /tmp before drafting; this is the THIRD entry (unit-04, checkpoint-02, project-01) with the same plan-002 substrate gap — flagged in the post-execution follow-ups for a proactive audit of units 06–10 / checkpoints 03–04 / project 02.

### Round 2 (2026-09-06)
- **[fable]**: APPROVE WITH NITS — all round-1 items verified resolved; amendment re-verified green (280 tests); amended union covers the scored arcade with no gap. Nit: `variable` attribution (unit 01 not 02) — `[FIXED]`.
- **[glm]**: REJECT — round-1 items confirmed fixed, but rev2 introduced two contradictions + a false rationale.
- **[sol]**: REJECT — 5 of 6 confirmed resolved; the headless design became internally contradictory.
  1. `[FIXED]` (glm/sol blocker) Out-of-scope still said "any map edit" while Phase B performs one → "beyond the project-01 practices amendment in Phase B".
  2. `[FIXED]` (glm/sol blocker) "menu DEFINED but not executed" conflicts with the source-scan no-`input()` check (an unexecuted def with input() still fails) → the solution now contains NO input() anywhere; the interactive menu is brief-only; the solution defines parameterized game functions + an EXECUTED driver calling them with fixed values (mirrors unit-02's solution).
  3. `[FIXED]` (glm should-fix) False "untaught until 07+" rationale (for-loop is unit 03, string-index unit 06) → reframed as the concept-BUDGET justification (none in this entry's union).
  4. `[FIXED]` (glm nit) Phase C blueprint union not updated with the amended practices; Phase C solutions line still said "scripted choices replace input" → both corrected.
  5. `[FIXED]` (fable/glm nit) `variable` unit-01 attribution.

### Round 3 (2026-09-06)
- **[sol]**: APPROVE — the headless no-input design, Phase C union, and out-of-scope all internally consistent.
- **[glm]**: APPROVE — all five verified against HEAD; no remaining contradiction.

### Gate result (2026-09-06)
- `[self]` APPROVE · `[sol]` APPROVE (round 3) · `[glm]` APPROVE (round 3) · `[fable]` APPROVE WITH NITS.
- Full consensus, no `[OPEN]` items — **gate PASSED; approval to implement.**

## Content Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE — clean concept sweep (no input/list/for in the solution), hook-first, 329 tests, ci-local ALL GREEN.

### Review 2 — [fable] (2026-09-06)
- **Verdict**: APPROVE WITH NITS — requirements checklist satisfied line-by-line; closure clean; tooling parity confirmed; selector matrix 0/2/1.
1. `[FIXED]` Reference driver's quit branch was dead (loop exited on the counter). → driver rewritten as `while True` with the `q` else-branch as the genuine exit; quit path now exercised.
2. `[WONTFIX]` Conditional-expression assert in a fixture reads non-obviously. → style-only; left as-is.

### Review 3 — [glm] (2026-09-06)
- **Verdict**: (no verdict — the opencode forwarder returned no output). Re-dispatched on the fixed tree in round 2.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT
1. `[FIXED]` (Blocker) Quit not exercised (= fable #1). → driver rewritten.
2. `[WONTFIX-misread]` (Blocker) "`## Rubric` absent from brief" — by design the `## Rubric` is a TEACHER-NOTES heading (present); the brief carries a student-facing `## Requirements` checklist. Underlying concern (student-facing criteria unenforced) addressed by #5.
3. `[FIXED]` (Major) Rubric granted full credit for ONE game while the brief requires TWO. → rubric reworked: two games = meets the brief (full credit); one game = a celebrated "developing" floor for strugglers, explicitly below the spec.
4. `[FIXED]` (Major) Pacing (one game + total by lesson 1) conflicted with the brief's milestone order (total is M4, after game two). → pacing rewritten to the brief's order: lesson 1 = M1–M2 (menu + one returning game), lesson 2 = M3–M4 + extensions.
5. `[FIXED]` (Blocker) Brief requirements checklist not mechanically enforced. → `project_milestone_findings` now requires a `## Requirements` heading in the brief; +fixture; fixture-factory baseline brief gains one.
6. `[FIXED]` (Blocker) Non-vacuous assert check missed executable tautologies (`1 == 1`, `x == x`, `not False`). → `_is_tautology` now rejects bare constants, `not <constant>`, and same-node/constant comparisons; +fixture; verified no real solution assert regresses.

## Post-Execution Report

(written before shipping.)

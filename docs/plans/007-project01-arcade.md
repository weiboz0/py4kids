# Plan 007 — Project 01 Arcade Night Implementation Plan

**Goal:** Ship `project-01-arcade-night` — Term 2's milestone build where students combine functions, loops, conditionals, and randomness into their own mini-arcade — and establish the PROJECT pipeline (conventions + `tools/` checks) the year's second project (the capstone) will reuse.

**Architecture:** Projects are a new content KIND (like checkpoints were in plan 005): a multi-lesson guided BUILD, `introduces: []`, integrating prior concepts. New first-class conventions mirroring units/checkpoints (student-facing brief, a reference solution, map-equal manifest, teacher notes with a rubric) and `tools/` checks extended from unit+checkpoint to also cover projects. One small correction rides along: project-01's map entry lists `random-module` in BOTH `requires` and `practices` (redundant) — but the map is the binding contract and this is harmless (a concept can be required and practiced), so NO map edit; the manifest mirrors it as-is.

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
    `import random` only + `random.seed(4)` before first use, no GUI, self-contained,
    ≥3 non-vacuous asserts, scaffolding note); it need NOT mirror milestone headings
    (a project isn't Q&A) but MUST define and call the functions the brief requires and
    assert on the game's computed outcomes (final score, a decided round).
  - `teacher-notes.md`: the five unit headings PLUS `## Rubric` (milestone-by-milestone
    "what done looks like", the minimum bar vs. stretch, how to run the 2-lesson build and
    the class showcase, how to assess a student's OWN game not a fixed answer key).
- All plan-004 solution executable rules apply to `solutions.ipynb` (per-line pattern bans,
  seed ordering, non-vacuous asserts). Turtle is NOT in project-01's concepts, so no assets.
- Process (standing): no commits while a `[sol]` review is in flight; codex content-gate
  prompts name the in-process fallback and avoid bare CLI-flag-like tokens; turtle N/A here.

## Out of scope

Content plan → Phase E is the mandatory named verification phase. Out of scope: the capstone
(project 02) and units 06+ (later plans); PDF handouts for the project; auto-grading (D-002 —
projects are assessed manually against the rubric); any map edit; turtle anything.

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
     shouldn't run ride in markdown fences, same as checkpoints);
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
   solutions assert-floor/bans/seed, `## Rubric` heading, project prefix, fail-closed
   missing-root/dir/target) from a generated valid project; nothing broken committed; the
   fixture-factory baseline gains an empty `projects/` + one valid project (map-equal to a
   fixture project entry). Parity: all existing unit + checkpoint checks unchanged.
- **Acceptance:** `uv run pytest -q` green (new fixtures pass; existing unchanged);
  `ci-local.sh` ALL GREEN with the project checks live.

### Phase B — manifest (inline, lands with content)

`book1/projects/project-01-arcade-night/manifest.yaml`, map-equal (`kind: project`,
`introduces: []`, requires/practices verbatim from the map incl. the redundant
`random-module`). Lands in the same commit as the complete directory.

### Phase C — project-01-arcade-night content

Blueprint (requires def-function/parameters/return-value/while-loop/if-statement/random-module;
practices print/input/f-string/accumulator/logical-ops/loop-counter/elif-else/break-statement/
comparison/scope/import-statement):
- Hook: ARCADE NIGHT — build a mini-arcade of 2–3 games the class plays on each other's.
- brief.ipynb, 3–6 milestones (~2 lessons): M1 a menu loop (`while` + input choice + `break`
  to quit); M2 game one as a FUNCTION returning points (a guess/luck game using
  `random.randint`); M3 game two as another function (a quick quiz or higher-lower using
  logical-ops/elif); M4 a running total across games (accumulator + f-string scoreboard,
  loop-counter for rounds played); a `## Make it yours` section (add a third game, a
  high-score message, a difficulty toggle). A requirements checklist ("your arcade must:
  use at least two game functions that RETURN points, keep a total score, let the player
  quit"). Starter scaffold cells with `input()` are fine (student-facing).
- solutions.ipynb: ONE complete arcade — two game functions returning points, a scored menu
  loop — made HEADLESS (scripted choices replace input, `random.seed(4)`), asserting the
  final score for a fixed play-through and that a game function returns the expected points.
- Teacher notes + `## Rubric`: minimum bar (two returning game functions + a working total +
  a quit path) vs. stretch (a third game, high-score, difficulty); how to run the 2-lesson
  build (design → build → showcase), how to grade a student's OWN arcade against the rubric,
  differentiation, the class-showcase logistics.

### Phase D — Verification (NAMED, mandatory)

Mechanical: full pytest green (incl. new project one-fault fixtures); `ci-local.sh` ALL GREEN
(project checks in steps 3–4); the reference solution executes with non-vacuous asserts;
manifest map-equal.
Reviewer duties: the reference arcade genuinely satisfies the brief's requirements checklist
and uses only requires ∪ practices concepts (no lists/dicts/classes); it is non-vacuous and
buildable by a student who finished unit 05; the brief's milestones are achievable in 2
lessons; the rubric is usable to assess DIFFERENT student arcades (not a fixed key); hook-first;
`## Make it yours` gives real, taught-concept-only extensions; age-appropriateness.

**Acceptance criteria:** the project directory is complete; `uv run pytest -q` green;
ci-local ALL GREEN; content gate 4-way consensus.

---

## Plan Review

(4-way gate verdicts land here.)

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)

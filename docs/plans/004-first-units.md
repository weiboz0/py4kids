# Plan 004 — First Units (01–03) Implementation Plan

**Goal:** Ship Book 1's first three units — `unit-01-story-machine`, `unit-02-number-detective`, `unit-03-turtle-art-studio` — complete (manifest, lesson, exercises, solutions, teacher notes) and proven through the content gate, establishing the unit pipeline every later unit follows.

**Architecture:** Each unit is a directory under `book1/units/` per design §1. Content is authored per the AGENTS.md dispatch table (statements via GPT-5.6-sol, solutions via a SEPARATE fresh GPT-5.6-sol session that never sees the statement outlines, teacher notes inline). Verification is a new planning-level pytest module (`tests/test_book1_units.py`) enforcing manifest/map agreement, student-notebook hygiene, stretch presence, and headless solution execution — promoted into `tools/` by plan 003.

**Spec:** `docs/designs/000-project-design.md` (§1–§3, First milestones item 4), `book1/curriculum/coverage-map.yaml` (the binding arc), plan 002's post-execution follow-ups.

## Global Constraints

- Numbering note: this plan takes number 004 (not the next-free 003) because design 000,
  `TODO.md`, and ci-local's `SKIP (plan 003)` markers already reserve 003 for verification
  tooling; renumbering would break those cross-references. Deviation flagged for the gate.
- The coverage map is the contract: each unit's `manifest.yaml` concept lists must EQUAL the
  map entry's `introduces`/`requires`/`practices` exactly (plan 002 Interfaces).
- Project-first law (D-001): every lesson notebook opens with its hook, never concept drill.
- D-005: turtle work runs as `.py` scripts in `assets/`, launched from the terminal;
  notebooks carry the loop reasoning, predictions, and write-ups.
- Pacing directive (plan 002): units 01–03 teacher notes allocate concepts to specific
  lessons explicitly; units 01–02 exercise sets stay short.
- Plan 002 gate follow-ups: unit 02 exercises deliberately practice reading error messages;
  unit 03 leans on `float-type` where `360/n` demands it; no `ord`/`chr` anywhere
  (ciphers are unit 06's problem, but the registry boundary binds all statements).
- **Executable conventions (binding on all Book 1 content):**
  - Student-facing notebooks (`exercises.ipynb`): NO solutions, NO executed outputs,
    `input()` allowed; at least one exercise cell tagged `stretch` (heading "Challenge").
  - `solutions.ipynb`: runs top-to-bottom headless — never calls `input()` (uses assigned
    sample values, stated inline), seeds randomness with `random.seed(4)`, imports no GUI
    (turtle solutions live in `assets/*.py`, not executed by CI until plan 003 decides).
  - `lesson.ipynb`: teacher-led; cells that require interaction or a GUI carry the cell tag
    `no-exec`; all untagged code cells must execute headless (checked from plan 003 on;
    this plan's reviewers check manually).
- Every `git commit` appends the two mandated trailer lines (shown commands give subjects only).
- The repo is PUBLIC: original content only; provenance `original` in every manifest;
  no student data.

## Out of scope

- Verification tooling in `tools/`/CLI form, PDF build, notebook-cell lint (plan 003) —
  this plan's pytest checks are the interim named verification.
- Units 04+, checkpoints, projects (later plans).
- Executing turtle `assets/*.py` in CI (needs a headless strategy — plan 003 decides;
  until then teacher notes carry a visual checklist).

## Phases

### Phase A — unit verification tests (interim tooling, TDD)

**Files:** `tests/test_book1_units.py`; Create: nothing else.
Checks (all parameterized over every `book1/units/unit-*/` directory present):
1. **Layout:** `manifest.yaml`, `lesson.ipynb`, `exercises.ipynb`, `solutions.ipynb`,
   `teacher-notes.md` all present.
2. **Manifest schema + map agreement:** keys exactly
   `{id, kind, blueprint_version, lessons, concepts, provenance, timing}`;
   `kind: unit`; `blueprint_version: 1`; `provenance: original`;
   `id` equals the directory name and a `coverage-map.yaml` entry;
   `lessons` equals the map entry's; `concepts.introduces/requires/practices` EQUAL the
   map entry's lists (order-insensitive).
3. **Student hygiene:** every cell in `exercises.ipynb` has empty `outputs` and null
   `execution_count`; no cell source matches `(?i)^#+\s*solution` in exercises.
4. **Stretch presence:** ≥1 cell in `exercises.ipynb` carries the `stretch` tag.
5. **Solutions execute:** `solutions.ipynb` runs headless via nbclient (timeout 120s),
   from the unit directory as cwd; forbidden calls: source must not contain `input(` or
   `import turtle`.
6. **Lesson hook rule:** the first markdown cell of `lesson.ipynb` mentions the unit's
   project hook (non-empty markdown before any code cell) — mechanical proxy; the real
   judgment stays with the content gate.
Tests are written FIRST and must fail (no units exist), then pass as units land phase by phase
(the module skips cleanly when no unit directories exist yet — a `pytest.skip` guard — so
Phase A can merge green before Phase B).

**Verification:** `uv run pytest tests/test_book1_units.py -q` green (skipped) pre-content;
green (running) after each unit phase. Commit per phase.

### Phase B — unit-01-story-machine (2 lessons)

**Files:** `book1/units/unit-01-story-machine/{manifest.yaml,lesson.ipynb,exercises.ipynb,solutions.ipynb,teacher-notes.md}`

Blueprint (statements dispatched to codex GPT-5.6-sol with this outline; solutions to a
SEPARATE fresh codex session given only the finished statement notebooks):
- Hook: the teacher runs a ridiculous Mad-Libs story live; students make it theirs.
- Lesson 1 (run-program, print, comment, string-literal, error-messages): run and modify a
  starter story printer; deliberately break it once to read the traceback together.
- Lesson 2 (variable, naming, input, string-concat, f-string): collect words with `input()`,
  assemble the story with f-strings; naming conventions via bad-name comedy.
- Exercises (~6 core + 2 stretch): greeting-card printer, fix-the-error (2 broken snippets),
  story remix with variables, interview bot; stretch: multi-paragraph story reusing
  variables, emoji-art title generator.
- Teacher notes: per-lesson concept allocation (pacing directive), 60–90 min plans,
  common mistakes (quote mismatch, name typos → NameError), discussion prompts,
  differentiation.

### Phase C — unit-02-number-detective (3 lessons)

Same file set under `book1/units/unit-02-number-detective/`.
- Hook: the computer picks a secret number; can you find it in few guesses?
- Lesson 1 (int-type, arithmetic, type-conversion, import-statement, random-module):
  number tricks, `random.randint` demos, str→int conversion of typed guesses.
- Lesson 2 (boolean, comparison, if-statement, elif-else): one-guess detective with
  too-high/too-low/correct verdicts.
- Lesson 3 (while-loop): the full game with a guess counter; debugging session practicing
  error-messages (plan 002 follow-up).
- Exercises (~6 core + 2 stretch): dice roller, higher-or-lower verdict function-free
  snippets, guess-counter tweaks, fix-the-error; stretch: "hot/cold" distance hints,
  computer-guesses-your-number (halving narrative, no formal algorithms).
- Solutions: `random.seed(4)`; sample values replace `input()`.
- Teacher notes: per-lesson allocation across the 3 lessons exactly as the pacing
  directive's example prescribes; short exercise set note.

### Phase D — unit-03-turtle-art-studio (3 lessons)

Same file set plus `assets/` under `book1/units/unit-03-turtle-art-studio/`.
- Hook: command a robot turtle to draw gallery-worthy art (teacher demos a spirograph).
- Lesson 1 (turtle-basics, run-program practice per D-005): first shapes by repeated
  commands in `assets/l1_square.py`, run from the terminal; the pain of repetition
  motivates loops.
- Lesson 2 (for-loop, range-function, loop-counter, turtle-drawing, float-type):
  polygons via `for` + `range`, `angle = 360 / n` (floats arrive because the turtle
  demands them — plan 002 resolution), colors and pen control; `assets/l2_polygons.py`.
- Lesson 3 (nested-loops): spirograph gallery; `assets/l3_spirograph.py`.
- Notebooks: `lesson.ipynb` carries the reasoning and loop-table predictions (`no-exec`
  tags on any turtle cells — none should import turtle per conventions);
  `exercises.ipynb` has predict-the-drawing, range-value tables, fix-the-loop, and
  design-your-polygon planning tasks (headless); drawing tasks reference the assets
  scripts; stretch: star polygons (angle 720/5), rainbow spiral.
- Solutions: loop/range answers executable headless; turtle answers as
  `assets/solutions_*.py` (not CI-executed; teacher visual checklist in notes).
- Teacher notes: per-lesson allocation (glm follow-up), window-management tips,
  visual checklist for the script outputs.

### Phase E — Verification (NAMED verification phase, design §5)

1. `uv run pytest -q` — full suite green (books + curriculum + units).
2. Solutions notebooks reproduce their stated answers (nbclient execution IS the check;
   any assertion cell failing fails the phase).
3. Manifests validate and EQUAL their coverage-map entries (Phase A test).
4. Student hygiene + stretch presence (Phase A tests).
5. Prereq closure at content level: reviewer duty — statements may use only each unit's
   `introduces` ∪ `requires` ∪ `practices` concepts (mechanical closure exists at map
   level from plan 002; content-level check is manual until plan 003).
6. Difficulty/timing budget: each teacher-notes file states the 60–90 min per-lesson plan;
   reviewers judge fit.
7. `bash scripts/ci-local.sh` — ALL GREEN.

**Acceptance criteria:** all three unit directories complete; every Phase A check green;
ci-local green; content gate (blind-solve roster) reaches 4-way consensus.

---

## Plan Review

(4-way gate verdicts land here.)

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)

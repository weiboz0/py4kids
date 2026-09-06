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
  - `exercises.ipynb` (student-facing): NO solutions, NO executed outputs, `input()` allowed;
    exercises are numbered markdown headings matching `^## Exercise \d+` with ≥6 core
    exercises; ≥2 stretch exercises as cells tagged `stretch` under a "Challenge" heading.
  - `solutions.ipynb`: runs top-to-bottom headless; mirrors every exercise heading from
    `exercises.ipynb` (core AND stretch) with ≥1 code cell under each; contains ≥3 `assert`
    cells checking key computed answers; never calls `input()` (assigned sample values,
    stated inline); if any code cell uses `random.`, the notebook calls `random.seed(4)`
    before the first use; imports no GUI (turtle/tkinter); self-contained — must NOT read
    `assets/` (turtle solution code lives in `assets/solutions_*.py`, not executed by CI
    until plan 003 decides).
  - `lesson.ipynb`: teacher-led; any code cell whose source matches the interactive/GUI
    patterns below MUST carry the cell tag `no-exec` (mechanically checked in Phase A);
    untagged code cells must execute headless (full execution check lands in plan 003;
    Phase E assigns the manual audit).
  - Mechanical patterns (code cells only, matched PER LINE — `re.MULTILINE` on each cell's
    source): interactive `\binput\s*\(`; GUI `^\s*(import|from)\s+(turtle|tkinter)\b`;
    random-form ban `^\s*from\s+random\s+import\b` (solutions import randomness ONLY via
    `import random`, so all usage reads `random.<fn>` and is checkable).
  - Seed ordering (mechanical): concatenating `solutions.ipynb` code cells in order, the
    first occurrence of `random.` other than `random.seed(4)` must come AFTER an occurrence
    of `random.seed(4)` — seeding precedes first use, not merely "appears somewhere".
  - `teacher-notes.md` (every unit): required headings `## Goals`, `## Pacing`
    (per-lesson concept allocation; each lesson opens on the continuing project thread),
    `## Common mistakes`, `## Discussion prompts`, `## Differentiation`;
    the pacing section states the 60–90 min budget, and names where each of the
    manifest's `practices` concepts reappears.
- Every commit made while executing this plan appends the two mandated trailer lines
  (exact text in plan 002 §Global Constraints).
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

Step 0 — **kernel resolution:** before anything else, verify nbclient can execute a trivial
in-memory notebook in this venv (`uv run python` snippet building a one-cell notebook and
running it via nbclient; also `uv run jupyter kernelspec list` shows a resolvable python
kernel). If this fails, fix the environment before Phase B — the interim verification
depends on it.

Checks (parameterized over every `book1/units/unit-*/` directory present; cell-based checks
apply to CODE cells only where stated — markdown/raw cells lack `outputs`/`execution_count`
keys, so the hygiene check branches on cell type):
1. **Layout:** `manifest.yaml`, `lesson.ipynb`, `exercises.ipynb`, `solutions.ipynb`,
   `teacher-notes.md` present; if the manifest introduces `turtle-basics`, `assets/` exists,
   every `assets/*.py` referenced by any notebook exists, and all `assets/*.py` pass
   `py_compile`.
2. **Manifest schema + map agreement:** keys exactly
   `{id, kind, blueprint_version, lessons, concepts, provenance}`;
   `kind: unit`; `blueprint_version: 1`; `provenance: original`;
   `id` equals the directory name and a `coverage-map.yaml` entry;
   `lessons` equals the map entry's; `concepts.introduces/requires/practices` EQUAL the
   map entry's lists (order-insensitive). `concepts.requires` IS the design's
   "prerequisites" manifest field — no separate key (resolves design §3 wording).
3. **Student hygiene:** every CODE cell in `exercises.ipynb` has empty `outputs` and null
   `execution_count`; no cell source matches `(?i)^#+\s*solution`. (Proxy — heading-style
   leaks only; the content gate judges real leakage.)
4. **Exercise structure:** ≥6 markdown headings matching `^## Exercise \d+`; ≥2 cells
   tagged `stretch`. (Proxy for the mixed-ability rule; the gate judges quality.)
5. **Solutions structure + execution:** every `## Exercise \d+` heading in exercises
   appears in `solutions.ipynb`, each followed by ≥1 code cell before the next heading;
   ≥3 code cells containing `assert`; no code-cell line matches the interactive/GUI or
   random-form-ban patterns (Global Constraints, per-line matching); the seed-ordering rule
   holds (seed precedes first `random.` use); the notebook executes headless via nbclient
   (timeout 120s, kernel cwd = the unit directory via `resources={"metadata": {"path": ...}}`).
6. **Lesson conventions:** the first cell of `lesson.ipynb` is non-empty markdown (hook
   position — hookness itself is the content gate's call, per D-001 this is a UNIT-level
   property); every code cell matching the interactive/GUI patterns carries the `no-exec` tag.
7. **Teacher notes structure:** all five required headings present (Global Constraints).
8. **All three units present** (non-parameterized): `unit-01-story-machine`,
   `unit-02-number-detective`, `unit-03-turtle-art-studio` directories all exist —
   marked `xfail`/skipped until Phase D lands, strict after (plan 003 generalizes this
   from the coverage map).

TDD shape: tests are written FIRST; the red state is demonstrated against a throwaway stub
unit directory (create `book1/units/unit-01-story-machine/` with an empty manifest, observe
the failures, delete it before committing); the module then clean-skips while
`book1/units/` contains no unit directories, fails on any partially populated unit, and
passes when a unit is complete.

**Verification:** kernel step 0 output recorded; red demonstrated on the stub; then
`uv run pytest tests/test_book1_units.py -q` green (skipped) pre-content;
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
- Lesson 3 (while-loop): the full game — loop until the guess is correct; debugging session
  practicing error-messages (plan 002 follow-up).
  CONCEPT BOUNDARY (gate finding sol #1, round 1): NO guess counter anywhere in unit 02 —
  `loop-counter` is introduced by unit 03 per the binding map. The "fewest guesses"
  competition is run off-screen: students tally guesses on paper and the class keeps a
  hand-written leaderboard (teacher notes explain the deliberate omission and that
  counters arrive next unit).
- Exercises (~6 core + 2 stretch): dice roller, higher-or-lower verdict function-free
  snippets, change-the-range remix (1–1000: how does it feel?), two-player take-turns
  variant, fix-the-error; stretch: "hot/cold" distance hints (arithmetic + comparison
  only), computer-guesses-your-number (halving narrative, no formal algorithms,
  no counters).
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
- Notebooks: `lesson.ipynb` carries the reasoning and loop-table predictions; any cell
  showing turtle code carries the `no-exec` tag (mechanically enforced, Phase A check 6);
  `exercises.ipynb` has predict-the-drawing, range-value tables, fix-the-loop, and
  design-your-polygon planning tasks (headless); drawing tasks reference the assets
  scripts; stretch: star polygons (angle 720/5), rainbow spiral.
- Solutions: loop/range answers executable headless in `solutions.ipynb` (self-contained,
  never reads `assets/`); turtle answers as `assets/solutions_*.py` (`py_compile`-checked
  by Phase A; not CI-executed; reviewers code-read them; the teacher's first classroom
  run works through the visual checklist in the notes).
- Teacher notes: per-lesson allocation (glm follow-up); an explicit L1 first-run terminal
  walkthrough (open terminal in JupyterLab, `cd` to the unit, `python assets/l1_square.py`) —
  this is most students' first terminal encounter; window-management tips;
  visual checklist for the script outputs.

### Phase E — Verification (NAMED verification phase, design §5)

Mechanical (Phase A tests, wired into ci-local via pytest):
1. `uv run pytest -q` — full suite green (books + curriculum + units), including solutions
   execution with assertion cells, structure floors, hygiene, no-exec tagging, assets
   `py_compile`, teacher-notes headings, all-three-units presence.
2. Honesty note: nbclient execution proves the notebooks RUN and their `assert` cells hold;
   answer CORRECTNESS rests on those assertions plus the content gate's blind solves —
   stated per gate findings glm #3 / sol #4.
3. `bash scripts/ci-local.sh` — ALL GREEN.

Reviewer duties (explicit, until plan 003 mechanizes them):
4. Content-level prereq closure: statements use only each unit's
   `introduces` ∪ `requires` ∪ `practices` concepts.
5. Solutions cover EVERY exercise, core and stretch, and are non-vacuous.
6. Exercises genuinely exercise the manifest's `practices` claims (teacher notes name where
   each reappears).
7. `no-exec` audit: untagged lesson code cells are in fact headless-safe.
8. Turtle scripts: code-read `assets/*.py` and `assets/solutions_*.py` for correctness;
   the teacher's first classroom run performs the visual checklist.
9. Difficulty/timing: 60–90 min fit per lesson, pressure-testing unit-01 L2 and unit-03 L2
   specifically (5 introductions each — gate finding glm #8); differentiation guidance is
   mandatory for those two lessons.

**Acceptance criteria:** all three unit directories complete; every Phase A check green;
ci-local green; reviewer duties 4–9 discharged in the content-gate round; content gate
(blind-solve roster) reaches 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE
- Lesson allocations cover each unit's map `introduces` exactly (10/10/7); named verification phase present; executable conventions resolve input()/turtle-vs-CI explicitly; numbering deviation flagged.

### Review 2 — [fable] (2026-09-06)
- **Verdict**: APPROVE WITH NITS
- Confirmed: numbering deviation correct (design/TODO/ci-local all encode 003=tooling, 004=units); coverage-map cross-check exact for all three units; Phase E satisfies design §5 as an honest interim; dispatch compliant (blind-solutions distinction correctly on outlines, not finished statements); all plan-002 follow-ups honored; nbclient/ipykernel already in deps so ci-local picks Phase A up automatically.
1. `[OPEN]` Manifest `timing` key required by check 2 but never defined anywhere — dead schema field. Define its shape or drop it. Priority: Should Fix.
2. `[OPEN]` Empty `solutions.ipynb` passes every mechanical check; Phase E's "assertion cell failing" is vacuous without required assertion cells. Add a mechanical floor and/or explicit reviewer duty. Priority: Should Fix.
3. `[OPEN]` `import turtle` in `lesson.ipynb` neither forbidden nor checked, yet Phase D cites a nonexistent convention. Extend a grep ban to lessons or fix the parenthetical. Priority: Should Fix.
4. `[OPEN]` TDD wording self-contradiction (fail vs skip pre-content). Priority: Nit.
5. `[OPEN]` Phase A green with 0–2 units; add a non-parameterized all-three-present test. Priority: Nit.
6. `[OPEN]` Substring bans fragile (`from turtle import`, `import tkinter` slip; literal `input(` in markdown trips) — restrict to code cells, anchor patterns. Priority: Nit.
7. `[OPEN]` Hygiene check must branch on cell type (markdown/raw lack outputs keys). Priority: Nit.
8. `[OPEN]` Layout check omits `assets/` for turtle units. Priority: Nit.
9. `[OPEN]` Hook check not mechanically decidable as worded; specify the implementable proxy. Priority: Nit.
10. `[OPEN]` Unit-03 is students' first terminal encounter — teacher notes need an explicit first-run terminal walkthrough item. Priority: Nit.
11. `[OPEN]` State that solutions.ipynb is self-contained and must not read `assets/`. Priority: Nit.

### Review 3 — [glm] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (no blockers)
- Confirmed: exact once-only lesson allocation for all three units; numbering deviation defensible; content-before-tooling sequencing acceptable and de-risked by the stated promotion intent; dispatch compliant; all plan-002 follow-ups honored.
1. `[OPEN]` `timing` key undefined (overlaps fable #1). Priority: Should Fix.
2. `[OPEN]` "Tests fail first" contradicts the skip guard (overlaps fable #4); demonstrate red on a stub dir. Priority: Should Fix.
3. `[OPEN]` "Solutions reproduce stated answers" over-claims: execution ≠ answer comparison; require assertion cells or state that correctness rests on blind solves. Priority: Should Fix.
4. `[OPEN]` Forbidden-call patterns evadable (`from turtle import`, `input (`); lesson-notebook conventions never mechanically checked — add: lesson code cells importing turtle or calling input must carry `no-exec`. Priority: Should Fix.
5. `[OPEN]` nbclient kernel resolution never exercised in this repo — verify kernelspec resolves in Phase A or the interim verification is a Phase-B landmine. Priority: Should Fix.
6. `[OPEN]` Stretch/hygiene checks are thin proxies — say so explicitly like the hook check does. Priority: Nice to Have.
7. `[OPEN]` `practices` reinforcement not content-checked — direct the content gate to check it; teacher notes name where each practiced concept reappears. Priority: Nice to Have.
8. `[OPEN]` Unit-01 L2 and unit-03 L2 carry 5 introductions each — Phase E difficulty review must pressure-test these two lessons; differentiation guidance mandatory there. Priority: Nice to Have.
9. `[OPEN]` Hook proxy is first-lesson-only; teacher notes should open every lesson with the project thread. Priority: Nice to Have.
10. `[OPEN]` `assets/*.py` never verified — add existence + `py_compile` checks for referenced scripts. Priority: Nice to Have.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT
1. `[OPEN]` (Blocker) Unit 02 blueprint uses a guess counter, but `loop-counter` is introduced by unit 03 per the binding map — violates content-level closure.
2. `[OPEN]` (Blocker) Interim verification permits vacuous exercises/solutions (overlaps fable #2, glm #3).
3. `[OPEN]` (Major) Lexical bans evadable; `random.seed(4)` binding never checked (overlaps fable #6, glm #4).
4. `[OPEN]` (Major) `no-exec` has no assigned verification anywhere.
5. `[OPEN]` (Major) D-005 turtle scripts can be absent/broken and pass; visual checklist never assigned (overlaps fable #8, glm #10).
6. `[OPEN]` (Major) Manifest schema conflicts with design's "prerequisites" wording; `timing` untyped (overlaps fable #1, glm #1).
7. `[OPEN]` (Major) Teacher-note completeness required only for unit 01.
8. `[OPEN]` (Major) TDD fail-first vs skip-guard contradiction (overlaps fable #4, glm #2).
9. `[OPEN]` (Nit) Trailer clause dangles — no embedded commit commands in this plan.
10. Confirmations: numbering acceptable and canonical; hooks/pacing otherwise aligned (hook is a UNIT-level property, first-markdown proxy correct); dispatch compliant; plan-002 follow-ups honored.

### Revision 2 resolutions (2026-09-06) — applied across all three reviews
- sol 1 `[FIXED]`: unit 02 is now counter-free — loop-until-correct game, guesses tallied on paper for a hand-written class leaderboard; exercises reworked (change-the-range, two-player) with an explicit CONCEPT BOUNDARY note; teacher notes explain that counters arrive in unit 03. Map untouched.
- sol 2 / fable 2 / glm 3 `[FIXED]`: mechanical floors added — ≥6 `## Exercise N` headings + ≥2 stretch cells in exercises; solutions mirror every heading with ≥1 code cell each and carry ≥3 assert cells; Phase E honesty note states correctness rests on assertions + blind solves; reviewer duty 5 requires non-vacuous full coverage.
- sol 3 / fable 6 / glm 4 `[FIXED]`: patterns anchored and code-cell-only (`\binput\s*\(`, `^\s*(import|from)\s+(turtle|tkinter)\b`); `random.seed(4)` mechanically required when `random.` appears.
- sol 4 `[FIXED]`: no-exec now mechanically enforced in Phase A (pattern-matching lesson cells must carry the tag) plus Phase E reviewer duty 7 (untagged cells headless-safe).
- sol 5 / fable 8 / glm 10 `[FIXED]`: turtle-unit layout check requires `assets/`, referenced-script existence, and `py_compile`; reviewer duty 8 assigns code-reading and the teacher's first-run visual checklist.
- sol 6 / fable 1 / glm 1 `[FIXED]`: `timing` dropped from the schema; `concepts.requires` documented as the design's "prerequisites" field (answers sol's open question); timing budget lives in teacher-notes pacing.
- sol 7 `[FIXED]`: teacher-notes five-heading requirement is now a binding convention for EVERY unit, mechanically checked (Phase A check 7), including where each `practices` concept reappears.
- sol 8 / fable 4 / glm 2 `[FIXED]`: TDD reworded — red demonstrated on a throwaway stub unit dir, then clean-skip pre-content, fail on partial, pass on complete.
- sol 9 `[FIXED]`: trailer clause now references plan 002's exact text and binds commits made while executing this plan.
- fable 5 `[FIXED]`: non-parameterized all-three-units test (xfail until Phase D, strict after).
- fable 7 `[FIXED]`: hygiene check specified as code-cells-only with cell-type branching.
- fable 9 `[FIXED]`: hook check specified as "first cell is non-empty markdown"; hookness judged by the gate.
- fable 10 `[FIXED]`: unit-03 teacher notes require the L1 first-run terminal walkthrough.
- fable 11 `[FIXED]`: solutions self-containment (never reads `assets/`) now a binding convention and stated in Phase D.
- glm 5 `[FIXED]`: Phase A step 0 verifies nbclient kernel resolution before any content work.
- glm 6 `[FIXED]`: stretch/hygiene checks now labeled proxies with the gate as judge.
- glm 7 `[FIXED]`: reviewer duty 6 checks `practices` coverage; teacher notes name reappearances.
- glm 8 `[FIXED]`: Phase E duty 9 pressure-tests unit-01 L2 and unit-03 L2; differentiation mandatory there.
- glm 9 `[FIXED]`: teacher-notes pacing sections open every lesson on the project thread (binding convention).

### Review 5 — [sol] round 2 (2026-09-06)
- **Verdict**: REJECT (7 of 9 checklist items PASS incl. the counter blocker; two mechanical-check holes remain)
1. `[FIXED]` (Major) Seed check enforced presence, not ordering, and `from random import x` evaded it.
   → Response: solutions now import randomness only via `import random` (from-import mechanically banned); seed-ordering rule added — first `random.` use other than the seed call must FOLLOW `random.seed(4)` in cell order.
2. `[FIXED]` (Major) GUI pattern not specified as multiline — `# comment\nimport turtle` evaded it.
   → Response: all mechanical patterns now matched per line (`re.MULTILINE`) on each code cell's source.
3. `[FIXED]` (Nit) Concept-boundary note cited "sol #2" instead of "sol #1". → Response: corrected.

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)

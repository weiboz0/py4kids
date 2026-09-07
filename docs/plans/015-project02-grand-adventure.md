# Plan 015 — Project 02 Grand Adventure (Year-1 Capstone) Implementation Plan

**Goal:** Ship `project-02-grand-adventure` — the Year-1 CAPSTONE — a 4-lesson text-adventure build
that integrates the whole year: a `Hero` OBJECT with attributes + methods, a `rooms` DICTIONARY
world, an exploration LOOP with choices + a seeded RANDOM event, and SAVE/LOAD to a FILE. It is the
culminating "you use everything" project.

**Architecture:** Standard project pipeline (plan 007/010, project-01-arcade-night as the template):
`brief.ipynb` (student milestones) + `solutions.ipynb` (reference, headless + input-free) +
`teacher-notes.md` (SIX headings incl. `## Rubric`) + `manifest.yaml` (map-equal). Inherits the
unit-09 file-I/O CI-safety rules and the unit-10 OOP-closure rules, PLUS project-01's
"parameterize-and-script" pattern for making an interactive program run deterministically in CI.

**Spec:** `book1/curriculum/coverage-map.yaml` (project-02 entry, reconciled in Phase C);
design-000 §"Project-spine principle" (the spine ends `text adventure → capstone`); plan 007/010
project conventions; plans 012 (file-I/O) + 013 (OOP) binding rules; D-001.

## Global Constraints

- **Project conventions (plan 007/010; project-01 template):**
  - `brief.ipynb`: a title cell `# Grand Adventure`, then `## Milestone N` markdown cells (4) each
    with a short hook + a SCAFFOLD code cell the student extends (the brief MAY use `input()` — it is
    the student's interactive game), then `## Make it yours` (extension ideas, non-graded) and
    `## Requirements checklist` (what a complete submission has). NO solutions in the brief. Unique
    cell ids (descriptive, per the project-01 template — hex not required; glm-6). Valid nbformat 4.
  - `solutions.ipynb`: a REFERENCE build that runs headless, INPUT-FREE, top-to-bottom clean. Each
    interactive milestone is refactored into a `Hero` class + PARAMETERIZED functions (the values a
    player would type become function ARGUMENTS), driven by a FIXED SCRIPTED sequence of choices — a
    `choice` variable stepped through a known path ending in `"quit"` so the quit/`break` branch is
    genuinely exercised with NO typed menu. Non-vacuous asserts pin outcomes AND each function's
    branches (so results can't be hard-coded — project-01 precedent: `assert quick_quiz(...) == 2`
    for the middle branch).
  - `teacher-notes.md`: SIX `##` headings — `## Goals`, `## Pacing`, `## Common mistakes`,
    `## Discussion prompts`, `## Differentiation`, `## Rubric` (projects use **Rubric**, not
    Grading). Pacing = 4 lessons of 60–90 min. Rubric points sum to a stated total.
  - Project dir prefix `project-02-`. Manifest map-equal to the (Phase-C reconciled) entry.
- **CI-SAFETY — no input in executable cells (project-01 binding):** the `solutions.ipynb` executable
  cells contain ZERO `input()`. The interactive loop is driven by a scripted `choice` variable (or a
  fixed LIST of moves walked by index) that terminates via a `"quit"`→`break`. `input` stays a
  practiced concept via the BRIEF milestones only (unit-05/unit-10 precedent: input in prompts,
  executable cells input-free).
- **CI-SAFETY — seeded random (project-01 binding, CI-machine-enforced):** `import random;
  random.seed(4)` is the FIRST code cell of `solutions.ipynb`. The value MUST be the literal `4`
  and MUST lexically precede the first `random.` token ANYWHERE in the notebook — `tools/notebooks.py`
  `_is_seed_four_call` accepts only the constant `4` and scans per-cell in notebook order, so even a
  helper `def` body that textually contains `random.` before the seed cell FAILS `structure-check`
  (glm-1). The ONLY random API is `random.randint(a, b)` (unit-02); `random.choice`/`random.shuffle`
  are UNTAUGHT and forbidden (glm-2). Assert exact seeded outcomes.
- **CI-SAFETY — driver determinism (glm-4):** the scripted path's length is FIXED and INDEPENDENT of
  the random event's outcome — the seeded event changes the hero's health, never the loop's iteration
  count and never an early exit — so every final-state assert is an exact integer.
- **CI-SAFETY — file I/O (unit-09 binding):** CI executes `solutions.ipynb` with cwd = the project
  dir. The save/load milestone is WRITE-THEN-READ within the notebook (Milestone-4 solution WRITES
  `adventure_save.txt` BEFORE it reads it); write mode `"w"` (deterministic, idempotent); the scratch
  filename `adventure_save.txt` is gitignored in Phase A; NO append mode; NO `os`/`tempfile`/
  `pathlib`; NO `.split()` (untaught in Book 1). The save is a FIXED-LAYOUT text file read
  one-line-at-a-time with `for line in f` + `.strip()` + a LINE COUNTER: line 0 = hero name (text),
  line 1 = health (int-parsed), lines 2+ = inventory items (text, appended). This PAYLOAD-LAYOUT
  keeps `int(...)` off the text lines (unit-09 int-crash lesson). Phase C runs a CLEAN-SLATE `rm -f`
  of `adventure_save.txt` before the final ci-local so green proves create-before-read.
- **CLOSURE (binding):** every construct is taught ≤ project-02 (i.e. anywhere in units 01–10, since
  the capstone is the last entry). `builtin-functions` (`len`/`max`/`min`) IS taught (unit-07) and
  ALLOWED here (unlike checkpoints). FORBIDDEN (untaught in Book 1): `.split()`; sets;
  comprehensions; inheritance (`class X(Y)`); any dunder beyond `__init__`; `@property`/decorators;
  `isinstance`/`type`/`getattr`/`setattr`; f-string `=`/format-spec beyond `{name}`. Dict ops:
  `[key]`/`.items`/`.get` are taught (unit-08); `.pop`/`.update` are NOT — avoid. String methods are
  ONLY the unit-06 subset `upper`/`lower`/`strip`/`replace` — the save parse needs only `.strip()`;
  NO `.split`/`.title`/`.capitalize`/`.find`/`.index` (glm-5).
- **OOP CLOSURE — EXACTLY ONE plain class (sol-1, unit-10 binding "keep it one plain class"):** each
  notebook defines exactly ONE class type, `Hero` (`__init__` + instance methods only). The WORLD is
  modelled with plain DICTS + LISTS, NEVER a second class — no `Room`/`World`/`Item` class. Phase C
  asserts (AST + reviewer) that `Hero` is the only `ClassDef` name.
- **WORLD MODEL — FLAT dicts only, NO nested dict-of-dicts (fable-c):** `rooms[current]["exits"][dir]`
  (chained `][` on nested dicts) is a STRUCTURAL FIRST never taught in Book 1 (unit-08 dicts are flat
  string→string). Instead the world is FLAT, single-subscript dicts: `descriptions` (room → text),
  `exits` (composite key `current + " " + direction` → next room, so access is ONE subscript on a
  string key built with taught string-concat, and presence is `if (current + " " + direction) in
  exits:` — in-operator), and `items` (room → item). This keeps every dict access single-level and
  taught, and doubles as a string-concat + membership beat.
- **SUBSTRATE (binding, Phase-C reconciled):** the project-02 map entry already lists the full Year-1
  practices set (the capstone integrates everything). Phase C SCANNER-DERIVES the concepts the
  authored 4 milestones actually use — scanning BOTH the brief scaffolds AND the input-free solution
  (glm-3), so a concept practiced only in the brief is not wrongly trimmed. `input`'s home is the
  BRIEF (the standing prompt-homing pattern); it MUST SURVIVE the trim even though the solution is
  input-free. RECONCILE the map `practices` + `requires` to match: TRIM any listed concept NEITHER
  the brief nor the solution exercises, ADD any used-but-unlisted concept (must be ≤ project-02).
  Manifest == the reconciled entry. `practices ∩ introduces` empty (introduces = []). Apply map edits
  surgically (no YAML round-trip).
- **Deliberate-bug beat (optional for projects):** NOT required for a project (projects are builds,
  not assessments); if a "common bug" is shown in the brief it lives in a MARKDOWN fence, never an
  executable cell.
- Process (standing): no commits while a `[sol]` review is in flight; codex prompts name the
  in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Project plan → Phase C is the mandatory named verification phase. Out of scope: the latent
practice-completeness hygiene PR + `concept_scan.py` promotion into `tools/` (tracked separately);
PDF handout styling beyond the standard build; Book-2 anything; `.split()`/sets/comprehensions/
inheritance; `os`/`tempfile`; append-mode files; any typed `input()` in an executable solution cell.

## Phases

Dispatch per AGENTS.md: milestone STATEMENTS (brief) via codex; the reference solution via a SEPARATE
blind codex session; teacher notes inline; gitignore + manifest + Phase-C map reconciliation inline.

### Phase A — gitignore + provisional manifest (inline)

1. Append to `.gitignore` (surgical): a comment + `book1/projects/project-02-grand-adventure/adventure_save.txt`.
2. `book1/projects/project-02-grand-adventure/manifest.yaml`, provisionally map-equal to the CURRENT
   project-02 entry (Phase C reconciles both together once the scanner has the real content).
- **Acceptance (Phase A):** gitignore + provisional manifest are green (`uv run pytest -q` +
  `ci-local` — manifest == the current map entry) before the notebooks exist.

### Phase B — project-02-grand-adventure content (4 milestones)

Blueprint (a text-adventure capstone; the brief scaffolds, the solution refactors to headless):
- **Brief title:** `# Grand Adventure` + a framing line (build the year's biggest program — a text
  adventure with a hero, a world, exploration, and saved progress).
- **M1 — Meet your hero (class-def, init-method, attributes):** scaffold a `class Hero:` with
  `__init__(self, name)` setting `self.name`, `self.health` (e.g. 20), `self.inventory = []`; make a
  hero and print its stats. Brief may read the name via `input()`.
- **M2 — Build the world (dict-literal, dict-access, string-concat, in-operator):** THREE FLAT dicts
  (no nesting): `descriptions` (room → description text), `exits` (composite key `room + " " +
  direction` → next room), and `items` (room → item text). Print the starting room's description via
  `descriptions[current]`. The M2 scaffold PROVIDES the three dicts pre-populated so the student
  extends them (adds rooms/exits), never invents the structure.
- **M3 — Explore (while-loop, dict-access, string-concat, in-operator, if/elif/else, list-append,
  accumulator, random, methods):** a loop that reads a direction, builds the exit key
  `key = current + " " + direction`, and IF `key in exits:` moves to `exits[key]` ELSE stays put
  (an if/else the asserts pin both ways); picks up `items[current]` when `current in items`
  (`hero.pick_up(...)` → `self.inventory.append(...)`); and applies ONE seeded RANDOM event via a
  `hero.take_damage(n)` method (accumulator on `self.health`). Loop ends on `"quit"`. Brief drives it
  with `input()`; the SOLUTION scripts the choices. The event changes health only — never the loop
  length.
- **M4 — Save & load (file-write, file-read, with-statement, for-loop, loop-counter, type-conversion):**
  write the hero's `name`, `health`, and each inventory item to `adventure_save.txt` (one value per
  line, fixed layout), then load it back into fresh variables and confirm they match.
- **`## Make it yours`:** extension ideas (more rooms, a combat method, a score) — non-graded.
- **`## Requirements checklist`:** a hero class, a rooms dict, an exploration loop, a save/load — the
  marks of a complete submission.
- **Solution refactor (headless, input-free):**
  - `import random; random.seed(4)` as the FIRST code cell (literal 4; before ANY `random.` text).
  - `class Hero:` (the ONLY class) with `__init__` + methods (`take_damage(self, n)` → accumulator on
    `self.health` + returns health; `pick_up(self, item)` → `self.inventory.append(item)`; optionally
    `status(self)` → returns a health string so it is assertable). NO second class.
  - Parameterized helpers over the FLAT dicts: `describe(descriptions, room)` returns the text;
    `move(exits, current, direction)` builds `current + " " + direction` and returns `exits[key]` if
    `key in exits` else `current` (an if/else the asserts pin BOTH ways). The only random draw is
    `apply_event(hero, roll)` where `roll = random.randint(1, 6)` (or the helper takes the roll as a
    param) — a trap fires (`hero.take_damage(n)`) on some rolls and misses on others.
  - A FIXED driver: a scripted `moves = ["east", "west", "quit"]` (or a `choice` variable stepped)
    inside `while True:` that `break`s on `"quit"`; NO `input()`. The path length is FIXED regardless
    of the event outcome.
  - Save/load: `with open("adventure_save.txt", "w") as f:` writes `hero.name + "\n"`,
    `str(hero.health) + "\n"`, then a `for item in hero.inventory:` writing `item + "\n"`; then read
    back with `for line in f` + `.strip()` + a `line_number` counter (0→name, 1→`int(health)`, else
    `.append`). NO `.split`.
  - Non-vacuous asserts: hero state after the scripted run (health after the seeded event via the
    method); inventory contents by INDEX (`hero.inventory[0] == "sword"`); `move` returns the right
    room for a valid exit AND the SAME room for a missing exit (both branches pinned); the RANDOM
    EVENT helper pinned on BOTH outcomes — call it with a roll that FIRES and one that MISSES and
    assert the resulting health each way (fable-a), plus pin the actual seeded roll from the run; the
    SAVE ROUND-TRIP with INDEX + `len` as the PRIMARY pins — `loaded_name == hero.name`,
    `loaded_health == hero.health`, `len(loaded_items) == len(hero.inventory)`,
    `loaded_items[0] == hero.inventory[0]` — and a whole-list `loaded_items == hero.inventory` as a
    secondary check (fable-b); the loop terminated (`choice == "quit"` / counter exhausted).
    `builtin-functions` OK (`len(hero.inventory) == 2`).
- Teacher notes: SIX headings incl. `## Rubric` — per-milestone points summing to a total; 4-lesson
  pacing (60–90 min each) with per-lesson goals; common mistakes (forgetting `self`; a missing dict
  key → `KeyError`; forgetting `.strip()` before `int()`; `.sort()` returns None; an infinite loop
  with no quit branch; a typo'd attribute); discussion prompts; differentiation (give the finished
  `Hero` class to strugglers; a combat system / score for fast finishers).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; **CLEAN-SLATE RUN** (`rm -f book1/projects/project-02-grand-adventure/
adventure_save.txt` before the final `ci-local.sh` so green proves create-before-read);
`ci-local.sh` ALL GREEN; AST concept-scanner scoped to project-02 clean (advisory — user-defined
methods exempt); SUBSTRATE RECONCILIATION — scanner-derive the authored concepts from BOTH the brief
scaffolds AND the solution (glm-3), TRIM any concept NEITHER exercises + ADD any used-but-unlisted in
BOTH `coverage-map.yaml` (surgical) AND `manifest.yaml`, so map == manifest == reality (KEEP `input`
— its home is the brief); ONE-CLASS AST CHECK — the only `ClassDef` name in each notebook is `Hero`
(sol-1); solutions execute headless with non-vacuous asserts; the scratch `adventure_save.txt`
gitignored (no git noise).
Reviewer duties (both gates): blind-BUILD the milestones from the brief; verify the solution runs
headless + input-free (NO `input()` in executable cells); seeded-random determinism (literal
`random.seed(4)` first cell; `random.randint` only); file I/O is write-then-read + no-split +
clean-slate; closure (only ≤ project-02 — NO `.split`/sets/comprehensions/inheritance/
dunders-beyond-init/second-class/nested-dict-of-dicts, check explicitly); each milestone solvable +
reference correct; asserts non-vacuous (mutation-test each, incl. BOTH random-event branches); rubric
usable; 4-lesson timing; map == manifest == the concepts actually used.

**Acceptance criteria:** the project directory complete; `uv run pytest -q` green; ci-local ALL GREEN
(clean-slate); concept-scanner clean; map == manifest == authored concepts; `adventure_save.txt`
gitignored; plan-review + content-review 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. The capstone inherits every hard-won binding rule from the year: project-01's
parameterize-and-script pattern (interactive milestones → parameterized functions + a fixed
scripted-choices driver so the program runs headless + input-free), seeded random for determinism,
unit-09 file-I/O CI-safety (write-then-read `adventure_save.txt`, gitignored, deterministic `"w"`,
fixed-layout line-counter parse with NO `.split`, clean-slate Phase-C run), and unit-10 OOP closure
(single plain `Hero` class, `__init__` + methods only, no inheritance/dunders-beyond-init).
`builtin-functions` is ALLOWED here (taught unit-07), the one deliberate relaxation vs the
checkpoints. Substrate is Phase-C SCANNER-DERIVED and reconciled so map == manifest == reality
(the capstone's existing comprehensive practices list is trimmed to what the 4 milestones truly
exercise, avoiding the over-listing the checkpoint gates flagged). Input stays practiced via the
brief; executable solution cells are input-free. `practices ∩ introduces` empty (introduces = []).

### Review 2 — [fable] (2026-09-07) → APPROVE WITH NITS, reconciled
Fable 5, read-only; prereq + coverage PASS on scratch. Input-free CI-safety airtight (three-way
stated + CI mechanically backstops it), seeded determinism sound, file-I/O payload-layout sound,
OOP closure correct, substrate-deferral acceptable.
- **[FIXED] (a) event branch-pinning** — the seeded event's fires/misses branches weren't both
  required → solution now pins the `apply_event`/`take_damage` helper on BOTH outcomes (a roll that
  fires + one that misses) plus the actual seeded roll.
- **[FIXED] (b) whole-list `==` round-trip** — INDEX + `len` asserts are now the PRIMARY save-load
  pins; whole-list `==` is secondary.
- **[FIXED] (c) nested dict-of-dicts is an untaught structural first** (`rooms[c]["exits"][d]`;
  unit-08 dicts are flat string→string) → REDESIGNED the world as THREE FLAT single-subscript dicts
  (`descriptions`, `exits` with composite `"room direction"` keys via string-concat + membership,
  `items`). No nesting anywhere — resolves the closure concern AND adds a string-concat/membership
  beat. (glm's taxonomy view didn't flag it, but the flat design is clean for both.)

### Review 3 — [glm] (2026-09-07) → APPROVE WITH NITS, reconciled
GLM-5.2, read-only; prereq + coverage PASS. Confirmed the CI machine enforces the rails
(`tools/notebooks.py` bans `input(` in every solution cell, requires literal `random.seed(4)`, runs
project solutions with cwd=project dir, never executes briefs). No untaught concept in the 4
milestones; `.get`/`.items` genuinely unit-08; `len`/`max`/`min` correctly allowed.
- **[FIXED] 1** literal `random.seed(4)` as the FIRST code cell, before any `random.` token (CI
  checker is lexical + constant-4-only) → pinned in Global Constraints + solution refactor.
- **[FIXED] 2** only `random.randint(a, b)` (no `choice`/`shuffle`) → pinned.
- **[FIXED] 3** Phase-C scanner scans BOTH brief + solution; `input`'s home is the brief and survives
  the trim → stated in the SUBSTRATE bullet + Phase C.
- **[FIXED] 4** scripted-path length independent of the event outcome → added a driver-determinism
  Global Constraint.
- **[FIXED] 5** string-methods restated as the unit-06 subset (upper/lower/strip/replace; no
  `.title`/`.capitalize`) → CLOSURE bullet.
- **[FIXED] 6** dropped "8-hex cell ids" → "descriptive ids per the project-01 template".

### Review 4 — [sol] (2026-09-07) → REJECT, reconciled
GPT-5.6-sol, read-only. Input-free (P1), seeded (P2), and file-I/O (P3) all PASS with project-01 /
unit-09 / unit-12 citations; payload-layout confirmed to avoid the plan-012 `int("Ada")` crash.
- **[FIXED] BLOCKER — the plan forbade inheritance/dunders but not a SECOND plain class** (a `Room`
  class could pass every stated check; plan-013 binding is "one plain class") → added an EXACTLY-ONE
  plain class (`Hero`) Global Constraint + a Phase-C ONE-CLASS AST check (only `ClassDef` name is
  `Hero`). Aligns with the flat-dict world (no `Room`/`World`/`Item` class).

### Reconciliation (2026-09-07)
Applied all fable (a/b/c) + glm (1–6) + sol (1) findings to HEAD. Net design changes: (1) world is
THREE FLAT dicts, no nesting; (2) exactly one `Hero` class, world is dicts/lists; (3) `random.seed(4)`
literal first cell + `randint` only; (4) event both-branch pinned; (5) index/`len` primary save
asserts; (6) driver length event-independent; (7) string-methods = unit-06 subset; (8) scanner scans
brief+solution, `input` survives trim; (9) descriptive cell ids. No closure violation remains; all
concepts trace ≤ unit-10. prereq + coverage PASS on scratch (unchanged — the map entry is untouched
until Phase C reconciliation). Round-2 confirmation dispatched.
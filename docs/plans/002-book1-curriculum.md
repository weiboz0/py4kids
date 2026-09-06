# Plan 002 — Book 1 Curriculum Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship Book 1's concept registry, machine-checkable coverage map, and the full Year 1 project-first syllabus, so every later unit plan (004+) builds against a fixed, verifiable arc.

**Architecture:** Two YAML data files under `book1/curriculum/` — `concepts.yaml` (the registry: every teachable concept gets a stable id) and `coverage-map.yaml` (the planned arc: units/projects/checkpoints with `introduces`/`requires`/`practices` concept mappings) — plus a human-readable `book1/syllabus.md` consistent with the map. Pytest validates registry schema, prereq ordering, and syllabus consistency now; plan 003 turns these into first-class CI tools.

**Tech Stack:** YAML data + pytest validation (PyYAML already in the environment).

**Spec:** `docs/designs/000-project-design.md` (§2 Curriculum architecture, §First milestones item 2)

## Global Constraints

- Every `git commit` command in this plan implicitly appends the two mandated trailer lines
  (`Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` and the executing session's
  `Claude-Session:` URL) as additional `-m` arguments; commands show only the subject.
- Docs use semantic line breaks — one sentence per line (design §3).
- Unit/project/checkpoint directory names (used by plan 004+, declared here):
  `unit-NN-slug`, `project-NN-slug`, `checkpoint-NN-slug`.
- User-settled curriculum parameters (2026-09-06): ~30 lessons;
  Year 1 lands through lists/dicts/files PLUS a gentle OOP intro;
  graphics stack is built-in turtle + text games (zero new dependencies);
  ~4 checkpoints (one per 2–3 units).
- Turtle delivery assumption (binding on plan 004+): built-in `turtle` opens a Tk window and
  does NOT render inside notebook cells, so turtle-based lessons (units 03/05, optional in
  projects) run as `.py` scripts launched from the JupyterLab/VS Code terminal;
  notebooks remain the medium for all non-turtle work and for turtle exercise write-ups.
  Propose recording this as decision D-005 at ship time (decisions.md is governance —
  needs user sign-off).
- Pacing directive (binding on plan 004): units 01–02 carry the year's heaviest introduction
  load (10 concepts each) at the students' most fragile point; their teacher notes MUST
  allocate concepts to specific lessons explicitly (e.g. unit 02: lesson 1 numbers+random,
  lesson 2 conditionals, lesson 3 the while-loop finale), and their exercise sets stay short.

## Out of scope

This is a curriculum-data/docs plan (plus planning-level pytest code): it ships NO units, projects, or checkpoints (only their planned registry entries), so the design's "named verification phase" rule for content plans does not apply (exemption per design §5).
Verification here is the pytest suite added by this plan (registry schema, unique ids, prereq ordering, introduce-exactly-once, practice coverage, syllabus consistency) plus green `ci-local.sh`.
Also out of scope: unit/lesson content and manifests (plan 004+), verification tooling in `tools/` (plan 003), Book 2 curriculum (later), teacher notes (ship with units).

---

### Task 1: concept registry (TDD)

**Files:**
- Create: `book1/curriculum/concepts.yaml`
- Delete: `book1/curriculum/.gitkeep`
- Test: `tests/test_book1_curriculum.py` (registry tests only in this task)

**Interfaces:**
- Produces: `concepts.yaml` with top-level `concepts_version: 1` and `concepts:` — a list of `{id, name, category}` entries; ids are unique kebab-case, referenced by `coverage-map.yaml` (Task 2) and by every unit `manifest.yaml` from plan 004 on. Categories (fixed vocabulary): `io`, `data`, `strings`, `control`, `loops`, `functions`, `collections`, `files`, `oop`, `graphics`, `modules`.

- [ ] **Step 1: Write the failing registry tests**

`tests/test_book1_curriculum.py`:

```python
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
CURRICULUM = REPO / "book1" / "curriculum"

CATEGORIES = {
    "io", "data", "strings", "control", "loops", "functions",
    "collections", "files", "oop", "graphics", "modules",
}


def load_concepts():
    data = yaml.safe_load((CURRICULUM / "concepts.yaml").read_text(encoding="utf-8"))
    assert data["concepts_version"] == 1
    return data["concepts"]


def test_concepts_schema_and_unique_ids():
    concepts = load_concepts()
    assert len(concepts) >= 40
    ids = [c["id"] for c in concepts]
    assert len(ids) == len(set(ids)), "duplicate concept ids"
    import re

    for c in concepts:
        assert set(c) == {"id", "name", "category"}, f"bad keys in {c}"
        assert c["category"] in CATEGORIES, f"unknown category: {c}"
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", c["id"]), f"non-kebab id: {c['id']!r}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_book1_curriculum.py -q`
Expected: FAIL (`concepts.yaml` not found).

- [ ] **Step 3: Write `book1/curriculum/concepts.yaml`**

```yaml
concepts_version: 1
concepts:
- {id: print, name: Printing output, category: io}
- {id: comment, name: Code comments, category: io}
- {id: input, name: Reading user input, category: io}
- {id: run-program, name: Running a program in the classroom environment, category: io}
- {id: error-messages, name: Reading error messages and tracebacks, category: io}
- {id: string-literal, name: String literals and quotes, category: strings}
- {id: f-string, name: f-string formatting, category: strings}
- {id: string-concat, name: String concatenation and repetition, category: strings}
- {id: string-index, name: String indexing, category: strings}
- {id: string-slice, name: String slicing, category: strings}
- {id: string-methods, name: "String methods (upper/lower/strip/replace)", category: strings}
- {id: in-operator, name: Membership testing with in, category: strings}
- {id: variable, name: Variables and assignment, category: data}
- {id: naming, name: Naming conventions, category: data}
- {id: int-type, name: Integers, category: data}
- {id: float-type, name: Floats and decimal arithmetic, category: data}
- {id: arithmetic, name: "Arithmetic operators (+ - * / // %)", category: data}
- {id: type-conversion, name: "Type conversion (int/str/float)", category: data}
- {id: boolean, name: Boolean values, category: data}
- {id: comparison, name: Comparison operators, category: control}
- {id: logical-ops, name: "Logical operators (and/or/not)", category: control}
- {id: if-statement, name: if statements, category: control}
- {id: elif-else, name: elif and else branches, category: control}
- {id: conditional-nesting, name: Nested conditionals, category: control}
- {id: while-loop, name: while loops, category: loops}
- {id: break-statement, name: Exiting loops with break, category: loops}
- {id: for-loop, name: for loops, category: loops}
- {id: range-function, name: The range function, category: loops}
- {id: loop-counter, name: Counter variables, category: loops}
- {id: accumulator, name: Accumulator pattern, category: loops}
- {id: nested-loops, name: Nested loops, category: loops}
- {id: import-statement, name: Importing modules, category: modules}
- {id: random-module, name: "Random numbers (randint/choice)", category: modules}
- {id: turtle-basics, name: "Turtle setup and movement (forward/turn)", category: graphics}
- {id: turtle-drawing, name: "Turtle pen, color, and shapes", category: graphics}
- {id: def-function, name: Defining functions, category: functions}
- {id: parameters, name: Function parameters and arguments, category: functions}
- {id: return-value, name: Return values, category: functions}
- {id: scope, name: Local vs global scope, category: functions}
- {id: list-literal, name: Creating lists, category: collections}
- {id: list-index, name: List indexing, category: collections}
- {id: list-append, name: Growing lists with append, category: collections}
- {id: list-loop, name: Looping over lists, category: collections}
- {id: list-sort, name: Sorting lists with the sort method, category: collections}
- {id: builtin-functions, name: "Built-in functions (len/min/max)", category: functions}
- {id: dict-literal, name: Creating dictionaries, category: collections}
- {id: dict-access, name: Dictionary lookup and update, category: collections}
- {id: dict-loop, name: Looping over dictionaries, category: collections}
- {id: file-read, name: Reading files, category: files}
- {id: file-write, name: Writing files, category: files}
- {id: with-statement, name: Opening files with with, category: files}
- {id: class-def, name: Defining classes, category: oop}
- {id: init-method, name: "__init__ and creating objects", category: oop}
- {id: attributes, name: Object attributes, category: oop}
- {id: methods, name: Object methods, category: oop}
```

- [ ] **Step 4: Remove the placeholder and run tests green**

Run: `git rm -q book1/curriculum/.gitkeep && uv run pytest tests/test_book1_curriculum.py -q`
Expected: PASS (1 test).

- [ ] **Step 5: Commit**

```bash
git add book1/curriculum/concepts.yaml tests/test_book1_curriculum.py
git commit -m "feat(book1): concept registry, 55 concepts (plan 002)"
```

### Task 2: coverage map (TDD)

**Files:**
- Create: `book1/curriculum/coverage-map.yaml`
- Test: append to `tests/test_book1_curriculum.py`

**Interfaces:**
- Consumes: concept ids from Task 1.
- Produces: `coverage-map.yaml` with `map_version: 1` and `entries:` — ordered list of `{id, kind, title, lessons, introduces, requires, practices}` where `kind` ∈ `unit|project|checkpoint`, `id` matches the directory-name contract, `lessons` is the lesson-count budget, and the three concept lists reference registry ids. Plan 004+ unit manifests must agree with this map; plan 003 tooling enforces it.
- Field semantics (binding on plan 003/004 authors): `requires` = prerequisites the entry's core path depends on; `practices` = concepts from EARLIER entries this entry deliberately revisits in exercises (a reinforcement claim, not an exhaustive exercise inventory); `requires` and `practices` may overlap; an entry never lists its own `introduces` in `practices`.

- [ ] **Step 1: Write the failing coverage-map tests**

Append to `tests/test_book1_curriculum.py`:

```python
def load_map():
    data = yaml.safe_load((CURRICULUM / "coverage-map.yaml").read_text(encoding="utf-8"))
    assert data["map_version"] == 1
    return data["entries"]


def test_map_schema_and_id_contract():
    import re

    entries = load_map()
    kinds = {"unit": r"^unit-[0-9]{2}-[a-z0-9-]+$",
             "project": r"^project-[0-9]{2}-[a-z0-9-]+$",
             "checkpoint": r"^checkpoint-[0-9]{2}-[a-z0-9-]+$"}
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "duplicate entry ids"
    for e in entries:
        assert set(e) == {"id", "kind", "title", "lessons", "introduces", "requires", "practices"}
        assert e["kind"] in kinds and re.match(kinds[e["kind"]], e["id"]), f"bad id: {e['id']}"
        assert isinstance(e["lessons"], (int, float)) and e["lessons"] > 0


def test_lesson_budget_close_to_thirty():
    total = sum(e["lessons"] for e in load_map())
    assert 28 <= total <= 32, f"lesson budget {total} outside 28-32"


def test_all_referenced_concepts_exist():
    known = {c["id"] for c in load_concepts()}
    for e in load_map():
        for field in ("introduces", "requires", "practices"):
            unknown = set(e[field]) - known
            assert not unknown, f"{e['id']}.{field} references unknown concepts: {unknown}"


def test_every_concept_introduced_exactly_once():
    known = {c["id"] for c in load_concepts()}
    introduced = [c for e in load_map() for c in e["introduces"]]
    assert len(introduced) == len(set(introduced)), "concept introduced twice"
    assert set(introduced) == known, f"never introduced: {known - set(introduced)}"


def test_prereq_closure_planning_level():
    # Both requires AND practices may only use concepts introduced by EARLIER entries —
    # design §2's "nothing may be used before it is taught", enforced for every entry kind.
    seen: set[str] = set()
    for e in load_map():
        missing = (set(e["requires"]) | set(e["practices"])) - seen
        assert not missing, f"{e['id']} uses concepts not yet introduced: {missing}"
        seen |= set(e["introduces"])


def test_practice_coverage_planning_level():
    # Practicing means an entry OTHER than the introduction: practices-only union must
    # cover the whole registry, and no entry may "practice" what it itself introduces.
    for e in load_map():
        overlap = set(e["practices"]) & set(e["introduces"])
        assert not overlap, f"{e['id']} practices its own introductions: {overlap}"
        for field in ("introduces", "requires", "practices"):
            assert len(e[field]) == len(set(e[field])), f"{e['id']}.{field} has duplicates"
    # Coverage must hold WITHOUT the capstone: an omnibus final project must not be the
    # only place a concept is ever practiced (anti-tautology rule, gate finding sol #2).
    known = {c["id"] for c in load_concepts()}
    pre_capstone = {
        c for e in load_map() if e["id"] != "project-02-grand-adventure" for c in e["practices"]
    }
    assert pre_capstone == known, f"only the capstone practices: {known - pre_capstone}"


def test_checkpoints_only_assess_taught_concepts():
    seen: set[str] = set()
    for e in load_map():
        if e["kind"] == "checkpoint":
            assert not e["introduces"], f"{e['id']} introduces concepts"
            untaught = set(e["practices"]) - seen
            assert not untaught, f"{e['id']} assesses untaught concepts: {untaught}"
        seen |= set(e["introduces"])
```

- [ ] **Step 2: Run tests to verify the new ones fail**

Run: `uv run pytest tests/test_book1_curriculum.py -q`
Expected: registry test passes, the seven new tests FAIL (`coverage-map.yaml` not found).

- [ ] **Step 3: Write `book1/curriculum/coverage-map.yaml`**

The Year 1 arc — every entry opens with its hook (project-first law D-001); order is teaching order:

```yaml
map_version: 1
entries:
- id: unit-01-story-machine
  kind: unit
  title: "Mad-Libs Story Machine — your first programs"
  lessons: 2
  introduces: [run-program, print, comment, string-literal, variable, naming, input,
               string-concat, f-string, error-messages]
  requires: []
  practices: []
- id: unit-02-number-detective
  kind: unit
  title: "Number Detective — the guessing game"
  lessons: 3
  introduces: [int-type, arithmetic, type-conversion, boolean, comparison,
               if-statement, elif-else, import-statement, random-module, while-loop]
  requires: [print, input, variable, f-string]
  practices: [string-literal, naming, comment, run-program, error-messages]
- id: checkpoint-01-first-steps
  kind: checkpoint
  title: "Checkpoint 1 — First Steps"
  lessons: 0.5
  introduces: []
  requires: [print, input, variable, if-statement, while-loop]
  practices: [print, comment, string-literal, variable, naming, input, string-concat, f-string,
              int-type, arithmetic, type-conversion, boolean, comparison, if-statement,
              elif-else, while-loop]
- id: unit-03-turtle-art-studio
  kind: unit
  title: "Turtle Art Studio — drawing with loops"
  lessons: 3
  introduces: [turtle-basics, turtle-drawing, for-loop, range-function, loop-counter,
               nested-loops, float-type]
  requires: [import-statement, variable, arithmetic]
  practices: [naming, comment, run-program]
- id: unit-04-quiz-show
  kind: unit
  title: "Quiz Show — keeping score"
  lessons: 2
  introduces: [accumulator, logical-ops, conditional-nesting, break-statement]
  requires: [if-statement, elif-else, while-loop, comparison, input, f-string]
  practices: [boolean, type-conversion, loop-counter, error-messages]
- id: unit-05-function-factory
  kind: unit
  title: "Function Factory — greeting cards and turtle stamps"
  lessons: 3
  introduces: [def-function, parameters, return-value, scope]
  requires: [turtle-basics, turtle-drawing, for-loop, variable, f-string]
  practices: [range-function, loop-counter, arithmetic, nested-loops, float-type]
- id: checkpoint-02-loops-and-functions
  kind: checkpoint
  title: "Checkpoint 2 — Loops and Functions"
  lessons: 0.5
  introduces: []
  requires: [for-loop, while-loop, def-function]
  practices: [for-loop, range-function, while-loop, accumulator, logical-ops,
              conditional-nesting, def-function, parameters, return-value, scope,
              turtle-basics, turtle-drawing]
- id: project-01-arcade-night
  kind: project
  title: "Arcade Night — build your own mini-game"
  lessons: 2
  introduces: []
  requires: [def-function, parameters, return-value, while-loop, if-statement, random-module]
  practices: [print, input, f-string, accumulator, logical-ops, loop-counter,
              elif-else, break-statement, comparison, scope, import-statement, random-module]
- id: unit-06-secret-codes
  kind: unit
  title: "Secret Codes — ciphers and string surgery"
  lessons: 2
  introduces: [string-index, string-slice, string-methods, in-operator]
  requires: [for-loop, string-concat, def-function, parameters, return-value]
  practices: [f-string, accumulator, if-statement, loop-counter]
- id: unit-07-high-score-hall
  kind: unit
  title: "High-Score Hall of Fame — lists"
  lessons: 2
  introduces: [list-literal, list-index, list-append, list-loop, list-sort, builtin-functions]
  requires: [for-loop, variable, def-function, comparison]
  practices: [accumulator, f-string, while-loop, string-methods]
- id: unit-08-word-wizard
  kind: unit
  title: "Word Wizard — dictionaries and translation games"
  lessons: 2
  introduces: [dict-literal, dict-access, dict-loop]
  requires: [list-loop, string-methods, in-operator, def-function]
  practices: [list-literal, list-append, if-statement, f-string]
- id: checkpoint-03-data-wrangler
  kind: checkpoint
  title: "Checkpoint 3 — Data Wrangler"
  lessons: 0.5
  introduces: []
  requires: [list-literal, dict-literal, string-index]
  practices: [string-index, string-slice, string-methods, in-operator, list-literal,
              list-index, list-append, list-loop, list-sort, builtin-functions,
              dict-literal, dict-access, dict-loop]
- id: unit-09-save-point
  kind: unit
  title: "Save Point — files that remember"
  lessons: 2
  introduces: [file-read, file-write, with-statement]
  requires: [list-append, string-methods, def-function, for-loop]
  practices: [list-loop, dict-access, f-string, in-operator]
- id: unit-10-pet-simulator
  kind: unit
  title: "Pet Simulator — a gentle intro to objects"
  lessons: 3
  introduces: [class-def, init-method, attributes, methods]
  requires: [def-function, parameters, return-value, dict-access, while-loop]
  practices: [scope, f-string, if-statement, accumulator, list-append]
- id: checkpoint-04-year-one-finale
  kind: checkpoint
  title: "Checkpoint 4 — Year One Finale"
  lessons: 0.5
  introduces: []
  requires: [file-read, class-def]
  practices: [file-read, file-write, with-statement, class-def, init-method,
              attributes, methods, dict-loop, list-sort, return-value]
- id: project-02-grand-adventure
  kind: project
  title: "Grand Adventure — the Year 1 capstone"
  lessons: 4
  introduces: []
  requires: [class-def, init-method, attributes, methods, file-read, file-write,
             dict-literal, list-literal, def-function]
  practices: [run-program, error-messages, print, comment, input, string-literal, f-string,
              string-concat, string-index, string-slice, string-methods, in-operator,
              variable, naming, int-type, float-type, arithmetic, type-conversion, boolean,
              comparison, logical-ops, if-statement, elif-else, conditional-nesting,
              while-loop, break-statement, for-loop, range-function, loop-counter,
              accumulator, nested-loops, import-statement, random-module,
              def-function, parameters, return-value, scope, list-literal, list-index,
              list-append, list-loop, list-sort, builtin-functions, dict-literal,
              dict-access, dict-loop, file-read, file-write, with-statement,
              class-def, init-method, attributes, methods]
```

Note: the capstone's `practices` is the full registry MINUS `turtle-basics`/`turtle-drawing` (a text-adventure capstone need not draw — claiming turtle practice here would be false; the arcade variant may still use it informally). Coverage does not depend on this list: `test_practice_coverage_planning_level` requires the pre-capstone union alone to cover the registry. If the registry changes, regenerate this list rather than editing it by hand.

- [ ] **Step 4: Run tests green**

Run: `uv run pytest tests/test_book1_curriculum.py -q`
Expected: PASS (8 tests). If `test_practice_coverage_planning_level` or `test_every_concept_introduced_exactly_once` fails, fix the named concept in the map (typically the capstone `practices` list) — never by deleting registry concepts.

- [ ] **Step 5: Commit**

```bash
git add book1/curriculum/coverage-map.yaml tests/test_book1_curriculum.py
git commit -m "feat(book1): Year 1 coverage map — 10 units, 2 projects, 4 checkpoints (plan 002)"
```

### Task 3: Year 1 syllabus

**Files:**
- Modify: `book1/syllabus.md` (replace the plan-002 placeholder entirely)
- Test: append one consistency test to `tests/test_book1_curriculum.py`

**Interfaces:**
- Consumes: entry ids and titles from Task 2's map.
- Produces: the human/teacher-facing arc document; plan 004+ unit plans cite it.

- [ ] **Step 1: Write the failing consistency test**

Append to `tests/test_book1_curriculum.py`:

```python
def test_syllabus_table_matches_map():
    import re

    syllabus = (REPO / "book1" / "syllabus.md").read_text(encoding="utf-8")
    positions = []
    for e in load_map():
        # A table row must carry the id, kind, and lesson count together, e.g.
        # "| `unit-01-story-machine` | unit | 2 |"
        row = re.search(
            rf"\|\s*`{re.escape(e['id'])}`\s*\|\s*{e['kind']}\s*\|\s*{e['lessons']:g}\s*\|",
            syllabus,
        )
        assert row, f"syllabus table missing/incorrect row for {e['id']}"
        positions.append(row.start())
    assert positions == sorted(positions), "syllabus table order differs from map order"
```

Run: `uv run pytest tests/test_book1_curriculum.py -q` → the new test FAILS (placeholder syllabus).

- [ ] **Step 2: Write `book1/syllabus.md`**

```markdown
# Book 1 — Year 1 Syllabus

Project-first Python fundamentals for middle school students with zero programming experience.
~30 lessons of 60–90 minutes across one school year.
Every unit opens with a project the students want to build; concepts arrive only when the project needs them (decision D-001).
Machine-readable arc: `curriculum/coverage-map.yaml` against `curriculum/concepts.yaml`.
Every unit ships stretch ("Challenge") exercises for faster students; core content never depends on them.

## Arc at a glance

| # | Entry | Kind | Lessons | The hook |
|---|-------|------|---------|----------|
| 1 | `unit-01-story-machine` | unit | 2 | Build a Mad-Libs machine that writes silly stories from your friends' words. |
| 2 | `unit-02-number-detective` | unit | 3 | The computer picks a secret number — outsmart it in as few guesses as possible. |
| 3 | `checkpoint-01-first-steps` | checkpoint | 0.5 | Show what you've got: stories and guessing. |
| 4 | `unit-03-turtle-art-studio` | unit | 3 | Command a robot turtle to draw spirals, stars, and gallery-worthy art. |
| 5 | `unit-04-quiz-show` | unit | 2 | Host your own quiz show with scores, streaks, and sudden death. |
| 6 | `unit-05-function-factory` | unit | 3 | Package your best tricks into reusable machines — greeting cards and turtle stamps. |
| 7 | `checkpoint-02-loops-and-functions` | checkpoint | 0.5 | Loops and functions, proven. |
| 8 | `project-01-arcade-night` | project | 2 | Milestone: design and build your own mini-game; class plays everyone's. |
| 9 | `unit-06-secret-codes` | unit | 2 | Encrypt messages with ciphers only your friends can crack. |
| 10 | `unit-07-high-score-hall` | unit | 2 | A Hall of Fame that tracks and sorts every score in the class. |
| 11 | `unit-08-word-wizard` | unit | 2 | A translator and word-game engine powered by dictionaries. |
| 12 | `checkpoint-03-data-wrangler` | checkpoint | 0.5 | Strings, lists, and dicts, proven. |
| 13 | `unit-09-save-point` | unit | 2 | Games that remember you — save and load real files. |
| 14 | `unit-10-pet-simulator` | unit | 3 | Adopt a virtual pet: feed it, teach it tricks, keep it alive (objects!). |
| 15 | `checkpoint-04-year-one-finale` | checkpoint | 0.5 | Files and objects, proven. |
| 16 | `project-02-grand-adventure` | project | 4 | Capstone: a text adventure (or arcade game) using everything from the year. |

Lesson budget: the map's `lessons` values are workload units summing to 32 — 24 unit lessons + 6 project lessons + 4 half-lesson checkpoints.
On the calendar this fits ~30–32 class sessions: each checkpoint's half-lesson is absorbed into the session that opens the following unit when the schedule is tight.
Turtle-based lessons (units 03/05) run as `.py` scripts launched from the JupyterLab/VS Code terminal — turtle opens its own window and does not draw inside notebook cells; all other work stays in notebooks.

## Term shape

- **Term 1 (foundations):** units 01–02, checkpoint 01 — output, input, variables, decisions, first loops.
- **Term 2 (loops & functions):** units 03–05, checkpoint 02, project 01 — turtle graphics, for/while mastery, functions.
- **Term 3 (data):** units 06–08, checkpoint 03 — string surgery, lists, dictionaries.
- **Term 4 (persistence & objects):** units 09–10, checkpoint 04, project 02 — files, a gentle OOP intro, capstone.

## Rules this syllabus is bound by

- Prereq closure: no concept appears before the entry that introduces it (`coverage-map.yaml` is the contract; enforced by `tests/test_book1_curriculum.py` now, `tools/` from plan 003).
- Practice coverage: every concept is practiced beyond its introduction.
- Checkpoints assess only concepts already taught; they introduce nothing.
- Stretch exercises may preview, but core paths never depend on stretch content.
```

- [ ] **Step 3: Run all curriculum tests green**

Run: `uv run pytest tests/test_book1_curriculum.py -q`
Expected: PASS (9 tests).

- [ ] **Step 4: Commit**

```bash
git add book1/syllabus.md tests/test_book1_curriculum.py
git commit -m "feat(book1): Year 1 syllabus — project-first arc over 30 lessons (plan 002)"
```

### Task 4: bookkeeping + full gate

**Files:**
- Modify: `TODO.md` (flip plan-002 box during Ship, not here; this task only verifies)

- [ ] **Step 1: Run the full local gate**

Run: `bash scripts/ci-local.sh`
Expected: ALL GREEN (now 11 tests total: 2 registry/skeleton + 9 curriculum).

- [ ] **Step 2: No commit** — Ship-step items (TODO flip, post-execution report) land with the ship commit.

---

## Plan Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE
- Hand-verified all map invariants against the embedded tests (52 introduced-exactly-once, prereq closure, checkpoint rules, disjointness, capstone = full registry, budget 32 ∈ [28,32]); caught and fixed four self-inconsistencies pre-commit (concept count, trivially-passing coverage test, capstone duplicates, budget wording).

### Review 2 — [fable] (2026-09-06)
- **Verdict**: APPROVE WITH NITS
- Mechanically verified every embedded-test invariant plus stricter extras (all pass, including the unenforced practices-ordering invariant); arc judged pedagogically sound (while-before-for explicitly defensible; hooks age-appropriate; OOP landing gentle).
1. `[OPEN]` Turtle requires a Tk window and won't run in a notebook cell — contradicts design's notebooks-as-medium unless the delivery assumption (turtle lessons launch as .py scripts from a JupyterLab/VS Code terminal) is recorded now, before plan 004 hits it. Priority: Should Fix.
2. `[OPEN]` Test hole: `practices` ordering unenforced for units/projects — an entry could practice a concept introduced later and pass. Data is currently clean (verified); fold practices into the closure walk. Priority: Should Fix.
3. `[OPEN]` Unit 02 heaviest load (12 concepts) at the most fragile point; `float-type` not demanded by an integer guessing game (violates D-001's "only when the project demands it"). Priority: Should Fix.
4. `[OPEN]` No registry concepts for "running a program" / "reading error messages" — unavoidable in lesson 1, formally unteachable under the closed vocabulary. Priority: Nice to Have.
5. `[OPEN]` Budget sits at the test's exact upper bound (32) and the syllabus sentence double-counts checkpoint slots. Priority: Nice to Have.
6. `[OPEN]` Concept-id kebab check weaker than the entry-id regexes. Priority: Nice to Have.
7. `[OPEN]` Syllabus test is substring-only; note that plan 003 tooling should also check table kinds/lesson counts. Priority: Nice to Have.

### Review 3 — [glm] (2026-09-06)
- **Verdict**: APPROVE WITH NITS (no blockers)
- Extracted and ran the embedded pytest suite against the embedded YAML: 9/9 pass; all invariants hold; exemption legitimate; arc pedagogically sound.
1. `[OPEN]` Unit 02 front-loads 12 introductions in 3 lessons at the most fragile point (overlaps fable #3); move `break-statement`/`conditional-nesting` out or document the pacing call. Priority: Should Fix.
2. `[OPEN]` Capstone's all-52 `practices` masks that `import-statement` and `random-module` get no deliberate pre-capstone practice; strengthen test or add pre-capstone practice. Priority: Should Fix.
3. `[OPEN]` Syllabus test substring-only (overlaps fable #7). Priority: Nice to Have.
4. `[OPEN]` Budget narrative arithmetic confusing (overlaps fable #5). Priority: Nice to Have.
5. `[OPEN]` `practices` field semantics (cross-unit revisits, not exhaustive exercise coverage) should be stated in the Task 2 Interfaces block. Priority: Nice to Have.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT (data currently consistent — static trace all-PASS — but test rigor insufficient)
1. `[OPEN]` (Must Fix) Practice ordering unenforced for units/projects (overlaps fable #2): future-concept `practices` would pass the suite.
2. `[OPEN]` (Must Fix) Capstone's all-52 omnibus makes practice coverage tautological, and claims turtle practice in a possibly text-only capstone; `import-statement`/`random-module` get no real pre-capstone practice.
3. `[OPEN]` (Should Fix) Unit 02 overloaded; `float-type` not demanded by an integer guessing game (overlaps fable #3, glm #1).
4. `[OPEN]` (Should Fix) Syllabus test substring-only (overlaps fable #7, glm #3).
5. `[OPEN]` (Should Fix) Concept-id test doesn't enforce its kebab contract (overlaps fable #6).
6. `[OPEN]` (Should Fix) `list-methods` groups built-ins (`len/min/max`) with the `.sort()` method — teaches kids `scores.len()`.
7. `[OPEN]` (Nice to Have) Checkpoint scheduling wording ambiguous (overlaps fable #5, glm #4).
8. `[OPEN]` (Nice to Have) "docs-only" imprecise — the plan also ships test code.

### Revision 2 resolutions (2026-09-06) — applied across all three reviews
- fable 1 `[FIXED]`: turtle delivery assumption recorded in Global Constraints and the syllabus; D-005 proposal flagged for ship time (governance needs user sign-off).
- fable 2 / sol 1 `[FIXED]`: closure test now walks `requires` ∪ `practices` for EVERY entry.
- fable 3 / glm 1 / sol 3 `[FIXED]`: unit 02 slimmed to 10 introductions — `float-type` moved to unit 03 (turtle angles like `360/7` genuinely demand floats), `break-statement` to unit 04 (sudden-death round); binding pacing directive for units 01–02 teacher notes added to Global Constraints.
- fable 4 `[FIXED]`: `run-program` and `error-messages` added to the registry, introduced in unit 01, practiced in units 02/03/04.
- fable 5 / glm 4 / sol 7 `[FIXED]`: budget wording rewritten (32 workload units, ~30–32 calendar sessions, absorption rule stated).
- fable 6 / sol 5 `[FIXED]`: concept-id test now enforces `[a-z0-9]+(-[a-z0-9]+)*` via `re.fullmatch`.
- fable 7 / glm 3 / sol 4 `[FIXED]`: syllabus test now matches full table rows (id + kind + lesson count) and asserts map order.
- glm 2 / sol 2 `[FIXED]`: coverage test now requires the PRE-capstone practices union to cover the registry (anti-tautology rule); `import-statement`/`random-module` practiced in project 01; capstone list regenerated as registry minus the turtle pair with an honesty note.
- glm 5 `[FIXED]`: `requires`/`practices` semantics documented in the Task 2 Interfaces block.
- sol 6 `[FIXED]`: `list-methods` split into `list-sort` (collections) and `builtin-functions` (functions); all references updated. Registry is now 55 concepts.
- sol 8 `[FIXED]`: Out-of-scope wording now says "curriculum-data/docs plan (plus planning-level pytest code)".

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)

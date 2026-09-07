# Plan 014 — Checkpoint 04 Year One Finale Implementation Plan

**Goal:** Ship `checkpoint-04-year-one-finale` — the Year-1 finale assessment — where students
demonstrate the term's two big skills together: OBJECTS (define a class with `__init__` + methods)
and FILES (write data to a file and load it back), plus dict-looping and list-sorting.

**Architecture:** Standard checkpoint pipeline (plan 005/006), plus the file-I/O infra from unit 09.
Two things land UP FRONT in Phase A: (1) a `.gitignore` entry for the checkpoint's runtime scratch
file, and (2) the substrate map amendment (scanner-DERIVED + validated green). This checkpoint
combines the two hardest domains — file I/O in CI-executed notebooks (unit 09) and OOP (unit 10) —
so it inherits both units' binding rules.

**Spec:** `book1/curriculum/coverage-map.yaml` (binding, amended); plan 005/006 checkpoint
conventions; design-000 §4 (notebook execution); D-001.

## Global Constraints

- Checkpoint conventions (plan 005/006/011): `checkpoint.ipynb` has `## Question N` headings (6–8,
  sequential, unique), each followed by an EMPTY student code cell; any broken/"fix this" snippet
  lives in a MARKDOWN fence (never an executable code cell); NO stretch tags; NO solutions in the
  checkpoint. `solutions.ipynb` mirrors `## Question N`, runs top-to-bottom clean and input-free
  with non-vacuous asserts (no tautologies). `teacher-notes.md` carries SIX headings incl.
  **Grading**. Checkpoint dir prefix `checkpoint-04-`. Manifest map-equal. INPUT-FREE everywhere
  (a checkpoint gives all data — NO `input()`).
- Coverage-map amendment (EXACTLY this, scanner-DERIVED + validated green):
  - append to `checkpoint-04-year-one-finale.requires` — `for-loop`.
  - append to `checkpoint-04-year-one-finale.practices` — `def-function, parameters, dict-literal,
    list-literal, list-append, list-index, for-loop, if-statement, in-operator, arithmetic,
    int-type, type-conversion, string-concat, string-literal, string-methods, f-string, print,
    variable, boolean, error-messages, accumulator, elif-else`. NOTE: `accumulator` covers the `heal` method's
    `self.health = self.health + amount` (read-modify-write on an attribute — my scanner initially
    missed attribute-target accumulators; scanner fixed + `accumulator` added).
  - All introduced by units 01–10; `checkpoint-only-taught` holds. Apply surgically (no YAML
    round-trip). Manifest carries the amended lists.
- **FILE-I/O CI-SAFETY (binding, from unit 09):** CI executes `solutions.ipynb` with cwd = the
  checkpoint dir. So: the ONE file question is WRITE-THEN-READ within the solution notebook
  (creates the file it reads); write mode `"w"` (deterministic, idempotent); the scratch filename
  `finale.txt` is gitignored in Phase A; NO append mode; NO `os`/`tempfile`/`pathlib`; the file
  stores ONE integer per line and is read with `for line in f` + `.strip()` + `int(...)` — NO
  `.split()`. Phase C runs a CLEAN-SLATE `rm -f` of `finale.txt` before the final ci-local so green
  proves create-before-read.
- **OOP CI-SAFETY (binding, from unit 10):** the class question uses ONE plain class with `__init__`
  + instance methods. FORBIDDEN: inheritance (`class X(Y)`), any dunder beyond `__init__`,
  decorators/`@property`, `isinstance`/`type`/`getattr`/`setattr`.
- **Closure (binding):** only concepts taught ≤ unit 10. `builtin-functions` (`len`/`max`/`min`) is
  NOT in the union and must NOT appear ANYWHERE — including asserts (only bare comparison operators
  are exempt scaffolding); assert list state via INDEX (`scores[0]`, `pets[1].name`), the sorted
  top via `scores[0]` after `.sort(reverse=True)`. String methods stay in the taught subset
  (upper/lower/strip/replace, NO `.split`). Lists use `.append`/`.sort` only; dicts use
  `[key]`/`.items` only (NO `.get`/`.pop`/`.update`). NO nested loops, NO comprehensions, NO sets.
- **Deliberate-bug beat (Q8):** ONE fix-the-bug question — a `KeyError` (accessing a missing dict
  key) OR an `AttributeError` (a typo'd attribute) in a MARKDOWN fence (never executed); the student
  rewrites the safe/correct line in the code cell; names the traceback's final line (error-messages).
  If the bug is file-related it must NOT be a bare read of a missing file in an executable cell.
- Process (standing): no commits while a `[sol]` review is in flight; codex prompts name the
  in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Checkpoint plan → Phase C is the mandatory named verification phase. Out of scope: project 02
(later plan); the latent practice-completeness hygiene PR + scanner promotion (tracked separately);
PDF handouts; any map edit beyond the Phase-A substrate amendment; inheritance/dunders-beyond-init;
`.split()`; append-mode files; `os`/`tempfile`/`pathlib`; `len`/`max`/`min`.

## Phases

Dispatch per AGENTS.md: checkpoint question STATEMENTS via codex; solutions via a SEPARATE blind
codex session; teacher notes inline; gitignore + map amendment + manifest inline.

### Phase A — gitignore + map amendment + manifest (inline)

1. Append to `.gitignore` (surgical): a comment + `book1/checkpoints/checkpoint-04-year-one-finale/finale.txt`.
2. Amend `coverage-map.yaml` per Global Constraints (surgical, requires + practices).
3. `book1/checkpoints/checkpoint-04-year-one-finale/manifest.yaml`, map-equal to the amended entry.
- **Acceptance (Phase A):** the gitignore + map amendment ALONE are green (`uv run pytest -q` +
  `ci-local`) before any checkpoint directory exists.

### Phase B — checkpoint-04-year-one-finale content (8 questions)

Blueprint (requires file-read, class-def, for-loop; practices = the 10 headline concepts + amended
22-concept substrate):
- Title: `# Checkpoint 4 — Year One Finale`. A short framing line (put the year's biggest skills
  together — objects and files).
- **Q1 — define a class (class-def, init-method, attributes):** define `class Hero:` with
  `def __init__(self, name):` setting `self.name = name` and `self.health = 10`. Make
  `hero = Hero("Ada")` and print `hero.name` and `hero.health`.
- **Q2 — a method (methods, parameters, return-value, arithmetic):** add `def heal(self, amount):`
  that does `self.health = self.health + amount` and returns the new health. Call `hero.heal(3)`
  and print the returned value.
- **Q3 — write a save file (file-write, with-statement, for-loop, type-conversion, string-concat):**
  given `scores = [40, 90, 20]`, `with open("finale.txt", "w") as f:` write each score as text +
  `"\n"` (one integer per line).
- **Q4 — load the save file (file-read, for-loop, list-append, string-methods, type-conversion):**
  `loaded = []`; `with open("finale.txt") as f: for line in f: loaded.append(int(line.strip()))`;
  print `loaded`.
- **Q5 — rank the scores (list-sort, boolean, list-index):** `loaded.sort(reverse=True)`; print the
  top score `loaded[0]` (NO `max()`).
- **Q6 — walk an inventory (dict-literal, dict-loop, f-string):** build
  `inventory = {"sword": 1, "potion": 3}`; loop `for item, count in inventory.items():` printing
  each `item` and `count`.
- **Q7 — check the inventory (in-operator, if-statement, dict-access):** print whether
  `"sword" in inventory` (a True/False value — boolean); then an `if "shield" in inventory:` /`else:`
  that prints the shield count or "no shield".
- **Q8 — fix the bug (error-messages, dict-access):** a MARKDOWN fence shows
  `inventory = {"sword": 1}` then `print(inventory["shield"])` raising `KeyError: 'shield'`; the
  student rewrites it safely (e.g. an `if "shield" in inventory:` guard, or a printed default);
  name the traceback's final line as the clue.
- Solutions: mirror `## Question N`, execute headless + input-free, WRITE-THEN-READ `finale.txt`
  (deterministic `"w"`, gitignored), non-vacuous asserts — `hero.health == 13` after `heal(3)`;
  `loaded == [40, 90, 20]` after load; `loaded[0] == 90` after reverse-sort; a dict membership
  assert on a computed lookup; the Q8 safe result. NO `len`/`max`/`min`; NO `.split`; NO append
  mode; index-based list asserts.
- Teacher notes: SIX headings incl. `## Grading` — per-question points summing to a total; full-
  credit + partial-credit notes; 35–40 min pacing (this is the hardest checkpoint — files + OOP);
  common mistakes (forgetting `self`; KeyError vs a guard; `.sort()` returns None; forgetting
  `.strip()` before `int()`; a typo'd attribute).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; **CLEAN-SLATE RUN** (`rm -f book1/checkpoints/
checkpoint-04-year-one-finale/finale.txt` before the final `ci-local.sh` so green proves
create-before-read); `ci-local.sh` ALL GREEN; AST concept-scanner scoped to checkpoint-04 clean
(advisory — user-defined methods exempt); solutions execute with non-vacuous asserts; manifest
map-equal; the scratch `finale.txt` gitignored (no git noise).
Reviewer duties: blind-solve every question; cumulative closure (only ≤unit-10 — NO inheritance/
dunders-beyond-init, NO `.split`, NO `len`/`max`/`min` (index-based asserts), NO append mode, NO
`os`/`tempfile`, NO nested loops — check explicitly); the file question is write-then-read + no-split;
the class is a single plain class; each question solvable + reference correct; asserts non-vacuous;
grading usable; timing; no `input()` anywhere; assesses only taught skills.

**Acceptance criteria:** the checkpoint directory complete; `uv run pytest -q` green; ci-local ALL
GREEN (clean-slate); concept-scanner clean; `finale.txt` gitignored; content gate 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. Substrate scanner-DERIVED from the planned 8-question code (files + OOP + dict-loop +
list-sort) + validated green. This is the hardest checkpoint — it combines unit-09 file I/O and
unit-10 OOP — so it inherits BOTH units' hard-won binding rules: file-I/O CI-safety (write-then-read
`finale.txt`, gitignored, deterministic `"w"`, no `.split`, clean-slate Phase-C run) and OOP safety
(single plain class, no inheritance/dunders-beyond-init). Closure: NO `len`/`max`/`min` (index-based
asserts, sorted-top via `[0]`); membership-based Q7; KeyError fix-the-bug in a markdown fence.
Input-free (checkpoint gives all data). `practices ∩ introduces` empty (introduces = []).

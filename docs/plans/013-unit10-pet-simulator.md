# Plan 013 — Unit 10 Pet Simulator Implementation Plan

**Goal:** Ship `unit-10-pet-simulator` — Book 1's OOP unit and its LAST unit — where students build
a virtual pet as a CLASS: `__init__` sets up each pet's attributes (name, hunger, happiness),
methods (`feed`, `play`, `status`) read and change those attributes, and a little simulation runs
several pets through a few rounds.

**Architecture:** Standard unit pipeline (plan 004), no new tooling in the unit itself. ONE map
amendment lands UP FRONT (the standing substrate audit, DERIVED with the AST concept-scanner from
the planned Pet-class code): the entry lists only OOP headline concepts + a few practices and omits
the substrate the class bodies use — `arithmetic` (hunger/happiness changes), `comparison`+`elif-else`
(the `status` mood ladder), `dict-literal` (a foods table), `for-loop`+`list-literal` (a list of
pets), `print`/`variable`/`string-literal`/`int-type`, and `error-messages` (an AttributeError beat)
→ practices. All taught by units 01–09; verified green in scratch.

**Spec:** `book1/curriculum/coverage-map.yaml` (binding, amended); plan 004 unit conventions; D-001.

## Global Constraints

- All plan-004 unit Global Constraints apply (map-equal manifest, hook-first, exercise ≥6 core +
  ≥2 stretch, solution floors + per-line bans, non-vacuous asserts incl. no tautologies, five
  teacher-notes headings, per-lesson allocation for THREE lessons, commit trailers).
- Coverage-map amendment (EXACTLY this, pre-audited + scanner-derived green):
  - `unit-10-pet-simulator.requires` — UNCHANGED (`def-function, parameters, return-value,
    dict-access, while-loop`; methods are functions with parameters/return, so these are the OOP
    prereqs).
  - append to `unit-10-pet-simulator.practices` — `arithmetic, comparison, dict-literal, elif-else,
    for-loop, list-literal, print, variable, string-literal, int-type, error-messages`.
  - All introduced by units 01–09; `practices ∩ introduces` empty (introduces = class-def/
    init-method/attributes/methods). Apply surgically (no YAML round-trip). Manifest carries the list.
- **Pre-gate closure self-check (standing, with an OOP caveat):** run the AST concept-scanner scoped
  to unit-10 before the `[sol]` content gate. NOTE: the scanner's untaught-method check flags
  USER-DEFINED class methods (`feed`/`play`/`status`/…) as "untaught" because they are not in its
  library allowlist — these are FALSE POSITIVES (they ARE the `methods` concept this unit teaches).
  Phase B extends the scanner to exempt method names defined in the notebooks' own `class` bodies;
  a genuinely-untaught library method (`.sort`, `.split`, etc.) is the only real hit.
- **OOP mechanics (binding):** a class is `class Pet:` with an `__init__(self, ...)` that assigns
  `self.<attr> = ...`; methods are `def <name>(self, ...):` inside the class and read/modify
  `self.<attr>`. Objects are made with `Pet(...)` and used as `buddy.<attr>` / `buddy.<method>(...)`.
  FORBIDDEN (untaught): class INHERITANCE (`class X(Y):`), any dunder beyond `__init__`
  (`__str__`/`__repr__`/`__eq__`/…), `@property`/decorators, `@classmethod`/`@staticmethod`,
  `isinstance`/`type`/`hasattr`/`getattr`/`setattr`, `self.__dict__`. Keep it one plain class with
  `__init__` + a few instance methods.
- **Closure (binding):** only concepts taught through unit 10. NO files (`open`) — that was unit 09;
  NO `.split()`; string methods stay in the taught subset; lists use `.append`/`.sort` only; dicts
  use `[]`/`.get`/`.items`. NO nested loops, NO comprehensions, NO sets. The `status` mood ladder
  uses `comparison` + `elif-else` (this unit DOES teach comparison-based branching, unlike the
  membership-only checkpoint 03).
- **Input discipline:** executed cells (lessons + solutions) are input-free; `input()` only in an
  exercise PROMPT with a parameterized solution.
- **Deliberate-bug beat:** an `AttributeError` (e.g. reading `buddy.hapiness` — a typo'd attribute,
  or calling a method the class does not define) in a `no-exec`-tagged cell, traceback in a following
  markdown cell (error-messages). NO file I/O, so no FileNotFoundError here.
- Process (standing): no commits while a `[sol]` review is in flight; codex prompts name the
  in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Content plan → Phase C is the mandatory named verification phase. Out of scope: checkpoint 04 /
project 02 (later plans); the latent practice-completeness hygiene PR + scanner promotion (tracked
separately); PDF handouts; any map edit beyond the Phase-A substrate amendment; class inheritance;
dunders beyond `__init__`; decorators/properties; `isinstance`/`type`.

## Phases

Dispatch per AGENTS.md: lesson/exercise statements via codex; solutions via a SEPARATE blind codex
session; teacher notes inline; map amendment + manifest inline; scanner OOP-exemption enhancement
inline (scratchpad tool, not shipped).

### Phase A — map amendment + manifest (inline)

1. Amend `coverage-map.yaml` per Global Constraints (surgical, practices only; requires unchanged).
2. `book1/units/unit-10-pet-simulator/manifest.yaml`, map-equal to the amended entry.
- **Acceptance (Phase A):** the map amendment ALONE is green (`uv run pytest -q` + `ci-local`)
  before any unit directory exists.

### Phase B — unit-10-pet-simulator content (3 lessons)

Blueprint (introduces class-def, init-method, attributes, methods; requires def-function, parameters,
return-value, dict-access, while-loop; practices scope, f-string, if-statement, accumulator,
list-append, + amended arithmetic/comparison/dict-literal/elif-else/for-loop/list-literal/print/
variable/string-literal/int-type/error-messages):
- Hook: PET SIMULATOR — adopt a virtual pet that has its OWN name and mood and remembers them; feed
  it and play with it and watch its stats change. The teacher "adopts" a pet live and the class
  suggests actions.
- **Lesson 1 (class-def, init-method, attributes):** `class Pet:` with `def __init__(self, name):
  self.name = name; self.hunger = 5; self.happiness = 5`. Make a pet `buddy = Pet("Buddy")` and read
  its attributes `buddy.name`, `buddy.hunger` (print them). Explain `self` is "this particular pet",
  and each `Pet(...)` gets its OWN attributes (make two pets, show their hungers are independent —
  the `scope`/identity idea).
- **Lesson 2 (methods):** add methods inside the class — `feed(self, amount)` does `self.hunger =
  self.hunger - amount` (accumulator-on-attribute + arithmetic) and returns the new hunger;
  `play(self)` does `self.happiness = self.happiness + 1`; `status(self)` prints an f-string and uses
  a mood ladder `if self.hunger > 6: "hungry"  elif self.hunger < 3: "stuffed"  else: "content"`
  (comparison + elif-else). Call `buddy.feed(2)`, `buddy.play()`, `buddy.status()`.
- **Lesson 3 (a little simulation):** a `foods = {"apple": 2, "steak": 4}` table (dict-literal +
  dict-access) feeds by name; a LIST of pets `pets = []` / `pets.append(Pet("Rex"))` (list-literal +
  list-append), then `for pet in pets: pet.status()` (for-loop). A `while rounds > 0:` loop
  (while-loop, from requires) runs a few play/feed rounds. The `no-exec` AttributeError beat
  (`buddy.hapiness` typo) + traceback (error-messages) — name why the attribute must match `__init__`.
- Exercises ≥6 core + ≥2 stretch: make-a-pet (class + __init__ + read attributes), two-pets
  (independent attributes), add-a-feed-method (method that changes an attribute + returns), the-mood-
  ladder (status with comparison/elif-else), a-pet-list (list of pets + for-loop status), feed-from-
  the-foods-table (dict-access), type-a-name (input PROMPT → parameterized solution making a pet),
  fix-the-attribute-typo (the AttributeError → correct the attribute name); stretch: happiest-pet
  (loop the pets, track the max happiness — accumulator/comparison), a-play-until-happy `while` loop.
- Solutions: execute headless, input-free, non-vacuous asserts — `buddy.hunger == 3` after
  `feed(2)` from 5; two pets' attributes independent (`a.hunger != b.hunger` after feeding one — the
  `!=` lives only in the assert); a mood-ladder assert (a pet with hunger 8 → "hungry"); a
  list-of-pets length assert. No inheritance, no dunders beyond `__init__`.
- Teacher notes: five headings, per-lesson allocation for THREE lessons (L1 class/attributes, L2
  methods, L3 simulation), 60-min cuts, differentiation; common mistakes (forgetting `self` in a
  method signature or body; a typo'd attribute → AttributeError; expecting two pets to share
  attributes; changing `self.hunger` but forgetting to `return` when a value is needed).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN; AST concept-scanner scoped to unit-10 clean
AFTER the OOP-exemption enhancement (user-defined class methods exempt; only genuinely-untaught
library methods flagged) — advisory, closure enforced by reviewers + blind-solve; solutions execute
with non-vacuous asserts; manifest map-equal.
Reviewer duties: blind-solve exercises; cumulative closure (only ≤unit-10 — NO inheritance, NO
dunders beyond `__init__`, NO decorators/properties, NO `isinstance`/`type`/`getattr`, NO files/
`.split`/nested-loops/comprehensions — check explicitly); every method takes `self`; attributes set
in `__init__` match those read; the AttributeError beat is `no-exec`; solutions non-vacuous/complete;
grading usable; three-lesson timing; hook-first; age-appropriate for a first OOP encounter.

**Acceptance criteria:** the unit directory complete; `uv run pytest -q` green; ci-local ALL GREEN;
concept-scanner clean (post-enhancement); content gate 4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. Substrate scanner-DERIVED from the planned Pet-class code + validated green. This is the
LAST Book-1 unit (3 lessons) and the first OOP encounter, so the constraints hard-forbid everything
beyond a single plain class with `__init__` + instance methods (no inheritance/dunders/decorators/
`isinstance`). Closure: no files (unit 09), comparison-based `status` ladder is in-scope (amended).
The scanner's untaught-method check will FALSE-POSITIVE on user-defined methods (`feed`/`play`/
`status`) — Phase B extends it to exempt names defined in the notebooks' own `class` bodies.
`practices ∩ introduces` empty. AttributeError deliberate-bug beat homes `error-messages` in a
`no-exec` cell (no file I/O here).

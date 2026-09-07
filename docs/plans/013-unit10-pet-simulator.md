# Plan 013 — Unit 10 Pet Simulator Implementation Plan

**Goal:** Ship `unit-10-pet-simulator` — Book 1's OOP unit and its LAST unit — where students build
a virtual pet as a CLASS: `__init__` sets up each pet's attributes (name, hunger, happiness),
methods (`feed`, `play`, `pass_time`, `status`) read and change those attributes, and a small FLAT
simulation gives a list of pets one status/time pass and plays one pet until it is happy.

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
  - REMOVE `scope` from the pre-existing `practices` (sol plan-review): a first OOP unit does not
    teach local-vs-global scope, independent instances are NOT scope, and the incidental method-local
    variables do not amount to a deliberate scope beat. `scope` remains practiced in checkpoint-02
    and the project-02 capstone, so removal is closure-safe (not a capstone-only concept).
  - append to `unit-10-pet-simulator.practices` — `arithmetic, comparison, dict-literal, elif-else,
    for-loop, list-loop, list-literal, list-index, print, variable, string-literal, int-type,
    error-messages, input`. Notes: `list-index` covers `pets[1]` (used in the index-based list-state
    assert that replaced `len`, and any `pets[0]` access — introduced unit-07, closure-safe; glm
    round-2 caught it used-but-unlisted). `input` homed by the `type-a-name` exercise PROMPT only — prose, not an
    executable cell; solution parameterized with a fixed name, matching units 07/08/09 (fable
    plan-review). `list-loop` covers `for pet in pets` (looping over a LIST — the registry's
    list-iteration concept, distinct from `for-loop`; glm plan-review); `for-loop` is kept because
    the AST scanner classifies any `for` statement as `for-loop` — both are genuinely present and
    ≤unit-08. No range-based `for` ships (so no `loop-counter`/`range-function`).
  - All introduced by units 01–09; `practices ∩ introduces` empty (introduces = class-def/
    init-method/attributes/methods). Apply surgically (no YAML round-trip). Manifest carries the list.
- **Pre-gate closure self-check (standing, with an OOP caveat):** run the AST concept-scanner scoped
  to unit-10 before the `[sol]` content gate. NOTE: the scanner's untaught-method check flags
  USER-DEFINED class methods (`feed`/`play`/`status`/…) as "untaught" because they are not in its
  library allowlist — these are FALSE POSITIVES (they ARE the `methods` concept this unit teaches).
  Phase B extends the scanner to exempt method names defined in the notebooks' own `class` bodies;
  a library method that is genuinely untaught (`.split`) OR taught earlier but OUTSIDE unit-10's
  union (`.sort` = list-sort, `.items` = dict-loop — both forbidden here) is the only real hit. CAVEAT (glm
  plan-review): the exemption is NAME-scoped, not type-scoped — a user method that happened to share
  a library name (e.g. a `.sort` method) would be masked. Low risk here (a single `Pet` class with
  `feed`/`play`/`pass_time`/`status`, none shadowing a taught library method), and the scanner is
  advisory — reviewers + blind-solve are the real closure enforcement.
- **OOP mechanics (binding):** a class is `class Pet:` with an `__init__(self, ...)` that assigns
  `self.<attr> = ...`; methods are `def <name>(self, ...):` inside the class and read/modify
  `self.<attr>`. Objects are made with `Pet(...)` and used as `buddy.<attr>` / `buddy.<method>(...)`.
  FORBIDDEN (untaught): class INHERITANCE (`class X(Y):`), any dunder beyond `__init__`
  (`__str__`/`__repr__`/`__eq__`/…), `@property`/decorators, `@classmethod`/`@staticmethod`,
  `isinstance`/`type`/`hasattr`/`getattr`/`setattr`, `self.__dict__`. Keep it one plain class with
  `__init__` + a few instance methods.
- **Closure (binding, tightened per sol plan-review):** only concepts taught through unit 10. NO
  files (`open`) — that was unit 09; NO `.split()`. Lists use ONLY `.append` (NO `.sort` — that is
  `list-sort`, not in the unit-10 union); dicts use ONLY `[key]` read (NO `.items`/`.get` — those
  are `dict-loop`/`dict-access`-plus; only plain `[key]` lookup, which is the required `dict-access`).
  `builtin-functions` (`len`/`max`/`min`) is NOT in the union and must NOT appear ANYWHERE — the
  exemption for solution asserts covers COMPARISON OPERATORS (`==`/`!=`/`<`/`>`, all under the
  listed `comparison` practice) but NOT FUNCTION CALLS like `len(...)` (sol round-1). Assert list
  state via `list-index` (`pets[1].name == "Rex"` — `list-index` is now listed), never `len`. NO nested loops, NO comprehensions, NO sets. The
  `status` mood ladder uses `comparison` + `elif-else` (this unit DOES teach comparison-based
  branching, unlike the membership-only checkpoint 03).
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
return-value, dict-access, while-loop; practices f-string, if-statement, accumulator,
list-append (scope REMOVED), + amended arithmetic/comparison/dict-literal/elif-else/for-loop/
list-loop/list-literal/list-index/print/variable/string-literal/int-type/error-messages/input):
- Hook: PET SIMULATOR — adopt a virtual pet that has its OWN name and mood and remembers them; feed
  it and play with it and watch its stats change. The teacher "adopts" a pet live and the class
  suggests actions.
- **Lesson 1 (class-def, init-method, attributes):** `class Pet:` with `def __init__(self, name):
  self.name = name; self.hunger = 5; self.happiness = 5`. Make a pet `buddy = Pet("Buddy")` and read
  its attributes `buddy.name`, `buddy.hunger` (print them). Explain `self` is "this particular pet".
  Make TWO pets and show their hungers are independent — explain this plainly as "each object
  carries its OWN attributes" (independent-instance identity is NOT "scope" — fable/sol plan-review;
  `scope` has been removed from unit-10 practices, so it is neither taught nor claimed here).
- **Lesson 2 (methods):** add methods inside the class — `feed(self, amount)` does `self.hunger =
  self.hunger - amount` (accumulator-on-attribute + arithmetic) and returns the new hunger;
  `play(self)` does `self.happiness = self.happiness + 1`; a `pass_time(self)` method does
  `self.hunger = self.hunger + 2` (time makes a pet HUNGRIER — so the "hungry" mood is reachable
  organically and feeding is motivated, glm plan-review); `status(self)` builds a LOCAL `mood`
  variable via a ladder `if self.hunger > 6: mood = "hungry"  elif self.hunger < 3: mood = "stuffed"
  else: mood = "content"` (comparison + elif-else; `mood` is an incidental method-local, covered by
  `variable` — NOT a taught scope beat, `scope` is removed) and
  prints an f-string. Call `buddy.feed(2)`, `buddy.play()`, `buddy.pass_time()`, `buddy.status()`.
- **Lesson 3 (a little simulation, FLAT — no nested loops, glm plan-review):** a
  `foods = {"apple": 2, "steak": 4}` table (dict-literal + dict-access) feeds by name; a LIST of
  pets `pets = []` / `pets.append(Pet("Rex"))` (list-literal + list-append), then ONE loop
  `for pet in pets: pet.pass_time(); pet.status()` (list-loop — a single status/time pass over all
  pets, NOT nested). SEPARATELY (not nested inside the pets loop), a `while buddy.happiness < 10:
  buddy.play()` loop plays ONE pet until it is happy (while-loop from requires + comparison; the
  `play` method's increment is the accumulator that advances the loop — NO separate counter, so no
  `loop-counter`). The `no-exec` AttributeError beat (`buddy.hapiness` typo) + traceback
  (error-messages) — name why the attribute must match `__init__`.
- Exercises ≥6 core + ≥2 stretch: make-a-pet (class + __init__ + read attributes), two-pets
  (independent attributes), add-a-feed-method (method that changes an attribute + returns), the-mood-
  ladder (status with comparison/elif-else), a-pet-list (list of pets + `for pet in pets` list-loop
  status), feed-from-the-foods-table (dict-access), type-a-name (input PROMPT → parameterized
  solution making a pet), fix-the-attribute-typo (the AttributeError → correct the attribute name);
  stretch: happiest-pet (loop the pets, track the max happiness with a MANUAL running-best —
  `best = 0; if pet.happiness > best: best = pet.happiness` (accumulator + comparison), NOT
  `max()`), a-play-until-happy `while buddy.happiness < 10` loop.
- **builtin-functions NOT in the union (sol plan-review — no assert exemption for it):** `len`/
  `max`/`min` must NOT appear ANYWHERE — not in student cells AND not in solution asserts (sol
  rejects the scaffolding exemption for a function call; only bare `==`/`<`/`>` are exempt).
  happiest-pet tracks the max MANUALLY; list state is asserted via INDEX (`assert pets[1].name ==
  "Rex"`), never `len(pets)`. Reviewers check no cell anywhere uses len/max/min.
- Solutions: execute headless, input-free, non-vacuous asserts — `buddy.hunger == 3` after
  `feed(2)` from 5; two pets' attributes independent (`a.hunger != b.hunger` after feeding one — the
  `!=` lives only in the assert); a mood-ladder assert (a pet with hunger 8 → "hungry"); a
  list-of-pets assert BY INDEX (`pets[1].name == "Rex"` — NEVER `len(pets)`, sol plan-review). No
  inheritance, no dunders beyond `__init__`, no `len`/`max`/`min` anywhere.
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

### Review 2 — [fable] (2026-09-07)
REJECT → all findings RESOLVED (revised in place before commit):
1. `[FIXED]` (BLOCKER) `input` used-but-unlisted (type-a-name prompt) — added to the practices
   amendment (homed by the PROMPT only, parameterized solution; the identical unit-09 pattern).
2. `[FIXED]` (Nit) `scope` mis-homed on "independent instances = scope" (a misconception) — L1 now
   explains independent instances plainly as "each object carries its own attributes", NOT scope;
   `scope` is homed silently by method-local variables (`amount` param, local `mood`) in L2.
3. `[FIXED]` (Watch) `builtin-functions` (len/max) not in union — added a binding note: no
   len/max/min in any STUDENT cell; happiest-pet tracks max MANUALLY; `len(pets)` only in a solution
   assert (exempt scaffolding).
- fable affirmed: OOP closure safety (single plain class, no inheritance/dunders/decorators/
  isinstance), completeness of every other beat, correctness, `practices ∩ introduces` empty,
  hook-first 3-lesson pedagogy.

### Review 3 — [glm] (2026-09-07)
APPROVE WITH NITS → all addressed:
1. `[FIXED]` `list-loop` used-but-unlisted (`for pet in pets`) — added to the amendment (kept
   `for-loop` too since the AST scanner classifies any `for` as for-loop; both genuinely present).
2. `[FIXED]` (Design) "several pets × a few rounds" read as NESTED loops — L3 pinned FLAT: one
   `for pet in pets` status/time pass, and SEPARATELY a `while buddy.happiness < 10` play loop (not
   nested).
3. `[FIXED]` `while rounds > 0` decrement → `loop-counter` (not in union) — reframed the while as
   `while buddy.happiness < 10: buddy.play()` (the method increment advances it; no counter).
4. `[FIXED]` (Pedagogy) feeding only lowers hunger so "hungry" was unreachable — added a
   `pass_time` method (`self.hunger += 2`) so hunger rises over time (hungry reachable, feeding
   motivated).
5. `[FIXED]` scanner exemption name-scoped-not-type-scoped caveat — noted (low risk, advisory).

### Round 2 revisions (2026-09-07)
Amendment now: requires UNCHANGED; practices += `arithmetic, comparison, dict-literal, elif-else,
for-loop, list-loop, list-literal, print, variable, string-literal, int-type, error-messages, input`
(13). L2 gains `pass_time`; L3 is flat (list-loop pass + separate play-until-happy while). Scope
homed on method-local vars. Re-validated green. Awaiting [sol].

### Review 4 — [sol] (2026-09-07)
REJECT → all findings RESOLVED. sol confirmed the beat mapping, accumulator, arithmetic, and (in the
revised working tree) list-loop + input are homed; scratch prereq/coverage PASS. Fixes:
- `[FIXED]` sol-4: `builtin-functions` (`len(pets)` in a solution assert) used-but-unlisted — sol
  rejects the scaffolding exemption for a FUNCTION CALL (only bare `==`/`<`/`>` are exempt). Now
  FORBIDDEN everywhere; list state asserted by INDEX (`pets[1].name == "Rex"`).
- `[FIXED]` sol-6: `scope` over-listed — REMOVED from unit-10 practices (a first OOP unit doesn't
  teach local-vs-global scope; method-locals are incidental; scope stays in cp-02 + capstone →
  closure-safe). Re-validated green.
- `[FIXED]` sol-8: the OOP-mechanics rule permitted `.sort`/`.items` (= list-sort/dict-loop, not in
  union) — now FORBIDDEN; unit-10 uses ONLY `.append` (lists) + `[key]` (dicts). Scanner-note
  example corrected.
- `[FIXED]` sol-9 (nit): Phase-B blueprint summary now lists list-loop + input, drops scope.
- sol affirmed OOP scope-safety (no inheritance/dunders/decorators/reflection/files/.split/nested-
  loops/comprehensions/sets).

### Round 2 revisions (2026-09-07)
Amendment now: requires UNCHANGED; practices = REMOVE `scope`, then the pre-existing
`f-string/if-statement/accumulator/list-append` + amended `arithmetic, comparison, dict-literal,
elif-else, for-loop, list-loop, list-literal, print, variable, string-literal, int-type,
error-messages, input`. builtin-functions/.sort/.items FORBIDDEN; len-assert → index. Re-validated
green. Re-dispatching [glm]/[fable]/[sol] round 2.

### Round 2 re-review verdicts (2026-09-07)
**[fable] round 2: APPROVE WITH NITS.** Round-1 `input` blocker RESOLVED; full closure CLEAN (no
used-but-unlisted, no over-listing, all 17 practices introduced ≤unit-09, `practices ∩ introduces`
empty); `scope` removal closure-safe (still practiced cp-02 + project-01/02); closure-safety clean
(`.append`/`[key]` only, no len/max/min, no inheritance/dunders/nested-loops; L3 flat; `pass_time`
makes "hungry" reachable). One doc nit `[FIXED]`: L2 blueprint said "`mood` … homes `scope`" —
reworded ("incidental method-local, covered by `variable`, NOT a taught scope beat"). Awaiting
[glm]/[sol] round 2.

**[glm] round 2: REJECT → fixed.** All 5 round-1 nits confirmed resolved; scope removal confirmed
closure-safe (no downstream entry requires scope); the .sort/.items/len bans create no gap.
Substantive finding + nits, all fixed:
- `[FIXED]` (BLOCKER) `list-index` used-but-unlisted — my sol-4 fix (`pets[1].name == "Rex"` to avoid
  len) introduced `pets[1]` = `list-index`, absent from the union. Added `list-index` to the
  practices amendment (introduced unit-07, already practiced cp-03 → closure-safe). Re-validated green.
- `[FIXED]` (nit) the "only bare comparison operators exempt" sentence contradicted the `!=`/`==`
  asserts — reworded: the assert exemption covers COMPARISON OPERATORS (listed `comparison`), the
  ban is on FUNCTION CALLS (`len`).
- `[FIXED]` (nit) L2 "`mood` … homes `scope`" — already struck (fable round-2).
- `[FIXED]` (nit) stale goal summary — updated to list `pass_time` + the flat single-pass L3.

### Round 2 revisions v2 (2026-09-07)
Added `list-index` to the amendment (14 practices additions now; scope still removed). Comparison-
exemption sentence + goal summary + Phase-B parenthetical aligned. Re-validated green. Awaiting
[sol] round 2 (dispatched before the list-index fix — may independently flag it; now resolved).

**[sol] round 2: (reviewed committed pre-fix version) — its 2 used-but-unlisted findings both
already FIXED in working tree.** sol confirmed sol-4/6/8/9 + input/list-loop resolved,
listed-but-unhomed: none. Its two used-but-unlisted: `list-index` (= glm round-2; added to
amendment) and the residual L2 "`mood` homes `scope`" text (= fable round-2; reworded to "incidental
method-local, covered by `variable`"). Both resolved. Re-dispatching a focused [glm]/[sol] round 3
to confirm the list-index add + scope-text removal.

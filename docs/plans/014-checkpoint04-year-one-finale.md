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
  - append to `checkpoint-04-year-one-finale.practices` — `parameters, dict-literal,
    dict-access, list-literal, list-append, list-index, for-loop, list-loop, if-statement,
    in-operator, arithmetic, int-type, type-conversion, string-concat, string-literal,
    string-methods, f-string, print, variable, boolean, error-messages, accumulator, elif-else`.
    NOTE: `dict-access` covers the Q7/Q8 `inventory["shield"]` subscript (my scanner folded it into
    `list-index` — both are AST `Subscript`; fable + glm gates caught it; checkpoint-03 precedent
    lists it). `list-loop` covers Q3's `for score in scores:` over a concrete list (glm caught it;
    plan-012 taxonomy keeps BOTH `for-loop` and `list-loop`; introduced unit-07). `def-function` is
    NOT listed: every `def` is a class-body method (`__init__`/`heal` = `methods`/`init-method`,
    per unit-10's scanner exemption), no module-level function exists — glm + fable both flagged the
    over-listing. `parameters` IS kept (`heal(self, amount)`/`__init__(self, name)` genuinely bind a
    parameter). `accumulator` covers the `heal` method's
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
  are exempt scaffolding); assert list state via INDEX (`loaded[0]`) and attribute state directly
  (`hero.health == 13`) — cp-04 has ONE `hero`, no list-of-objects, so no `pets[i].attr` beat; the
  sorted top via `loaded[0]` after `.sort(reverse=True)`. String methods stay in the taught subset
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

### Phase A — gitignore + map amendment (inline)

1. Append to `.gitignore` (surgical): a comment + `book1/checkpoints/checkpoint-04-year-one-finale/finale.txt`.
2. Amend `coverage-map.yaml` per Global Constraints (surgical, requires + practices).
- **Acceptance (Phase A):** the gitignore + map amendment ALONE are green (`uv run pytest -q` +
  `ci-local`) before any checkpoint directory exists. (The `manifest.yaml`, map-equal to the amended
  entry, lands in Phase B alongside the checkpoint dir — glm-6: it cannot exist before its dir.)

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
  mode; index-based list asserts. SELF-CONTAINMENT (glm-5, unit-10 content-gate precedent): the
  Q2 solution cell REDEFINES `class Hero:` with both `__init__` and `heal` (so it stands alone in
  a headless top-to-bottom run); Q3 writes `finale.txt` BEFORE Q4 reads it (the write cell precedes
  the read cell in notebook order). Solutions run top-to-bottom clean; the checkpoint is
  RUN-IN-ORDER (a student running Q4 before Q3 hits a FileNotFoundError — teacher notes flag this).
- `book1/checkpoints/checkpoint-04-year-one-finale/manifest.yaml`, map-equal to the amended entry
  (glm-6: manifest lands here in Phase B, with its dir — not Phase A).
- Teacher notes: SIX headings incl. `## Grading` — per-question points summing to a total; full-
  credit + partial-credit notes; 35–40 min pacing (this is the hardest checkpoint — files + OOP);
  common mistakes (forgetting `self`; KeyError vs a guard; `.sort()` returns None; forgetting
  `.strip()` before `int()`; a typo'd attribute; running Q4 before Q3 → FileNotFoundError, so
  RUN THE QUESTIONS IN ORDER — the save file must be written before it is read).

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

## Post-Execution Report (2026-09-07)

**Status: implemented, Phases A–C GREEN. Content gate next.**

- **Phase A (map + gitignore):** committed `c4a0674`. `.gitignore` += `finale.txt`; coverage-map
  checkpoint-04 amended (requires += `for-loop`; practices += the 23-concept substrate,
  `def-function` omitted). Acceptance: pytest 364 pass, prereq + coverage PASS, ci-local ALL GREEN
  with the amendment alone (empty checkpoint dir).
- **Phase B (content):** `checkpoint.ipynb` (17 cells: title + 8 `## Question N` + 8 EMPTY student
  cells; Q8 bug in a non-executable markdown fence; no `input()`; no leaked solutions; unique 8-hex
  ids), `teacher-notes.md` (six ordered headings incl. `## Grading` — 40 pts, 5/question, rubric
  denies credit for out-of-scope tools `max`/`len`/`.split`/`.get`; RUN-IN-ORDER + FileNotFoundError
  note), `solutions.ipynb` (blind-authored, 16 cells, 7 non-vacuous assert cells — Q3 writes,
  Q4 verifies `loaded == [40,90,20]`, Q5 `loaded[0] == 90`, Q2 `hero.health == 13`), `manifest.yaml`
  map-equal. Solutions authored by a SEPARATE blind codex session (read only `checkpoint.ipynb`).
- **Phase C (verification, clean-slate):** `rm -f finale.txt` then authoritative checks — exec-solutions
  PASS (Q3 creates `finale.txt`, Q4 reads it), manifest/structure/noexec/hygiene/cell-lint PASS,
  scanner scoped to cp-04 shows ONLY the `def-function` false-positive (documented blind spot; gate
  adjudicated it homes to `methods`/`init-method`), `finale.txt` gitignored (no git noise), full
  `ci-local.sh` **ALL GREEN** (exit 0), pre-merge-guard OK.

---

## Content Review

Roster + tags per the plan-review gate; findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`; all `[OPEN]`
resolve before merge.

### Review 1 — [self] (2026-09-07) → APPROVE
Blind-audited all 8 questions against the authored solutions. Each question is solvable with only
units 01–10, and each reference is correct. Closure clean: single plain `Hero` class (`__init__` +
`heal` only, no inheritance/dunder-beyond-init/isinstance/type); NO `len`/`max`/`min` anywhere
(Q5 uses `loaded[0]` after `.sort(reverse=True)`); NO `.split` (Q4 reads one int/line via
`.strip()`+`int()`); NO append mode / `os`/`tempfile`; dicts use `[key]`/`.items` only. Asserts
NON-VACUOUS: Q4 `loaded == [40,90,20]` proves the write→read round-trip (computed from the file);
Q5 `loaded == [90,40,20]`/`loaded[0] == 90` proves the sort; Q2 `new_health == 13`/`hero.health == 13`
proves `heal` (computed via the method); Q7 membership booleans; Q8 `result == "no shield"` proves
the guard took the else branch. File-I/O: Q3 writes `finale.txt` BEFORE Q4 reads it; clean-slate
`exec-solutions` PASS; `finale.txt` gitignored. Q8 bug in a non-executable markdown fence; student
cells empty; no `input()`. Grading: 40 pts (5/question) summing to total, rubric denies out-of-scope
credit. NITS (non-blocking): Q6's `assert inventory["sword"] == 1` re-reads a dict literal (the
`.items()` loop's value is a print side-effect, not cheaply assertable — matches checkpoint-03
precedent); Q3 carries no assert (Q4 verifies the round-trip). Both defensible.
[UPDATED post-gate: the Q6 assert was strengthened — see resolutions below.]

### Review 2 — [fable] (2026-09-07) → APPROVE WITH NITS
Blind-solved all 8 (matched reference); closure PASS; non-vacuity empirically confirmed (6 wrong
solutions all fail); clean-slate `exec-solutions` PASS; finale.txt gitignored; grading sums to 40.
- **[FIXED] N1 — Q7 assert pins only given data** (a swapped branch still passes) → Q7 now captures
  `result` and asserts it (mutation-verified: wrong-key guard fails).
- **[FIXED] N2 — `f-string` over-listed** (no question used one) → Q6 reference now builds
  `line = f"{item}: {count}"` (f-string genuinely used; AST confirms 1 JoinedStr node).

### Review 3 — [glm] (2026-09-07) → APPROVE WITH NITS (no blockers)
Blind-solved all 8 (matched); clean-slate `exec-solutions`/prereq/coverage/pytest PASS; manifest ==
map; AST closure scan clean.
- **[FIXED] G1 (Should-Fix) — rubric misstates course facts** (`len`/`max`/`.get` ARE taught, units
  07–08; only `.split()` is outside 01–10) → rubric reworded: each question assesses ONE technique,
  a substitute that skips it earns no credit *even if taught*; `.split()` noted as untaught, the
  others as taught-but-not-assessed-here.
- **[FIXED] G2 (Should-Fix) — Q6 assert vacuous** → strengthened (see below; three reviewers concur).
- **[FIXED] G3 (Should-Fix) — Q7 assert vacuous w.r.t. branch** → captured `result` (fable-N1 dup).
- **[FIXED] G4 (Nice) — f-string listed-but-unused** → now used (fable-N2 dup).
- **[WONTFIX] G5 (Nice, informational) — Q4 assert can't catch a forgotten `.strip()`** since
  `int("40\n") == 40`. The round-trip assert (`loaded == [40,90,20]`) is otherwise strong; `.strip()`
  is a taught habit enforced by grading. A contrived whitespace assert would read worse than the
  natural round-trip; accepted as-is (matches unit-09's own solution idiom).

### Review 4 — [sol] (2026-09-07) → Must-Fix Q6, reconciled
Blind-solved all 8 (exact match); closure clean (AST); manifest order-for-order == map; grading +
Q8-placement no finding.
- **[FIXED] S-4.1 (Must Fix) — Q6 assert vacuous** (negative probe: deleting the `.items()` loop
  still passed) → Q6 now accumulates `lines.append(f"{item}: {count}")` and asserts
  `lines == ["sword: 1", "potion: 3"]`. Mutation-verified: delete-loop, swapped-unpack BOTH fail.
- **[RESOLVED — reviewer-env] S-3.1 (Open) — clean-slate run UNVERIFIED in sol's sandbox** (`rm`
  policy-blocked; read-only EROFS mount held a stale `finale.txt`; kernels socket-blocked). NOT a
  checkpoint defect: the mandated clean-slate `rm -f finale.txt` → `exec-solutions` PASS was run
  independently by [self], [glm], AND [fable] from a file-free state (create-before-read proven);
  sol's own /dev/shm fallback also passed all asserts and wrote exactly `40\n90\n20\n`.

### Content-gate resolutions (2026-09-07)
Batch fix over solutions.ipynb Q6 + Q7 and teacher-notes rubric:
- **Q6:** `lines = []; for item, count in inventory.items(): line = f"{item}: {count}"; print(line);
  lines.append(line)` then `assert lines == ["sword: 1", "potion: 3"]` — resolves the Q6-vacuous
  Must/Should-Fix (all 3 externals) AND the f-string-unused nit in one change.
- **Q7:** capture `has_sword` + `result` in the branch; `assert has_sword == True and
  result == "no shield"` — resolves the Q7-vacuous nit.
- **Rubric:** reworded to distinguish untaught (`.split()`) from taught-but-not-assessed
  (`max`/`len`/`.get`).
Re-verified clean-slate: exec-solutions PASS; manifest/structure/noexec/hygiene/cell-lint/coverage/
prereq PASS; scanner scoped to cp-04 shows ONLY the `def-function` false-positive; all new asserts
mutation-verified non-vacuous. No new concept introduced (f-string/list-literal/list-append/boolean
all already in the union). Full `ci-local.sh` re-run + round-2 content re-review to confirm.


## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. Substrate scanner-DERIVED from the planned 8-question code (files + OOP + dict-loop +
list-sort) + validated green. This is the hardest checkpoint — it combines unit-09 file I/O and
unit-10 OOP — so it inherits BOTH units' hard-won binding rules: file-I/O CI-safety (write-then-read
`finale.txt`, gitignored, deterministic `"w"`, no `.split`, clean-slate Phase-C run) and OOP safety
(single plain class, no inheritance/dunders-beyond-init). Closure: NO `len`/`max`/`min` (index-based
asserts, sorted-top via `[0]`); membership-based Q7; KeyError fix-the-bug in a markdown fence.
Input-free (checkpoint gives all data). `practices ∩ introduces` empty (introduces = []).

### Review 2 — [glm] (2026-09-07) → REJECT, reconciled
GLM-5.2, read-only. File-I/O CI-safety, OOP/closure safety, conventions, amendment hygiene all
confirmed clean. Blockers, ALL FIXED in the amendment:
- **[FIXED] `dict-access` used but unlisted** (Q7/Q8 `inventory["shield"]`; introduced unit-08) →
  added.
- **[FIXED] `list-loop` used but unlisted** (Q3 `for score in scores:` over a concrete list;
  plan-012 taxonomy keeps BOTH `for-loop` and `list-loop`; introduced unit-07) → added.
- **[FIXED] `def-function` over-listed** (every `def` is a class-body method; no module-level
  function) → dropped from practices (`parameters`/`return-value`/`methods`/`init-method` cover
  the method defs).
Nits, all applied: [FIXED] stale `pets[1].name` → `loaded[0]`/`hero.health` (cp-04 has one hero);
[FIXED] solution self-containment + RUN-IN-ORDER (Q2 redefines `Hero`; Q3 writes before Q4 reads;
FileNotFoundError note added to teacher notes); [FIXED] `manifest.yaml` moved Phase A → Phase B
(cannot exist before its dir).

### Review 3 — [fable] (2026-09-07) → REJECT, reconciled
Fable 5, read-only. Structure (CI-safety, OOP closure, conventions, closure-legality) all correct.
Blockers, ALL FIXED:
- **[FIXED] `dict-access` used but unlisted** (Q7/Q8 subscript; scanner folded it into `list-index`
  since both are AST `Subscript`) → added (corroborates glm).
- **[FIXED] `elif-else` used but unlisted** (Q7/Q8 `else` branches) → already added pre-gate.
- **[NOTE] `accumulator`** (heal `self.health = self.health + amount`) — fable leans omit-fine
  (single attribute read-modify-write, not a loop; `arithmetic` covers `+`); KEPT listed (stricter
  scanners treat any `x = x + y` as accumulator; harmless, defensibly present).
- **[NOTE] `def-function` over-listed** — corroborates glm; dropped (see glm review).

### Reconciliation validation (2026-09-07)
Amended union: requires += `for-loop`; practices += `parameters, dict-literal, dict-access,
list-literal, list-append, list-index, for-loop, list-loop, if-statement, in-operator, arithmetic,
int-type, type-conversion, string-concat, string-literal, string-methods, f-string, print, variable,
boolean, error-messages, accumulator, elif-else` (def-function DROPPED, dict-access + list-loop
ADDED vs the pre-gate draft). Validated on a `/dev/shm` scratch map: `prereq-check: PASS`,
`coverage-check: PASS`. Scanner `detect()` on the planned 8-question code: union complete — the lone
residual flag is `def-function`, the scanner's known blind spot (it counts every `def`, including
class-body method defs, as `def-function`; both gates confirmed these are `methods`/`init-method`,
so the drop is correct). `heal` is the expected exempt user-method. `practices ∩ introduces` empty.

### Review 4 — [sol] (2026-09-07) → REJECT, reconciled
GPT-5.6-sol, read-only. Beat-by-beat substrate walk of all 8 questions. File-I/O CI-safety and
OOP/closure safety both confirmed clean (all 6 + 5 sub-checks PASS). Two blockers — EXACTLY the two
already reconciled from glm/fable:
- **[FIXED] `list-loop`** (Q3 `for score in scores`, distinct from `for-loop`, registered
  `concepts.yaml:46`; taught unit-07) → added.
- **[FIXED] `dict-access`** (Q7/Q8 `inventory["shield"]`, registered `concepts.yaml:49`; taught
  unit-08) → added.
sol's scratch prereq-check + coverage-check both exited 0 on the pre-fix amendment, and sol notes
(as glm did) that those checks CANNOT catch used-but-unlisted substrate — human beat-mapping is the
enforcement. On `def-function`: sol homes it in Q1/Q2 and did NOT flag it as over-listed (a 1-keep
minority vs glm+fable's 2-drop). RESOLUTION: dropped, following the unit-10 precedent glm cited
(`coverage-map.yaml:121` — the OOP unit itself put `def-function` in `requires`, not `practices`,
because method defs are homed by `methods`/`init-method`). Dropping is CI-clean (prereq-check PASS
without it) and does not violate sol's review (sol REJECTed on absent concepts, not on this one's
removal). All three external REJECT-blockers (dict-access ×3, list-loop ×2, elif-else ×1) resolved.

### Consensus (2026-09-07)
Round-1: [self] APPROVE; [glm]/[fable]/[sol] REJECT on used-but-unlisted substrate (dict-access,
list-loop, elif-else) + over-listed def-function + doc nits — ALL mechanical list-additions the
reviewers named explicitly. Reconciled on HEAD: +dict-access +list-loop +elif-else, −def-function,
3 doc nits. Round-2 confirmation dispatched on the reconciled HEAD.

**Round-2 (on HEAD 5cbd8c1): CONSENSUS REACHED — 4-way APPROVE, no open blockers.**
- [self] APPROVE (round-1).
- [glm] APPROVE — dict-access + list-loop confirmed present; def-function dropped/parameters kept;
  all 3 nits confirmed in the diff; prereq-check + coverage-check PASS on /dev/shm replica.
- [fable] APPROVE — both round-1 blockers resolved; beat-mapped all 8 questions (union exact, no new
  used-but-unlisted); scratch validates green.
- [sol] APPROVE — both round-1 blockers resolved; def-function drop creates no closure/prereq
  problem (prereq + coverage PASS); no new used-but-unlisted; consistent with unit-10 precedent.
Plan-review gate CLOSED. Proceeding to implementation (Phase A).

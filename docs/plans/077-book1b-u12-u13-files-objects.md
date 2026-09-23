# Plan 077 — Book 1b Unit 12 (Files) + Unit 13 (Objects) + Checkpoint 05

**Origin:** Book 1b buildout ("full book 1b implementation"). This is the LAST content plan; 078 is the
end-of-book Algorithm Challenge (project) that takes Book 1b out of `buildout`.
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (U12/U13 rows + the mandatory post-U13 checkpoint),
§5 (fastforward), §6 (coverage — the full-practice anchor activates at 078, so U12/U13/cp05 must PRACTICE
their own + the deferred concepts), §7 (mini-CP exercises, function form), §8 (self-contained data, no opaque blobs).
**Templates:** Book 1b U07–U11 (function-form units); **Book 1 `unit-09-save-point` for the file-I/O pattern**;
cp03/cp04 for the checkpoint shape.

## Scope

Two units + the mandatory final checkpoint (design §3):
- **U12 Files** — introduces `file-read`, `file-write`, `with-statement`. Domains: read numbers → stats,
  save/load records. **Discharges the plan-076 debt:** practices `transform-each` (transform each line read)
  and `linear-search` (find the first matching line).
- **U13 Objects** — introduces `class-def`, `init-method`, `attributes`, `methods`. Domains: a
  `Fraction`/`Point`/`Counter` class with methods; a class that **saves and loads itself to a file** (file
  I/O reuse). **Discharges the plan-076 debt:** practices `string-slice` (slice an attribute string).
- **Checkpoint 05** — MANDATORY, after U13. It is the ONLY practice site for U12's + U13's introductions
  before the capstone, so it practices BOTH file concepts AND the four OOP concepts (design §3 note).

After this plan every one of the 62 catalog concepts is introduced (55 → 62) and practiced in a non-capstone
entry; plan 078 then verifies full coverage out of buildout.

## Coverage-map entries (contracts)

**unit-12-files** — `kind: unit`, `title: "Files — read, write, and the with statement"`, `lessons: 3`
- introduces: `[file-read, file-write, with-statement]`
- requires: `[def-function, parameters, return-value, for-loop, list-append, string-methods, if-statement,
  comparison, arithmetic, type-conversion, variable, print]`
- practices: `[transform-each, linear-search, list-literal, builtin-functions, running-total,
  count-by-condition, find-extreme, accumulator, int-type, f-string, in-operator, comment, naming]`

**unit-13-objects** — `kind: unit`, `title: "Objects — classes, __init__, attributes, and methods"`, `lessons: 3`
- introduces: `[class-def, init-method, attributes, methods]`
- requires: `[def-function, parameters, return-value, arithmetic, comparison, boolean, if-statement,
  variable, print]`
- practices: `[string-slice, file-read, file-write, with-statement, f-string, int-type, float-type,
  type-conversion, comment, naming]`

**checkpoint-05-files-and-objects** — `kind: checkpoint`, `title: "Checkpoint 5 — Files & Objects"`, `lessons: 0.5`
- introduces: `[]`
- requires: `[print, variable, def-function, parameters, return-value, file-read, file-write, with-statement,
  class-def, init-method, attributes, methods, for-loop, list-append, string-methods, type-conversion,
  if-statement, elif-else, comparison, boolean, arithmetic, f-string, string-literal]`
- practices: `[print, variable, def-function, parameters, return-value, file-read, file-write, with-statement,
  class-def, init-method, attributes, methods, for-loop, list-append, list-literal, string-methods,
  type-conversion, if-statement, elif-else, comparison, boolean, arithmetic, count-by-condition, accumulator,
  builtin-functions, int-type, f-string, string-literal]`

Closure: U12 requires ⊆ U01–U10; U13 requires ⊆ U01–U07; cp05 requires/practices ⊆ U01–U13 (no fastforward).
No self-practice. 55 → 62 introduced-once (adds file-read/file-write/with-statement + class-def/init-method/
attributes/methods).

### Design §6 practice-coverage record — CLOSES the book's coverage
- **Debt discharged (from plan 076 ledger):** `transform-each`/`linear-search` practiced in U12 (line
  transforms / first-matching-line search); `string-slice` practiced in U13 (slice an attribute string).
- **U12 introductions** (`file-read`/`file-write`/`with-statement`) are practiced in **U13** (a class that
  saves/loads itself) AND **cp05** — their only sites before the capstone.
- **U13 introductions** (`class-def`/`init-method`/`attributes`/`methods`) are practiced in **cp05** — its
  only site (design §3 note). `attributes` is credited by declaration + reviewer (detector is partial).
- After this plan, every introduced concept has a non-capstone practice site; plan 078 leaves `buildout` and
  the full practice-coverage anchor (curriculum.py:462-473) must go GREEN.

## Tooling pins (enforcement tiers)

- **CI-enforced (concept-scan):** file methods = ONLY `read`/`readlines`/`readline`/`write`/`close`
  (TAUGHT_METHODS, concept_scan.py:54); `with-statement` detected (visit_With); `class-def`/`methods`/
  `init-method` detected (visit_ClassDef). Dict methods ⊆ {items,keys,values,get}; list ⊆ {append,sort};
  string ⊆ {upper,lower,strip,replace}; builtins ⊆ {len,min,max,sum,sorted,abs,round}, no `key=`.
- **`attributes`** is credited by declaration + reviewer-verified (the detector is partial); U13/cp05 genuinely
  use `self.x = …`.
- **NOT scanner-flagged in Book 1b (reviewers + Phase-E audit):** `ord`/`chr`, comprehensions, tuple/multiple
  ASSIGNMENT (`a, b = …`; `for k, v in d.items()` stays exempt), step slices, `collections`/`defaultdict`,
  and **inheritance / dunder methods other than `__init__`** (no `__str__`/`__repr__`/`__eq__`/base classes —
  a `describe()`/`to_text()` method returns the string instead), and **`@` decorators / `@property` /
  `@staticmethod`**. Keep classes to `class Name:` + `__init__(self, …)` + plain methods + `self.attr`.
- **FILE I/O SAFETY (clone Book 1 u09-save-point):** every file drill is SELF-CONTAINED — a setup cell (or the
  function itself) WRITES the file with known content before reading it, so `exec-solutions`/`exec-lessons`
  are idempotent and order-independent. Commit small seeded `.txt` fixtures in the unit dir so exec rewrites
  TRACKED files (no new untracked files); use relative paths (CWD = unit dir at exec). No opaque data blobs
  (design §8) — the content is written in-cell. `with open(path, "w")`/`with open(path)` + `f.read()`/
  `f.write()`/`for line in f`.
- Function form: solutions define the function + assert several distinct cases (round-trip save/load asserts
  for files; construct-then-check for objects); ≥3 non-vacuous assert cells; no `input()`; unique cell ids;
  student notebooks solution-free with NO executed outputs.

## Teaching outlines

### U12 Files (3 lessons, problem-first, function form)
- **L1 — Write and Read (`file-write`, `file-read`, `with-statement`).** `with open(path, "w") as f: f.write(...)`
  (why `with` closes the file for you); read it back with `with open(path) as f: f.read()`; loop lines with
  `for line in f:` and `int(line.strip())`. Self-contained setup writes the file first. Hook: save a list of
  scores, load them back.
- **L2 — Numbers → Stats.** Load numbers from a file and compute stats: total (`running-total`/`accumulator`),
  count-by-condition, `min`/`max`/`sum`/`len` (`builtin-functions`), the best (`find-extreme`). Package as
  seeded functions (`save_scores(scores, path)` / `load_scores(path)` / `stats(path)`).
- **L3 — Records & Search.** Save/load simple records (one field per line); **transform each line** into a
  cleaned/typed value (`transform-each` — the debt site); a **linear-search** that returns the first line
  matching a target (or a "not found" message) — the debt site; `name in text` membership.
60-min cut per lesson in teacher-notes.

### U13 Objects (3 lessons, problem-first, function form + classes)
- **L1 — Define a Class (`class-def`, `init-method`, `attributes`).** `class Point:` with
  `def __init__(self, x, y): self.x = x; self.y = y`; create instances; read `p.x`. A `Fraction`/`Point`
  with attributes. Trap: forgetting `self`.
- **L2 — Methods (`methods`).** Methods that use the attributes and RETURN a value: `distance_to`, `add`,
  `describe()` returning an f-string (no `__str__`); `string-slice` on an attribute string (e.g. a name's
  `initials`). Contrast a method with a plain function that takes the object.
- **L3 — Objects that Persist.** A `Counter`/`Point` with a `save(path)` method (`file-write`) and a
  `load(path)` (or module-level loader) that rebuilds the object (`file-read`/`with-statement`) — the file
  reuse from design §3. Put it together.
60-min cut per lesson in teacher-notes.

### Checkpoint 05 (mandatory, after U13, strict, no turtle, no fastforward)
6–8 VISIBLE `## Question N`, practicing BOTH units (its only site for their intros). Mix: a save/load
round-trip function (`file-write`+`file-read`+`with`); a load-then-stat function; a `linear-search` over
lines; define a small class with `__init__` + attributes; a method returning a computed value / an f-string;
a method that slices an attribute string (`string-slice`); and a class whose method saves itself to a file
(ties U12+U13). File questions are SELF-CONTAINED (write before read). Strict — only concepts ≤ U13; no
inheritance/dunders-beyond-`__init__`/decorators; f-strings only (list `string-literal`); `type-conversion`
for `int()`/`str()`. teacher-notes has `## Grading` (two named pass-bar items: save/load-round-trip;
define-a-class-with-a-method) + the full heading set incl. `## Discussion prompts`.

## Value plan
Distinct inputs per exercise/question, distinct from lesson examples and each other; list the
(function/class, sample inputs) inventory in each unit's + the checkpoint's teacher-notes so the gate can check.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: 3 coverage-map entries + 2 unit manifests + 1 checkpoint manifest + 3 syllabus rows; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): U12 + U13 lesson.ipynb + exercises.ipynb + cp05 checkpoint.ipynb + committed seeded `.txt` fixtures for U12/cp05 file drills. Per unit ≥8 exercises (core ≤7, ≥2 stretch); cp05 6–8 visible `## Question N`. Pin: function form; file self-contained-setup pattern; file/dict/list/string method subsets; classes limited to `class`+`__init__`+methods+`self.attr` (no inheritance/dunders/decorators); no ord/chr/comprehensions/tuple-assignment.
### Phase D — solutions (SEPARATE fresh Codex): U12 + U13 + cp05 solutions.ipynb (function/class form; round-trip file asserts; ≥3 assert cells; no forbidden forms). Verify `exec-solutions`.
### Phase E — teacher-notes (inline, all three) + verification: full `TMPDIR=/dev/shm bash scripts/ci-local.sh`
ALL GREEN (registry/lint, unit tests, notebook exec+hygiene incl. no stray untracked files, manifest/prereq/
coverage/stretch, concept-scan, checkpoint questions, PDF, pre-merge-guard). Static AST audit: file/dict/list/
string methods within subsets; builtins in-set + no `key=`; no `ord`/`chr`/`collections`/comprehensions/
tuple-assignment/step-slices; classes use no inheritance, no dunders beyond `__init__`, no decorators. Confirm
exec leaves the tracked `.txt` fixtures unchanged (idempotent) and creates no untracked files. Scope allowlist
= this plan + the U12/U13/cp05 trees + coverage-map + syllabus.

## Out of scope
- The Algorithm Challenge (plan 078). No tooling/stub changes; no governance/Book-1/2 changes.
- No inheritance / dunder methods beyond `__init__` / decorators / `@property`; no `collections`; file methods
  limited to read/readlines/readline/write/close.
- **Verification phase:** Phase E is the named verification phase (both units + checkpoint → required).

## Plan Review

### Round 1 (2026-09-23)
**[self] APPROVE.** Closure: U12 requires ⊆ U01–U10, U13 requires ⊆ U01–U07, cp05 requires/practices ⊆ U01–U13
(no fastforward); no self-practice; 55→62 introduced-once (ALL 62 catalog concepts now introduced). The
plan-076 debt is discharged (transform-each/linear-search → U12; string-slice → U13); U12 intros practiced in
U13+cp05, U13 intros practiced in cp05 — so after this plan every concept has a non-capstone practice site and
078 can leave buildout. Risks pinned: file self-contained-setup pattern (idempotent exec, tracked fixtures);
classes limited to `class`+`__init__`+methods+`self.attr` (NO inheritance/dunders-beyond-`__init__`/decorators);
file methods ⊆ read/readlines/readline/write/close; tier-C forms via reviewers + Phase-E audit. Named
verification phase (E) covers both units + the checkpoint.
_(Awaiting [sol]/[glm]/[fable].)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(Filled before shipping.)_

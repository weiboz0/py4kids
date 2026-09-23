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
- **Checkpoint 05** — MANDATORY, after U13. It practices BOTH U12's file concepts AND U13's four OOP concepts
  (design §3 note). It is the ONLY practice site for U13's OOP introductions before the capstone; U12's file
  concepts are practiced in U13 (reuse) AND cp05.

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
  class-def, init-method, attributes, methods, linear-search, string-slice, for-loop, list-append, list-literal,
  string-methods, type-conversion, if-statement, elif-else, comparison, boolean, arithmetic, count-by-condition,
  accumulator, builtin-functions, int-type, f-string, string-literal]`
  (**[sol] blocker:** cp05's outline assesses `linear-search` (search lines) and `string-slice` (slice an
  attribute) — `string-slice` is scanner-detected so it MUST be listed; `linear-search` is added for honesty.)

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
- **`attributes` IS detected** (`visit_Attribute` on `self.x`, concept_scan.py:406) — `open()`-mode →
  file-read/file-write is also detected (:457-464); reviewers still confirm the concept is genuinely present.
- **NOT scanner-flagged in Book 1b (reviewers + Phase-E audit):** `ord`/`chr`, comprehensions, tuple/multiple
  ASSIGNMENT (`a, b = …`; `for k, v in d.items()` stays exempt), step slices, `collections`/`defaultdict`,
  and **inheritance / dunder methods other than `__init__`** (no `__str__`/`__repr__`/`__eq__`/base classes —
  a `describe()`/`to_text()` method returns the string instead), and **`@` decorators / `@property` /
  `@staticmethod` / `@classmethod`**. Keep classes to `class Name:` + `__init__(self, …)` + plain methods +
  `self.attr`. `distance` uses `** 0.5` or squared/Manhattan distance — NEVER `math.sqrt` (untaught `import`;
  `sqrt` ∉ TAUGHT_METHODS). `Fraction` (needs gcd + multi-return) is a STRETCH at most; the reachable core
  classes are `Point`, `Counter`, and one record class (`Student`/`Rectangle`).
- **FILE I/O SAFETY (clone Book 1 u09-save-point EXACTLY):** every file drill is SELF-CONTAINED — a setup cell
  (or the function itself) WRITES the file with known content before reading it, so `exec-solutions`/
  `exec-lessons` are idempotent and order-independent. **Scratch `.txt` files are NEVER committed — they are
  runtime scratch, `.gitignore`d** (matching book1 `.gitignore:25-35`): add the U12/U13/cp05 scratch paths to
  `.gitignore` with a "never commit" comment. Use relative paths (CWD = content dir at exec, notebooks.py:1000)
  and a per-exercise filename (`ex3_scores.txt`, `q4_records.txt`, …) so lesson/exercise/solution runs don't
  collide. Content is written in-cell (no opaque blobs, design §8): `with open(path, "w") as f: f.write(...)`
  then `with open(path) as f: ...`. **Write lines with f-strings (`f.write(f"{x}\n")`), NEVER `str(x) + "\n"`**
  (the Book-1 `+`-concat idiom would emit `string-concat`). There is no CI "untracked files" check → the
  Phase-E audit asserts manually that exec leaves the working tree clean (all scratch gitignored).
- **cp05 strict avoid-list (no fastforward; every detected concept must be in requires∪practices):** write
  files with f-strings (no `string-concat`); search lines with `==`/`string-methods` (NO `in-operator`); NO
  `break`, `and`/`or` (`logical-ops`), `range`, `sorted` (`list-sort`) — none are needed by the question mix,
  and each is a detected-but-unlisted concept that would fail the checkpoint scan.
- Function form: solutions define the function/class + assert several distinct cases (round-trip save/load
  asserts for files; construct-then-check + attribute-after-call for objects); ≥3 non-vacuous assert cells;
  no `input()`; unique cell ids; student notebooks solution-free with NO executed outputs.

## Teaching outlines

### U12 Files (3 lessons, problem-first, function form)
- **L1 — Write and Read (`file-write`, `file-read`, `with-statement`).** Hook: save a list of scores, load
  them back. `with open(path, "w") as f: f.write(f"{x}\n")`; read the whole file with
  `with open(path) as f: f.read()`. **Motivate `with` with a contrast cell:** `f = open(path); f.write(...);
  f.close()` — "`with` does the `close()` for you even if you forget or the program crashes" (`close` is in
  TAUGHT_METHODS, so scan-safe). Self-contained setup writes the file first.
- **L2 — Numbers → Stats.** `for line in f:` + `int(line.strip())` to load numbers (introduced here — L1 read
  whole-file only); compute stats: total (`running-total`/`accumulator`), count-by-condition, `min`/`max`/
  `sum`/`len` (`builtin-functions`), the best (`find-extreme`). Seeded functions (`save_scores(scores, path)`
  / `load_scores(path)` / `stats(path)`).
- **L3 — Records & Search.** Save/load simple records (one field per line); **transform each line** into a
  cleaned/typed value with an `append` loop (`transform-each` — the debt site); a **linear-search** written as
  `for line in f: if line.strip() == target: return …` returning the first match (or a "not found" message) —
  the debt site (the line-by-line `for … return` shape, NOT `target in text`).
60-min cut per lesson in teacher-notes: L1 = write + whole-file read (the `for line in f` + `int(line.strip())`
loop opens L2).

### U13 Objects (3 lessons, problem-first, function form + classes)
Hook (design §6 engagement): "a scoreboard needs each player to carry name + score + wins together — a class
bundles those into one object you can pass around."
- **L1 — Define a Class (`class-def`, `init-method`, `attributes`).** `class Point:` with
  `def __init__(self, x, y): self.x = x; self.y = y`; create instances; read `p.x`. **Explain `self` as "THIS
  particular object" (reuse Book 1 u10's phrasing — NOT "scope"); the object-identity beat: make TWO
  instances, change one's attribute, show the other is untouched.** Core classes: `Point`, `Student`/
  `Rectangle`, `Counter`. Trap: forgetting `self`.
- **L2 — Methods (`methods`).** Methods that use the attributes and RETURN a value: `area`/`perimeter`,
  a `distance` via `** 0.5` (or Manhattan/squared — NO `math.sqrt`), `describe()` returning an f-string (no
  `__str__`); **`string-slice` on an attribute string — a GENUINE slice** (e.g. `self.code[0:2]` region from a
  ticket ID, or `self.name[:3]` short-name — NOT `name[0]`, which is string-index). Contrast a method with a
  plain function that takes the object.
- **L3 — Objects that Persist.** A `Counter`/`Point` with a `save(path)` method (`file-write` via f-string
  lines) and a **MODULE-LEVEL `load_point(path)` that reads and RETURNS a new object** (`file-read`/
  `with-statement`) — the file reuse from design §3 (a `@classmethod` is banned; a mutating `load(self)` is
  odd for beginners). Mutating methods (`Counter.increment`) are fine — assert via the attribute after the
  call. `Fraction` (gcd/simplify) is a stretch at most.
60-min cut per lesson in teacher-notes (OOP is the hardest unit).

### Checkpoint 05 (mandatory, after U13, strict, no turtle, no fastforward)
**7 VISIBLE `## Question N`** (min 6), practicing BOTH units; budget 45–60 min in teacher-notes (heavier than
cp04 — file setup + class definitions). Each declared practice tag maps to a named question:
1. save/load round-trip function (`file-write`+`file-read`+`with-statement`; f-string lines). *Pass-bar.*
2. load-then-stat (`for line in f`, `int(line.strip())`, `list-append`, `count-by-condition`, `accumulator`,
   a builtin like `max`/`sum`).
3. `linear-search` over lines (`for line in f: if line.strip() == target: return`; NO `in-operator`).
4. define a small class (`class-def`+`__init__`+`attributes`); construct + read an attribute.
5. a method returning a computed value AND a `describe()`-style f-string method (`methods`, `f-string`).
6. a band/verdict method using an `elif-else` ladder on an attribute (`elif-else`, `boolean`, `comparison`).
7. a class whose method **saves itself to a file** and a slice of an attribute string (`string-slice`) —
   ties U12+U13. *Pass-bar (define-a-class-with-a-method).*
File questions are SELF-CONTAINED (write before read, per-question filename, gitignored). Strict — only
concepts ≤ U13; no inheritance/dunders-beyond-`__init__`/decorators; f-strings only (no `+`-concat); NO
`in-operator`/`break`/`and`/`or`/`range`/`sorted`. teacher-notes has `## Grading` (pass-bars: save/load
round-trip [Q1]; define-a-class-with-a-method [Q7]) + the full heading set incl. `## Discussion prompts`.

## Value plan
Distinct inputs per exercise/question, distinct from lesson examples and each other; list the
(function/class, sample inputs) inventory in each unit's + the checkpoint's teacher-notes so the gate can check.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: 3 coverage-map entries + 2 unit manifests + 1 checkpoint manifest + 3 syllabus rows; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): U12 + U13 lesson.ipynb + exercises.ipynb + cp05 checkpoint.ipynb + a `.gitignore` block adding the U12/U13/cp05 runtime scratch `.txt` paths (per-exercise filenames; "never commit", cloning book1 `.gitignore:25-35`). Per unit ≥8 exercises (core ≤7, ≥2 stretch); cp05 7 visible `## Question N`. Pin: function form; files written in-cell with f-string lines (self-contained setup, NEVER `str(x)+"\n"`); file methods ⊆ {read,readlines,readline,write,close}; classes limited to `class`+`__init__`+methods+`self.attr` (NO inheritance/dunders-beyond-`__init__`/decorators, distance via `**0.5`, module-level `load_*` returns a new object); no ord/chr/collections/comprehensions/tuple-assignment; cp05 avoid-list (no in-operator/break/and-or/range/sorted).
### Phase D — solutions (SEPARATE fresh Codex): U12 + U13 + cp05 solutions.ipynb (function/class form; round-trip file asserts; ≥3 assert cells; no forbidden forms). Verify `exec-solutions`.
### Phase E — teacher-notes (inline, all three) + verification: full `TMPDIR=/dev/shm bash scripts/ci-local.sh`
ALL GREEN (registry/lint, unit tests, notebook exec+hygiene incl. no stray untracked files, manifest/prereq/
coverage/stretch, concept-scan, checkpoint questions, PDF, pre-merge-guard). Static AST audit: file/dict/list/
string methods within subsets; builtins in-set + no `key=`; no `ord`/`chr`/`collections`/comprehensions/
tuple-assignment/step-slices; classes use no inheritance, no dunders beyond `__init__`, no decorators; no
`math`/`sqrt`; cp05 has no in-operator/break/and-or/range/sorted/`+`-concat. **Manually assert exec leaves the
working tree CLEAN** — every scratch `.txt` the notebooks write is `.gitignore`d, so `git status` shows no
new untracked files after `exec-lessons`/`exec-solutions` (there is no CI check for this). Scope allowlist =
this plan + the U12/U13/cp05 trees + coverage-map + syllabus + **`.gitignore`** (a one-block exception to
"no tooling changes", adding only the runtime scratch paths).

## Out of scope
- The Algorithm Challenge (plan 078). No tooling/stub changes (the ONLY exception: a one-block addition to
  `.gitignore` for the U12/U13/cp05 runtime scratch `.txt` paths, cloning book1's existing pattern); no
  governance/Book-1/2 changes.
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

**[fable] APPROVE WITH NITS; [glm] APPROVE WITH NITS; [sol] REJECT.** All three confirm closure + full
practice-coverage (the 078 anchor's unpracticed set = ∅). Folded:
- `[FIXED]` ([sol] blocker) cp05 practices += `linear-search` + `string-slice` (its outline assesses both;
  string-slice is scanner-detected).
- `[FIXED]` ([fable]N1, verified against `.gitignore:25-35` + `git ls-files`) — reversed the fixture pin:
  scratch `.txt` are NEVER committed, they are `.gitignore`d runtime scratch written in-cell; per-exercise
  filenames; `.gitignore` gets a one-block addition (Phase-E scope); "no untracked files after exec" is a
  manual Phase-E assertion. (Resolves the [fable]↔[glm]1 contradiction in favor of the actual house convention.)
- `[FIXED]` ([fable]N2) distance via `**0.5`/Manhattan/squared (no `math.sqrt`); `Fraction` → stretch; core
  classes `Point`/`Counter`/`Student`/`Rectangle`.
- `[FIXED]` ([fable]N3/[sol]) string-slice debt site is a GENUINE slice (`code[0:2]`/`name[:3]`, not `name[0]`);
  U12 linear-search pinned to the `for line in f: … return` shape (not `target in text`).
- `[FIXED]` ([fable]N4) `self` = "THIS particular object" (not scope) + the two-instance identity beat.
- `[FIXED]` ([fable]N5) L3 loader is a MODULE-LEVEL `load_*(path)` returning a new object (no `@classmethod`;
  mutating methods like `Counter.increment` fine).
- `[FIXED]` ([fable]N6) U12 L1 split (write + whole-file read; `for line in f` opens L2) + a `with`-motivation
  contrast cell (`open`/`close` → "`with` closes it for you").
- `[FIXED]` ([glm]2) cp05 avoid-list (no `in-operator`/`break`/`and`-`or`/`range`/`sorted`/`+`-concat) so its
  strict scan stays closed; write lines with f-strings.
- `[FIXED]` ([fable]N8) cp05 = 7 questions, 45–60 min, every practice tag mapped to a named question.
- `[FIXED]` ([fable]N9) U13 project-first hook added; `attributes` note corrected (IS detected, :406).
- `[FIXED]` ([sol] nit) scope wording (U13+cp05 practice U12's file intros, not "cp05 only").
- `[WONTFIX/record]` ([fable]N7 vs [glm]3) file concepts stay in U13 `practices` (design §3 frames U13's file
  I/O as REUSE; closure holds; cp05 also practices them) — NOT moved to requires.

### Round 2 (2026-09-23) — re-dispatched [sol]/[glm]/[fable].
**[self] APPROVE** — cp05 lists linear-search+string-slice; fixtures gitignored (not committed) per the
verified house convention; class/distance/slice/loader/`with`/`self` pins corrected; cp05 avoid-list closes
its strict scan.
_(Awaiting [sol]/[glm]/[fable] round-2 verdicts.)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(Filled before shipping.)_

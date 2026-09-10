# Plan 031 — Book 1 Worked-Example Ladders (pilot: U01 + U02)

**Goal:** Replace the single-example-per-concept lessons in U01 and U02 with a graduated **worked-example
ladder** (3 examples of rising complexity per newly-introduced concept) so young beginners can generalize
each concept, and establish the ladder as a reusable standard for rolling out to U03–U10 in later plans.

**Architecture:** Lesson-only content change. Each newly-introduced concept's single example becomes a
3-rung ladder (minimal → one twist → realistic), each rung followed by a one-line **Notice:** naming what
changed. Concepts a unit only reuses (not introduces) get a one-line recap, not a ladder. The concepts a unit
introduces/requires/practices are UNCHANGED — only the number of examples grows — so coverage/prereq/
concept-scan stay stable. The per-unit `lessons` value is an ADVISORY workload estimate, not a fixed
schedule — the teacher pulls in as many ladder rungs as class time allows (user: "budget isn't a constraint;
teacher can flexibly adopt content anytime"). We still bump the estimates to reflect the richer content (U01
2→3, U02 3→4) and raise book-1's `lesson_budget` ceiling generously in `books.yaml` so the tooling guardrail
never crowds content, but the numbers are guidance, not a timetable.

**Tech stack:** Jupyter lesson notebooks; `tools/` verification; `scripts/ci-local.sh`.

**Spec / design:** `docs/designs/000-project-design.md` (self-containedness + project-first). This plan adds
the worked-example-ladder standard below; later rollout plans (U03–U10) cite it. User decisions (2026-09-09,
AskUserQuestion): pilot U01+U02; 3 graduated examples + Notice per new concept; allow more lessons.

## The worked-example ladder standard (reusable)

**Two governing principles (the key quality bar):**
- **Completeness** — the rungs together cover a concept's realistic everyday variations, not one lucky case,
  so a beginner sees the *pattern* and can generalize (e.g. f-strings: one value, several values, a value
  used twice; comparisons: `<`, `>`, `==`, and `!=`, not just one operator).
- **Gradual pacing** — each rung adds exactly ONE new increment of difficulty over the one before it. No
  rung introduces two new ideas at once, and there are no difficulty jumps; a student who followed rung *k*
  can follow rung *k+1* with one small step.

For each concept a unit **introduces**, the lesson presents, right after the concept's one-sentence
explanation, a ladder of rungs:

1. **Rung 1 — minimal:** the simplest possible use, one idea only.
2. **Rung 2 — one step up:** the same concept with exactly one added wrinkle.
3. **Rung 3 — realistic:** the concept as it appears in real use / combined with earlier concepts, still
   within what has been taught.

**The rung count follows the concept's difficulty — it is not a fixed number.** Most concepts get 3 rungs
(minimal → one step up → realistic); a beginner-hard concept (`if-statement`/`elif-else`, `while-loop`,
`arithmetic`) gets 4+ so no single rung is a leap; a trivially simple concept (e.g. `comment`) may need only
2. The target is completeness + gradual pacing, never a rung quota. Each rung (after the first) carries a one-line **`Notice:`** markdown line naming precisely the one
thing that changed from the previous rung ("Notice: you can drop in more than one `{…}`"), so the gradual
progression is explicit and students extract the rule rather than memorize a line. Rungs are short (2–5 code
lines). A concept a unit only **reuses** gets a single one-line recap + at most one example, not a ladder.
The `error-messages` deliberate-error demo stays a single `no-exec` example (its job is to show one
traceback, not to generalize). `input` DOES get a ladder, but since `input()` can't be executed under CI its
rungs are all tagged `no-exec` (e.g. prompt → save the reply in a variable → reuse the saved reply in a
later line); `run-program`/`error-messages` keep their existing single-demo framing.

## Global Constraints

- **Closure is law (the central risk):** a ladder rung may use ONLY concepts already taught at that point in
  the unit's lesson ORDER (concept-scan is unit-level and will NOT catch a within-unit ordering violation —
  reviewers must). In particular **U01 rungs use only strings / variables / `input` / concat / f-string — NO
  numbers or arithmetic** (those arrive in U02). U02 rungs may use U01 concepts + the U02 concepts taught
  earlier in U02, never a later-in-U02 concept. Two closure clarifications so the audit doesn't false-positive: (a)
usage-order ≠ formal-naming-order within a cell is fine — a `print` rung uses a string literal before
`string-literal` is formally named, exactly as the current notebook already does; the audit keys on whether a
concept has been TAUGHT by that lesson, not on naming sequence; (b) CO-TAUGHT pairs that share one lesson cell
(`boolean`+`comparison`; `import-statement`+`random-module`) may appear together in a rung — the author picks
a sensible intra-cell order, and neither counts as "used before taught".
- **`accumulator`/`loop-counter` are OFF-LIMITS (CI-enforced trap):** `loop-counter` is U03 and `accumulator`
  is U04, and `accumulator` is AST-detected by concept-scan (any `x = x + …` read-modify-write or `x += …`
  fails CI as used-but-unlisted). So **`while-loop` rungs must NOT use a counting/accumulating variable** —
  use condition-driven termination instead (an `input()`-driven loop as a `no-exec` rung, or shrinking a
  value with taught arithmetic that is not `+`-accumulation, e.g. `n = n // 2`), matching U02's existing
  counter-free while-loop. The general closure law covers this, but it is called out because it is the
  natural-but-wrong way to write a loop ladder.
- **Execution:** `exec-lessons` runs every lesson code cell EXCEPT those tagged `no-exec`. New executable
  rungs must run top-to-bottom clean in the shared kernel (use literal values; they may build on variables
  set by earlier executed cells). Any rung using `input()` or demonstrating an error is tagged `no-exec`.
  Prefer executable `print`/f-string rungs (real output aids learning) over `input()` ones.
- **Concepts unchanged:** U01/U02 `manifest.concepts` (introduces/requires/practices) and their coverage-map
  entries stay identical EXCEPT the `lessons` count. No new concept is introduced or used. Exercises,
  solutions, and checkpoints are untouched.
- **Lessons stay worked examples:** no solutions to the exercises, no graded tasks — lessons demonstrate;
  practice stays in `exercises.ipynb`. Each lesson still opens project-first (the unit's hook is preserved).
- **House style:** allowed Book-1 constructs only (no concept used before its unit/position); every code cell
  a unique id; no stored outputs; semantic line breaks in markdown.
- **Pacing:** `teacher-notes.md` for U01/U02 updates its per-lesson concept allocation to the new lesson
  count and keeps each lesson within 60–90 min; `## Pacing` must cover ALL lessons (`lessons: N` → N blocks).

## Out of scope

- U03–U10 (later rollout plans, citing this standard) and all projects/checkpoints.
- Any change to the concept set, exercises, solutions, or checkpoints.
- Book 2 (unaffected; its budget default is independent).
- **Verification-phase note:** this plan ships reworked unit lessons WITH a named verification phase
  (Phase D). The change is lesson-content + pacing/metadata only; exercises/solutions are unchanged, so the
  "named verification phase" requirement is met by Phase D (exec-lessons + closure review).

## Phases

### Phase A — U01 "Story Machine" lesson ladders

Rework `book1/units/unit-01-story-machine/lesson.ipynb`: for each introduced concept
(`print, comment, string-literal, variable, naming, input, string-concat, f-string`; `run-program` and
`error-messages` keep their existing framing/single demo), expand the single example into a graduated ladder
(typically 3 rungs; 2 for a trivial concept like `comment`, 4+ where completeness/gradual pacing need it) +
`Notice:` lines per the standard. All rungs use STRINGS only (no numbers). `input()` rungs and the
`SyntaxError` demo stay `no-exec`; the rest execute clean. Re-segment the lesson arc into **3 lesson
sections** (the richer ladders no longer fit two). Update `book1/units/unit-01-story-machine/
teacher-notes.md` `## Pacing` to 3 lessons with the concept→lesson allocation, and set
`manifest.yaml` `lessons: 3` (concepts unchanged).

### Phase B — U02 "Number Detective" lesson ladders

Rework `book1/units/unit-02-number-detective/lesson.ipynb`: graduated ladders (≥3 rungs; `arithmetic`,
`comparison`, and `while-loop` carry 4–5 rungs; `if-statement` and `elif-else` get 3 each and together form a
6-rung conditional arc — all complete and one-increment-per-rung) for the introduced concepts (`int-type, arithmetic, type-conversion, boolean, comparison, if-statement,
elif-else, import-statement, random-module, while-loop`), respecting U02's internal order (e.g. a
`comparison` rung must not use `while-loop`). Reused U01 concepts (`print, input, variable, f-string`) get a one-line recap, not a ladder.
Executable rungs run clean; `input()`/error rungs `no-exec`. Re-allocate across **4 lessons**; update
`teacher-notes.md` `## Pacing` to 4 lessons and set `manifest.yaml` `lessons: 4` (concepts unchanged).

### Phase C — Lesson budget + map + syllabus

- `books.yaml`: add `lesson_budget: [28, 44]` to the `book1` entry — real headroom so neither this pilot
  (total 34) nor the eventual U03–U10 rollout has to re-bump the ceiling every plan (min unchanged; the
  number is a loose guardrail, per "budget isn't a constraint", not a target).
- `book1/curriculum/coverage-map.yaml`: set U01 `lessons: 3`, U02 `lessons: 4` (must equal the manifests).
- `book1/syllabus.md`: update the arc-table `Lessons` cells for U01 (2→3) and U02 (3→4); the prose
  "summing to 32 — 24 unit lessons…" → the new total (34 — 26 unit lessons + 6 project + 4 half-checkpoints);
  and the stale "~30 lessons" (line ~4) and "~30–32 class sessions" (line ~31) phrases → the new figure.
  (Syllabus prose is consistency-only, not CI-checked, but keep it accurate.)

### Phase D — Verification (named verification phase)

- `scripts/ci-local.sh` ALL GREEN, with attention to: **`exec-lessons`** (every non-`no-exec` U01/U02 rung
  runs clean), **`prereq-check`/`coverage-check`** (concept sets unchanged → still pass), **`lesson-budget`**
  (total 34 ≤ new ceiling 34), **`structure-check`/`hygiene-check`/`noexec-check`** (unique ids, no stored
  outputs, `no-exec` tags correct), manifest==map (`lessons` values), PDF build, pre-merge guard.
- **Closure audit (manual + AST):** confirm NO ladder rung uses a concept introduced later in its own unit or
  a not-yet-taught concept — especially that no U01 rung uses numbers/arithmetic. (This is the gate's primary
  content-review duty, since concept-scan is unit-level.)
- Confirm each lesson still opens project-first and the `## Pacing` blocks match the new `lessons` counts.
- **Completeness + gradual-pacing audit (the key content-review duty):** for every introduced concept,
  confirm (a) the rungs cover its realistic everyday variations (a beginner could generalize the pattern,
  not just replay one line), and (b) each rung adds exactly ONE increment over the previous — no rung
  introduces two new ideas and there is no difficulty jump. Reviewers flag any concept whose ladder is thin
  (incomplete) or whose rungs jump. This is the bar the whole plan exists to meet.

## Post-Execution Report

**Shipped (pilot):** reworked U01 (Story Machine) and U02 (Number Detective) lessons with worked-example
ladders, establishing the reusable standard for a later U03–U10 rollout.

**Phase A — U01:** `lesson.ipynb` rebuilt (24 → 62 cells; 26 code, 5 `no-exec`), re-segmented into 3 lesson
sections (output basics → saving/reusing → combining + project). Each introduced concept is now a graduated
ladder + `Notice:` lines (print 3 rungs, string-literal 3, comment 2, variable 3, naming 3, input 3 all
`no-exec`, string-concat 3, f-string 3; `error-messages` keeps its single broken/fixed demo). All rungs are
STRINGS only (no numbers — arithmetic is U02). teacher-notes `## Pacing` → 3 lessons; manifest `lessons: 3`.

**Phase B — U02:** `lesson.ipynb` rebuilt (23 → 72 cells; 31 code, 8 `no-exec`), re-segmented into 4 lesson
sections (numbers → picks & judges → one-guess verdict → full game + debugging). Ladders for all 10 introduced
concepts: `arithmetic` 5 rungs (`+` → `-`/`*` → saved numbers → `//` → `%`), `comparison` 5 (one `==` → `<`
both ways → all four operators → compare variables → store the `True`/`False`), `while-loop` 4; `if-statement`
and `elif-else` 3 each (a 6-rung conditional arc together); the rest 3 (`int-type`/`type-conversion`/
`random`) — every ladder complete and one-increment-per-rung (rung counts follow difficulty, not a quota). **while-loop rungs are all `no-exec` + input-driven with NO counting variable** — any read-modify-
write (`x = x - 1`, `x = x // 2`, …) is flagged `accumulator` (U04) by concept-scan, so loops make progress by
re-reading `input()`, matching the existing unit. teacher-notes `## Pacing` → 4 lessons; manifest `lessons: 4`.

**Phase C:** `books.yaml` book1 `lesson_budget: [28, 44]` (headroom for the rollout); coverage-map U01 `lessons:
3`, U02 `lessons: 4` (= manifests; total 34); syllabus arc-table + the "~30 lessons"/"summing to 32"/"~30–32
class sessions" prose updated to the advisory new figures.

**Phase D — verification:** `ci-local.sh` ALL GREEN. concept-scan clean (two `+` false-classifications fixed:
a U01 variable+variable concat read as `arithmetic` → kept a string literal in every U01 `+`; a U02 concat
read as `string-concat` not in U02's manifest → used an f-string instead, keeping U02 concat-free as shipped).
exec-lessons runs every non-`no-exec` rung clean; AST closure audit confirms no U01 rung uses a number and no
rung uses a later-in-unit concept or `accumulator`/`loop-counter`. Concepts introduced/required/practiced
unchanged (only `lessons` + examples grew); exercises/solutions/checkpoints untouched.

**Deviations:** none to scope. `lesson_budget` set to `[28, 44]` (not the exact 34) for rollout headroom, per
the round-1 nit + "budget isn't a constraint".

## Plan Review

### Round 1 (2026-09-09, HEAD 04aaaba) — [self] APPROVE · [glm] AWN · [fable] AWN · [sol] pending

[glm] and [fable] both independently verified (against both manifests, both notebooks, and the tooling): the
closure constraint is correct (U01 strings-only; `int-type` is `MANUAL_ONLY` so a stray number wouldn't even
be CI-caught → reviewer-enforced is accurate), metadata stays stable (concepts untouched; `manifest.lessons
== map.lessons` enforced), the budget override is valid (`books.yaml` not governance-restricted; total 34),
Phase D is an adequate named verification phase, and the ladder pedagogy is sound (worked-example effect +
variation theory). Both APPROVE WITH NITS on the same 5 points; [sol]'s codex task backgrounded without a real
verdict (flaky) — re-dispatched on the fixed HEAD. Dispositions (all `[FIXED]`):

1. `[FIXED]` **while-loop `accumulator` trap** — a counting loop (`x = x + 1`) is AST-detected as `accumulator`
   (U04) and FAILS concept-scan; `loop-counter` is U03. → Added an explicit Global-Constraints rule:
   while-loop rungs use condition-driven termination (input-driven `no-exec`, or shrinking via non-`+`
   arithmetic like `n = n // 2`), never a counter/accumulator — matching U02's existing counter-free loop.
2. `[FIXED]` **"3 is the floor" vs "comment may need 2" + co-taught pairs** — added closure clarifications:
   usage-order ≠ naming-order is fine; co-taught pairs (`boolean`+`comparison`, `import-statement`+
   `random-module`) may share a rung with an author-chosen intra-cell order.
3. `[FIXED]` **budget ceiling exactly-tight vs "generously"** — set `lesson_budget: [28, 44]` (real headroom
   for the rollout), not `[28, 34]`.
4. `[FIXED]` **`input` ladder contradiction** — the standard said input keeps a single demo, but Phase A
   laddered it. → `input` gets a ladder of all-`no-exec` rungs (prompt → save → reuse); only the
   `error-messages` deliberate-error demo stays a single example.
5. `[FIXED]` **wording** — Phase A "keep Lesson One/Two but re-allocate" → "re-segment into 3 lesson
   sections"; Phase C now also updates the stale syllabus "~30 lessons" / "~30–32 class sessions" prose.

### Round 2 (2026-09-09, HEAD 04e7b7e) — [sol] REJECT (one wording contradiction) → `[FIXED]`

[sol]'s codex task failed to return a verdict on several attempts this session (infrastructure flakiness);
the attempt that landed gave: **REJECT — "the ≥3-rung floor is contradictory: the standard and Phase A
explicitly permit only 2 rungs for `comment`."** This is the same logical contradiction [glm] flagged as N1.
`[FIXED]`: removed the "floor" framing entirely — the standard and Phase A now say the rung count follows
difficulty (typically 3; 2 for a trivial concept like `comment`; 4+ for beginner-hard concepts), with
completeness + gradual pacing as the target, not a quota. No contradiction remains.

### Round 3 — [sol] APPROVE (re-confirm on fixed wording)

[sol]: "APPROVE — the standard says rung count follows concept difficulty, not a quota, and Phase A
consistently says 'typically 3', '2 for a trivial concept like comment', and '4+' when needed."

### CONSENSUS — plan-review gate CLOSED

[self] APPROVE · [glm] APPROVE WITH NITS · [fable] APPROVE WITH NITS · [sol] APPROVE. Full 4-way consensus;
every finding `[FIXED]` (while-loop accumulator trap, closure clarifications, budget headroom, input ladder,
rung-count wording). Cleared for implementation (Phases A–D).

## Content Review

### Review 1 — [self] (2026-09-09, HEAD 6940e66) — APPROVE

Both lessons execute clean (no-exec stripped); AST closure audit clean (U01 zero numbers/non-Add BinOps;
U02 zero accumulator/loop-counter — while rungs input-driven); every concept's ladder is complete +
one-increment; concepts introduced/required/practiced unchanged; conventions clean; both open project-first.

### Reviews 2–3 — [glm] & [fable] (2026-09-09, HEAD 6940e66) — both APPROVE WITH NITS

Both independently executed both lessons (no-exec stripped), AST-audited closure/accumulator/numbers, and
judged the primary bar: **both confirm completeness + gradual pacing is MET** for every concept, Notices
accurate, closure clean (U01 zero numbers; U02 zero accumulator — while rungs input-driven), concepts
unchanged, conventions clean. No blocking findings. Nits (all `[FIXED]` unless noted):

1. `[FIXED]` **[glm/fable] arithmetic `//`/`%` in one rung** (the one rung both flagged as two-idea). →
   Split into two rungs (`//` quotient, then `%` remainder) — arithmetic now 5 rungs, strictly one-increment.
2. `[FIXED]` **[fable] `boolean` never stored in a variable** (only printed). → Added a comparison-ladder
   rung `is_too_low = guess < secret` / `print(is_too_low)` — shows a `True`/`False` value is storable.
3. `[FIXED]` **[glm/fable] int-type rung-3 Notice over-claimed "compute with"** before arithmetic. →
   Reworded to "Python treats them differently (you will see how in a moment)".
4. `[FIXED]` **[glm N1] plan/report claimed `if`/`elif` get 4 rungs** but they get 3 (complete + gradual, a
   6-rung arc together). → Phase B + post-exec report corrected to the actual per-concept counts.
5. `[FIXED]` **[fable] U02 teacher-notes "lesson-3 debugging session"** (stale after re-segmentation) →
   "lesson-4"; also fixed the Differentiation "lesson-2 detective" stale ref.
6. `[WONTFIX]` **[fable/glm] operator-pair rungs** (arithmetic `-`/`*`; comparison's four-operator rung) —
   both reviewers call these defensible single-category increments matching the operator-completeness intent.
7. `[WONTFIX]` **[fable] U01 naming rung-3** can't show a live misspelling (the teacher's traceback ritual
   does) — non-blocking; a teacher-notes pointer suffices at rollout.

Solutions re-executed clean after the fixes (U02 now 72 cells / 31 code); all book1 checks PASS. Awaiting
[sol] on the improved version.

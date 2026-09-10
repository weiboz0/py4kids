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

**Three rungs is the FLOOR, not a fixed count** — a concept gets as many rungs as completeness + gradual
pacing require. Simple concepts (e.g. `comment`) may need only 2; harder ones a beginner struggles to
generalize (e.g. `if-statement`/`elif-else`, `while-loop`, `arithmetic`) get 4+ so that no single rung is a
leap. Each rung (after the first) carries a one-line **`Notice:`** markdown line naming precisely the one
thing that changed from the previous rung ("Notice: you can drop in more than one `{…}`"), so the gradual
progression is explicit and students extract the rule rather than memorize a line. Rungs are short (2–5 code
lines). A concept a unit only **reuses** gets a single one-line recap + at most one example, not a ladder.
The deliberate-error / `input()` demos keep their existing single-example + `no-exec` treatment (executing
them would hang or raise).

## Global Constraints

- **Closure is law (the central risk):** a ladder rung may use ONLY concepts already taught at that point in
  the unit's lesson ORDER (concept-scan is unit-level and will NOT catch a within-unit ordering violation —
  reviewers must). In particular **U01 rungs use only strings / variables / `input` / concat / f-string — NO
  numbers or arithmetic** (those arrive in U02). U02 rungs may use U01 concepts + the U02 concepts taught
  earlier in U02, never a later-in-U02 concept.
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
(≥3 rungs; fewer only for a trivial concept like `comment`, more where completeness/gradual pacing need it) +
`Notice:` lines per the standard. All rungs use STRINGS only (no numbers). `input()` rungs and the
`SyntaxError` demo stay `no-exec`; the rest execute clean. Keep the Lesson One / Lesson Two structure but
re-allocate across **3 lessons** (see teacher-notes). Update `book1/units/unit-01-story-machine/
teacher-notes.md` `## Pacing` to 3 lessons with the concept→lesson allocation, and set
`manifest.yaml` `lessons: 3` (concepts unchanged).

### Phase B — U02 "Number Detective" lesson ladders

Rework `book1/units/unit-02-number-detective/lesson.ipynb`: graduated ladders (≥3 rungs; the
beginner-hard concepts `arithmetic, comparison, if-statement, elif-else, while-loop` get 4+ so no rung is a
leap) for the introduced concepts (`int-type, arithmetic, type-conversion, boolean, comparison, if-statement,
elif-else, import-statement, random-module, while-loop`), respecting U02's internal order (e.g. a
`comparison` rung must not use `while-loop`). Reused U01 concepts (`print, input, variable, f-string`) get a one-line recap, not a ladder.
Executable rungs run clean; `input()`/error rungs `no-exec`. Re-allocate across **4 lessons**; update
`teacher-notes.md` `## Pacing` to 4 lessons and set `manifest.yaml` `lessons: 4` (concepts unchanged).

### Phase C — Lesson budget + map + syllabus

- `books.yaml`: add `lesson_budget: [28, 34]` to the `book1` entry (raise the ceiling 32→34 for the two added
  lessons; min unchanged).
- `book1/curriculum/coverage-map.yaml`: set U01 `lessons: 3`, U02 `lessons: 4` (must equal the manifests).
- `book1/syllabus.md`: update the arc-table `Lessons` cells for U01 (2→3) and U02 (3→4), and the prose
  "summing to 32 — 24 unit lessons…" → the new total (34 — 26 unit lessons + 6 project + 4 half-checkpoints).

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

_(filled at Phase D)_

## Plan Review

_(4-way plan-review gate — consensus before any implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_

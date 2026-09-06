# Plan 005 — Checkpoint 01 + Unit 04 Implementation Plan

**Goal:** Ship the next two coverage-map entries in teaching order — `checkpoint-01-first-steps` (the year's first assessment, covering units 01–02) and `unit-04-quiz-show` — establishing the checkpoint pipeline (conventions + mechanical checks) the remaining three checkpoints will reuse.

**Architecture:** Unit 04 follows the plan-004 unit pipeline unchanged. Checkpoints get first-class conventions mirroring units (student notebook with no solutions, blind-authored solutions, map-equal manifest, teacher notes with grading guidance) and the `tools/` checks are extended from unit-only to unit+checkpoint scope. One curriculum-data amendment rides along: the coverage map's `unit-04-quiz-show.requires` gains `arithmetic` and `int-type` (standing plan-002 follow-up — the score accumulator plainly depends on them; closure holds, both taught in unit 02).

**Spec:** design 000 §1–§3; `book1/curriculum/coverage-map.yaml` (binding); plan 004's conventions + follow-ups; plan 003's check registry.

## Global Constraints

- All plan-004 Global Constraints apply verbatim to unit 04 (map-equal manifest, hook-first,
  exercise/solution floors and bans, seed rules, five teacher-notes headings, per-lesson
  concept allocation in Pacing, commit trailers per plan 002).
- **Checkpoint conventions (binding on all Book 1 checkpoints, new):**
  - Directory `book1/checkpoints/<map-id>/` with `manifest.yaml`, `checkpoint.ipynb`
    (student-facing), `solutions.ipynb`, `teacher-notes.md`.
  - `manifest.yaml`: same schema as units with `kind: checkpoint`; `concepts` EQUAL the map
    entry (the map already forces `introduces: []`).
  - `checkpoint.ipynb`: questions are markdown headings matching `^## Question \d+`,
    6–8 of them for a half-lesson; NO solutions, NO outputs, `input()` allowed;
    NO stretch requirement (assessments assess — the mixed-ability rule lives in units);
    every question uses only concepts from the entry's `practices` ∪ `requires`.
  - `solutions.ipynb`: mirrors every `## Question N` heading with ≥1 code cell,
    ≥3 assert cells, the unit solution conventions verbatim (no input()/GUI,
    `import random` only, seed-before-first-use, self-contained, scaffolding note).
  - `teacher-notes.md`: the five unit headings PLUS `## Grading` (per-question intent,
    what partial understanding looks like, when to re-teach vs move on).
- Coverage-map amendment is EXACTLY: append `arithmetic, int-type` to
  `unit-04-quiz-show.requires`. Nothing else in the map changes; all curriculum
  invariants must still pass; unit-04's manifest carries the amended list.
- Unit 04 finally has counters: `loop-counter` (introduced in unit 03) is in its
  `practices` — the "machine learns to count" promise from unit 02's teacher notes
  is paid off explicitly in the lesson.

## Out of scope

This is a CONTENT plan (a named verification phase is therefore mandatory — Phase E).
Out of scope: checkpoints 02–04 and units 05+ (later plans reuse today's conventions);
PDF handouts for checkpoints (build-pdf stays unit-scoped until a checkpoint-print need
is real); auto-grading (design 000 out-of-scope); any change to unit-01..03 content.

## Phases

Dispatch per AGENTS.md: statements (checkpoint questions + unit-04 lesson/exercises) via
codex GPT-5.6-sol; SOLUTIONS via a SEPARATE fresh blind codex session (finished statements
only — never the blueprints); teacher/grading notes inline; `tools/` extension via codex;
map amendment + manifests inline (trivially-scoped data edits).

### Phase A — checkpoint support in tools (TDD, codex)

**Files:** `tools/notebooks.py`, `tools/checks.py`, `tests/test_tools.py`, `tests/test_book1_units.py` (or a new thin wrapper module for checkpoints).
1. `checkpoint_dirs(root, book, checkpoint=None)` mirroring `unit_dirs` (fail-closed the
   same way; empty checkpoints/ = N=0 pass).
2. Extend or twin the checks: layout (checkpoint file set), manifest (map-equal, kind
   checkpoint), hygiene (checkpoint.ipynb), structure (`^## Question \d+` count 6–8,
   solutions mirroring + floors + bans + seed), exec-solutions; the checkpoint prefix rule
   (existing checkpoint dirs = first M checkpoint map entries, in order). NO stretch, NO
   lesson/no-exec, NO turtle checks for checkpoints.
3. CLI: existing check names gain checkpoint coverage transparently (a check reports both
   scopes); `--unit` continues to accept a checkpoint id for unit-scoped checks where that
   is coherent, else document.
4. One-fault fixtures for every NEW rule (question-count floor both directions, mirror,
   manifest kind/equality, prefix rule, hygiene) from a generated valid checkpoint —
   same fixture-factory discipline as plan 003; nothing broken committed.
5. Parity guard: all existing unit checks unchanged on the real book (same pass set).

### Phase B — map amendment + manifests (inline)

1. Amend `coverage-map.yaml` (`unit-04-quiz-show.requires` += arithmetic, int-type).
2. `book1/checkpoints/checkpoint-01-first-steps/manifest.yaml` and
   `book1/units/unit-04-quiz-show/manifest.yaml`, both map-equal.
3. Full curriculum suite green before any content lands.

### Phase C — checkpoint-01-first-steps content

Blueprint (statements codex; solutions blind codex; grading notes inline):
- 7 questions over the entry's practices (u01–u02 material), ~30–45 min of a lesson slot:
  fix-the-error (traceback reading), predict-the-output (f-string + arithmetic),
  write-a-line (input + int conversion), trace an if/elif chain, complete a while loop,
  a naming/comment judgment question, one small build-it (mini mad-libs or one-guess
  detective variant). Tone: "show what you've got", zero trick questions.
- Teacher notes + `## Grading`: what each question is FOR, common partial answers,
  the re-teach signal (≥1/3 of class missing loops → re-teach before unit 03's density).

### Phase D — unit-04-quiz-show content (2 lessons)

Blueprint per the map (introduces accumulator, logical-ops, conditional-nesting,
break-statement; practices boolean, type-conversion, loop-counter, error-messages):
- Hook: host your own quiz show — scores, streaks, sudden death.
- Lesson 1 (accumulator, logical-ops): a 3-question quiz in straight-line code from
  concepts kids already own (input, int conversion, if/elif); `score = score + 1` names
  the accumulator pattern, and a visible `questions_asked` counter pays off unit 02's
  "the machine learns to count" promise (loop-counter practice without needing a
  question-dispatch loop — that would demand lists). The streak bonus needs `and`
  (answer right AND streak alive) — logical operators arrive because the bonus rule
  demands them.
- Lesson 2 (conditional-nesting, break-statement): a final round where a question has a
  follow-up only if the first part is right (nesting), and SUDDEN DEATH — one wrong
  answer ends the round immediately (`break` arrives as the drama mechanic).
- Exercises ≥6 core + 2 stretch: score-the-answers snippets, fix-the-streak-logic,
  add-a-category-bonus (nesting), sudden-death remix, error-messages debugging,
  predict-the-score; stretch: double-or-nothing round, lightning round with a countdown
  (loop-counter countdown, no new concepts).
- Teacher notes: five headings, per-lesson allocation, 60-min cut points, differentiation;
  common mistakes (accumulator reset inside the loop, `and`/`or` swap, break outside loop).

### Phase E — Verification (NAMED, mandatory)

Mechanical: full pytest green (including the new checkpoint one-fault fixtures);
`bash scripts/ci-local.sh` ALL GREEN (checkpoint checks now live in steps 3–4 via the
extended registry); solutions execute with asserts; manifests map-equal; curriculum
invariants green with the amended map.
Reviewer duties (content gate): blind-solve every question and exercise; content-level
cumulative closure (checkpoint questions use only practices ∪ requires; unit-04 content
only taught-before concepts); solutions non-vacuous and complete; grading notes usable by
a real teacher; difficulty/timing (checkpoint ≤ half a lesson; unit lessons 60–90 min);
hook-first for unit 04; age-appropriateness.

**Acceptance criteria:** both directories complete; extended checks green with negative
coverage; ci-local ALL GREEN; content gate 4-way consensus.

---

## Plan Review

(4-way gate verdicts land here.)

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)

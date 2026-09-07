# Plan 006 — Unit 05 + Checkpoint 02 Implementation Plan

**Goal:** Ship `unit-05-function-factory` (functions — the Term 2 capstone concept) and `checkpoint-02-loops-and-functions`, closing the loops-and-functions teaching block so project 01 (Arcade Night) has all its prerequisites.

**Architecture:** Both follow the now-established pipelines unchanged — unit per plan 004, checkpoint per plan 005. Unit 05 is a turtle unit (introduces functions but `requires` turtle-basics/turtle-drawing), so it carries `assets/*.py` turtle scripts per D-005, exactly like unit 03. NO new tooling: plan 003/005 checks already cover both kinds. NO map amendment: both entries' concept sets are used as-is.

**Spec:** `book1/curriculum/coverage-map.yaml` (binding); plan 004 unit conventions; plan 005 checkpoint conventions; D-001, D-005.

## Global Constraints

- All plan-004 unit Global Constraints apply to unit 05; all plan-005 checkpoint conventions
  apply to checkpoint 02 (map-equal manifests; `## Question N` 6–8 sequential; broken
  snippets in markdown fences; no stretch/solutions in the checkpoint; six teacher-notes
  headings incl. `## Grading`; solution bans/seed/≥3 non-vacuous asserts; hook-first for
  the unit; per-lesson concept allocation; commit trailers).
- Turtle-in-checkpoint rule (binding, new — checkpoints can't run turtle, D-005): any
  checkpoint question touching `turtle-basics`/`turtle-drawing` is TRACE/PREDICT style —
  the student reads a turtle snippet shown in a markdown fence and answers about what it
  draws (shape, count, closure); no turtle code cell, no execution. Its solution reasons
  in prose/plain values, imports no turtle.
- Unit 05 turtle assets follow D-005 + the plan-003 turtle conventions (closure to a
  multiple of 360°, `# turtle-check: open-path` opt-out for deliberately open art);
  `assets/solutions_*.py` are `py_compile`-checked, not CI-executed.
- Process (standing): no commits while a `[sol]` review is in flight; codex content-gate
  prompts name the in-process fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Content plan → Phase D is the mandatory named verification phase. Out of scope: project 01
and units 06+ (later plans); PDF handouts for the checkpoint; any tooling change (the
checkpoint/unit checks already exist); any map edit.

## Phases

Dispatch per AGENTS.md: unit-05 lesson/exercises + checkpoint-02 questions + turtle asset
scripts via codex GPT-5.6-sol; solutions (unit + checkpoint) via a SEPARATE blind codex
session on finished statements only; teacher/grading notes inline; manifests inline.

### Phase A — manifests (inline, land with content)

`book1/units/unit-05-function-factory/manifest.yaml` and
`book1/checkpoints/checkpoint-02-loops-and-functions/manifest.yaml`, both map-equal.
Land each in the same commit as its complete directory (no manifest-only intermediate).

### Phase B — unit-05-function-factory content (3 lessons)

Blueprint (introduces def-function, parameters, return-value, scope; requires turtle +
for-loop + variable + f-string; practices range-function, loop-counter, arithmetic,
nested-loops, float-type):
- Hook: a greeting-card + turtle-stamp FACTORY — stamp the same shape or card many times
  without copy-pasting; functions are the machine that makes machines.
- Lesson 1 (def-function, parameters): `def greeting_card(name):` — the same card for any
  name; parameters are the blanks the factory fills. A turtle `stamp` function drawing a
  shape at the current spot, called in a `for` loop (practices for-loop/loop-counter).
  Turtle work runs as `assets/l1_cards.py` from the terminal (D-005).
- Lesson 2 (return-value): functions that hand something BACK — `area(w, h)` returns a
  number to use in a message; a `polygon_points(n)` helper returns the turn angle
  `360 / n` (practices float-type, arithmetic) used by the drawing script `assets/l2_shapes.py`.
- Lesson 3 (scope): local vs global — why a name inside a function doesn't leak out;
  a nested-loops turtle pattern factory (`assets/l3_stamps.py`, practices nested-loops)
  where each call is self-contained. A deliberate scope bug + traceback moment.
- Notebooks carry the reasoning, predict-the-output for functions, and turtle predictions
  (turtle cells tagged `no-exec` or shown as markdown; nothing imports turtle in notebooks);
  `exercises.ipynb` ≥6 core + ≥2 stretch (write-a-function, fix-the-parameter,
  return-vs-print, scope-trace, design-a-stamp; stretch: a function with two parameters
  making a name-badge, a recursive-free "flower" stamp calling a petal function in a loop).
- Solutions: function/return/scope answers execute headless; turtle answers as
  `assets/solutions_*.py`.
- Teacher notes: five headings, per-lesson allocation (L1 def+params, L2 return, L3 scope),
  60-min cut points, differentiation; common mistakes (print vs return, forgetting the
  parameter, expecting a local name outside, calling before defining).

### Phase C — checkpoint-02-loops-and-functions content

Blueprint (practices for-loop, range-function, while-loop, accumulator, logical-ops,
conditional-nesting, def-function, parameters, return-value, scope, turtle-basics,
turtle-drawing — units 03–05 material):
- 8 questions, ~35–45 min: trace a `for`/`range` loop's output; complete a `while`
  accumulator; write a small function with a parameter; return-vs-print judgment; a
  scope trace (what's visible where); a logical-ops/nesting condition; a TURTLE
  TRACE/PREDICT question (read `for i in range(5): forward(...); right(72)` in a markdown
  fence → "a pentagon", no execution); one build-it (a function that draws OR scores,
  student's choice, notebook-runnable version = the scoring one).
- Teacher notes + `## Grading`: per-question intent, partial reads, re-teach signal
  (functions are the hard idea — ≥1/3 missing the write-a-function or return question →
  revisit before project 01 leans on functions).

### Phase D — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN (unit-05 turtle-check on its assets;
checkpoint-02 through the checkpoint checks); solutions execute with non-vacuous asserts;
manifests map-equal; turtle assets close per convention.
Reviewer duties: blind-solve all questions/exercises; cumulative closure (unit 05 uses only
≤unit-05 concepts; checkpoint uses only its practices ∪ requires — the turtle question is
trace-only); solutions non-vacuous/complete; grading usable; timing; hook-first; the
turtle-in-checkpoint question is genuinely trace/predict with no execution dependency.

**Acceptance criteria:** both directories complete; ci-local ALL GREEN; content gate 4-way
consensus.

---

## Plan Review

(4-way gate verdicts land here.)

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)

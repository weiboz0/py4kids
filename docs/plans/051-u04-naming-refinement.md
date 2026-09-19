# Plan 051 — u04 naming refinement (CP-light) + numbered score prompts

**Status:** DRAFT — plan-review gate pending.
**Type:** Post-merge content refinement of `unit-04-quiz-show` (author-directed; not an errata bug).
**Branch:** `feature/plan-051-u04-naming`. **Base:** main @ 2120e56 (plan 050 merged).

## Motivation

Course-author directive after the plan-050 u04 pilot merged:
1. Per-iteration score prompts should name the round via an f-string (`f"Score for round {r}: "`),
   not a generic "Score for this round: ".
2. Variable names should be **less verbose, closer to competitive-programming style** — the author chose the
   **"Light trim"** level (keep short domain nouns; drop verbose suffixes; single-letter loop counters).

Scope decision (author): **all of u04** — lesson + exercises + solutions, statements included, so the unit
stays internally consistent. (NOT the whole Book-1 rollout — plans 052+ inherit the style by example, and
design 003 needs no amendment for this.)

## Hard constraints (self-containedness — unchanged)

u04's taught union is **`while`-only** with the explicit accumulator `total = total + score`. This plan
changes **names and prompt strings only**. It MUST NOT introduce `+=`, `for`/`range`, `sys.stdin`, list, or any
concept outside u04's union — those are not yet taught. Control flow, logic, outputs, asserts' *values*, and
the fixed-data/real-form pairing all stay identical; only identifiers and prompt text change.

## Naming scheme (Light trim)

| Old | New | Rule |
|---|---|---|
| `round_number` | `r` | loop counter → single letter from the noun |
| `question_number` | `q` | loop counter → single letter |
| `questions_asked` | `asked` | drop `_number`-style verbosity, keep the verb |
| count of items read (new real-forms) | `rounds` / `answers` / `scores` | descriptive plural for the count |
| `answer_correct` | `correct` | drop `_` suffix; per-item correctness boolean |
| `correct_count` (sole counter, Ex12) | `count` | short domain noun |
| `correct_count` / `wrong_count` (dual, Ex13) | `right` / `wrong` | domain pair; avoids clash with the `correct` boolean |
| `answer_1_correct` … (Ex1) | `a1` / `a2` / `a3` | fixed per-item booleans → short |
| `streak_alive` | `alive` | boolean; drop `_` (no clash with the `streak` **counter** in Ex16 — different cells) |
| `sudden_death_score` (L3) | `score` | short domain noun (no other `score` in that cell) |
| `first_correct` / `second_correct` (Ex6) | `first` / `second` | drop `_correct` |
| `third_answer_message_shown` (Ex4) | `shown` | drop verbosity |
| `total`, `count`, `score`, `streak`, `strikes`, `budget`, `attempts`, `category`, `eligible`, `penalty`, `accepted`, `on_streak`, `answer`, `bonus`, `risk_choice`, `tipping_*`, `fitting_*`, `fit_count`, `tip_count`, `tipping_round` | kept / lightly trimmed | already short domain nouns; trim only obvious `_count` → `_n` where it reads better, else keep |

Prompt f-strings (point 1): per-iteration prompts name the index —
`f"Score for round {r}: "`, and for parallel consistency `f"Answer {q} correct? (yes/no) "` where an
answer is read per iteration. One-shot prompts (single reads) keep their plain text.

## Phases

### Phase A — apply to u04 (lesson + exercises + solutions)
Rename per the scheme across all three notebooks and the exercise **statements** (which name variables), and
add the numbered f-string prompts. Keep every cell's control flow, logic, output text (except the numbered
prompt), and assert values identical. The executable fixed-data twin and its markdown/`no-exec` real-form must
stay name-for-name parallel (design 003 §6).

### Phase B — verification
- `ast.parse` + piped-run every real-form and executable twin; confirm each still produces the SAME result
  line as before (values unchanged, only names/prompts differ).
- Grep-assert: no `+=`, no `for `/`range(`, no `import sys`, no `.` string methods, no `list(`/`[]` collection
  literals introduced anywhere in u04.
- `scripts/ci-local.sh` ALL GREEN (exec-lessons runs the twins; exec-solutions runs the asserted cells;
  concept-scan/prereq/coverage must stay clean — names don't change the concept set).

## Out of scope
- Any Book-1 unit other than u04; design 003 (no amendment); the plans 052+ rollout.
- Verification phase present (Phase B) — this plan modifies unit content, so it is NOT verification-exempt.

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

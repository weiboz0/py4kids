# Plan 053 — checkpoint-01 real-input mini-pilot (non-unit markdown path)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the real-input treatment to `book1/checkpoints/checkpoint-01-first-steps`.
**Branch:** `feature/plan-053-checkpoint01-real-input`. **Base:** main @ 199ec1c.

## Motivation

Rollout slice 2 (design 003 §7): the **checkpoint mini-pilot**, chosen to exercise the untested **non-unit
markdown / cell-lint / solution-policy path** before the remaining units. checkpoint-01 is the simplest
checkpoint — list-less, early (`requires: print, input, variable, if-statement, while-loop`), clean names —
so it isolates the checkpoint-path mechanics from list-arm / rename / growth complexity. Authorities:
`docs/designs/003-book1-real-input.md` (§2 form-by-kind — checkpoint row; §3 v2; §6 validation); the u04/u07
pilots (plans 050/052) for the established real-form style.

## The treatment (adapted for a checkpoint)

1. **Real-input forms in `solutions.ipynb` (markdown fenced ```python blocks``` beside the fixed-data asserted
   solutions).** The student `checkpoint.ipynb` stays **solution-free** (Content Conventions) — real-forms live
   ONLY in the paired solutions, exactly as units do. This is the key non-unit-path check: markdown real-forms
   in a checkpoint's solutions must pass `cell-lint` + `_solution_policy_findings` (0 `input()` in solutions
   CODE cells; ≥3 non-vacuous assert cells; a fenced block must not contain a line starting `## Question <digit>`).
2. **No data growth.** checkpoint-01 is list-less; its data is single realistic scalars (`clues_found=4`,
   `stars=8`, `secret`), not toy `n=3`/2-element lists — design 003 §3 v2 satisfied, nothing to grow.
3. **No rename.** Names (`clues_found`, `clue_message`, `stars`, `bonus`, `total`, `secret`, `guess`,
   `clue_count`, `keep_guessing`, `clue`) are already clean/meaningful — CP-light yields no renames.
4. **No numbered prompts.** No question reads a *sequence* of values; the guess loops read a single running
   guess (`"Guess: "`/`"Guess again: "`) with no round index. Prompts stay as-is.
5. `input` is already in checkpoint-01's `requires` → **no metadata change**.

## Per-question SHAPE table

| Shape | Questions | Real-form (in solutions.ipynb) |
|---|---|---|
| **exempt** (predict / trace / conceptual — input would defeat it) | Q2 (predict the output), Q4 (trace the if/elif chain), Q6 (naming + comment concept) | NO real-form; a one-line note in the solution ("predict/trace/concept question — fixed data on purpose, no input version") |
| **single-read** (already reads `input()`; the question IS the real program) | Q3 (`clue_count = int(input("How many clues? "))`), Q5 (guess-until-match `while` loop), Q7 (one-guess if/elif/else) | markdown fenced real-form = the actual `input()`-reading program the fixed-data solution stands in for |
| **read-and-compute** (fixed value → real version reads it) | Q1 (fix TypeError; `clues_found` via `int(input(...))` then `str()`+concat) | markdown fenced real-form reading `clues_found` with `int(input("How many clues? "))` |

Q3/Q5/Q7 solutions currently use stand-ins (`int("6")`, `guess = 3`, `guess = 10`); the markdown real-form is
the input()-reading version (line-for-line the fixed-data cell with the stand-in replaced by `input()`).

## Closure

Real-forms use only checkpoint-01's union (print, input, int/str, variable, comparison, if/elif/else, while,
f-string, string-concat, arithmetic). No `sys.stdin`, no list, no `+=`, no new concept. No metadata change.

## Phases

### Phase A — apply to checkpoint-01 (solutions + light checkpoint/teacher-notes cues)
Add the markdown real-forms to `solutions.ipynb` per the SHAPE table (single-read Q3/Q5/Q7, read-and-compute
Q1) + one-line exempt notes for Q2/Q4/Q6. Add a one-line `**Real version:**` cue to the checkpoint QUESTION
statements that are fixed-data-with-a-real-analogue (Q1), where it aids without revealing the answer; Q3/Q5/Q7
already ask for `input()` (no cue needed). Sweep teacher-notes if any variable is renamed (none expected). No
data growth, no rename, no numbered prompts.

### Phase B — verification
- `ast.parse` + piped-run every markdown real-form; each reproduces its fixed-data twin's result line **modulo
  `input()` prompt text**.
- CLOSURE AST scan: no concept outside checkpoint-01's union; no `sys.stdin`.
- Non-unit-path checks: 0 `input()` in `solutions.ipynb` CODE cells; ≥3 non-vacuous assert cells; no fenced
  real-form contains a `## Question <digit>` line; `checkpoint.ipynb` stays solution-free (no real-form/answers).
- `scripts/ci-local.sh` ALL GREEN (esp. checkpoint cell-lint / solution-policy / structure checks).

## Out of scope
- Any Book-1 entry other than checkpoint-01 (rollout continues: remaining units + checkpoints + projects,
  design 003 §7 order). No design amendment. No data growth (list-less; §3 v2 satisfied). Phase B present.

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

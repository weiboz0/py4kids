# Plan 054 — u02 number-detective: full real-input treatment (list-less arm)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full treatment to `unit-02-number-detective`.
**Branch:** `feature/plan-054-u02-real-input`. **Base:** main @ 8cf48a1.

## Motivation

Rollout slice 3 (design 003 §7 — list-less units). u02 is the number-detective guessing game: it already reads
`input()` heavily (lesson has 9 no-exec input cells incl. the plan-049 sentinel ladder; several exercise cells
are already `no-exec` interactive). So the treatment is mostly **ensuring every exercise carries BOTH forms**
(executable fixed-data twin + `input()` real-form) with the established conventions. Reuses: the u04 list-less
template (plans 050/051), cp01's guess-loop / exempt-predict/debug patterns + §6(d) oracle (plan 053).
Authorities: `docs/designs/003-book1-real-input.md` (v3 — §2/§3 v2/§6d); u04 + cp01 merged pilots.

## The treatment (list-less, guessing-game)

1. **Real-input forms.** solutions.ipynb: markdown fenced ```python``` real-forms beside the fixed-data asserted
   twins. lesson.ipynb: put-it-togethers/Algorithm-Extension homes as `no-exec` input() cells (most already
   exist from plan 049 — verify each complete task has both forms; add where missing). `input` is already in
   u02's `requires` → **no metadata change**.
2. **No data growth.** List-less; data are single realistic scalars (`secret=37`, `low=12`/`high=47`) — not toy
   `n=3`/2-element lists (design 003 §3 v2 satisfied). `random.randint(...)` secrets stay; the fixed-data twin
   pins a concrete `secret` + a stand-in guess so it runs + asserts; the real-form reads guesses.
3. **CP-light naming.** u02 names (`secret`, `guess`, `low`, `high`, `is_correct`, `attempts`, `span`,
   `midpoint`) are already short domain nouns — expect near-zero renames (identifier-scoped only if any verbose
   name appears). Default: keep verbatim.
4. **No numbered prompts.** Guess loops are sentinel (`while guess != secret`) with no round index — prompts
   stay (`"Guess: "` / `"Guess again: "`), exactly as cp01 Q5.

## Per-exercise SHAPE table

| Shape | Exercises | Real-form |
|---|---|---|
| **exempt** | Ex1 (dice roller — a `random` generator, reads NO external input, like a countdown), Ex4 (broken code / read-the-traceback debug — `input()` would remove the graded `TypeError`) | NO real-form; one-line note in the SOLUTION ("generator/debug question — no `input()` version") |
| **single-read / interactive** (statement already reads `input()`) | Ex2 (one guess → higher/lower verdict), Ex3 (Player A types the secret, Player B guess-loop — multi-read), Ex5 (treasure depth guess-loop, sentinel), Ex8 (full 1–1000 game) | markdown real-form = the `input()`-reading program the fixed-data stand-in stands in for (fixed `secret` for the runnable twin; real-form reads secret/guesses) |
| **read-and-compute** (fixed values → real version reads them) | Ex6 (range-width report from `low`/`high`), Ex7 (one-guess truth check `is_correct = guess == secret`) | markdown real-form reads `low`/`high` (Ex6) / the guess (Ex7) via `int(input(...))`; Ex7's `is_correct` fragment follows the §6(d) pattern if it grades the comparison |
| **stretch (Challenge)** | Ch1 (hot/cold hints — arithmetic on a wrong guess), Ch2 (computer guesses via binary search — reads `1/2/3` replies) | Ch1: real-form reads the guess; Ch2: already interactive (reads replies) — real-form mirrors it |

(If a reviewer judges Ex6 or Ex7 to be primarily predict/trace, reclassify to exempt — flagged for the gate.)

## Closure
Real-forms use only u02's union (input, int/str, arithmetic, comparison, boolean, if/elif/else, while,
sentinel-loop, random-module, f-string, string-concat). No list, no `sys.stdin`, no `+=`, no concept outside
u02. No metadata change.

## Phases
### Phase A — apply to u02 (solutions + lesson verify + teacher-notes if renamed)
Add solutions markdown real-forms per the SHAPE table (single-read/interactive Ex2/Ex3/Ex5/Ex8 + Ch2;
read-and-compute Ex6/Ex7 + Ch1) + one-line exempt notes for Ex1/Ex4. Verify each lesson complete task has both
forms (plan-049 ladder already added the sentinel PIT — add a no-exec input() form only where a put-it-together
still lacks one). No growth, no rename (unless a verbose name surfaces), no numbered prompts. Fenced real-forms
must not contain a line starting `## Exercise <digit>`.

### Phase B — verification
- `ast.parse` + piped-run every real-form; result line == fixed-data twin modulo prompt text; §6(d) oracle for
  any condition/fragment case (Ex7); guess loops terminate on the matching guess.
- CLOSURE AST scan (no concept outside u02's union; no `sys.stdin`); random-module real-forms use a fixed seed
  or a pinned secret for the parity check.
- 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>` line.
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u02 (rollout continues per design 003 §7). No design amendment. No data growth
  (list-less; §3 v2). Phase B present.

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

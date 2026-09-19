# Plan 056 — u03 turtle-art-studio: full real-input treatment (compute-and-print arm)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full treatment to `unit-03-turtle-art-studio`.
**Branch:** `feature/plan-056-u03-real-input`. **Base:** main @ 580ddf2.

## Motivation

Rollout slice 6 (design 003 §7 — list-less units). u03 teaches turtle drawing via `for`/`range`/nested-loops.
**Key structural finding:** every `solutions.ipynb` cell is **compute-and-print with a fixed shape parameter**
(`n=7`, `side_count=4`, `shape_count=3`, `side_length`) — it computes loop counts / `angle = 360 / n` and
`print`s them; the actual turtle DRAWING lives in separate `assets/*.py` files (validated by structure-check,
**out of the notebook real-input scope**). So the treatment is a uniform **read-and-compute**: read the shape
parameter via `int(input())`, then the unchanged compute + print. Authorities: design 003 v3
(§2/§3 u01–u06 arm/§6); merged pilots u02/u04 (read-and-compute) + u01. Recurring audits baked in.

## Metadata add (a design-003 §5 REFINEMENT)

design 003 §5 lists u03 as needing a `practices:[input]` add. Reading a numeric shape parameter needs
`n = int(input(...))` → **`int-type` + `type-conversion`** too (both introduced in u02 — prereq-valid in u03,
but u03's manifest lists neither). So the add is **`practices: [input, int-type, type-conversion]`** (manifest +
coverage-map, in sync). `input` is category `io`; `int-type`/`type-conversion` are u02 concepts used here — no
`requires` change (prereq satisfied by u02), no technique/spiral trip. (Flag for the gate: design §5 should note
u03's add is the 3-concept set, not just `input`.)

## The treatment (read-and-compute, compute-and-print unit)

1. **Real-input forms — all three notebooks:** solutions.ipynb markdown real-forms beside the fixed-data
   asserted twins; lesson.ipynb complete-task capstones get a `no-exec` `input()` real-form + Notice (audit
   below); exercises.ipynb statements get `**Real version:**` cues (non-exempt) / `**No real version:**` notes.
2. **No data growth.** Shape params (`n=7`, `side_count=4`) are realistic, not toy (design 003 §3 u01–u06 arm).
3. **CP-light naming — near-zero.** `n`, `side_count`, `shape_count`, `side_length`, `angle`, `side_number`,
   `shape_number` are clean domain nouns. Keep verbatim.
4. **No numbered prompts.** Each real-form reads ONE shape parameter up front ("How many sides? "), then loops
   over `range(n)` — no per-iteration read, so no `{i+1}` indices.
5. **Closure:** real-forms add only `n = int(input(...))` (input + int-type + type-conversion — see metadata)
   to the existing `for`/`range`/arithmetic/`print`/f-string. **NO `if`/comparison/list/while/sys.stdin** (u03
   has none of these). Turtle asset `.py` files are NOT touched.

## Lesson both-forms audit (design §1/§8)

u03's lesson has 0 `input()` cells and 12 `no-exec` cells (turtle-DRAWING demos — turtle can't run headless).
| Lesson content | Status | Action |
|---|---|---|
| compute-and-print put-it-together capstone(s) (executable, fixed `n`) | executable only | **ADD a `no-exec` `input()` real-form** (read `n` → same computed/printed output) + Notice, so the complete compute task has both forms |
| turtle-DRAWING `no-exec` demos (12 cells) | draw, read nothing | **graphics demos — reads-nothing class** (like the dice roller / countdown): a drawing generates output, it doesn't read input; no input real-form. (Turtle-reads-`n` belongs to the asset files, out of scope.) |
| build-up rungs (single range/loop steps) | executable | rungs — exempt from both-forms parity |

(The exact capstone cell(s) to pair are identified in Phase A from the lesson's "put it together" markers.)

## Per-exercise SHAPE table

| Shape | Exercises | Real-form + statement treatment |
|---|---|---|
| **exempt** | Ex2 (range() prediction TABLE — predict counter values without running), Ex4 (nested-loop TRACE table) | predict/trace → NO real-form; `**No real version:**` statement note |
| **read-and-compute** (fixed shape param → read it) | Ex1, Ex3 (repair the loop count → read the count), Ex5, Ex6 (repair two counts → read them), Ex7, Ex8, Ex9, Ex10, Challenge 1, Challenge 2 | markdown real-form reads `n`/`side_count`/`shape_count` via `int(input(...))` then the unchanged compute+print; statements get a `**Real version:**` cue. (Ex3/Ex6 are "fix the wrong loop number" — after the fix the program computes+prints a count, so the real version reads it; NOT a traceback/SyntaxError debug.) |

(If a reviewer judges Ex3/Ex6 to be primarily fix-the-error debug, reclassify to exempt — flagged for the gate.
Turtle-drawing *asset* exercises: the notebook solution cell is compute-and-print, so it takes the
read-and-compute real-form; the `assets/*.py` drawing files are out of scope.)

## Phases
### Phase A — apply to u03 (manifest + lesson + exercises + solutions + coverage-map)
- **manifest.yaml + coverage-map.yaml:** add `practices: [input, int-type, type-conversion]` (in sync).
- **lesson.ipynb:** add a `no-exec` `input()` real-form (+ Notice) after the compute put-it-together
  capstone(s); turtle-drawing no-exec demos + build-up rungs untouched.
- **exercises.ipynb:** `**Real version:**` cues on the read-and-compute exercises + Challenges; `**No real
  version:**` notes on Ex2/Ex4.
- **solutions.ipynb:** markdown real-forms per the SHAPE table.
- No growth, no rename, no numbered prompts. Fenced real-forms must not contain a `## Exercise <digit>` line.

### Phase B — verification
- `ast.parse` + piped-run every real-form + the new lesson no-exec form; result line == fixed-data twin modulo
  `input()` prompt text (standard §6(a–c); a single up-front read, then the unchanged loop/print).
- CLOSURE AST scan: only `input`/`int`/`for`/`range`/arithmetic/`print`/f-string; NO `if`/compare/list/while/
  sys.stdin. `int(input())` is in-union via the metadata add.
- prereq-check / coverage-check / concept-scan / technique-spiral stay clean after the metadata add.
- 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>` line.
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u03 (rollout continues per design 003 §7). No design amendment (may flag §5's
  metadata-set note as a follow-up). Turtle `assets/*.py` drawing files (separate artifact). No data growth.
  Phase B present.

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

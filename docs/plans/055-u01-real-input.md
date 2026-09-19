# Plan 055 — u01 story-machine: full real-input treatment (text-only arm)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full treatment to `unit-01-story-machine`.
**Branch:** `feature/plan-055-u01-real-input`. **Base:** main @ 5bdfc80.

## Motivation

Rollout slice 4 (design 003 §7 — list-less units). u01 is the **text-only** unit (Mad-Libs story machine):
concepts = run-program, print, comment, string-literal, variable, naming, **input**, string-concat, f-string,
error-messages — **NO `int`, no `if`, no loop, no comparison**. Per design 003 §4, u01 real-forms are
**TEXT-ONLY: read/print strings, fixed-count named prompts, NO `int()`, no loop, no sentinel**. `input` is in
`introduces` → **no metadata change**. Authorities: design 003 v3 (§2/§3 u01–u06 arm/§4/§6); merged pilots
u02/u04 (list-less) + cp01. This plan bakes in the recurring gate audits (lesson both-forms twins, statement
cues, per-exercise SHAPE) up front.

## The treatment (text-only)

1. **Real-input forms — all three notebooks (unit convention):**
   - **solutions.ipynb:** markdown fenced real-forms beside fixed-data asserted twins.
   - **lesson.ipynb:** every complete task keeps an executable fixed-data twin AND a `no-exec` input() real-form
     (Lesson both-forms audit below).
   - **exercises.ipynb statements:** `**Real version:**` cue on non-exempt fixed-data exercises; one-line note
     on exempt ones.
2. **No data growth.** Text-only, no numbers/lists — nothing toy to fix; the input() real-form carries realism
   (design 003 §3, u01–u06 arm).
3. **CP-light naming — near-zero.** u01 names (`hero`, `name`, `color`, `word`, `story`, `hero_name`,
   `silly_object`, `favorite_snack`) are clean domain nouns. Keep verbatim.
4. **No numbered prompts.** Fixed-count NAMED text prompts ("Your name? ", "A noun: ", "An action: ") — not a
   sequence, so no `{i + 1}` indices.
5. **Text-only closure.** Real-forms read strings with `input(...)` and combine via `+`/f-string — **NO
   `int(input())`** (int/str are u02), no loop, no comparison, no `if`. Nothing outside u01's union.

## Lesson both-forms audit (design §1/§8)

| Lesson cell | Status | Action |
|---|---|---|
| cell 60 (full Mad-Libs Story Machine capstone) | `no-exec` input only | **ADD executable twin** before it (fixed stand-in words → the same printed story) + a Notice |
| L2 input demos (cells 39/41/43, "save a typed word") | `no-exec` input, but their **executable fixed-value analogs are cells 25–36** (same "save a word to a variable" task with fixed values) | paired — no new twin; verify each reads-and-uses one word |
| L1 (print basics, cells 2–23), L3 combine demos (46–57, fixed values) | executable, no interactive capstone | no unpaired task — unchanged |

## Per-exercise SHAPE table

| Shape | Exercises | Real-form + statement treatment |
|---|---|---|
| **exempt** (debug — fixing it doesn't add input) | Ex2 (fix the missing quote — SyntaxError; the fix is a `print` statement), Ex3 (fix the mixed-up name — NameError; the fix renames a variable) | NO real-form; one-line exempt note in the STATEMENT ("a fix-the-error question — no `input()` version") |
| **interactive** (statement already reads `input()`) | Ex5 (interview bot — asks name/snack/dream job), Ex6 (Story Machine remix — collects character/place/object/action with `input(...)`) | markdown real-form = the input()-reading program (fixed stand-in words in the runnable twin); no cue (already interactive) |
| **read-and-compute** (fixed values → real version reads them) | Ex1 (greeting-card printer — read the recipient's name), Ex4 (story remix — read hero/place/object), Ex7 (build a greeting with `+` — read `name`) | markdown real-form reads the word(s) with `input(...)` (text, NO `int()`) then the unchanged concat/print; statements get a `**Real version:**` cue |

## Phases
### Phase A — apply to u01 (lesson + exercises + solutions)
- **lesson.ipynb:** add an executable fixed-data twin (+ Notice) before cell 60 (full Mad-Libs — fixed words →
  the printed story). L2/L3 audited as paired.
- **exercises.ipynb:** `**Real version:**` cues on Ex1/Ex4/Ex7; exempt notes on Ex2/Ex3.
- **solutions.ipynb:** markdown real-forms per the SHAPE table (interactive Ex5/Ex6; read-and-compute
  Ex1/Ex4/Ex7). Ex2/Ex3 exempt (no real-form).
- No growth, no rename, no numbered prompts. Fenced real-forms must not contain a `## Exercise <digit>` line.

### Phase B — verification
- `ast.parse` + piped-run every real-form + the new lesson twin; result line == fixed-data twin modulo
  `input()` prompt text (all standard §6(a–c) — no random, no fragment).
- CLOSURE AST scan: **NO `int(`**, no `for`/`while`/`if`/comparison/list/`sys.stdin` in any real-form (text-only).
- 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>` line.
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u01 (rollout continues per design 003 §7). No design amendment. No data growth
  (text-only). Phase B present.

## Plan Review
_(pending — 4-way.)_

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

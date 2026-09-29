# Plan 094 — ACSL Contest 2: Prefix/Infix/Postfix, Bit-String Flicking, WDTPD – Looping, LISP

**Goal:** Ship the Contest 2 part of *Contest Python: ACSL*: one unit per Contest 2 category, then the Contest 2 practice checkpoint.
This is the study block for the second contest window (Jan 4 – Feb 28, 2027).

**Spec:** design 009 and the roadmap row for 094. User decision, 2026-09-29: "continue with plan 093 on autopilot and all other contest followed".
Conventions and lessons carried over from plan 093:
- canonical short-answer text; one-line WDTPD outputs
- the ACSL dialect: `int` = floor, inclusive substrings, inclusive `FOR`
- `.pop`, `.index`, `.count`, `.find` and `.join` banned in contest code
- per-entry `requires` boundaries
- registry changes before authoring; coverage map and syllabus after, reconciled
- teacher notes inline; separate solutions sessions; blind solves in the gate

## Survey (2026-09-29, main at b59796a)

- **`season.yaml` Contest 2 units:**
  - Prefix/Infix/Postfix Notation — elementary, junior, intermediate, senior
  - Bit-String Flicking — junior, intermediate, senior
  - WDTPD – Looping — junior
  - LISP — intermediate, senior
- **ACSL papers** (6 short-answer questions each):
  - Junior: Prefix/Infix/Postfix, Bit-String Flicking, What Does This Program Do? – Looping
  - Intermediate and Senior: Prefix/Infix/Postfix, Bit-String Flicking, LISP
  - Elementary: Elementary Prefix/Infix/Postfix Notation
- **Shared ids** with USACO (identical entries): `postfix-eval` (technique, techniques) and `bitwise-ops` (feature, number-theory). `code-tracing` and `acsl-pseudocode` already exist in `acsl`.
- **Tooling constraint:** checkpoints allow 6–8 question headings (`tools/notebooks.py`). Contest 2's two paths share only 4 questions, so a practice with both full papers plus the programming problem needs 9.

## The entries (all under `acsl/`)

Unit conventions:
- a project-first hook and 3 lessons
- **at least 14 exercises**, mixing programming items (judged line-exact) and short-answer items (`**Answer:**` line and a top-level `verify` assert)
- a heading ladder tag plus a visible division line on every exercise
- at least 2 `stretch` Challenges
- ACSL-style statements

Contest code never uses `.pop`; a stack is a list with a tracked top index or a slice.

### `unit-04-prefix-infix-postfix` — Prefix/Infix/Postfix Notation

- **Divisions:** elementary, junior, intermediate, senior. **Introduces:** `postfix-eval`.
- **Lesson 1 is the Elementary section**, with no code the student runs:
  - reading prefix and postfix
  - evaluating short prefix and postfix expressions with single-digit operands and `+ - * / ↑`
  - converting simple infix to prefix or postfix
  - ≥ 6 contiguous `acsl-elementary` short-answer items open the exercises
- **Junior and above:**
  - operator precedence and parentheses, and the fully parenthesised method for conversion
  - multi-digit operands separated by spaces
  - evaluating with a stack by hand
  - expression trees (reading them, and prefix/infix/postfix from a tree)
  - a Python postfix evaluator using a list stack (no `.pop`)
- **Intermediate+:** unary operators and longer expressions.
- ACSL's `↑` (power) uses small whole-number exponents.

### `unit-05-bit-string-flicking` — Bit-String Flicking

- **Divisions:** junior, intermediate, senior. **Introduces:** `bitwise-ops`.
- **Taught ACSL style:**
  - bit strings as text; `NOT`, `AND`, `OR`, `XOR` bit by bit
  - `LSHIFT-x`, `RSHIFT-x`, `LCIRC-x`, `RCIRC-x`
  - ACSL precedence: `NOT`, then shift/circulate, then `AND`, then `XOR`, then `OR`, with parentheses first
- **Solving for an unknown bit string**, where the answer is all solutions or the count of solutions as the question asks:
  - Junior: one operation
  - Intermediate+: two or more operations, and ACSL `*` wildcard answers
- **Python:** bit-string operations on strings of `0`/`1`, written by hand with loops; the `&`, `|`, `^`, `<<`, `>>` operators on integers shown as the fast equivalent.

### `unit-06-wdtpd-looping` — What Does This Program Do? – Looping

- **Divisions:** junior. **Introduces:** no new concept; it practises `code-tracing` and `acsl-pseudocode`. If the tools require an introduction, the ACSL-only `loop-tracing` is added.
- Junior's Contest 2 category: tracing `FOR`, `WHILE`, nested loops, loops with counters and accumulators, and loops over strings. ACSL pseudocode and Python are side by side, and at least one third of items are in pseudocode.
- Mostly short-answer, plus a few predict-then-verify programs.
- *(Intermediate and Senior students met every construct in Contest 1; the teacher notes point them here for extra loop practice.)*

### `unit-07-lisp` — LISP

- **Divisions:** intermediate, senior. **Introduces:** the ACSL-only `lisp-eval` ("Evaluating ACSL LISP expressions", technique, techniques).
- **ACSL's LISP subset:**
  - atoms and lists; quote (`'`)
  - `SETQ`
  - `CAR`, `CDR` and their compositions (`CADR` …)
  - `CONS`, `REVERSE`
  - `ADD`, `SUB`, `MULT`, `DIV`, `SQUARE`, `EXP`
  - `EQ`, `ATOM`
  - `DEFUN` with simple bodies
  - evaluation order from the inside out
- **Short-answer items:** evaluate an expression and give its value (a list written as `(A B C)`).
- **Programming items:** Python list versions of `CAR`, `CDR`, `CONS` and `REVERSE` on lists read from input. No `.pop`; loops and slices only.
- The solutions session verifies LISP answers with a small evaluator in a trace asset. Verify code is exempt from `source-policy`.

### `checkpoint-02-contest-2-practice` — Practice (contest 2)

- **Divisions:** junior, intermediate, senior. **9 questions:**
  - Q1–Q2 Prefix/Infix/Postfix, `acsl-junior`
  - Q3–Q4 Bit-String Flicking, `acsl-junior`
  - Q5–Q6 WDTPD – Looping, `acsl-junior`, at least one in pseudocode
  - Q7–Q8 LISP, `acsl-intermediate`
  - Q9 the single `acsl-junior` programming problem, last, with the sample plus ≥ 4 hidden-style fixtures
- **Paths:**
  - Junior: Q1–Q6 + Q9
  - Intermediate and Senior: Q1–Q4, Q7–Q8 + Q9
  - Both are full six-question papers.
- Strict prerequisites.
- **Teacher notes:** Grading follows ACSL's format (6 short-answer questions in 30 minutes; the programming problem scored on its test data). Classroom takes Q1–Q8 as short-answer practice (the real Classroom test is 10 questions in 50 minutes). Elementary uses unit 04's Elementary items as its mock test.

## Phase A1 — Registry, before authoring (inline)

`acsl/curriculum/concepts.yaml`:
- `postfix-eval` and `bitwise-ops`, byte-identical to USACO's
- the ACSL-only `lisp-eval`

## Phase B — Lessons and statements (Opus subagents in parallel, one per entry, each owning only its folder)

## Phase C — Solutions (Opus subagents, separate fresh sessions, one per entry, solved from the statements)

## Phase A2 — Coverage and syllabus, after authoring (inline)

Coverage-map entries in season order (units 04, 05, 06, 07, then the checkpoint), reconciled against the manifests. Syllabus rows in the check's form.

## Phase D — Teacher notes (inline) and one tooling rule (Opus subagent)

- Five `teacher-notes.md` files, with the required headings and Grading for the checkpoint.
- **Tooling:** the checkpoint question-count rule allows **6–10** question headings for `acsl`-flag books (ACSL's Classroom test has 10) and keeps 6–8 elsewhere. Tests for 9 and 10 passing in `acsl` and 9 failing in `usaco-bronze`.

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN, in a solo run on the final commit.
2. The global concept check passes with the new shared ids.
3. Division paths are counted by script, and the counts are reported:
   - unit 04 has ≥ 6 contiguous `acsl-elementary` items
   - the checkpoint's Junior and Intermediate paths are each 6 short-answer questions plus 1 programming question
4. Blind solves: reviewers solve all 8 checkpoint short answers and at least 3 items per unit.
5. Post-execution report.

## Out of scope

- Contests 3–4 (095–096).
- The USACO trim (097).
- ACSL publication.

## Plan Review

### Round 1 — `[self]` APPROVE WITH NITS

- The verification phase is named. Plan 093's lessons are folded in up front: the dialect, answer text, banned methods and registry timing.
- Watch items:
  - LISP answers are hard to verify, so the trace-asset evaluator must implement exactly ACSL's subset.
  - Bit-string "solve for x" answers need a canonical form (ACSL `*` wildcards).
  - WDTPD – Looping is Junior-only; confirm the tools accept a unit with no new concept.
- `[glm]` skipped (user decision 2026-09-28).

## Content Review
_(filled before PR.)_

## Post-Execution Report
_(filled before merge.)_

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

## Shared rules for this plan

**Verification helpers.** Evaluators that check answers live in `acsl/units/<unit>/assets/verify/`:
- `lisp_eval.py` (unit 07)
- `pip_eval.py` (unit 04: a prefix/postfix evaluator and an infix→prefix/postfix converter)
- `bsf_eval.py` (unit 05: bit-string operators and a brute-force solve-for-x)

They are imported only by `verify` cells, which use one recipe: `sys.path.insert(0, "assets/verify")`, then `import lisp_eval` (cells run from the entry folder), with `assets/verify/__pycache__/` git-ignored.

`source-policy` and `concept-scan` already scan only `assets/*.py`, which leaves the subfolder alone. A1 makes `judge-check` ignore `assets/verify/`, compiles `assets/verify/*.py` in the asset-reference pass, and tests both.

Each evaluator must pass its **pre-written** test file before any answer is trusted. The A1 tooling session writes these, and the evaluator authors do not edit them:
- `tests/test_acsl_eval_lisp.py`
- `tests/test_acsl_eval_pip.py`
- `tests/test_acsl_eval_bsf.py`

A verify cell's expression string is byte-identical to the statement's.

**Stack and list idioms for student code** (`.pop`, `.index`, `.count`, `.find`, `.join` and slices of lists are not used):
- a **stack** is a list plus a tracked `top` count: push appends while `top == len(stack)`, else overwrites `stack[top]`; `top` goes up and down; the top item is read as `stack[top - 1]`
- a LISP `CDR` / `CONS` in Python builds a new list with a loop and `append`

These map to `list-literal`, `list-append`, `list-index` and `list-loop` from *Python by Projects*.

**Per-entry concept boundaries:**
- Units 04, 05 and 07 require only *Python by Projects* and Foundations ids.
- Unit 06 also practises `code-tracing` and `acsl-pseudocode` (unit 03) and **introduces nothing** (`introduces: []`, which the tools already accept).
- The checkpoint is strict over *Python by Projects* plus units 00–07. Its author writes from these specs; A2 re-checks every id against the units' final manifests.

**Canonical answer text** (plan 093's rules, plus the rules below):
- **Prefix/postfix expressions:** single-space-separated tokens (`+ 3 * 4 2`), `↑` for powers in statements and answers, operands never reordered, equal precedence left to right. Items never stack `↑` without parentheses.
- **Evaluation results:** an integer when whole, otherwise Python's decimal (`13.5`). Items are designed so every division is whole or terminating (halves, quarters, tenths), never a repeating decimal.
- **LISP values:**
  - numbers as above (`(DIV 6 (SUB 2 5))` is `-2`; `(DIV 54 4)` is `13.5`)
  - lists as `(A B C)` with single spaces, in the case the question uses
  - the empty list and false as `NIL`, true as `true`
  - items prefer a number or list as the final value
- **Bit strings:** the full width stated in the question. **Solve-for-x:** all solutions in ascending binary order, separated by `, `. A "how many" item takes a bare integer. The `*` wildcard form appears only when the item explicitly asks for it *and* the solution set is one pattern.

## The entries (all under `acsl/`)

Unit conventions:
- a project-first hook and 3 lessons
- **at least 14 exercises**, mixing programming items (judged line-exact) and short-answer items (`**Answer:**` line and a top-level `verify` assert)
- a heading ladder tag plus a visible division line on every exercise
- at least 2 `stretch` Challenges
- ACSL-style statements

### `unit-04-prefix-infix-postfix` — Prefix/Infix/Postfix Notation

- **Divisions:** elementary, junior, intermediate, senior. **Introduces:** `postfix-eval`.
- **Non-programming hook.**
- **Lesson 1 is the Elementary section**, with no code the student runs. It follows the official Elementary doc:
  - single-digit operands; division only by 1 or 2; powers only 1 or 2. Powers are shown as both `^` (the Elementary paper's glyph) and `↑`; the book answers with `↑`.
  - PEMDAS, with left to right for equal precedence
  - five skills: evaluate postfix, evaluate prefix, infix→prefix, infix→postfix, and **prefix↔postfix**
  - ≥ 6 contiguous `acsl-elementary` short-answer items open the exercises, before any other tag
- **Junior and above:**
  - multi-digit operands and variables (`A B C`)
  - nested parentheses; `↑` with precedence
  - the fully parenthesised conversion method; converting directly between prefix and postfix
  - evaluating with a stack by hand, then a Python postfix evaluator using the stack idiom
- **Intermediate and above:** longer expressions, and division producing non-integers.
- **No unary minus** (not on ACSL's page). Expression trees are a short optional aside, not assessed.

### `unit-05-bit-string-flicking` — Bit-String Flicking

- **Divisions:** junior, intermediate, senior. **Introduces:** `bitwise-ops`.
- **Rules from ACSL's page:**
  - `NOT` / `~`, `AND` / `&`, `OR` / `|`, `XOR` / `⊕`, with the word and symbol forms both used
  - `LSHIFT-x` and `RSHIFT-x` (bits shifted out are lost, zeros shifted in); `LCIRC-x` and `RCIRC-x` (bits wrap round); a circulate count may exceed the length, taken mod the length
  - precedence from highest to lowest: `NOT`; shift/circulate; `AND`; `XOR`; `OR`
  - **equal precedence evaluates left to right; unary operators bind right to left** (`NOT RSHIFT-1 x` = `NOT (RSHIFT-1 x)`)
  - operands of unequal length are **padded with 0s on the left**
- **Solve for an unknown x:** Junior has one operation; Intermediate and above chain two or more. Answers use the canonical list or count form above.
- **Python:**
  - bit strings as text, processed with hand-written loops (no `bin` or `format`)
  - integer operators shown as the fast equivalent, including the width mask: `~x` becomes `x ^ mask`, and `<<` is followed by `& mask`

### `unit-06-wdtpd-looping` — What Does This Program Do? – Looping

- **Divisions:** junior. **Introduces:** none; it practises `code-tracing` and `acsl-pseudocode`.
- **Construct list:**
  - `FOR … TO … STEP` (inclusive, including **negative STEP**)
  - `WHILE`, tested at the top
  - nested loops with dependent bounds
  - counters, accumulators, and a running maximum
  - `%`, `int` (floor) and `abs` inside loops
  - integer-only arithmetic
- **No string traversal and no arrays:** Junior strings are Contest 4, Junior arrays Contest 3.
- At least one third of items are in pseudocode; every short-answer item has one-line output.
- *(Intermediate and Senior met every construct in Contest 1; the teacher notes suggest this unit as loop drill only.)*

### `unit-07-lisp` — LISP

- **Divisions:** intermediate, senior. **Introduces:** the ACSL-only `lisp-eval` ("Evaluating ACSL LISP expressions", technique, techniques).
- **ACSL's function set, taught and assessed** (per the wiki):
  - atoms and lists; `NIL` = `()`; quote `'`
  - `SET` (first argument quoted), `SETQ`, `EVAL`
  - `CAR`, `CDR` (`CDR` of a one-element list is `NIL`) and the compositions `CAAR`, `CADR`, `CDAR`, `CDDR`, `CADDR`, `CDDAR` (no others are assessed)
  - `CONS` (second argument always a list), `REVERSE`
  - variadic `ADD` and `MULT`; `SUB`, `DIV`, `SQUARE`, `EXP`; symbol forms `+ - * /`
  - `EQ`, `POS`, `NEG`, `ATOM`
  - `DEF` / `DEFUN`
- **Explicitly out:** `COND`, `IF`, `NULL`, `LIST`, `LENGTH`, `MEMBER`, `APPEND`, `NTH`, `MAPCAR`, lambda.
- **Short-answer items:** evaluate and give the value. **Programming items:** Python list versions of `CAR`, `CDR`, `CONS` and `REVERSE` on lists read from input, using the list idiom.

### `checkpoint-02-contest-2-practice` — Practice (contest 2)

- **Divisions:** junior, intermediate, senior. **9 questions:**
  - Q1–Q2 Prefix/Infix/Postfix, `acsl-junior` (Q2 the harder)
  - Q3–Q4 Bit-String Flicking, `acsl-junior` (Q4 the harder, solve-for-x)
  - Q5–Q6 WDTPD – Looping, `acsl-junior`, at least one in pseudocode
  - Q7–Q8 LISP, `acsl-intermediate` (one `DEFUN`/`SETQ` item, one `CAR`/`CDR` composition)
  - Q9 the single `acsl-junior` programming problem, last, with the sample plus ≥ 4 hidden-style fixtures
- **Paths:**
  - Junior: Q1–Q6 + Q9
  - Intermediate and Senior: Q1–Q4, Q7–Q8 + Q9
  - Classroom (its Contest 2 categories are Prefix/Infix/Postfix, Bit-String Flicking and LISP): Q1–Q4 + Q7–Q8, with Q5–Q6 optional extra
  - Elementary: unit 04's Elementary items, as 6 questions in 30 minutes
- **Teacher notes:** Grading uses ACSL's format (6 short answers in 30 minutes; the programming problem scored on its test data).

## Phase A1 — Registry and tooling, before authoring

- **Inline:** `acsl/curriculum/concepts.yaml` gains `postfix-eval` and `bitwise-ops` (byte-identical to USACO's) and the ACSL-only `lisp-eval`.
- **Opus tooling subagent:**
  - The checkpoint question-count rule allows **6–10** for `acsl`-flag books and keeps 6–8 elsewhere; the sequential-numbering check runs for every allowed count, Q1–Q10 included.
  - The `assets/verify/` carve-out in `judge-check` (the one tool that needs it), plus regression checks that `source-policy` and `concept-scan` still scan `assets/*.py` and leave the subfolder alone.
  - Tests: 9 and 10 pass for `acsl`; 9 fails for `usaco-bronze`; numbering gaps fail at 9 and 10. `judge-check` ignores `assets/verify/`, while `source-policy` and `concept-scan` still scan `assets/*.py` beside it.
  - **Pre-written evaluator tests** (expected values from the ACSL wiki, one test file per evaluator):
    - `tests/test_acsl_eval_lisp.py`: the wiki samples (`-440`, `((4 (5 6) 7))`, `CA`, `24.5`, `(red white blue)`, `SECOND`, and the wiki's `EVAL` and `ATOM` examples) plus **at least one case for every supported operation**: `SET`, `SETQ`, `EVAL`, `CAR`, `CDR`, `CONS`, `REVERSE`, `ADD`, `SUB`, `MULT`, `DIV`, `SQUARE`, `EXP`, `+ - * /`, `EQ`, `POS`, `NEG`, `ATOM`, **`DEF` and `DEFUN` as separate cases**, quote and `NIL`
      - **one case for each supported composition**: `CAAR`, `CADR`, `CDAR`, `CDDR`, `CADDR` and `CDDAR` (the wiki's example)
    - `tests/test_acsl_eval_pip.py`: the wiki's conversions and evaluations
    - `tests/test_acsl_eval_bsf.py`: the wiki's operator examples and the solve-for-x example (`00000, 00001, 00100, 00101`)
    - Each file imports its evaluator from the unit's `assets/verify/` and skips until that module exists.

## Phase B — Lessons and statements (Opus subagents in parallel, one per entry, each owning only its folder)

## Phase C — Solutions (Opus subagents, separate fresh sessions, one per entry)

- Solved from the statements only.
- The unit 04, 05 and 07 solutions sessions each write their `assets/verify/*_eval.py`, which must pass the pre-written test file for it. They do not edit that file.

## Phase A2 — Coverage and syllabus, after authoring (inline)

Coverage-map entries in season order (units 04, 05, 06, 07, then the checkpoint), reconciled against the manifests. Syllabus rows in the check's form.

## Phase D — Teacher notes (inline)

Five `teacher-notes.md` files, with the required headings and Grading for the checkpoint. They cover division paths (including unit 06 as loop drill for Intermediate/Senior, and the Elementary mock test at 6 in 30), the canonical answer forms, and the ACSL rules students most often get wrong.

## Phase E — VERIFICATION

1. `scripts/ci-local.sh` ALL GREEN, in a solo run on the final commit.
2. The global concept check passes with the new shared ids. The three pre-written evaluator test files pass, with no skips, on the ACSL wiki samples:
   - **LISP:** `-440`, `((4 (5 6) 7))`, `CA`, `24.5`, `(red white blue)`, `SECOND`
   - **Bit-String Flicking:** the wiki's operator and solve-for-x examples
   - **Prefix/Infix/Postfix:** the wiki's conversions and evaluations
3. A script reports the actual question ids and tags for each checkpoint path:
   - Junior: Q1–Q6 + Q9
   - Intermediate/Senior: Q1–Q4, Q7–Q8 + Q9
   - Classroom: Q1–Q4, Q7–Q8

   It also checks that unit 04 has ≥ 6 contiguous `acsl-elementary` items before any other tag.
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

### Round 1 — verdicts

- `[sol]` **REJECT:**
  - the LISP evaluator placement conflicts with `source-policy`
  - the LISP subset and answer formats are imprecise
  - bit-string semantics and solve-for-x forms are underspecified
  - Junior string tracing belongs to Contest 4
  - the no-new-concept unit and the boundaries are not locked
  - Phase E must verify both paths and Q1–Q10 numbering
- `[fable]` **APPROVE WITH NITS** (conditional), checked against the ACSL wiki pages and the Elementary PIP doc:
  - Must fix: the full LISP set (`SET`, `EVAL`, `POS`, `NEG`, `DEF`, symbol forms, variadic `ADD`/`MULT`); canonical LISP text (`DIV` whole results, `true`/`NIL`); evaluator placement with wiki-sample tests; canonical PIP and BSF answer forms; the Classroom path
  - Should fix: drop unary minus; Elementary per the official doc (limits, prefix↔postfix, a non-programming hook); BSF rules (left to right, right-to-left unary, left padding, mod circulates, symbol forms, Python masks); per-entry boundaries; a concrete stack idiom; an explicit Looping construct list with `introduces: []`; the 6–10 rule moved to A1; verification per unit
  - Nice: expression trees as an aside; harder Q2/Q4; LISP Q7–Q8 variety; Phase E wording; teacher-notes paths
- `[glm]` skipped (user decision 2026-09-28).

### Round 1 — fold

- `[FIXED]` all of the above:
  - A "Shared rules" section: the `assets/verify/` helpers with a tested carve-out and wiki-sample evaluator tests; the stack and list idioms and their ids; per-entry boundaries; canonical answer text for prefix/postfix, evaluation results, LISP and bit strings.
  - The entries rewritten from the ACSL pages: the Elementary PIP limits and five skills with a non-programming hook; no unary minus; the full BSF rules; the Looping construct list (no strings or arrays; `introduces: []`); the full LISP function set with an explicit out-list.
  - Checkpoint paths including Classroom.
  - A1 carries the 6–10 rule (numbering checked for all counts) and the carve-out.
  - Phase E: evaluator tests on the wiki samples and a scripted path report.

### Round 2 — verdicts and fold

- `[sol]` **REJECT** (r2): four of the six blockers are resolved. Remaining:
  - the LISP tests don't cover `EVAL`, `EQ`, `POS`, `NEG` and `ATOM`
  - three sessions share one test file with no owner
  - `[FIXED]` The A1 tooling session pre-writes three separate test files, one per evaluator, with the wiki samples plus ≥ 1 case per supported LISP operation. The evaluator authors must pass them and never edit them.
- `[fable]` **APPROVE WITH NITS** (r2), all round-1 items verified.
  - `[FIXED]` Carve-out scope: `judge-check` is the one tool that needs the exclusion.
  - `[FIXED]` The verify-cell import recipe, with `__pycache__` ignored.
  - `[FIXED]` Only terminating divisions in items.
  - `[FIXED]` Elementary shows both `^` and `↑`.
  - `[FIXED]` Tests are seeded by A1 rather than by the evaluator authors.

### Round 3

- `[sol]` **REJECT** (r3): test-file ownership is resolved. Remaining: LISP coverage is ambiguous for `DEF` vs `DEFUN` and for compositions.
  - `[FIXED]` `DEF` and `DEFUN` are separate test cases. The assessed compositions are bounded to `CAAR`, `CADR`, `CDAR`, `CDDR`, `CADDR` and `CDDAR`, each with a test.
  - `[FIXED]` Nit: A1 names `judge-check` as the one carve-out, with regression checks for the other two tools.

### Round 4 — CONSENSUS

- `[sol]` **APPROVE** (r4), no findings.
- `[fable]` APPROVE WITH NITS (r2, folded).
- `[self]` APPROVE.
- `[glm]` skipped (user decision 2026-09-28).

**Consensus reached; implementation starts.**

## Content Review

### Round 1

- `[sol]` **REJECT.**
  - Blind solve: all 28 sampled items and the checkpoint match. 147 evaluator tests, 146 fixture runs and 29 independent probes pass.
  - `[FIXED]` O1: unit 04's Lesson 1 (Elementary) offered a runnable self-checker. Lesson 1 now has no code cell and only mentions the optional program. The `l1.py` mirror cell and its run instructions moved to the start of Lesson 2, and the back-reference was updated.
  - `[FIXED]` O2: the checkpoint's student page lacked the Classroom path. It now has "Classroom (no programming): Q1–Q4 and Q7–Q8; Q5–Q6 optional".
- `[fable]` **APPROVE WITH NITS.**
  - Blind solve: all 29 requested items plus about 35 more match. Q9 and unit 05 Ex 19 were solved independently; wrong variants were caught, except for the shift-clamp gap below. Fidelity to the ACSL wiki and the Elementary doc was verified; 261 evaluator and tooling tests pass.
  - `[FIXED]` F1: unit 05 Ex 14 and Ex 19 had no fixture for a shift longer than the string. New fixtures (`LSHIFT-9 NOT 0110` → `0000`; `RSHIFT-7 x` = `000` → all 8 strings) were cross-checked with `bsf_eval`, and a clamp-less solver fails them.
  - `[WONTFIX]` F2: lengthening Elementary items to the official 9–13 tokens. The current items already cover every Elementary skill within the doc's limits; this is noted for a future enrichment pass.
  - `[FIXED]` F3: Q3 no longer restates the precedence ladder.
  - `[FIXED]` F4: Q6 notes that ACSL papers also write keywords in lowercase.
  - `[FIXED]` F5: the post-execution report is written before the PR.
- `[self]` APPROVE: every short answer was solved blind by the solutions sessions and matched the authors' keys:
  - checkpoint 8/8
  - U04 19/19
  - U05 17/17
  - U06 16/16
  - U07 17/17
- `[glm]` skipped (user decision 2026-09-28).

### Round 2

- `[sol]` **REJECT** (r2): O1 is resolved and the other folds are verified. Remaining: the intro told every path, Classroom included, to spend 60 minutes on Q9.
  - `[FIXED]` The Q9 timing line is conditional: "On the Junior, Intermediate or Senior path … (the Classroom path skips it)".

### Round 3 — CONSENSUS

- `[sol]` **APPROVE** (r3): no `[OPEN]` findings. Q9's timing and programming instructions now apply only to the Junior, Intermediate and Senior paths; the Q3 and Q6 folds hold; the new unit 05 Ex 14 and Ex 19 fixtures match direct `bsf_eval` results.
- `[fable]` APPROVE WITH NITS (r1; every nit folded or WONTFIX with reason).
- `[self]` APPROVE.
- `[glm]` skipped (user decision 2026-09-28).

## Post-Execution Report

**Shipped: ACSL Contest 2** (study window Jan 4 – Feb 28, 2027).

| Entry | Items | Divisions (by heading tag) |
|---|---|---|
| `unit-04-prefix-infix-postfix` | 23 (19 short-answer, 4 programming) | 9 elementary (contiguous mock test, first), 8 junior, 4 intermediate, 2 senior |
| `unit-05-bit-string-flicking` | 21 (17 short-answer, 4 programming) | 14 junior, 5 intermediate, 2 senior |
| `unit-06-wdtpd-looping` | 19 (16 short-answer, 3 programming) | 19 junior |
| `unit-07-lisp` | 21 (17 short-answer, 4 programming) | 16 intermediate, 5 senior |
| `checkpoint-02-contest-2-practice` | 9 (Q1–Q6 junior, Q7–Q8 intermediate short-answer; Q9 junior programming, last) | see paths |

- **Checkpoint paths** (from the question tags):
  - Junior: Q1–Q6 + Q9
  - Intermediate/Senior: Q1–Q4, Q7–Q8 + Q9
  - Classroom: Q1–Q4, Q7–Q8 (Q5–Q6 optional; no programming)
  - Elementary: unit 04 Exercises 1–9, as 6 questions in 30 minutes
- **Unit 04** opens with a code-free Elementary lesson (the five official skills); its optional self-checker starts Lesson 2. It introduces the shared `postfix-eval`, with the stack-plus-`top` idiom.
- **Unit 05** follows ACSL's precedence and right-to-left unary rule, pads on the left, clamps long shifts, and covers solve-for-x in the canonical list form. It introduces the shared `bitwise-ops`.
- **Unit 06** is Junior loop drill in ACSL pseudocode and Python (`introduces: []`).
- **Unit 07** covers ACSL's LISP function set and the six assessed `CxR` compositions. It introduces the ACSL-only `lisp-eval`.
- **Verify helpers:** `pip_eval.py`, `bsf_eval.py` and `lisp_eval.py` in each unit's `assets/verify/`, each passing its pre-written test file (ACSL wiki samples plus one case per supported operation).
- **Tooling:**
  - ACSL checkpoints allow 6–10 questions (other books keep 6–8), with sequential numbering checked at every count.
  - `judge-check` ignores `assets/verify/`; `source-policy` and `concept-scan` still scan `assets/*.py`.
- **Registry:** `postfix-eval` and `bitwise-ops` are identical to USACO's; `lisp-eval` is ACSL-only. The coverage map and syllabus rows are reconciled against the manifests.
- **Teacher notes** (inline) for all five entries: division paths, ACSL timing, canonical answer forms, and Grading.

**Verification.**
- `scripts/ci-local.sh` ALL GREEN, solo run at 472b596 (pytest 1071 passed, 2 environment skips).
- Blind solves: the solutions sessions matched every author key (checkpoint 8/8, U04 19/19, U05 17/17, U06 16/16, U07 17/17). [sol] and [fable] independently matched their samples. [sol] ran 147 evaluator tests, 146 fixture runs and 29 probes; [fable] ran 261 evaluator and tooling tests.

**Deviations:**
- Content round 1: the runnable self-checker moved out of the Elementary lesson; the checkpoint gained its Classroom path; shift-clamp fixtures were added.
- Content round 2: Q9's timing applies only to the programming paths.
- `[WONTFIX]` F2: Elementary items stay shorter than the official 9–13 tokens, noted for a future enrichment pass.

**Next:** plan 095, Contest 3 (Boolean Algebra with its Elementary section, Data Structures, WDTPD – Arrays, FSAs and Regular Expressions for Intermediate+, and the Contest 3 practice).

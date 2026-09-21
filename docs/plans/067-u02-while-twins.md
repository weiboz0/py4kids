# Plan 067 — Unit 02 `while`-loop twins: replace the one-pass `guess = secret` script with genuine multi-pass loops

**Origin:** author feedback (2026-09-21) on the u02 Algorithm-Extension twin
(`secret = 7 / guess = 1 / while guess != secret: guess = secret`):
"this algo is too edge case, not enough to showcase the while loop usage."
**Design:** `docs/designs/003-book1-real-input.md` (v6) — the executable fixed-data twins added by plan 054.

## Motivation

Plan 054 gave every u02 interactive capstone an executable twin.
Because a CI cell cannot read `input()`, each twin scripts the "next guess" as `guess = secret`,
so every `while` loop in the unit's executable cells runs **exactly one pass** (or, in cell 88/90, one pass with no body output at all).
A student running the cell never sees a loop *repeat*, which is the whole point of `while`.

The obvious repair — `guess = guess + 1` — is NOT available:
`tools/concept_scan.py` `visit_Assign` flags read-modify-write as `accumulator`,
which u02 does not teach (closure violation).
Lists and `range` are also untaught.
So the multi-pass script must use only u02 concepts.

## The two idioms (both inside u02's union)

1. **Computer-guesser** (`random-module`, introduced in u02 before `while-loop`):
   `guess = random.randint(1, 10)` inside the loop.
   The loop runs an UNKNOWN number of trips until the sentinel — the real reason `while` exists —
   and it is line-for-line the real `input()` game with the read replaced by a random guess.
   Terminates with probability 1 (expected ~10 trips on 1–10); no `accumulator`.
2. **Scripted player** (`if-statement`/`elif-else`/`comparison`):
   an `if/elif/else` chain maps the current guess to the next scripted guess
   (`if guess == 50: guess = 25 / elif guess == 25: guess = 40 / else: guess = 37`).
   Assigning a constant is not read-modify-write, so no `accumulator`.
   The final `else` always assigns the secret, so the loop cannot run forever.

## Changes (5 code cells + 3 Notices; ids unchanged)

| Where | Cell | Now | After |
|---|---|---|---|
| lesson L4 game twin | `u02-l4-fixed-twin` (73) | 50 → `guess = secret` (1 pass, 1 hint) | scripted player 50 → 25 → 40 → 37: prints `Too high!`, `Too low!`, `Too high!`, then `Correct! Case closed.` (3 passes, both hints) |
| lesson L4 Notice | `u02-l4-fixed-notice` (74) | "the fixed follow-up guess…" | names the scripted guesses and that the loop repeats once per wrong guess |
| lesson AE rung | `dfe1ea40e81f` (88) | `guess = secret`, prints guess (1 pass) | computer-guesser, `secret = 7`, prints every guess so the trips are visible, then `Got it!` |
| lesson AE Notice | `a7ea18f50f76` (89) | "here one pass sets `guess` to the secret…" | the loop repeats an unknown number of times; run it again and the count changes; the match is the sentinel |
| lesson AE twin | `u02-ae-fixed-twin` (90) | `guess = secret` (1 silent pass) | line-for-line the real game (cell 92): `secret = random.randint(1, 10)`, `guess = 0`, loop body `guess = random.randint(1, 10)`, `print("Got it!")` |
| lesson AE Notice | `u02-ae-fixed-notice` (91) | "the scripted follow-up reaches the sentinel…" | the computer's random guesses stand in for the typing player; same result line as the real game below |
| solutions Ex8 | `u2-ex8-code` | 500 → `guess = secret` | scripted player 500 → 250 → 240 → secret (seed 4 → 242): `Too high!`, `Too high!`, `Too low!`, correct; final `else: guess = secret` keeps it seed-proof; assert unchanged |
| solutions Ch1 (stretch) | `u2-ch1-code` | 50 → `guess = secret` | scripted player 50 → 35 → secret (seed 4 → 31): `cold…`, `HOT!`, `Got it!` (both hints); assert unchanged |

Unchanged: all `no-exec` real `input()` forms, all markdown real-program blocks, exercises.ipynb statements,
manifest/coverage-map (no concept added — `random-module`, `elif-else`, `comparison` are already introduced by u02),
teacher-notes (audit: no claim about one-pass twins).
Solutions Ch2 already runs a genuine multi-pass scripted loop — untouched.

## Design-003 fit

§6(b) result-line parity is preserved: every twin still ends on the same result line as its real form
(`Correct! Case closed.` / `Got it!` / the Ex8 and Ch1 final lines).
Twins still run unattended with no `input()`.
Lesson cells stay unseeded (the lesson never teaches `random.seed`; lesson cells carry no asserts);
solutions keep their existing `random.seed(4)` + asserts.

## Phases

### Phase A — edit the 5 code cells + 3 Notices (lesson.ipynb, solutions.ipynb only)

### Phase B — verification
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN
  (concept-scan proves no `accumulator`/list/`range` crept in; exec-lessons/exec-solutions prove termination).
- Run each changed cell standalone: cell 73 prints exactly the 4 expected lines; cells 88/90 terminate and end with `Got it!`
  (repeat 200× to exercise the random path); Ex8/Ch1 print the expected hint sequence and pass their asserts.
- Scope allowlist: `git diff --name-only $(git merge-base HEAD main)..HEAD` =
  this plan + u02 `lesson.ipynb` + u02 `solutions.ipynb`.

## Out of scope

- No new concept, no exercise-statement change, no metadata change, no other unit
  (other units' twins use taught loops/lists and already iterate).
- Not an erratum (nothing was wrong or broken — a pedagogy improvement), so no `ERRATA.md` entry.
- **Verification phase:** Phase B is the named verification phase.

## Plan Review
_(pending)_

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_

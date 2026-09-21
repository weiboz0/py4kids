# Plan 067 — Unit 02 `while`-loop twins: replace the one-pass `guess = secret` script with genuine multi-pass loops

**Origin:** author feedback (2026-09-21) on the u02 Algorithm-Extension twin
(`secret = 7 / guess = 1 / while guess != secret: guess = secret`):
"this algo is too edge case, not enough to showcase the while loop usage."
**Design:** `docs/designs/003-book1-real-input.md` (v6) — the executable fixed-data twins added by plan 054.

## Motivation

Plan 054 gave every u02 interactive capstone an executable twin.
Because a CI cell cannot read `input()`, each twin scripts the "next guess" as `guess = secret`,
so every guessing-game `while` loop in the unit's executable cells runs **exactly one pass** (or, in cell 88/90, one pass with no body output at all) —
7 cells in all: 3 in the lesson, 4 in the solutions (Exercise 3 two-player, Exercise 5 treasure, Exercise 8, Challenge 1).
Only solutions Challenge 2 already iterates.
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
   **It MUST be one `if/elif/else` chain, never separate `if`s** — with separate `if`s, 50 → 25 would immediately match
   `if guess == 25` in the same pass and skip a guess ([fable] check 1).
   (Solutions Ch2 uses separate `if`s safely only because it sets `reply`, not the tested variable — not a template.)
   Where the body already holds a hint `if/else`, a separating comment
   (`# scripted player: the next guess (stands in for typing)`) keeps the two decisions visibly apart.

## Changes (7 code cells + 3 Notices + teacher-notes; ids unchanged)

| Where | Cell | Now | After |
|---|---|---|---|
| lesson L4 game twin | `u02-l4-fixed-twin` (73) | 50 → `guess = secret` (1 pass, 1 hint) | scripted player 50 → 25 → 40 → 37: prints `Too high!`, `Too low!`, `Too high!`, then `Correct! Case closed.` (3 passes, both hints) |
| lesson L4 Notice | `u02-l4-fixed-notice` (74) | "the fixed follow-up guess…" | names the scripted guesses and that the loop repeats once per wrong guess |
| lesson AE rung | `dfe1ea40e81f` (88) | `guess = secret`, prints guess (1 pass) | computer-guesser: starts with `import random` (the cell has none today; a student may run it cold), `secret = 7`, `guess = 0` (a value that can never be the secret, so the loop always runs — consistent with cells 90/92), prints every guess so the TRIPS ARE VISIBLE, then `Got it!` |
| lesson AE Notice | `a7ea18f50f76` (89) | "here one pass sets `guess` to the secret…" | the loop repeats an unknown number of times; run it again and the count changes; the match is the sentinel |
| lesson AE twin | `u02-ae-fixed-twin` (90) | `guess = secret` (1 silent pass) | line-for-line the real game (cell 92): `secret = random.randint(1, 10)`, `guess = 0`, loop body `guess = random.randint(1, 10)`, `print("Got it!")` |
| lesson AE Notice | `u02-ae-fixed-notice` (91) | "the scripted follow-up reaches the sentinel…" | the computer's random guesses stand in for the typing player; same result line as the real game below |
| solutions Ex3 (two-player) | `u2-ex4-code` (idx 8) | 50 → `player_b_guess = player_a_secret` | scripted Player B 50 → 75 → 63 (secret 63): `Too low, Player B!`, `Too high, Player B!`, correct; assert unchanged ([fable] B1) |
| solutions Ex5 (treasure) | `u2-ex6-code` (idx 14) | 25 → `guessed_depth = secret_depth` | scripted 25 → 10 → secret (seed 4 → 16): `Too deep!`, `Too shallow!`, found; final `else` assigns `secret_depth`; assert unchanged ([fable] B1) |
| solutions Ex8 | the SECOND cell with id `u2-ex8-code` — idx 24, "Number Detective 1–1,000" (the id is duplicated at idx 20; pre-existing, NOT fixed here — follow-up) | 500 → `guess = secret` | scripted player 500 → 250 → 240 → secret (seed 4 → 242): `Too high!`, `Too high!`, `Too low!`, correct; final `else: guess = secret` keeps it seed-proof; assert unchanged |
| solutions Ch1 (stretch) | `u2-ch1-code` | 50 → `guess = secret` | scripted player 50 → 35 → secret (seed 4 → 31): `cold…`, `HOT!`, `Got it!` (both hints); assert unchanged |

**teacher-notes.md ([fable] B2 — my first audit was wrong):** line 34 calls the Spotlight ladder's loop "a deterministic `while` rung" —
reword to a computer-guesser rung whose trip count changes every run, and add the tip "run it several times and tally the trips"
(ties to the existing flip-cards-until-the-ace unplugged trace).
Line 30 says "Every rung is teacher-run (it waits for typing)" — untrue since plan 054 added the executable twin; correct it in the same edit.

Notice content ([fable] check 3): cell 74 says a self-running notebook cannot wait for typing, so a scripted player guesses 50, 25, 40, 37,
the body runs once per wrong guess (three times), and the real game below swaps the scripted lines for one `input()` line;
cell 89 says nobody — not even the programmer — knows the trip count ahead of time, run it again and count, and that is why it is a `while`;
cell 91 says the random guess stands in for the typing player, the loop is silent like the real game's body, and cell 88 above shows the trips.
**Division of labour:** cell 88 makes the trips VISIBLE (fixed secret, prints each guess); cell 90 is the silent §6b PARITY twin of cell 92 —
deliberately similar, not redundant.

Unchanged: all `no-exec` real `input()` forms, all markdown real-program blocks, exercises.ipynb statements,
manifest/coverage-map (no concept added — `random-module`, `elif-else`, `comparison` are already introduced by u02).
Solutions Ch2 already runs a genuine multi-pass scripted loop — untouched.

## Design-003 fit

§6(b) result-line parity is preserved: every twin still ends on the same result line as its real form
(`Correct! Case closed.` / `Got it!` / the Ex8 and Ch1 final lines).
Twins still run unattended with no `input()`.
**Deliberate deviation:** the two AE computer-guesser cells are no longer strictly "fixed-data" twins — they are unseeded random.
Accepted because lesson cells carry no asserts, termination has probability 1, and the lesson never teaches `random.seed`;
solutions keep their existing `random.seed(4)` + asserts.

## Phases

### Phase A — edit the 7 code cells + 3 Notices + teacher-notes lines 30/34 (lesson.ipynb, solutions.ipynb, teacher-notes.md only)

### Phase B — verification
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN
  (concept-scan proves no `accumulator`/list/`range` crept in; exec-lessons/exec-solutions prove termination).
- Run each changed cell standalone: cell 73 prints exactly the 4 expected lines; cells 88/90 terminate and end with `Got it!`
  (repeat 200× to exercise the random path and RECORD the maximum trip count seen);
  Ex3/Ex5/Ex8/Ch1 each print their expected hint sequence (both hints) and pass their asserts;
  AST check that every scripted chain is a single `if/elif/else` (no sibling `if`s on the tested variable).
- Scope allowlist: `git diff --name-only $(git merge-base HEAD main)..HEAD` =
  this plan + u02 `lesson.ipynb` + u02 `solutions.ipynb` + u02 `teacher-notes.md`.

## Out of scope

- No new concept, no exercise-statement change, no metadata change, no other unit
  (other units' twins use taught loops/lists and already iterate).
- The duplicated cell id `u2-ex8-code`/`u2-ex8-heading` in solutions.ipynb (idx 20 and 24) is pre-existing; ids stay unchanged here — separate cleanup.
- Not an erratum (nothing was wrong or broken — a pedagogy improvement), so no `ERRATA.md` entry.
- **Verification phase:** Phase B is the named verification phase.

## Plan Review

### Round 1 (2026-09-21) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-21)
**APPROVE.** Order check: `randint` first used at lesson cell 31, `elif` at 58, `while` at 67 — all before the
targets (73, 88, 90), so nothing is used before it is taught. `guess = random.randint(...)` and constant
assignments inside `if/elif` are not read-modify-write, so `visit_Assign` cannot flag `accumulator`.
Termination: scripted chains end in an `else` that assigns the secret; the computer-guesser hits 1-of-10 with
probability 1 (expected ~10 trips). §6b result lines unchanged. Seeded secrets verified: seed 4 → 242 (1..1000)
and 31 (1..100), so the Ex8 chain prints high/high/low and the Ch1 chain prints cold/HOT. No metadata change.

#### [fable] (2026-09-21)
**REJECT (revise and resubmit)** — the idioms are sound; two factual misses, both now FOLDED:
- B1: two more one-pass loops were unscoped — solutions `u2-ex4-code` (Exercise 3, `player_b_guess = player_a_secret`)
  and `u2-ex6-code` (Exercise 5, `guessed_depth = secret_depth`); my grep matched only `guess = secret`.
  → added to the Changes table (7 code cells) with scripted chains 50→75→63 and 25→10→secret(16).
- B2: my teacher-notes audit was wrong — line 34 says "a deterministic `while` rung" (stale once cell 88 is random),
  and line 30 says every rung is teacher-run. → teacher-notes added to Phase A and the scope allowlist.
Nits folded: chain MUST be `if/elif/else` (separate `if`s would skip a guess in one pass) + AST check in Phase B;
separating comment between the hint `if/else` and the scripted chain; cell 88 starts with `import random` and `guess = 0`;
specific Notice content; 88-visible / 90-parity division of labour; unseeded-random recorded as a deliberate
design-003 deviation; Ex8 target pinned to idx 24 (duplicated id is pre-existing, out of scope); record max trip count.

#### [sol] (pending)
#### [glm] (pending — opencode)

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_

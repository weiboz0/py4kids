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

1. **Computer-guesser — rung cell 88 ONLY** (`random-module`, introduced in u02 before `while-loop`):
   `guess = random.randint(1, 10)` inside the loop.
   The loop runs an UNKNOWN number of trips until the sentinel — the real reason `while` exists —
   and it is line-for-line the real `input()` game with the read replaced by a random guess.
   Terminates with probability 1 (expected ~10 trips on 1–10); no `accumulator`.
2. **Scripted player** (`if-statement`/`elif-else`/`comparison`):
   an `if/elif/else` chain maps the current guess to the next scripted guess
   (`if guess == 50: guess = 25 / elif guess == 25: guess = 40 / else: guess = secret`).
   Assigning a constant is not read-modify-write, so no `accumulator`.
   The final `else` always assigns the variable `secret` — never a literal — in the lesson cells too ([fable] N2),
   so the loop cannot run forever even if a student edits `secret = 7` to another number.
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
| lesson AE twin | `u02-ae-fixed-twin` (90) — the cell the author pasted | `guess = secret` (1 silent pass) | **deterministic scripted player** ([sol] finding 3): `secret = 7`, `guess = 0`, body = `if guess == 0: guess = 3 / elif guess == 3: guess = 9 / else: guess = secret` then `print(guess)` (there so you can WATCH the guesses; the real game has no such line because you see what you type), then `print("Got it!")` → prints `3`, `9`, `7`, `Got it!` — 3 visible passes, finite by construction |
| lesson AE Notice | `u02-ae-fixed-notice` (91) | "the scripted follow-up reaches the sentinel…" | a scripted player guesses 3, 9, then 7; the body runs once per GUESS (three trips — the scripted "read" sits inside the body, like `input()` in cell 92); same `Got it!` result line as the real game below, which swaps the scripted lines for one `input()` line |
| solutions Ex3 (two-player) | `u2-ex4-code` (idx 8) | 50 → `player_b_guess = player_a_secret` | scripted Player B 50 → 75 → 63 (secret 63): `Too low, Player B!`, `Too high, Player B!`, correct; assert unchanged ([fable] B1) |
| solutions Ex5 (treasure) | `u2-ex6-code` (idx 14) | 25 → `guessed_depth = secret_depth` | scripted 25 → 10 → secret (seed 4 → 16): `Too deep!`, `Too shallow!`, found; final `else` assigns `secret_depth`; assert unchanged ([fable] B1) |
| solutions Ex8 | the SECOND cell with id `u2-ex8-code` — idx 24, "Number Detective 1–1,000" (the id is duplicated at idx 20; pre-existing, NOT fixed here — follow-up) | 500 → `guess = secret` | scripted player 500 → 250 → 240 → secret (seed 4 → 242): `Too high!`, `Too high!`, `Too low!`, correct; final `else: guess = secret` keeps it seed-proof; assert unchanged |
| solutions Ch1 (stretch) | `u2-ch1-code` | 50 → `guess = secret` | scripted player 50 → 35 → secret (seed 4 → 31): `cold…`, `HOT!`, `Got it!` (both hints); assert unchanged |

**teacher-notes.md ([fable] B2 — my first audit was wrong):** line 34 calls the Spotlight ladder's loop "a deterministic `while` rung" —
reword to name BOTH new rungs ([fable] N3): "comparison rungs → a computer-guesser `while` rung (trip count changes each run) → a scripted-player twin → the display-only interactive game", and add the tip "run it several times and tally the trips"
(ties to the existing flip-cards-until-the-ace unplugged trace).
Line 30 says "Every rung is teacher-run (it waits for typing)" — untrue since plan 054 added the executable twin; correct it in the same edit.

Notice content ([fable] check 3): cell 74 says a self-running notebook cannot wait for typing, so a scripted player guesses 50, 25, 40, 37,
the body runs once per wrong guess (three times), and the real game below swaps the scripted lines for one `input()` line;
cell 89 says nobody — not even the programmer — knows the trip count ahead of time, run it again and count, and that is why it is a `while`;
cell 91 says a scripted player guesses 3, 9, 7 and the real game below replaces those lines with one `input()` line.
**Division of labour ([sol] finding 3):** cell 88 is a teaching RUNG, not a design-003 twin — the unseeded computer-guesser shows that the trip count is unknown
(a lucky first-try match, ~10% of runs, is part of the lesson: "run it again"); cell 90 is the design-003 TWIN of cell 92 and is fully deterministic and finite.
The twin's per-trip `print(guess)` is a pedagogy print (so students can watch the guesses); §6b compares the computed RESULT line only
(u05 precedent: pedagogy prints are excluded from parity).

Unchanged: all `no-exec` real `input()` forms, all markdown real-program blocks, exercises.ipynb statements,
manifest/coverage-map (no concept added — `random-module`, `elif-else`, `comparison` are already introduced by u02).
Solutions Ch2 already runs a genuine multi-pass scripted loop — untouched.

## Design-003 fit

§6(b) result-line parity is preserved: every twin still ends on the same result line as its real form
(`Correct! Case closed.` / `Got it!` / the Ex8 and Ch1 final lines).
Twins still run unattended with no `input()`.
Every design-003 TWIN (cells 73, 90, and the four solutions) is deterministic and finite by construction (final `else` assigns the secret).
**One deliberate non-twin:** rung cell 88 is unseeded random. Its run time has no finite bound in theory, but `P(trips > n) = 0.9^n`
(`n=200` → 7e-10; exceeding the 120 s exec-lessons timeout would need ~1e8 trips, probability 0 for all practical purposes).
Accepted because it is a rung (no asserts, no parity obligation) and the lesson never teaches `random.seed`;
solutions keep their existing `random.seed(4)` + asserts.

## Phases

### Phase A — edit the 7 code cells + 3 Notices + teacher-notes lines 30/34 (lesson.ipynb, solutions.ipynb, teacher-notes.md only)

### Phase B — verification
- Post-exec report records §6b parity (result lines unchanged from plan 054, re-executed per the parity item below).
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN
  (concept-scan proves no `accumulator`/list/`range` crept in; exec-lessons/exec-solutions prove termination).
- Run each changed cell standalone: cell 73 prints exactly the 4 expected lines; cells 88/90 terminate and end with `Got it!`
  (repeat 200× to exercise the random path and RECORD the maximum trip count seen);
  Ex3/Ex5/Ex8/Ch1 each print their expected hint sequence (both hints) and pass their asserts;
  AST check that every scripted chain is a single `if/elif/else` (no sibling `if`s on the tested variable).
- **Real-form parity execution ([sol] finding 4, design §6):** for every changed twin↔real-form pair, `ast.parse` the real form and run it in a
  fresh process with piped guesses that replay the twin's scripted sequence (injecting `random.seed` where the real form draws the secret,
  and piping the drawn secret as the final guess), then compare hint lines + the final result line with the twin:
  lesson 73↔75 and 90↔92; solutions Ex3, Ex5, Ex8, Ch1 ↔ their markdown `**The real program**` blocks.
- Scope allowlist: `git diff --name-only $(git merge-base HEAD main)..HEAD` =
  this plan + u02 `lesson.ipynb` + u02 `solutions.ipynb` + u02 `teacher-notes.md`.

## Out of scope

- No new concept, no exercise-statement change, no metadata change, no other unit.
  **Known follow-up ([glm] §5):** u07 `solution-9-code` has the same defect class (`while new_score in scores:` retries once with a fixed `1310`).
  Every other Book-1 `while` cell iterates genuinely (u04/u05/u10, cp02, project-01/02). u07 is a separate small plan — this one answers the u02 feedback.
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

#### [fable] round 2 (2026-09-21) — on 4a3d7ac
**APPROVE WITH NITS.** B1, B2 and every nit RESOLVED; the 88/90 split judged sound and better than the first draft
(visible repetition in both cells; cell 90 is the closest twin↔real-form match in the unit). New nits, all FOLDED:
N1 cell 90 body runs once per GUESS not per wrong guess; N2 lesson chains end `else: guess = secret` (tinker-proof, no literal);
N3 teacher-notes:34 names both new rungs; Notice 91 says the per-trip print is for watching the guesses.

#### [fable] round 1 (2026-09-21)
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

#### [sol] round 2 (2026-09-21) — on 4a3d7ac
**APPROVE WITH NITS.** All four Must-Fix findings RESOLVED (7-cell inventory; teacher-notes in scope; rung-88 random / twin-90 deterministic split
accepted, with `print(guess)` accepted as a pedagogy print under the u05 rule; six-pair real-form parity in Phase B). Chains executed with the stated
outputs, no concept-scan gaps. Its three nits (once-per-guess wording, `else: guess = secret` in lesson chains, teacher-notes names both rungs)
are identical to [fable] N1–N3 and were already folded at 6aed441.

#### [sol] round 1 (2026-09-21) — reviewed first draft b19df66
**REJECT.** Findings 1 (Ex3/Ex5 twins missed) and 2 (teacher-notes lines 30/34) = [fable] B1/B2, already folded. New, both FOLDED:
- finding 3: the random idiom has a 10% one-pass chance, cell 90 would stay silent (repetition invisible), and its run time is unbounded →
  cell 90 (the design-003 twin, and the very cell the author pasted) is now a DETERMINISTIC scripted player that prints each guess (3, 9, 7);
  the random computer-guesser survives only as rung cell 88, documented as a deliberate non-twin with its probability bound.
- finding 4: Phase B lacked design-§6 real-form parity execution → added piped twin↔real-form runs for all six pairs; cells 88 states `import random`.
Closure PASS (randint taught cells 31–32, elif 57–59; no accumulator/loop-counter flag). cp01 Q5 confirmed NOT a missed twin (§6d condition form).
Re-verify pending.
#### [glm] round 2 (2026-09-21) — on 4a3d7ac
**APPROVE.** Every prior finding RESOLVED. Scanner on the revised cell 90 + Ex3/Ex5 chains: gaps NONE, accumulator False; cell 90 prints exactly
`3, 9, 7, Got it!`. Ran the new Phase-B items: piped real-form parity MATCHES on all six pairs (lesson pairs need a seed hunt so the real form's
draw equals the twin's fixed secret: seed 115 → 37 on 1..100, seed 0 → 7 on 1..10); AST single-chain check passes. Fresh sweep of every u02 `while`
cell found no further one-pass loops.

### Plan-review outcome: **FULL 4-way consensus** — [self] APPROVE · [glm] APPROVE · [sol]/[fable] APPROVE-WITH-NITS (all folded).
Round 1 was 3× REJECT on a completeness gap (two missed solution cells + stale teacher-notes) and the random-twin guarantee; round 2 clean. Gate CLOSED.

#### [glm] round 1 (2026-09-21) — reviewed first draft b19df66
**REJECT** on the same completeness gap ([fable] B1/B2 = Ex3/Ex5 cells + teacher-notes:34) — already FOLDED.
Verified with the repo scanner: `concept_scan.detect()` on every proposed source → gaps NONE, unknown methods NONE, accumulator False;
`randint` in TAUGHT_METHODS; seed 4 → 242 / 31; L4 chain prints the 4 predicted lines; 200 simulated computer-guesser runs → max 58 trips;
unseeded lesson random is CI-safe (exec-lessons compares no output, lesson has no asserts, PDF build converts exercises only).
New, FOLDED: the Out-of-scope claim "other units already iterate" was wrong for u07 `solution-9-code` → reworded + logged as a follow-up;
post-exec report must record that plan-054 parity carries over (result lines unchanged); cell 88 `import random` and the Ex8 idx-24 pin were already folded.

## Content Review

### Round 1 (2026-09-21) — on implementation commit 2e7c686. [self] inline; [sol]/[glm]/[fable] dispatched.

#### [self] (2026-09-21)
**APPROVE.** Phase B executed: cell 73 prints `Too high!/Too low!/Too high!/Correct! Case closed.`; cell 90 prints `3/9/7/Got it!`;
cell 88 terminated in 200/200 runs (max 66 trips; 25 one-trip runs — the ~10% lucky case the Notice covers);
Ex3 low/high, Ex5 deep/shallow, Ex8 high/high/low, Ch1 cold/HOT, all asserts pass.
AST: all six scripted chains are a single `if/elif/else` whose final `else` assigns the secret VARIABLE.
Real-form piped parity MATCHES on all six pairs (73↔75 with seed→37, 90↔92 with seed→7, Ex3/Ex5/Ex8/Ch1 ↔ markdown blocks).
ci-local ALL GREEN (concept-scan PASS — no accumulator/list/range). Scope = the three u02 files; ids unchanged; idx-20 Exercise 7 cell untouched.

#### [fable] (2026-09-21)
**APPROVE WITH NITS — nothing `[OPEN]`.** Ran all 7 changed cells (outputs as predicted; every solution chain shows both hints);
traced cells 73/90 with an EDITED secret — both still terminate via `else: guess = secret`. Notices 74/89/91 accurate; solutions still answer
their unchanged statements; teacher-notes accurate; grep of the unit finds no stale "deterministic"/"one pass" prose. Nits:
- N1 blank line before the `# scripted player` comment in cell 73 (separates "give the hint" from "pick the next guess"). → FOLD.
- N2 Notices 74/91 name the last guess as 37/7 while the code reads `guess = secret` — add a half-clause ("the last scripted line,
  `guess = secret`, is the player finally getting it right"). → FOLD.
- N3 Notice 89 "not a fixed number of lines" → smoother wording. → FOLD.
- N5 teacher-notes "tally the trips" tip as its own sentence. → FOLD.
- N4 `[WONTFIX]` capitalization "Scripted player" (solutions comments start a sentence) vs "scripted player" (lesson, mid-comment).

#### [sol] (2026-09-21)
**APPROVE WITH NITS.** Standalone outputs match; cell 88 200/200 runs end `7`/`Got it!` (max 46 trips); AST: every scripted loop has exactly one
mutating chain ending in an assignment of the secret variable; all six piped parity pairs match after prompt removal; concept-scan PASS
(no accumulator/list/range; randint cell 31, elif cell 58); blind-solve confirms Ex3/Ex5/Ex8/Ch1 still satisfy their statements;
hygiene/noexec/structure/cell-lint pass; changed cells exactly lesson 73/74/88/89/90/91 + solutions 8/14/24/27; idx-20 cell unchanged.
- `[OPEN]` N1: teacher-notes:34 "trip count changes each run" is too absolute (two runs can tie) → "can change each run". → FOLD.
- `[WONTFIX]` duplicated `u2-ex8-code` id — pre-existing, out of scope.

#### [glm] (pending — opencode)

## Post-Execution Report
_(pending)_

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

## The treatment (list-less unit, guessing-game)

1. **Real-input forms — in all three notebooks (unit convention, per u04/u07 — NOT cp01's solutions-only, which
   was to keep an *assessment* byte-unchanged):**
   - **solutions.ipynb:** markdown fenced ```python``` real-forms beside the fixed-data asserted twins.
   - **lesson.ipynb:** every complete task keeps an **executable fixed-data twin AND a `no-exec` input() real-form**.
     The `no-exec` input forms predate this work (8 of 9 pre-date plan 049; only the AE sentinel PIT is 049's);
     the **executable twins are MISSING for the complete interactive games → ADD them** (Lesson both-forms audit).
   - **exercises.ipynb statements:** non-exempt fixed-data exercises get a one-line `**Real version:**` cue;
     exempt exercises get a one-line student-facing note (u04/u07 wording style).
   `input` already in u02's `requires` → **no metadata change**.
2. **No data growth.** List-less; scalars (`secret=37`, `low=12`/`high=47`) already realistic — design 003 §3's
   **u01–u06 arm** (modest fixed dataset; the input() real-form carries realism). `random.randint` secrets stay.
3. **CP-light naming — near-zero.** u02 names (`secret`, `guess`, `low`, `high`, `is_correct`, `span`,
   `midpoint`, `player_a_secret`, `guessed_depth`) are domain nouns; **u02 bans guess counters** (no `attempts`).
   Keep verbatim.
4. **No numbered prompts.** Sentinel guess loops, no round index — prompts stay (`"Guess: "`/`"Guess again: "`),
   cp01-Q5 pattern.

## Lesson both-forms audit (design §1/§8 — every complete task keeps BOTH forms)

| Lesson cell | Status | Action |
|---|---|---|
| L3 cell 62 (`9d417a42`, one-guess game) | `no-exec` input only | **ADD executable twin** before it (pinned `secret`, fixed `guess` → same verdict line) |
| L4 cell 71 (`0cb62a32`, full game) | `no-exec` input only (L4 has ZERO executable cells) | **ADD executable twin** (pinned `secret`, scripted guesses → "Correct! Case closed.") |
| AE cell 86 (`7a0ffc200ee3`, sentinel PIT) | `no-exec` input only (rung 84 prints `7`, NOT 86's "Got it!" — not a parity twin) | **ADD executable twin** before it (pinned `secret`, scripted guess → "Got it!") — uniform with 62/71; the plan-049 ladder rungs 80/82/84 stay as the pattern build-up |
| L1 (4/6/15/22/24), L2 (35/46/48) | executable teaching, no interactive capstone | no unpaired input task — unchanged |
| traceback pair 74/76 | debug demo (both no-exec) | a traceback teaching pair, not a "complete task" — unchanged |

## Per-exercise SHAPE table

| Shape | Exercises | Real-form + statement treatment |
|---|---|---|
| **exempt** | Ex1 (dice roller — a `random` generator, reads NO external input, u04-Ch2-countdown class) | NO real-form; one-line note in the exercise STATEMENT ("a dice roller makes its own number, so there's no `input()` version") |
| **single-read / interactive** (statement already reads `input()`) | Ex2 (one guess), Ex3 (Player A types secret + Player B guess-loop), Ex4 (repaired `int(input(...))` program — the fix IS the real form; keeps the read-the-traceback statement framing), Ex5 (treasure guess-loop), Ex8 (full game) | markdown real-form = the input()-reading program (twin pins `secret` + scripted guess); no statement cue (already interactive) |
| **read-and-compute** (fixed values → real version reads them) | Ex6 (range-width report from `low`/`high`), Ex7 (one-guess truth check — a full program: `is_correct = guess == secret`, print, verdict) | markdown real-form reads the values via `int(input(...))`; **standard §6(a–c) parity** (Ex7 is a full program, NOT a §6(d) fragment); statements get a `**Real version:**` cue |
| **stretch (Challenge)** | Ch1 (hot/cold hints — random secret + guess loop → **interactive**), Ch2 (computer binary-search — reads `1/2/3` replies → **interactive**) | real-forms read the guess/replies; Ch2 replaces scripted replies with one `reply = int(input(...))`, §6(c) adapted (parity = "Found it: 68!" on piped `2\n1\n2\n3`) |

## Random-module parity protocol
Ex5/Ex8/Ch1 (+ Ex1) twins use `random`. Current Ex5/Ex8 twins are UNSEEDED (nondeterministic) → **change them to
seed** with `random.seed(N)` (like Ch1's existing twin; keeps `randint` visible, matches the teacher-note seeding
convention) so they run deterministically + assert. The `no-exec`/markdown real-form ships WITHOUT a seed (solutions
tell students not to seed); **Phase-B verification prepends `random.seed(N)` to the real-form only**, derives the
secret with the same `randint` call, and pipes a wrong-then-right guess sequence — parity = final result line +
termination (§6(d)-style oracle, since a scripted `guess = secret` twin isn't line-for-line a read).

## Closure
Real-forms use only u02's union (input, int/str, arithmetic, comparison, boolean, if/elif/else, while,
sentinel-loop, random-module, f-string, string-concat). No list, no `sys.stdin`, no `+=`, no `for`/`break`,
no concept outside u02. No metadata change.

## Phases
### Phase A — apply to u02 (lesson + exercises + solutions + teacher-notes)
- **lesson.ipynb:** add executable fixed-data twins before cells 62 + 71 + 86 (Lesson both-forms audit) with a
  Notice; the no-exec input forms stay as the real forms. (AE-86 twin: pinned `secret`, scripted guess → "Got
  it!"; the plan-049 rungs 80/82/84 remain the pattern build-up.)
- **exercises.ipynb:** add `**Real version:**` cues to Ex6/Ex7 statements; add the exempt note to Ex1's statement.
- **solutions.ipynb:** markdown real-forms per the SHAPE table (single-read Ex2/Ex3/Ex4/Ex5/Ex8; read-and-compute
  Ex6/Ex7; Ch1/Ch2 interactive); **seed the Ex5/Ex8 twins** (random parity protocol).
- No growth, no rename, no numbered prompts. Fenced real-forms must not contain a `## Exercise <digit>` line.

### Phase B — verification
- `ast.parse` + piped-run every real-form + the **3 new lesson twins (before cells 62/71/86)**; standard §6(a–c)
  parity (result line == twin modulo prompt text) for Ex2/Ex3/Ex4/Ex6/Ex7. The 3 lesson twins are
  **pinned-secret DETERMINISTIC** (run under `exec-lessons`; victory line "Correct! Case closed." / verdict /
  "Got it!" suffices — no seed). §6(d) termination+victory-line oracle (seed-injected per the parity protocol)
  for the random *exercise/challenge* guess-loops (Ex5/Ex8/Ch1) and the AE-86 real-form. **Ch2 is NOT random**
(binary-search, reads `1/2/3` replies) → §6(c) adapted, deterministic: piped `2\n1\n2\n3` → "Found it: 68!".
- CLOSURE AST scan (no concept outside u02's union; no `sys.stdin`).
- 0 `input()` in solutions CODE cells; ≥3 non-vacuous assert cells; no fenced `## Exercise <digit>` line;
  lesson executable twins run under `exec-lessons`.
- `scripts/ci-local.sh` ALL GREEN.

## Out of scope
- Any Book-1 entry other than u02 (rollout continues per design 003 §7). No design amendment. No data growth
  (list-less; §3 u01–u06 arm). Phase B present.

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.
#### [self] (2026-09-19)
- **Verdict**: APPROVE
- Reuses the proven u04 list-less template + cp01 guess-loop/exempt/§6(d) patterns; SHAPE table classifies all
  8 exercises + 2 Challenges (Ex6/Ex7 flagged for the gate to confirm read-and-compute vs exempt-predict);
  closure within u02's union (incl. random-module + sentinel-loop); `input` already in `requires` → no metadata;
  no growth (list-less scalars) / no rename (clean names) / no numbered prompts (sentinel loops) is correct;
  random parity handled by pinning a secret; Phase B verification present. No open blocker.
#### [sol] (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: complete interactive lesson tasks that are `no-exec` real forms WITHOUT executable
   fixed-data twins — L3 cell 62 (`9d417a42`, one-guess game), L4 cell 71 (`0cb62a32`, full game), AE cell 86
   (`7a0ffc200ee3`, sentinel PIT). design §1/§8 require both forms. Add executable twins + Phase-B parity.
   (Survey confirms: cell 84 is a degenerate sentinel RUNG (`guess = secret`, prints 7), not 86's parity twin.)
2. `[OPEN]` Should Fix: Ex7 is definitively read-and-compute (full program: assign `is_correct`, print
   comparison, branch to verdict) — standard §6(a–c), not §6(d). (== [fable]#4)

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: REJECT — SHAPE table (incl. Ex1/Ex4 exempt, Ex6/Ex7 read-and-compute), closure, no-growth,
  no-rename, no-prompts, no-metadata all affirmed sound. 3 findings:
1. `[OPEN]` Must Fix: L4 both-forms gap (== [sol]#1) — cell 71 (full game) has no executable twin (L4 has ZERO
   executable cells); Phase A's "add no-exec form where missing" is one-sided (blocks the executable ADD §8
   demands). Add an executable twin beside 71 (u04 L1/L3 pattern: pinned secret + stand-in guesses → "Correct!
   Case closed."); audit L3 cell 62, AE 86 (executable rungs adjacent — justify via the ladder or add).
2. `[OPEN]` Should Fix: statement-side conventions dropped — u04/u07 (UNITS) put exempt notes in exercise
   STATEMENTS + `**Real version:**` cues on non-exempt fixed-data statements. cp01's solutions-only was to keep
   the ASSESSMENT byte-unchanged — doesn't apply to a unit's exercises.ipynb. Add cues (Ex6/Ex7) + statement
   exempt notes (Ex1/Ex4).
3. `[OPEN]` Should Fix: random-parity contradictory — Ex5/Ex8 twins are UNSEEDED (can't be §6(b) oracles);
   state the twin change (seed like Ch1, keeping `randint` visible) + define parity coverage.
4. `[OPEN]` Nice: `attempts` not in u02 (counters banned); "most from plan 049" over-attributes (8 of 9
   predate 049); no-growth arm is §3's u01–u06 bullet, not §3 v2.

### Round 1 — outcome: REJECT (2 of 4: [sol]+[glm]). Fix → round 2.

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS — shape/closure/no-growth/no-rename/no-prompt/no-metadata sound; Ex1-exempt
  confirmed; Phase B present.
1. `[OPEN]` Must Fix: Ex4 is NOT exempt → **single-read**. Its broken starter already reads `input()` ("Run it
   and type 12"); the fix keeps `input()` + adds `int()`, so the program IS the real form (unlike cp01 Q1 where
   the value was typed in code). An exempt "no input() version" note would be false.
2. `[OPEN]` Should Fix: random-parity mechanism underspecified + contradicts current twins (Ex5/Ex8 use UNSEEDED
   random + scripted `guess = secret`; only Ex1/Ch1 seed). Specify: verification prepends `random.seed(N)` to
   the real-form ONLY (never shipped — solutions tell students not to seed), derives the secret with the same
   call, pipes wrong-then-right guesses; parity = victory line + termination (§6(d)-style oracle, since the
   twin's scripted `guess = secret` isn't line-for-line a read).
3. `[OPEN]` Should Fix: L4 both-forms gap — L4's whole ladder (lesson 65/67/69/71) is `no-exec` input(); the L4
   put-it-together (cell 71, full game) has NO executable fixed-data twin (design §1/§8 require both). Add an
   executable twin (`secret=37`, first guess 50, scripted follow-up) OR document the executable form is AE cell
   84 + the Ex8 solutions twin. Clarify L2 cell 48's PIT status. (L1 22↔26, L3 58↔62, AE 84↔86 already paired.)
4. `[OPEN]` Nice: Ex7 is a full program, not a fragment — standard §6(b)/(c), drop the §6(d) hedge; Ex6/Ex7 stay
   read-and-compute (not exempt).
5. `[OPEN]` Nice: Ch1 is an interactive random guess loop (not read-and-compute) — relabel; Ch2 §6(c) adapted
   (one `reply = int(input(...))` replaces the scripted replies; parity = "Found it: 68!" on piped 2\n1\n2\n3).

**Round 1 responses (plan revised):**
- → [FIXED] Lesson both-forms gap ([sol]#1 / [glm]#1 / [fable]#3 — Must): added a **Lesson both-forms audit**;
  ADD executable twins before L3 cell 62 + L4 cell 71 (u04 L1/L3 pattern); AE cell 86 justified via the
  plan-049 ladder; L1/L2/traceback audited as no unpaired task.
- → [FIXED] Ex4 → **single-read** ([fable]#1): its broken starter already reads `input()`; the repaired
  `int(input(...))` program IS the real form (not exempt); keeps the read-the-traceback statement framing.
- → [FIXED] Statement-side conventions ([glm]#2): exercises.ipynb gets `**Real version:**` cues (Ex6/Ex7) +
  Ex1 exempt statement note — unit convention (cp01 solutions-only was assessment-specific).
- → [FIXED] Random parity ([fable]#2 / [glm]#3): added the **Random-module parity protocol** — seed the
  Ex5/Ex8 twins, inject the seed into the real-form for verification only; §6(d) victory+termination oracle.
- → [FIXED] Ex7 → standard §6(a–c) ([sol]#2 / [fable]#4), NOT §6(d) (it's a full program); Ch1 interactive,
  Ch2 §6(c) adapted ([fable]#5).
- → [FIXED] Nice wording ([glm]#4): removed `attempts` (counters banned in u02); corrected plan-049
  attribution (8 of 9 no-exec cells predate 049); cite §3's u01–u06 arm (not §3 v2).
Re-dispatching round 2 (lesson twins + statement conventions changed materially).

### Round 2 (2026-09-19) — re-review after fixes (a145471)
#### [self] round 2 (2026-09-19)
- **Verdict**: APPROVE — lesson both-forms audit (executable twins for L3-62 + L4-71; AE-86 via the ladder)
  resolves the design §1/§8 gap; Ex4→single-read, Ex7→standard §6(a-c); exercises.ipynb statement cues +
  random-parity protocol added; Nice wording fixed. No open blocker.
#### [sol] round 2 (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: L3-62/L4-71 twins + Ex7 §6(a-c) + seeded random parity resolved, but **AE-86 remains
   unpaired** — rung 84 prints `7`, not 86's "Got it!", so it can't satisfy §1/6/8 result-line parity by
   ladder-adjacency alone. Add an executable fixed-data AE twin (parity with 86) + name its Phase-B check.
   → [FIXED]: audit AE row now ADDS a twin (uniform with 62/71), not via-ladder.

#### [glm] round 2 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — all 4 round-1 findings verified resolved (both-forms audit; statement cues;
  random protocol; Nice wording); cross-reviewer resolutions (Ex4 single-read, Ex7 standard, Ch1/Ch2) confirmed.
  2 wording Nice:
1. `[OPEN]` Nice: SHAPE "(statement already reads input())" is figurative for Ex2/3/5/8 (prose directs
   asking/typing; only Ex4 literally contains `input(`) — classification correct; tighten wording at impl.
2. `[OPEN]` Nice: Phase B groups the new L3/L4 twins under "§6(d) seed-injected" — they're pinned-secret
   DETERMINISTIC (exec-lessons run + victory line suffices; no seed) — wording only. → will clarify.

#### [fable] round 2 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all 5 round-1 items resolved + verified; AE-86-via-ladder sound (design §2
  ladder row + plan-049 rung 84 as the deterministic executable counterpart); Ch2 trace confirmed
  ("Found it: 68!" on 2\n1\n2\n3). 3 Nice (fold #1; honor #2/#3 at implementation):
1. `[OPEN]` Nice: add AE cell 86 to Phase B's §6(d) list (rung 84 prints `7`, not 86's oracle) — verify 86 on
   its own (seed-inject + wrong-then-right → "Got it!" + termination). → will fold into Phase B.
2. `[OPEN]` Nice: seed the Ex5/Ex8 twins with an `N` whose secret ≠ the scripted first guess (25/500), so the
   loop body executes. → implementation.
3. `[OPEN]` Nice: Ex4's real-form includes the statement-required type-problem comment (complete model answer).
   → implementation.

### Round 2 — outcome: REJECT (1 of 4, [sol] — AE-86 twin). [glm]/[fable] APPROVE-WITH-NITS. Fixed → [sol] round 3.
**Round 2 responses:** [sol]#1 [FIXED] AE cell 86 now gets its OWN executable twin (uniform with 62/71),
not via-ladder — audit + Phase A/B updated. [fable]#1 [FIXED] AE-86 named in Phase B (now has a deterministic
twin + §6(d) real-form oracle). [fable]#2/#3 → implementation (seed choice; Ex4 comment). [glm]#1/#2 [FIXED]
wording: SHAPE "already reads input()" figurative note; L3/L4/AE twins are pinned-secret deterministic (no
seed), distinct from the seed-injected exercise/challenge oracle. Re-dispatching [sol] round 3.

### Round 3 (2026-09-19) — [sol] re-review after AE-86 twin (4f121e0)
#### [self] round 3 (2026-09-19)
- **Verdict**: APPROVE — all 3 complete lesson interactive tasks (cells 62/71/86) now get executable
  fixed-data twins (uniform); every complete task has both forms per §1/§8. No open blocker.
#### [sol] round 3 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — AE-86 Must-Fix resolved (cells 62/71/86 each get an executable twin + named
  Phase-B check; §1/6/8 no blocker). Nice: Ch2 (non-random binary-search) shouldn't sit under the seed-injected
  §6(d) list → [FIXED] (Phase B now marks Ch2 §6(c)-adapted, deterministic).

### PLAN-REVIEW GATE CLOSED (2026-09-19) — 4-way consensus: [self] APPROVE, [sol]/[glm]/[fable] APPROVE WITH
NITS (all folded). No open blockers.

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

# Plan 068 — Unit 07 duplicate-guard `while` twin: make it retry several times

**Origin:** follow-up logged in plan 067 — the same one-pass defect class in u07.
The author's u02 feedback ("too edge case, not enough to showcase the while loop usage") applies to any
executable twin whose `while` runs a single pass. **Design:** the executable fixed-data twins pattern (plan 054);
scripted-player idiom (plan 067, PR #90). Related: [[twins-must-showcase-the-concept]].

## Motivation

Unit 07 Exercise 6 ("Guard Against a Repeated Score") teaches a duplicate-guard loop:
`while new_score in scores: print(...); ask again`.
Its reference solution (`solutions.ipynb` cell id `solution-9-code`, idx 16 — the id is misnamed; it sits under
`## Exercise 6`) scripts the retry as a single `new_score = 1310`, so the loop runs **one pass** and prints the
"already on the board" message once.
The paired exercise statement (`exercises.ipynb` cell id `dfc665d7`) suggests the matching one-retry playthrough
("try 990 and then 1310").

**Structural sweep (the plan-067 lesson: enumerate by shape, not one spelling).** All four executable `while`
cells in u07: lesson `f9ae6759` (doubling threshold, ~8 passes), solutions `solution-13-code` (accumulate to
1000, 3 passes), solutions `solution-12-code` (doubling, 8 passes) all iterate genuinely. Only `solution-9-code`
is one-pass. It is the single cell to fix.

## The change (1 solution cell + 1 exercise statement; ids unchanged)

Use the plan-067 **scripted-player** idiom: one `if/elif/else` chain mapping the current rejected score to the
next scripted score, the final `else` assigning a value NOT on the board so the loop always terminates.
The board is `[1500, 1200, 990, 850]`; script three already-present retries then a new score:
`990 → 1200 → 850 → 1310`.

| Cell | Now | After |
|---|---|---|
| solutions `solution-9-code` (idx 16) | `new_score = 1310` (1 pass) | a separating comment `# scripted player: the next score to try (stands in for input())` ([fable] N1 — the loop already holds a real `if/else` champion check right after, so the comment keeps the stand-in visibly distinct) then the scripted chain `if new_score == 990: new_score = 1200 / elif new_score == 1200: new_score = 850 / else: new_score = 1310` → the loop prints "already on the board" **3 times** (for 990, 1200, 850) before 1310 exits |
| exercises `dfc665d7` (Exercise 6 statement) | "try 990 and then 1310." | "try 990, 1200, 850, then 1310 — the first three are already on the board, so the loop asks again each time." |

**End state unchanged**, so the asserts are untouched: after the loop `new_score == 1310`; `scores.append(1310)`
+ `sort(reverse=True)` → `[1500, 1310, 1200, 990, 850]`; `1310 != scores[0]` (1500) → prints "The champion is
still 1500." The three asserts (`new_score not in [1500,1200,990,850]`, `scores == [1500,1310,1200,990,850]`,
`scores[0] == 1500`) all still hold.

Closure: the chain uses only `if`/`elif`/`else`, `==` comparison, and constant assignment — all in u07's union;
no `accumulator` (constant assigns; and u07 practices `accumulator` anyway), no new concept.

## Design-003 fit (§6b parity)

The paired real-program markdown block (`solutions.ipynb` idx 17, id `b05200000005`) reads `new_score` with
`int(input("New score: ").strip())` on the first read and on each retry — it is UNCHANGED (it already handles
any number of retries). Piped `990\n1200\n850\n1310`, it reproduces the twin's output line-for-line (its intro caption is extended to name the playthrough `try 990, 1200, 850, then 1310` for cue-consistency with the exercise statement — [fable] N2)
(the `print(new_score in scores)` → `True`, three "already on the board" lines, then "The champion is still
1500."). Result-line parity preserved.

## Phases

### Phase A — edit the solution cell + exercise statement (solutions.ipynb, exercises.ipynb only)

### Phase B — verification
- `TMPDIR=/dev/shm bash scripts/ci-local.sh` ALL GREEN (concept-scan proves no `accumulator`/list/range leak;
  exec-solutions proves the loop terminates and the three asserts pass).
- Run `solution-9-code` standalone: prints `True`, then the "already on the board" message exactly 3 times, then
  "The champion is still 1500." Confirm the scripted chain is a single `if/elif/else` (AST) whose final `else`
  assigns a value not in `scores`.
- §6b: pipe `990\n1200\n850\n1310` into the real-program block and confirm its output matches the twin modulo
  the input prompt text.
- Scope allowlist: `git diff --name-only $(git merge-base HEAD main)..HEAD` = this plan + u07 `solutions.ipynb`
  + u07 `exercises.ipynb`.

## Out of scope

- No other unit, no new concept, no metadata change, no teacher-notes change (audit: the Lesson-3 note does not
  mention the "990/1310" values, so it stays accurate).
- Not an erratum (the twin runs and its asserts pass — a pedagogy improvement, per the plan-067 framing), so no
  `ERRATA.md` entry.
- Still open elsewhere (unrelated): design-003 §4 dict-read idiom docs fix; the pre-existing duplicated cell id
  `u2-ex8-code` in u02 solutions; the misnamed `solution-9-code`/`solution-13-code`/`solution-12-code` ids in u07
  (ids stay unchanged here).
- **Verification phase:** Phase B is the named verification phase.

## Plan Review

### Round 1 (2026-09-21) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-21)
**APPROVE.** Structural sweep confirms `solution-9-code` is the ONLY one-pass while in u07 (lesson doubling ~8,
Ex13 accumulate 3, Ex12 doubling 8 all iterate). Self-check executed: twin prints `True` + 3× "already on the
board" + "The champion is still 1500.", all three asserts pass; loop body is one if/elif/else; real-form piped
`990/1200/850/1310` matches line-for-line (prompts stripped). Closure: chain is if/elif/else + `==` + constant
assign — all in u07 union, no accumulator flag. End state unchanged so asserts untouched. Exercise-6 statement
updated to match the new playthrough. No metadata/teacher-notes change (audit: Lesson-3 note doesn't cite the
990/1310 values).

#### [fable] (2026-09-21)
**APPROVE WITH NITS.** Executed the proposed cell: `True` + 3× retry message + "The champion is still 1500.", all three
asserts survive. Structural sweep confirmed independently (only `solution-9-code` is one-pass; lesson f9ae6759 = 8 passes,
Ex13 = 3, Ex12 = 8). Chain must be single if/elif/else (else 990→1200 skips a retry — plan-067 trap; Phase B AST-checks it).
Statement update correct + work cell `ee669daf` untouched; §6b parity holds on the unchanged real block; closure clean.
"Champion still 1500" is the better choice (landing 1310 in 2nd place also shows the sort). Nits:
- N1 (fold): add the plan-067 separating comment above the chain (a real `if/else` champion check sits right after it). → FOLDED into the plan + implementation.
- N2 (optional): name the playthrough in the real-program block's intro caption. → FOLDED (light caption tweak).

#### [sol] (2026-09-21)
**APPROVE** — no findings. Confirmed exactly 4 executable u07 while cells (f9ae6759=8, solution-9-code=1 defect,
solution-13-code=3, solution-12-code=8; exercises has none); trace 990→1200→850→1310 gives 3 messages, end state
+ 3 asserts unchanged; in-memory scan of the full cell → no accumulator/unknown-method/used-but-unlisted; §6b
piped parity exact after removing `New score: `; statement update necessary not scope creep, work cell stays
empty no-exec; pedagogy-improvement classification correct, teacher-notes accurate; Phase B adequate.

#### [glm] (2026-09-21)
**APPROVE** — no blockers. Independent AST enumeration of every code cell in all 3 u07 notebooks: exactly 4 executable
while cells (f9ae6759=8, solution-9-code=1 defect, solution-13-code=3, solution-12-code=8; exercises has zero). Executed
the revised cell: 3 passes, 3 messages, end state + asserts unchanged. concept_scan.detect → gaps NONE / accumulator
False / unknown methods NONE. §6b piped parity BYTE-IDENTICAL after stripping prompts. Statement update required (not
scope creep). Erratum call, verification phase, teacher-notes audit, CI-safety, misnamed-id note all sound.
Non-blocking observation: final `else` assigns the literal 1310 (no "secret variable" exists here; the same edit-hazard
predates the fix; no in-union alternative preserves the pinned asserts) — structurally inapplicable, not a regression.

### Plan-review outcome: **FULL 4-way consensus** — [self] APPROVE · [sol] APPROVE · [glm] APPROVE · [fable] APPROVE-WITH-NITS (N1/N2 folded). Gate CLOSED → implementation.

## Content Review

### Round 1 (2026-09-21) — on implementation commit a901499. [self] inline; [sol]/[glm]/[fable] dispatched.

#### [self] (2026-09-21)
**APPROVE.** Executed: `solution-9-code` prints `True` + 3× "already on the board" + "The champion is still 1500.",
all three asserts pass; loop body is one if/elif/else. Real-form piped `990/1200/850/1310` MATCHES the twin
(prompts stripped). 0 `input(` text in any solutions code cell (the separating comment says "stands in for
typing", not "input()" — the policy check tools/notebooks.py:279 is a raw-text regex that would flag even a
comment; caught during Phase B, reworded). ci-local ALL GREEN; scope = plan + u07 solutions.ipynb + exercises.ipynb;
exercise statement + real-block caption name the 990/1200/850/1310 playthrough; ids unchanged.

#### [fable] (2026-09-21)
**APPROVE WITH NITS — 0 `[OPEN]`.** Executed `solution-9-code`: `True` + 3× retry + "still 1500", asserts pass; output
matches the statement + caption promise for the 990→1200→850→1310 playthrough; §6b real-form differs only in prompts.
Pedagogy genuine (3 honest re-tests; the comment + blank line keep the fake-input chain distinct from the real champion
if/else). Statement/caption coherent; work cell `ee669daf` empty/no-exec/0-outputs; ids unchanged; teacher-notes accurate.
Nits (optional): N1 caption puts "then" in code font (`` `990, 1200, 850, then 1310` ``) → use `` `990`, `1200`, `850`, then `1310` `` → FOLD; N2 bare final `else` vs named `elif` → keep (standard catch-all, u02 precedent).

#### [sol] (pending)
#### [glm] (pending — opencode)

## Post-Execution Report
_(pending)_

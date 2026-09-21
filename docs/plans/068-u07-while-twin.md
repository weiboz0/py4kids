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
| solutions `solution-9-code` (idx 16) | `new_score = 1310` (1 pass) | scripted chain `if new_score == 990: new_score = 1200 / elif new_score == 1200: new_score = 850 / else: new_score = 1310` → the loop prints "already on the board" **3 times** (for 990, 1200, 850) before 1310 exits |
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
any number of retries). Piped `990\n1200\n850\n1310`, it reproduces the twin's output line-for-line
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

#### [sol] (pending)
#### [glm] (pending — opencode)
#### [fable] (pending)

## Content Review
_(pending)_

## Post-Execution Report
_(pending)_

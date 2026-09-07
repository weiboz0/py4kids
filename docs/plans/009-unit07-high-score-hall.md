# Plan 009 — Unit 07 High-Score Hall Implementation Plan

**Goal:** Ship `unit-07-high-score-hall` — the first collections unit — where students build an arcade leaderboard: a LIST that remembers every player's score, grows with `append`, is walked with a loop, ranked with `sort`, and summed/measured with built-in functions (`len`/`max`/`min`).

**Architecture:** Standard unit pipeline (plan 004), no new tooling. ONE map amendment lands UP FRONT (the standing plan-002 substrate audit, applied proactively and validated with the new AST concept-scanner from plan 008): unit-07's `requires ∪ practices` omits the foundational substrate its leaderboard content uses. The unit's helper functions take arguments and return values (`parameters`, `return-value` → requires); the display/scoring beats use `print`, `arithmetic` (running total, `place + 1`), `int-type` (scores), `range-function` + `loop-counter` (numbered board), `if-statement`/`elif-else` (tier ranking), `string-concat` + `type-conversion` (`"Place " + str(place) + ": " + str(score)`), `float-type` (the average from `/`), `input` (an exercise reads a score), `in-operator` (already-ranked check), `error-messages` (the Lesson-2 off-the-end IndexError beat), `string-literal` (names/tier labels/`": "`), and `boolean` (`scores.sort(reverse=True)` — a boolean literal) → practices. All taught by units 01–06; verified green in scratch. The `string-literal`/`boolean` pair was caught by the AST concept-scanner against the planned code shapes BEFORE authoring — the exact used-but-unlisted misses that cost unit-06 sol rounds 2–3, now pre-empted.

**Spec:** `book1/curriculum/coverage-map.yaml` (binding, amended); plan 004 unit conventions; D-001 (hook-first).

## Global Constraints

- All plan-004 unit Global Constraints apply (map-equal manifest, hook-first, exercise ≥6 core
  + ≥2 stretch, solution floors + per-line bans, seed ordering, non-vacuous asserts incl. no
  tautologies, five teacher-notes headings, per-lesson allocation, commit trailers).
- Coverage-map amendment (EXACTLY this, pre-audited + scanner-validated green):
  - append to `unit-07-high-score-hall.requires` — `parameters, return-value`.
  - append to `unit-07-high-score-hall.practices` — `print, arithmetic, int-type,
    range-function, loop-counter, if-statement, elif-else, string-concat, float-type,
    type-conversion, input, in-operator, error-messages, string-literal, boolean`.
    (`string-literal`: names/tier labels/`": "`; `boolean`: the `reverse=True` sort argument.
    Both caught by the AST scanner + [fable] plan review before authoring — the exact
    used-but-unlisted misses of unit-06 sol rounds 2–3, pre-empted.)
  - All introduced by units 01–06; `practices ∩ introduces` stays empty (introduces =
    list-*/builtin-functions, none repeated in practices). Apply surgically (no YAML
    round-trip — it reflows the file). The manifest carries the amended lists.
  - Every amended concept must be HOMED in ≥1 lesson beat or exercise (not padding —
    plan-008 gate round-1 lesson): `print` (show the board), `arithmetic` (`total = total +
    score`, `place + 1`), `int-type` (scores are integer literals), `range-function` +
    `loop-counter` (`for place in range(len(scores))` numbered board), `if-statement`/
    `elif-else` (gold/silver/bronze tiers), `string-concat` + `type-conversion`
    (`"Place " + str(place) + ": " + str(score)` label), `float-type`
    (`average = total / len(scores)`), `input` (an exercise reads a score to add),
    `in-operator` (`if new_score in scores` already-on-the-board — a CONDITION, never
    printed/assigned as a truth value, so it drags no boolean), `parameters` + `return-value`
    (the `add_score`/`board_line` helpers), `error-messages` (read the off-the-end IndexError
    together), `string-literal` (tier labels + `"Place "`/`": "` fragments + sample champion
    name), `boolean` (the `reverse=True` sort argument). Teacher notes name each reappearance.
- **Pre-gate closure self-check (NEW, standing from plan 008):** before dispatching the
  `[sol]` content review, run the AST concept-scanner over the drafted notebooks and confirm
  ZERO used-but-unlisted concepts. This is the mechanical catch for the substrate saga —
  no content review is dispatched until the scanner is clean for unit-07.
- **Lists mechanics (binding):** lists are built with `[...]` literals and grown with
  `.append(x)`; indexed with `scores[0]` / `scores[-1]`; walked with `for score in scores`;
  ranked with `.sort()` (ascending) and `.sort(reverse=True)` (top-first, IN PLACE — name
  the in-place mutation explicitly, contrast with unit-06's rebuild-don't-mutate strings).
  `len`/`max`/`min` are the taught `builtin-functions`. `.sort()` is the ONLY ranking tool —
  `sorted()` is FORBIDDEN (it is out of the `builtin-functions` "len/min/max" subset, exactly
  the plan-008 `.index()`/`.find()` subset-discipline logic; reviewers check for it). No list
  comprehensions, no slicing of lists into new lists (`scores[:]`/`list(...)`/`.copy()` are
  out of budget), no `enumerate` — the numbered board uses `for place in range(len(scores))`.
- **DATA MODEL (binding, glm plan-review — the central-artifact fix):** the leaderboard is a
  SINGLE list of integer scores. There is NO parallel `names` list: `scores.sort()` would
  silently break index alignment with a second list, and NOTHING in budget (`zip`/`enumerate`/
  tuples/dicts/keyed sort) can re-pair them. Instead: (a) the sorted board is ranked BY PLACE,
  labelled `"Place N: <score>"`, never by owner; (b) `string-methods` is homed on a SCALAR
  champion name (`winner = "  ada lovelace  ".strip().upper()`), not a list; (c) the champion
  SCORE is captured BEFORE sorting (`champion = max(scores)`) so any post-sort assert compares
  to it without needing an unsorted copy. Any name↔score pairing (a true named hall) waits for
  dicts (unit 08).
- **No nested loops (binding, fable plan-review):** `nested-loops` is taught (unit 03) and so
  usable, but it is NOT in unit-07's union and no beat needs it — every loop (numbered board,
  merge-two-boards, sort-then-top-three) is a SINGLE loop. Reviewers reject any
  `for … : for … :` nesting; it would be a used-but-unlisted drag.
- **No dicts/files/classes** (units 08/09/10). No `enumerate`, no `zip`, no list
  comprehension, no `.insert`/`.remove`/`.pop`/`.index` (untaught list methods — only
  `.append` and `.sort` are in the introduced set; reviewers check for these explicitly since
  they would slip a concept-ID closure check). No turtle (no assets).
- **Input discipline (binding):** executed cells (lessons + solutions) are input-free —
  `input()` appears only in an exercise PROMPT (markdown) and the exercise's reference
  solution is parameterized with a fixed sample score, exactly like plan 008. `input` is
  homed by the exercise prompt; solutions never call it (source-scan).
- Process (standing): no commits while a `[sol]` review is in flight; codex content-gate
  prompts name the in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Content plan → Phase C is the mandatory named verification phase. Out of scope: units 08+,
checkpoint 03 (later plans); the latent practice-completeness cleanup of shipped units 03/04/05
+ cp02 + proj01 (batched hygiene PR, tracked separately); promoting the concept-scanner into
`tools/` as an official check (same hygiene PR); PDF handouts; any map edit beyond the Phase-A
substrate amendment; dicts/files/classes.

## Phases

Dispatch per AGENTS.md: lesson/exercise statements via codex; solutions via a SEPARATE blind
codex session; teacher notes inline; map amendment + manifest inline.

### Phase A — map amendment + manifest (inline)

1. Amend `coverage-map.yaml` per Global Constraints (surgical, both requires + practices);
   full suite green with the amendment alone before content.
2. `book1/units/unit-07-high-score-hall/manifest.yaml`, map-equal to the amended entry; lands
   with the complete directory in Phase B.
- **Acceptance (Phase A):** the map amendment ALONE is green (`uv run pytest -q` + `ci-local`)
  before any unit directory exists (manifest-check lands with the content in Phase B).

### Phase B — unit-07-high-score-hall content (2 lessons)

Blueprint (introduces list-literal, list-index, list-append, list-loop, list-sort,
builtin-functions; requires for-loop, variable, def-function, comparison, + amended parameters/
return-value; practices accumulator, f-string, while-loop, string-methods, + amended print/
arithmetic/int-type/range-function/loop-counter/if-statement/elif-else/string-concat/float-type/
type-conversion/input/in-operator/error-messages/string-literal/boolean):
- Hook: HIGH-SCORE HALL OF FAME — every arcade game needs a leaderboard. Build one that
  remembers every player's score, ranks the top players, and crowns a champion. The teacher
  shows a messy scrap of paper with scores and asks: how would a program keep this in order?
- Lesson 1 (list-literal, list-index, list-append, list-loop, builtin-functions) — opens on
  the hook: a LIST is one variable holding many scores — `scores = [1200, 850, 990, 1500]`.
  Grab the first/last (`scores[0]`, `scores[-1]`), add a new score (`scores.append(1310)`),
  and walk the whole board (`for score in scores: print(score)`). A NUMBERED board with
  `for place in range(len(scores)): print(place + 1, scores[place])`. Measure it: `len`,
  `max` (the champion), `min` (the rookie); a running `total` accumulator and
  `average = total / len(scores)` (a decimal — float). f-string display throughout.
- Lesson 2 (list-sort; practices the helpers + tiers) — opens on the thread ("yesterday we
  listed scores; today we rank them and crown the champion"): `scores.sort()` (low→high) and
  `scores.sort(reverse=True)` (top-first) — mutates the SINGLE scores list IN PLACE (contrast
  unit-06's rebuild-don't-mutate); capture `champion = max(scores)` BEFORE sorting. A
  `board_line` helper `def board_line(place, score): return "Place " + str(place) + ": " +
  str(score)` (string-concat + type-conversion + parameters + return-value), called in a
  `for place in range(len(scores)): print(board_line(place + 1, scores[place]))` numbered
  board. A helper `def add_score(scores, new_score): scores.append(new_score); return scores`.
  The champion's NAME cleaned as a SCALAR `winner = "  ada lovelace  ".strip().upper()`
  (string-methods) — no parallel list (see DATA MODEL constraint). Tier ranking with
  `if score >= 1000: ... elif score >= 500: ... else:` → gold/silver/bronze (if-statement,
  comparison, elif-else). An already-on-the-board guard `if new_score in scores` — a CONDITION
  (in-operator), never printed as a truth value. A qualifying-threshold `while` loop that
  fits the leaderboard story — `threshold = 10; while threshold < champion: threshold =
  threshold * 2` ("each round the score you need to qualify doubles until it passes the
  champion's") — homes `while-loop` with no `input` and no banned list method. A deliberate
  bug + traceback: `scores[len(scores)]` off-the-end IndexError, read together (error-messages).
- Exercises ≥6 core + ≥2 stretch, each HOMING an amended concept: build-the-board (list-literal
  + append), champion-and-rookie (builtin-functions max/min), numbered-leaderboard (range +
  loop-counter + list-index via `board_line`), team-total-and-average (accumulator + arithmetic
  + float), rank-the-tier (if/elif-else + comparison), tidy-the-champion-name (string-methods
  on a SCALAR name), add-my-score (input prompt → parameterized solution + append + return),
  label-the-line (string-concat + type-conversion via `board_line`), already-on-the-board
  (`if new_score in scores` condition — in-operator); stretch: sort-then-top-three (list-sort +
  list-index), merge-two-boards (append in a SINGLE loop over a second scores list).
- Solutions: execute headless, input-free (assigned fixed sample scores + a scalar sample
  name), non-vacuous asserts — a sorted-order assert that captures `champion = max(scores)`
  BEFORE `scores.sort(reverse=True)` then asserts `scores[0] == champion` (no unsorted copy
  needed — glm plan-review), an append-grows-length assert (`len` before/after), a tier-boundary
  assert (score 1000 → gold, 999 → silver), an average assert on known values, and a
  `board_line(1, 1500) == "Place 1: 1500"` assert. `random.seed(4)` only if any randomness.
- Teacher notes: five headings, per-lesson allocation (L1 build/index/append/loop/builtins, L2
  sort/functions/tiers), 60-min cut points, differentiation; common mistakes (off-by-one on the
  numbered board / `place + 1`; `scores[len(scores)]` off-the-end; expecting `.sort()` to
  RETURN a new list — it returns `None` and mutates in place; forgetting `reverse=True` for a
  top-first board; integer vs float average).

### Phase C — Verification (NAMED, mandatory)

Mechanical: full pytest green; `ci-local.sh` ALL GREEN; **AST concept-scanner clean (zero
used-but-unlisted) BEFORE the content gate**; solutions execute with non-vacuous asserts
(sorted order, length growth, tier boundary, average); manifest map-equal.
Reviewer duties: blind-solve exercises; cumulative closure (only ≤unit-07 concepts — NO dicts,
NO files, NO classes, NO `enumerate`/`zip`/comprehensions, NO list methods beyond `.append`/
`.sort` — check for `.insert`/`.remove`/`.pop`/`.index`/`sorted()` explicitly since they map to
no taught concept (or out-of-subset) and would slip a mechanical closure check; NO nested
loops; NO parallel name/score arrays — the DATA MODEL is a single scores list); the leaderboard
is buildable and correct (sort mutates in place, `champion` captured pre-sort, numbered board is
1-based, average is a float, `in-operator` is a condition not a printed truth value); solutions
non-vacuous/complete; grading usable; timing; each lesson opens on the project thread
(hook-first, per D-001); age-appropriate; EACH amended concept is exercised by ≥1 named beat
(especially `input`, `in-operator`, `float-type`, `string-concat` — the padding risks).

**Acceptance criteria:** the unit directory complete; `uv run pytest -q` green; ci-local ALL
GREEN; concept-scanner clean; content gate 4-way consensus (`[self]`/`[sol]`/`[glm]`/`[fable]`).

---

## Plan Review

### Review 1 — [self] (2026-09-06)
APPROVE (after two self-fixes pre-dispatch): (1) added `error-messages` to the practices
amendment — the Lesson-2 off-the-end IndexError beat uses it (the exact substrate miss that
cost plan-008 a round-1 rejection); (2) reworked the while-loop beat from a pending-list
(`.pop` is a BANNED untaught list method) to a `bonus = bonus * 2` multiplier loop that homes
`while-loop` cleanly. Amendment re-validated green (curriculum checks incl. checkpoint-closure).
Design honors: hook-first, cumulative closure (only ≤unit-07), input discipline (executed cells
input-free), rebuild-vs-mutate contrast with unit-06, and the NEW pre-gate concept-scanner
self-check. Verified `practices ∩ introduces` stays empty.

### Review 2 — [glm] (2026-09-06)
REJECT → all findings RESOLVED (revised in place before commit):
1. `[FIXED]` (Blocker) `string-literal` used-but-unlisted — added to the practices amendment
   (independently caught by my AST scanner at the plan stage too).
2. `[FIXED]` (Major) parallel `names`/`scores` arrays break index alignment under `.sort()`
   with no in-budget re-pairing — DATA MODEL constraint now mandates a SINGLE scores list;
   sorted board is ranked by PLACE (`"Place N: <score>"`), `string-methods` homed on a scalar
   champion name, name↔score pairing deferred to dicts (unit 08).
3. `[FIXED]` (Minor) sorted-order assert needed an out-of-budget list copy — now captures
   `champion = max(scores)` BEFORE the sort, asserts `scores[0] == champion`.
4. `[FIXED]` (Nit) `sorted()` allowance contradicted the builtin-functions subset discipline —
   `sorted()` now FORBIDDEN, `.sort()` is the only ranking tool.
- glm affirmed: no over-listing; input discipline consistent; amendment closure otherwise sound
  (all 15 amended items introduced by units 01–06, `practices ∩ introduces` empty). Pacing note
  (Lesson 1 heavy) carried to teacher-notes pacing review.

### Review 3 — [fable] (2026-09-06)
REJECT → all findings RESOLVED:
1. `[FIXED]` (Blocker) `string-literal` used-but-unlisted — same fix as glm #1.
2. `[FIXED]` (Nit) `nested-loops` unguarded latent trap — added an explicit "no nested loops"
   binding constraint (no beat needs one; every loop is single).
3. `[FIXED]` (Nit) `boolean` risk on the already-ranked exercise — pinned `in-operator` as a
   CONDITION never printed/assigned; `boolean` is nonetheless listed for the `reverse=True`
   literal.
4. `[FIXED]` (Nit) Lesson 2 overload + off-narrative while-loop — removing the parallel-names
   beat lightens L2; the while-loop is now leaderboard-native (qualifying threshold doubles
   until it passes the champion).
- fable affirmed: closure of the amended concepts otherwise sound; correctness (1-based board,
  float average, `.sort()` returns None) verified.

### Round 2 revisions (2026-09-06)
Amendment now: requires += `parameters, return-value`; practices += `print, arithmetic,
int-type, range-function, loop-counter, if-statement, elif-else, string-concat, float-type,
type-conversion, input, in-operator, error-messages, string-literal, boolean` (15 added).
Re-validated green (prereq/practice/reference/schema/checkpoint/introduction curriculum checks).

### Review 4 — [sol] (2026-09-06)
REJECT → all findings ALREADY RESOLVED by the round-2 revisions above (sol reviewed the
pre-revision commit):
1. `[FIXED]` (Blocker) `string-literal` — added (sol, glm, fable, and the AST scanner all
   independently caught it).
2. `[FIXED]` (Blocker) `boolean` — added; sol independently caught the `reverse=True` literal,
   confirming the scanner's call.
3. `[FIXED]` (Major) `sorted()` allowance — removed (now FORBIDDEN).
4. `[FIXED]` (Major) unbounded "incidental" slicing allowance — now an unconditional
   prohibition (`scores[:]`/`list(...)`/`.copy()` all out of budget).
5. `[FIXED]` Phase-B blueprint union summary was stale (omitted `error-messages`) — now lists
   error-messages/string-literal/boolean.
- sol nit: teacher-notes ".sort() returns None" is teacher-facing common-mistake framing (warn
  students off `best = scores.sort()`) — kept as-is, teacher-only background.
- sol affirmed: no over-listing; no untaught leaks (`.pop`/`.insert`/`.remove`/`.index`/dicts/
  files/classes/enumerate/zip/comprehensions all absent).

### Round 2 re-review (2026-09-06)
All four round-1 verdicts REJECTed on the SAME convergent core (string-literal + boolean +
sorted() + parallel-array data model); fixes applied exactly as prescribed and re-validated
green. Re-dispatching [glm]/[fable]/[sol] to confirm the revised plan — especially the
single-scores-list data model — closes.

**[fable] round 2: APPROVE WITH NITS.** All round-1 findings affirmed resolved; mapped every
code shape to a listed concept (zero used-but-unlisted); DATA MODEL coherent with zero residual
name↔score pairing; no untaught leak / nested loops; input discipline intact. Non-blocking nits
folded into Phase B authoring: (N1) teacher-notes acknowledge `input` is homed via exercise
prompt only; (N2) lesson prose states the cleaned `winner` name is illustrative of string-methods,
not derived from the leaderboard (true pairing waits for dicts, unit 08).

**[glm] round 2: APPROVE WITH NITS.** All four round-1 findings verified truly resolved; closure
independently re-confirmed (31-concept union, `practices ∩ introduces` empty, no over-listing, no
untaught leak). Three authoring-level nits folded into Phase B: (G1) after any append to a ranked
board — `add_score`, add-my-score, merge-two-boards — RE-SORT (`append` then `.sort(reverse=True)`,
single loop, no copies) so the hall stays ranked; (G2) `"Place N"`/`board_line` implies RANK so
it runs on a SORTED list (L2 post-sort) — L1's pre-sort numbered board is framed as
"position/entry #N", not place/rank; (G3) concurs with fable's input-prose + illustrative-name nits.

**[sol] round 2: APPROVE.** Definitive beat-by-beat used-but-unlisted scan → `used-but-unlisted:
[]`, `listed-but-unhomed: []`. Amendment complete (all 15 practices + 2 requires, incl.
string-literal/boolean, introduced units 01–06); `sorted()` + slicing bans binding; single-list
data model coherent. In-memory prereq/coverage checks PASS (31-concept union).

## Plan Gate — CONSENSUS REACHED (2026-09-06)
- `[self]` APPROVE · `[glm]` APPROVE WITH NITS · `[fable]` APPROVE WITH NITS · `[sol]` APPROVE.
- Round 1 was a convergent 3× REJECT (string-literal/boolean/sorted()/parallel-array data model);
  all fixed in round-2 revisions and confirmed by all reviewers in round 2. No open blockers.
- All round-2 nits are Phase-B authoring specs (re-sort after append; position vs place framing;
  input-prose + illustrative-name acknowledgments) — staged, not plan blockers.
- **Gate PASSED. Proceeding to Phase A (map amendment) → Phase B (content) → Phase C.**

## Content Review

### Review 1 — [self] (2026-09-06)
APPROVE. Traced every exercise + solution: all 18 asserts correct (Ex4 total=2400/avg=800.0;
Ex7 `scores[0]==champion`; Ex9 dup-guard both branches; Challenge2 merged board
`[1500,1310,1200,1050,990,700]`). Closure clean (scoped AST scanner: no used-but-unlisted, no
untaught methods; only `.append`/`.sort`/index/loop/len/max/min). Pedagogy honors all round-2
gate nits: "Entry #N" (unsorted, L1) vs "Place N" (sorted, L2); `.sort()` mutates-in-place with
explicit unit-06 rebuild contrast; `add_score` re-sorts to keep the hall ranked; the scalar
`winner` name flagged as illustrative, not score-linked (dicts → unit 08); `input()` only in
Ex7's prompt, never an executable cell; IndexError traceback beat. ci-local ALL GREEN
(lessons not executed by CI, so the deliberate `scores[len(scores)]` bug cell is safe; solution
logic mirrors the lesson and IS executed with asserts).

### Review 2 — [fable] (2026-09-06)
APPROVE WITH NITS. Blind-solved all 9 exercises + 2 challenges, matched every reference solution;
all asserts correct + non-vacuous; grep-confirmed no untaught construct; no stored outputs / no
executed input(). Nits (to fix in the batch after [sol] returns):
- `[OPEN→pending]` N1: Challenge 2 initial list mismatch — exercises.ipynb states
  `scores = [1200, 990, 1500]` (genuinely unranked, fits "arrival-order"), solutions uses
  `[1500, 1200, 990]` (already descending, undercuts the framing). Align the SOLUTION to the
  statement's `[1200, 990, 1500]` (final assert holds either way — sort is order-invariant).
- `[OPEN→pending]` N2: `.sort()` returns `None` lives only in teacher-notes; add one sentence to
  the L2 lesson body naming the `None` return (hardens the most common list bug).
- Observation (no action): Ex3 is print-only, so no assert is fine.
- Affirmed: hook-first both lessons; Entry #N vs Place N kept rigorously straight; single-list
  model coherent; correctness spot-checks all pass.

### Review 3 — [glm] (2026-09-06)
APPROVE WITH NITS. Executed all three notebooks cell-by-cell, hand-traced every assert/merge/tier.
Closure clean (only taught constructs; the scanned `and`/`or`/`is` tokens are inside f-strings,
not operators). Findings:
- `[OPEN→pending]` F1: same Challenge-2 initial-list mismatch as fable N1 → align solution to
  `[1200, 990, 1500]`.
- `[OPEN→pending]` F2 (IMPORTANT): Ex7 assert `scores[0] == champion` (1500) is WEAK — it passes
  even if the re-sort is forgotten (sample new score 1310 < 1500 stays out of index 0), so it
  can't catch the unit's headline "forgot to re-sort" mistake. Strengthen to
  `assert scores[1] == 1310` (the pattern Ex9 already uses).
- `[WONTFIX]` F3: the L2 membership-guard demo shows only the "already present" branch (valid — it
  demonstrates the guard catching a duplicate); Ex9 exercises both branches. Justified WONTFIX.
- `[WONTFIX]` F4: traceback wording ("leave it unrun" vs "read together") matches the intended
  live flow (teacher runs the bug cell aloud after predictions). Justified WONTFIX.
- Affirmed: no closure/correctness/pedagogy blockers; manifest == map exactly.

### Review 4 — [sol] (2026-09-06)
REJECT (round 1) → blocker FIXED. sol's closure scan clean, all 18 asserts pass, headless-clean,
no input(). Single OPEN blocker: Challenge-2 reference started `[1500, 1200, 990]` vs the
statement's `[1200, 990, 1500]` — the same mismatch fable N1 + glm F1 found. `[FIXED]` — solution
aligned to `[1200, 990, 1500]` (final assert holds; sort is order-invariant over the multiset).

### Batch fix + resolution (2026-09-06)
Applied after all four reviews (sol done executing the notebooks):
- `[FIXED]` Challenge-2 start list → `[1200, 990, 1500]` (fable N1 / glm F1 / sol #1 — unanimous).
- `[FIXED]` Ex7 assert strengthened with `scores[1] == 1310` (glm F2 — the original `scores[0] ==
  champion` passed even with a forgotten re-sort since the sample 1310 < 1500).
- `[FIXED]` L2 lesson now states `.sort()` returns `None` — call it on its own line, never
  `best = scores.sort()` (fable N2).
- `[WONTFIX]` glm F3 (single-branch guard demo — Ex9 covers both) and F4 (traceback wording
  matches intended live flow).
Scanner clean post-fix; ci-local ALL GREEN. Re-dispatched [sol] to confirm its blocker is cleared
(disciplined close for a REJECT).

## Post-Execution Report (2026-09-06)

**Shipped:** `unit-07-high-score-hall` — Book 1's first collections unit (Term 3 unit 2).

**What was built:**
- `lesson.ipynb` (2 lessons, hook-first): L1 builds/indexes/appends/loops a scores list, numbers
  it as "Entry #N" (unsorted), measures with `len`/`max`/`min`, computes a float average; L2 sorts
  in place (with the mutate-vs-rebuild contrast + the `.sort()`→`None` note), ranks by "Place N"
  via a `board_line` helper, `add_score` re-sorts to stay ranked, tier ladder, membership guard,
  a qualifying-threshold `while` loop, and a deliberate IndexError traceback beat.
- `exercises.ipynb`: 9 core + 2 Challenge (stretch-tagged) exercises, empty starter cells, no
  leaked solutions, no executed outputs.
- `solutions.ipynb`: blind (authored from exercises.ipynb only), input-free, 19 non-vacuous
  asserts, executes headless clean.
- `manifest.yaml` (map-equal), `teacher-notes.md` (five headings, per-lesson pacing, 60-min cuts).

**Verification:** `scripts/ci-local.sh` ALL GREEN; AST concept-scanner scoped to unit-07 clean
(zero used-but-unlisted, zero untaught methods) on lesson + solution code.

**Map amendment (Phase A):** unit-07 `requires` += `parameters, return-value`; `practices` += 15
substrate concepts (print/arithmetic/int-type/range-function/loop-counter/if-statement/elif-else/
string-concat/float-type/type-conversion/input/in-operator/error-messages/string-literal/boolean).
Surgical diff (no YAML reflow).

**Gates:**
- Plan-review gate: round-1 convergent 3× REJECT (string-literal/boolean/sorted()/parallel-array
  data model), all fixed in round 2 → consensus ([self] APPROVE, [glm]/[fable] APPROVE WITH NITS,
  [sol] APPROVE).
- Content-review gate: [self] APPROVE, [fable]/[glm] APPROVE WITH NITS, [sol] REJECT→FIXED; all
  [OPEN] findings resolved (Challenge-2 start list, Ex7 assert strengthened, `.sort()`→None note).

**Key design decision:** a SINGLE integer scores list (no parallel names list — it breaks under
`.sort()` with no in-budget re-pairing); name↔score pairing deferred to dictionaries (unit 08).

**Deviations from plan:** none material. Solutions were authored with `## Solution N` headings and
remapped inline to the `## Exercise N` convention (CI requires the mirror). Cell ids were
normalized (codex omitted them).

**Process dividend:** the AST concept-scanner (prototyped during plan 008) caught the
string-literal/boolean closure gaps at the PLAN stage, before authoring — pre-empting the
multi-round used-but-unlisted saga that unit-06 suffered. Now also detects untaught method calls.

**Follow-ups (tracked, non-blocking):** (1) latent practice-completeness hygiene PR for shipped
units 03/04/05 + cp02 + proj01 (string-literal; unit-03 f-string; unit-05 import-statement) +
promote the concept-scanner into `tools/` as an advisory check; (2) plan 010 (unit 08 Word Wizard,
dicts) drafted and its substrate amendment pre-validated green.

## Content Gate — CONSENSUS REACHED (2026-09-06)
- `[self]` APPROVE · `[fable]` APPROVE WITH NITS (fixed) · `[glm]` APPROVE WITH NITS (fixed) ·
  `[sol]` APPROVE (round 2 — round-1 blocker fixed & re-confirmed clean).
- All `[OPEN]` findings resolved; F3/F4 justified WONTFIX. Scanner clean; ci-local ALL GREEN.
- **Gate PASSED. Shipping PR #9.**

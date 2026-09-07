# Plan 009 — Unit 07 High-Score Hall Implementation Plan

**Goal:** Ship `unit-07-high-score-hall` — the first collections unit — where students build an arcade leaderboard: a LIST that remembers every player's score, grows with `append`, is walked with a loop, ranked with `sort`, and summed/measured with built-in functions (`len`/`max`/`min`).

**Architecture:** Standard unit pipeline (plan 004), no new tooling. ONE map amendment lands UP FRONT (the standing plan-002 substrate audit, applied proactively and validated with the new AST concept-scanner from plan 008): unit-07's `requires ∪ practices` omits the foundational substrate its leaderboard content uses. The unit's helper functions take arguments and return values (`parameters`, `return-value` → requires); the display/scoring beats use `print`, `arithmetic` (running total, `place + 1`), `int-type` (scores), `range-function` + `loop-counter` (numbered board), `if-statement`/`elif-else` (tier ranking), `string-concat` + `type-conversion` (`"NAME: " + str(score)`), `float-type` (the average from `/`), `input` (an exercise reads a score), `in-operator` (already-ranked check), and `error-messages` (the Lesson-2 off-the-end IndexError beat) → practices. All taught by units 01–06; verified green in scratch.

**Spec:** `book1/curriculum/coverage-map.yaml` (binding, amended); plan 004 unit conventions; D-001 (hook-first).

## Global Constraints

- All plan-004 unit Global Constraints apply (map-equal manifest, hook-first, exercise ≥6 core
  + ≥2 stretch, solution floors + per-line bans, seed ordering, non-vacuous asserts incl. no
  tautologies, five teacher-notes headings, per-lesson allocation, commit trailers).
- Coverage-map amendment (EXACTLY this, pre-audited + scanner-validated green):
  - append to `unit-07-high-score-hall.requires` — `parameters, return-value`.
  - append to `unit-07-high-score-hall.practices` — `print, arithmetic, int-type,
    range-function, loop-counter, if-statement, elif-else, string-concat, float-type,
    type-conversion, input, in-operator, error-messages`.
  - All introduced by units 01–06; `practices ∩ introduces` stays empty (introduces =
    list-*/builtin-functions, none repeated in practices). Apply surgically (no YAML
    round-trip — it reflows the file). The manifest carries the amended lists.
  - Every amended concept must be HOMED in ≥1 lesson beat or exercise (not padding —
    plan-008 gate round-1 lesson): `print` (show the board), `arithmetic` (`total = total +
    score`, `place + 1`), `int-type` (scores are integer literals), `range-function` +
    `loop-counter` (`for place in range(len(scores))` numbered board), `if-statement`/
    `elif-else` (gold/silver/bronze tiers), `string-concat` + `type-conversion` (`"NAME: " +
    str(score)` label), `float-type` (`average = total / len(scores)`), `input` (an exercise
    reads a score to add), `in-operator` (`if name in names` already-ranked), `parameters` +
    `return-value` (the `add_score`/`board_line` helpers), `error-messages` (read the
    off-the-end IndexError together). Teacher notes name each reappearance.
- **Pre-gate closure self-check (NEW, standing from plan 008):** before dispatching the
  `[sol]` content review, run the AST concept-scanner over the drafted notebooks and confirm
  ZERO used-but-unlisted concepts. This is the mechanical catch for the substrate saga —
  no content review is dispatched until the scanner is clean for unit-07.
- **Lists mechanics (binding):** lists are built with `[...]` literals and grown with
  `.append(x)`; indexed with `scores[0]` / `scores[-1]`; walked with `for score in scores`;
  ranked with `.sort()` (ascending) and `.sort(reverse=True)` (top-first, IN PLACE — name
  the in-place mutation explicitly, contrast with unit-06's rebuild-don't-mutate strings).
  `len`/`max`/`min` are the taught `builtin-functions`; `sorted()` is ALSO allowed
  (builtin-functions) but the unit teaches `.sort()` as the primary tool. No list
  comprehensions, no slicing of lists into new lists beyond incidental, no `enumerate`
  (untaught) — the numbered board uses `for place in range(len(scores))`.
- **No dicts/files/classes** (units 08/09/10). No `enumerate`, no `zip`, no list
  comprehension, no `.insert`/`.remove`/`.pop` (untaught list methods — only `.append` and
  `.sort` are in the introduced set; reviewers check for these explicitly since they would
  slip a concept-ID closure check). No turtle (no assets).
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
type-conversion/input/in-operator):
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
  listed scores; today we rank them and let anyone add one"): `scores.sort()` (low→high) and
  `scores.sort(reverse=True)` (top-first) — mutates the list IN PLACE (contrast unit-06's
  rebuild-don't-mutate). A parallel `names` list cleaned with `name.strip().upper()`
  (string-methods). A helper `def add_score(scores, new_score): scores.append(new_score);
  return scores` (parameters, return-value). A `board_line` helper building `"NAME: " +
  str(score)` (string-concat + type-conversion). Tier ranking with
  `if score >= 1000: ... elif score >= 500: ... else:` → gold/silver/bronze (if-statement,
  comparison, elif-else). An already-ranked guard `if name in names` (in-operator). A
  bonus-multiplier `while` loop — `bonus = 10; while bonus < 1000: bonus = bonus * 2` — homes
  `while-loop` without `input` or any banned list method (no `.pop`). A deliberate bug +
  traceback: `scores[len(scores)]` off-the-end IndexError, read together (error-messages).
- Exercises ≥6 core + ≥2 stretch, each HOMING an amended concept: build-the-board (list-literal
  + append), champion-and-rookie (builtin-functions max/min), numbered-leaderboard (range +
  loop-counter + list-index), team-total-and-average (accumulator + arithmetic + float),
  rank-the-tier (if/elif-else + comparison), tidy-the-names (string-methods), add-my-score
  (input prompt → parameterized solution + append + return), label-the-line (string-concat +
  type-conversion), already-ranked (in-operator); stretch: sort-then-top-three (list-sort +
  list-index), merge-two-boards (append in a loop over a second list).
- Solutions: execute headless, input-free (assigned fixed sample scores/names), non-vacuous
  asserts — a sorted-order assert (`sort(reverse=True)` then `scores[0] == max(original)`), an
  append-grows-length assert (`len` before/after), a tier-boundary assert (score 1000 → gold,
  999 → silver), an average assert on known values. `random.seed(4)` only if any randomness.
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
`.sort` — check for `.insert`/`.remove`/`.pop`/`.index` explicitly since they map to no taught
concept and would slip a mechanical closure check); the leaderboard is buildable and correct
(sort mutates in place, numbered board is 1-based, average is a float); solutions
non-vacuous/complete; grading usable; timing; each lesson opens on the project thread
(hook-first, per D-001); age-appropriate; EACH amended concept is exercised by ≥1 named beat
(especially `input`, `in-operator`, `float-type`, `string-concat` — the padding risks).

**Acceptance criteria:** the unit directory complete; `uv run pytest -q` green; ci-local ALL
GREEN; concept-scanner clean; content gate 4-way consensus (`[self]`/`[sol]`/`[glm]`/`[fable]`).

---

## Plan Review

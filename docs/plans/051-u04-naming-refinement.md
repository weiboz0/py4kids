# Plan 051 — u04 naming refinement (CP-light) + numbered score prompts

**Status:** DRAFT — plan-review gate pending.
**Type:** Post-merge content refinement of `unit-04-quiz-show` (author-directed; not an errata bug).
**Branch:** `feature/plan-051-u04-naming`. **Base:** main @ 2120e56 (plan 050 merged).

## Motivation

Course-author directive after the plan-050 u04 pilot merged:
1. Per-iteration score prompts should name the round via an f-string (`f"Score for round {r}: "`),
   not a generic "Score for this round: ".
2. Variable names should be **less verbose, closer to competitive-programming style** — the author chose the
   **"Light trim"** level (keep short domain nouns; drop verbose suffixes; single-letter loop counters).

Scope decision (author): **all of u04** — lesson + exercises + solutions, statements included, so the unit
stays internally consistent. (NOT the whole Book-1 rollout — plans 052+ inherit the style by example, and
design 003 needs no amendment for this.)

## Hard constraints (self-containedness — unchanged)

u04's taught union is **`while`-only** with the explicit accumulator `total = total + score`. This plan
changes **names and prompt strings only**. It MUST NOT introduce `+=`, `for`/`range`, `sys.stdin`, list, or any
concept outside u04's union — those are not yet taught. Control flow, logic, outputs, asserts' *values*, and
the fixed-data/real-form pairing all stay identical; only identifiers and prompt text change.

## Naming scheme (Light trim)

**Default rule: any identifier NOT in the rename table below is KEPT VERBATIM.** (Complete u04 identifier
inventory was enumerated from all three notebooks + the solutions markdown real-forms; every name has a
disposition.)

**Renamed:**

| Old | New | Note |
|---|---|---|
| `round_number` | `r` | loop counter → single letter from the noun |
| `question_number` | `q` | loop counter → single letter |
| `entry_number` (Ex19 twin) | `i` | loop counter |
| `questions_asked` | `asked` | drop `_number`-style verbosity, keep the verb |
| `n` (real-forms' count) | `rounds` / `answers` / `scores` | the count variable → descriptive plural by context (score-reading loops → `rounds`/`scores`; answer-reading → `answers`). **Author's explicit "Light trim" pick** (preview showed `rounds`); the exercise-statement prose that currently says "how many rounds `n`" / "**any `n`**" is reworded to "how many rounds" / "any number of rounds/answers". |
| `answer_correct` | `correct` | per-item correctness boolean |
| `correct_count` (sole counter — Ex12) | `count` | short domain noun (no `correct` counter co-occurs) |
| `correct_count` / `wrong_count` (dual — Ex13) | `right` / `wrong` | domain pair; avoids clashing with the `correct` boolean in the same cell |
| `answer_1_correct` … `answer_5_correct` (Ex1: 1–3; Ex9: 1–3; Ex12 twin: 1–5) | `c1` … `c5` | `c` = correct; keeps the "was it correct" (boolean) cue and stays distinct from lesson `answer_1`/`answer_2`, which are typed VALUES and are KEPT |
| `first_correct` / `second_correct` (Ex6) | `first` / `second` | drop `_correct` |
| `streak_alive` | `alive` | boolean; no clash with the `streak` **counter** (Ex16) — different cells |
| `sudden_death_score` (L3) | `score` | short domain noun (no other `score` in that cell; `Survived {score}…` text unchanged) |
| `third_answer_message_shown` (Ex4) | `shown` | drop verbosity |

**Kept verbatim** (already short domain nouns / typed values — NOT trimmed, so `_count` names do NOT drift):
`total`, `count`, `score`, `streak` (counter), `strikes`, `budget`, `attempts`, `category`, `eligible`,
`penalty`, `accepted`, `on_streak`, `answer`, `bonus`, `risk_choice`, `entry`, `tipping_total`, `tip_count`,
`tipping_round`, `fitting_total`, `fit_count`, `part_one`, `part_two`, `final_score`, `unlocked`,
`answer_1`/`answer_2` (lesson typed values), `seconds_left`, `last_shown`.

## Prompt f-strings (point 1)

Per-iteration prompts name the **1-based** index:
- **1-based loops** (lesson running-total & count real-forms start `r = 1`, `while r <= rounds`) →
  `f"Score for round {r}: "`.
- **0-based loops** (Ex11 `r = 0` `while r < rounds`; Ex9/Ex12–Ex18 `q = 0`) → `f"Score for round {r + 1}: "`
  / `f"Answer {q + 1} correct? (yes/no) "`. Arithmetic inside f-string braces is already taught **before u04**
  (u03 uses `f"…{shape_number + 1}…"`), so `{r + 1}` is in u04's union — control flow stays unchanged.

Every numbered prompt must therefore display rounds/answers **1..n** (never "round 0"). One-shot prompts
(single reads: "How many rounds? ", "Starting score: ", "Category: ", etc.) keep their plain text.

## Phases

### Phase A — apply to u04 (lesson + exercises + solutions + teacher-notes)
Rename per the scheme across all three notebooks, the exercise **statements** (which name variables), AND
`teacher-notes.md` (line 19 names `questions_asked`), and add the numbered f-string prompts. Keep every cell's
control flow, logic, non-prompt output text, and assert values identical. The executable fixed-data twin and
its markdown/`no-exec` real-form must stay name-for-name parallel (design 003 §6).

### Phase B — verification
- `ast.parse` + piped-run every real-form and executable twin; confirm each still produces the same **result
  line identical modulo `input()` prompt text** (design 003 §6) as its twin — values unchanged, only
  names/prompts differ — AND that numbered prompts display **1..n** (never 0).
- Grep-assert: no `+=`, no `for `/`range(`, no `import sys`, no `.`-string-methods, no `list(`/`[]` collection
  literals introduced anywhere in u04 (AST-level to avoid the "for" -in-prompt-string false positive).
- **Grep-assert: NO old scheme-table name survives anywhere under `book1/units/unit-04-quiz-show/`** (code,
  markdown real-forms, statements, teacher-notes) — catches any missed occurrence.
- `scripts/ci-local.sh` ALL GREEN (exec-lessons runs the twins; exec-solutions runs the asserted cells;
  concept-scan/prereq/coverage stay clean — names don't change the concept set).

## Out of scope
- Any Book-1 unit other than u04; design 003 (no amendment); the rollout.
- Verification phase present (Phase B) — this plan modifies unit content, so it is NOT verification-exempt.

**Renumbering note:** design 003 §7's narrative "first rollout plan (051)" is superseded — this plan 051 is the
u04 naming refinement; the real-input **rollout shifts to plans 052+** (first slice still: one u07–u10 list
unit + a checkpoint mini-pilot). No design-003 edit needed (governance-light; §7 uses SHOULD).

## Plan Review

### Round 1 (2026-09-19) — roster: [self] inline; [sol] codex gpt-5.6-sol; [glm] opencode; [fable] Fable 5.

#### [self] (2026-09-19)
- **Verdict**: APPROVE
- Scoped to u04 only; closure-safe (names + prompt strings only — control flow stays `while` +
  `total = total + score`, no `+=`/`for`/`range`/`sys.stdin`/list/string-methods); Phase B verification named
  (ast.parse + piped-run parity + grep-asserts + ci-local). Scheme is collision-aware (`correct` boolean vs
  `count`/`right`/`wrong` counters; `alive` vs `streak` counter live in different cells) and no new name shadows
  a builtin. Author-directed "Light trim" governs the age-appropriateness call.

#### [sol] (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Numbered-prompt contract undefined for zero-based loops: Ex11 begins `r = 0`, Ex9/Ex12–Ex16 begin
   `q = 0`, so direct `{r}`/`{q}` interpolation displays "round 0"/"Answer 0". Specify one-based display
   `{r + 1}`/`{q + 1}` for zero-based cells (keep `{r}` where the lesson counter starts at 1) and verify the
   exact prompt sequence in Phase B. Priority: Must Fix. (== [glm] #1, escalated to REJECT)

#### [glm] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
1. `[OPEN]` 0-based counters (Ex9, Ex11–Ex18 start at 0) would print "round 0"/"Answer 0"; only lesson loops
   are 1-based. Plan must specify `{r + 1}`/`{q + 1}` for 0-based loops (arithmetic+f-string in-union). Priority: Should Fix.
2. `[OPEN]` Scheme coverage gaps: `entry_number` (Ex19), `answer_1`/`answer_2` (lesson L1), `part_one`/
   `part_two`/`final_score` (lesson L2), `unlocked` (L2), `seconds_left`/`last_shown` (Challenge 2), and `n`
   (real-forms) are neither in the rename table nor a "kept" row; the "count → rounds/answers/scores" row must
   say it renames the real-forms' `n`. Enumerate explicitly. Priority: Should Fix.
3. `[OPEN]` Phase B: phrase parity as "result line identical modulo `input()` prompt text" (design 003 §6). Priority: Nice to Have.
4. `[OPEN]` Note the rollout renumbering: design 003 §7's narrative "051 = first rollout slice" now shifts to 052+. Priority: Nice to Have.
- Confirms: closure clean, renames collision-free, no builtin shadowing, single-letter counters OK under author's Light-trim choice, Phase B present.

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
1. `[OPEN]` 0-based prompts print "round 0"/"Answer 0"; the plan simultaneously forbids control-flow changes.
   Must state the convention (`{r + 1}`, confirming arithmetic-in-f-string is taught, or rebase, or 1-based-only). Priority: Must Fix. (== [sol]#1 / [glm]#1)
2. `[OPEN]` `n` → `rounds`/`answers`/`scores` contradicts CP-style ("`n` IS the CP name"); a plural bound to a
   scalar primes collection confusion; statements name `n`. Recommends keeping `n`. Priority: Should Fix.
3. `[OPEN]` Scope misses `teacher-notes.md:19` (`questions_asked`); add a teacher-notes sweep + a grep-assert
   that no old scheme name survives anywhere under the unit. Priority: Should Fix.
4. `[OPEN]` Scheme table incomplete (`answer_N_correct` is 5 in Ex12, 3 in Ex9/Ex1; `entry_number`,
   `seconds_left`, `unlocked`, `part_one/two`, `final_score`, `last_shown`, lesson `answer_1/2` unlisted). Add a
   default keep-verbatim rule + extend the a-series + settle `entry_number`. Priority: Should Fix.
5. `[OPEN]` Ex1 `a1/a2/a3` (correctness booleans) reads as answer VALUES (lesson uses `answer_1` for the value);
   suggests `c1/c2/c3` / `ok1..`. Priority: Nice to Have.
- Confirms: closure clean, collisions resolved, no builtin shadowing, Phase B named, scope coherent.

### Round 1 — outcome: REJECT (1 of 4, [sol]). Fixed → re-review round 2.

**Round 1 responses (plan revised; no implementation had begun — plan-review precedes implementation):**
- → [FIXED] (Must Fix — [sol]#1/[glm]#1/[fable]#1): added the **Prompt f-strings** section — 1-based loops use
  `{r}`, 0-based use `{r + 1}`/`{q + 1}`; confirmed arithmetic-in-f-string is taught before u04 (u03
  `f"…{shape_number + 1}…"`), so it stays in-union with control flow unchanged; Phase B verifies prompts show 1..n.
- → [FIXED] (Should Fix — [glm]#2/[fable]#4): rewrote the scheme as an explicit **rename table + default
  "keep verbatim" rule** from the full u04 identifier inventory; extended the correctness-boolean series to
  `c1..c5`; settled `entry_number`→`i`; enumerated the kept set.
- → [WONTFIX-`n` / FIXED-prose] ([fable]#2): keep `rounds`/`answers`/`scores` — the **author explicitly
  selected the `rounds` preview**, so that choice governs over the `n` recommendation; mitigated fable's
  concern by rewording the `n`-naming statement prose (enumerated in the table row) so no plural-noun/`n`
  mismatch ships.
- → [FIXED] (Should Fix — [fable]#3): Phase A now includes `teacher-notes.md`; Phase B adds a grep-assert that
  no old scheme name survives anywhere under the unit dir.
- → [FIXED] (Nice — [fable]#5): Ex1/Ex9/Ex12 correctness booleans use `c1..c5` (not `a…`), distinct from the
  lesson's `answer_1/answer_2` typed values.
- → [FIXED] (Nice — [glm]#3): Phase B parity phrased "result line identical modulo `input()` prompt text".
- → [FIXED] (Nice — [glm]#4): added the renumbering note (rollout → 052+).

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

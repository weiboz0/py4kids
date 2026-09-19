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
- **All 0-based loops** (Ex11/Ex14/Ex17/Ex18 use `r = 0`, `while r < …`; Ex9/Ex12/Ex13/Ex15/Ex16 use `q = 0`) →
  `f"Score for round {r + 1}: "` / `f"Answer {q + 1} correct? (yes/no) "`.
- **In-union justification:** u04's `manifest.yaml` `requires` lists **both `f-string` and `arithmetic`**, so
  `{r + 1}` is a composition of two u04-required concepts — control flow stays unchanged. (There is also a
  pre-u04 occurrence of the exact form in u03 solutions, `f"…{shape_number + 1}…"`.) **Sanctioned fallback**
  if a content-gate reviewer objects to arithmetic-in-f-string: precompute `label = r + 1` (plain arithmetic,
  already in-union) then interpolate plain `{label}` — no plan amendment needed.

Every numbered prompt must therefore display rounds/answers **1..n** (never "round 0"). One-shot prompts
(single reads: "How many rounds? ", "Starting score: ", "Category: ", etc.) keep their plain text; the
sentinel loop (Ex19, no counter) keeps "Score (0 to stop): ".

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
- **Assert NO old scheme-table name survives anywhere under `book1/units/unit-04-quiz-show/`** (code, markdown
  real-forms, statements, teacher-notes) — catches any missed occurrence. For `n`, use AST/extracted-source
  matching (a plain word-boundary grep over `.ipynb` JSON false-positives on `\n` escapes).
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

### Round 2 (2026-09-19) — re-review after fix commit 1b33f0a

#### [self] round 2 (2026-09-19)
- **Verdict**: APPROVE — all round-1 findings resolved: prompt convention specified (1-based `{r}`, 0-based
  `{r + 1}`/`{q + 1}`; arithmetic-in-f-string confirmed taught in u03); explicit rename table + default
  keep-verbatim rule from the full inventory; `c1..c5`; teacher-notes sweep + no-old-name grep-assert;
  author-chosen `rounds` kept with prose reworded; renumbering noted. No new blocker.

#### [sol] round 2 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — Must-Fix resolved, no new blocker.
1. `[FIXED]` Nice: parenthetical accuracy — Ex14/Ex17/Ex18 use `r = 0`, Ex9/Ex12/Ex13/Ex15/Ex16 use `q = 0`.

#### [glm] round 2 (2026-09-19)
- **Verdict**: APPROVE WITH NITS
1. `[FIXED]` Should Fix: cite u04's own `requires: [… f-string, arithmetic …]` (manifest.yaml:9-10) for `{r + 1}`
   being in-union (composition of two u04 concepts), not the u03-solutions occurrence. Done below.
2. `[FIXED]` Nice: 0-based parenthetical corrected to "all 0-based counters".

#### [fable] round 2 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all five round-1 findings confirmed resolved.
1. `[FIXED]` Nice: recorded the sanctioned in-union fallback (`label = r + 1` then plain `{label}`) should a
   content-gate reviewer object to arithmetic-in-f-string.
2. `[FIXED]` Nice: Phase B's "no old name survives" check for `n` must use AST/extracted-source (not
   word-boundary grep over `.ipynb` JSON — `\n` false-positives). Phase B updated.

### Round 2 — outcome: CONSENSUS — [self] APPROVE; [sol]/[glm]/[fable] APPROVE WITH NITS (all folded). **PLAN-REVIEW GATE CLOSED.**

## Content Review

### Round 1 — Phase A rename (2026-09-19, commit 09d8708)
Roster: [self] inline; [sol] codex gpt-5.6-sol; [glm] opencode; [fable] Fable 5 — all read-only.

#### [self] (2026-09-19)
- **Verdict**: APPROVE
- Verified: (a) CORRECTNESS — all 19 solutions markdown real-forms + 3 lesson `no-exec` forms + all executable
  twins keep their pre-rename result lines (Ex11→"Total score: 40", Ex12→"Correct answers: 3", Ex13→"Correct:
  3, wrong: 2", Ex17→"Fitting total: 10; scores added: 2", Ex18 tipping line, lesson RT→16 / count→2, etc.);
  asserts pass (ci-local exec-solutions). (b) NUMBERED PROMPTS display 1..n, never 0 (0-based → `{r + 1}`/
  `{q + 1}`, 1-based lesson → `{r}`); arithmetic-in-f-string in-union (u04 requires f-string + arithmetic).
  (c) CLOSURE AST-clean: no `+=`/`for`/`range`/`len`/`sum`/`list`/string-methods/`import sys` introduced.
  (d) CONSISTENCY: NO old scheme name survives anywhere under the unit dir (incl. the caught Ex6 solution-note
  prose `questions_asked`→`asked`); statements + teacher-notes updated. (e) nbformat valid; ci-local ALL GREEN.

#### [sol] (2026-09-19)
- **Verdict**: REJECT
1. `[FIXED]` Real-program notes say "works for any `n`" while code uses `rounds`/`answers` — retired scheme
   name referring to no variable, solutions.ipynb cells 35 (`a9459a59f915`) & 38 (`d4915f59d3c9`). Priority:
   Must Fix. → Response: reworded to "works for any number of rounds"/"…answers" (same fix [glm]#1/[fable]#1
   requested); verified no `` `n` `` prose ref remains anywhere in u04. Re-dispatched [sol] round 2 to confirm.

### Round 1 — outcome: REJECT (1 of 4, [sol]); all four converged on the single caption nit. Fixed → [sol] round 2.

#### [glm] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
- Verified (no findings beyond #1): blind-solved Ex9/11/13/16/17/18 matched; all real-forms + twins produce
  byte-identical output pre/post (result lines unchanged, asserts pass); prompts 1..n never 0; AST clean;
  no old multi-char scheme name survives; statements + teacher-notes match.
1. `[FIXED]` Stale `n` in the Ex11 (cell 35) and Ex12 (cell 38) real-form CAPTIONS ("works for any `n`") — the
   code + statements were reworded but these two captions were missed. Priority: Should Fix. → Response: reworded
   to "works for any number of rounds" / "…answers"; confirmed no `` `n` `` prose ref remains anywhere in the unit.

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
- Verified (diffed old-vs-new stdout at 09d8708~1 vs 09d8708): all 22 real-forms + twins + 3 lesson no-exec
  byte-identical result lines; numbered prompts 1..n never 0 (in-union confirmed: manifest requires f-string +
  arithmetic, u03 precedent); AST closure clean; no old scheme name survives; statements + teacher-notes:19
  (`asked`) match; `c1..c5` distinct from lesson `answer_1/2` values. (Out-of-scope note: checkpoint-02 still
  uses old names — correctly a 051+ follow-up, u04-only plan.)
1. `[FIXED]` Same as [glm]#1 — Ex11/Ex12 real-form captions "works for any `n`". → Response: reworded (above).

### Round 2 — [sol] re-review after caption fix (commit e6c6183)
#### [sol] round 2 (2026-09-19)
- **Verdict**: APPROVE — Must-Fix caption resolved; no `n`/old scheme name survives; no new blocker.

### Round 2 — outcome: CONSENSUS — [self] APPROVE; [sol] APPROVE (R2); [glm]/[fable] APPROVE WITH NITS (sole
caption nit FIXED). **CONTENT GATE CLOSED.** No open findings.

## Post-Execution Report

**Status: COMPLETE — plan 051 (u04 CP-light rename + numbered score prompts). 2026-09-19.**

### What shipped
Author-directed post-merge refinement of `unit-04-quiz-show` (the plan-050 real-input pilot). Two changes,
**names + prompt strings only** — control flow unchanged (`while` + `total = total + score`; no `+=`, `for`,
`range`, `sys.stdin`, list, or string methods introduced):
1. **Light-trim variable names** across lesson + exercises + solutions + teacher-notes: `round_number`→`r`,
   `question_number`→`q`, `entry_number`→`i`, `questions_asked`→`asked`, `answer_correct`→`correct`,
   `correct_count`→`count` (Ex12) / `right`+`wrong` (Ex13), `answer_N_correct`→`c1..c5`, `streak_alive`→`alive`,
   `sudden_death_score`→`score`, `first_correct`/`second_correct`→`first`/`second`,
   `third_answer_message_shown`→`shown`, and the real-forms' count `n`→`rounds`/`answers`/`scores` (author's
   explicit Light-trim pick; the `n` statement/caption prose reworded to "any number of rounds/answers").
   Default rule: every other identifier kept verbatim.
2. **Numbered per-iteration prompts:** 1-based lesson loops → `f"Score for round {r}: "`; 0-based exercise
   loops → `f"Score for round {r + 1}: "` / `f"Answer {q + 1} correct? (yes/no) "` (arithmetic-in-f-string is
   in-union: u04 `requires` f-string + arithmetic, u03 precedent). Prompts display 1..n, never 0.

### Verification
- Behavior-preserving: all 19 solutions markdown real-forms + 3 lesson `no-exec` forms + 2 lesson executable
  twins + every asserted twin produce byte-identical result lines pre/post rename (validated ast.parse +
  piped-run; independently diffed old-vs-new by [fable]). Numbered prompts confirmed 1..n.
- AST closure scan clean; no old scheme-table name survives anywhere under the unit dir (incl. the caught Ex6
  solution-note prose and the Ex11/Ex12 real-form captions).
- `scripts/ci-local.sh` ALL GREEN; `pre-merge-guard` OK.
- **Content gate: 4-way, 2 rounds → CONSENSUS.** R1: [sol] REJECT + [glm]/[fable] APPROVE-WITH-NITS — all four
  converged on ONE nit (the "any `n`" captions). R2 after fix: all APPROVE / APPROVE-WITH-NITS.

### Scope / follow-ups
- u04 only (author's scope choice); no design-003 amendment. Renumbering: design 003 §7's narrative "051 =
  first rollout slice" shifts to **plans 052+**.
- Noted for 052+ (out of scope here): `checkpoint-02-loops-and-functions` still uses the old verbose names;
  align it when the real-input rollout reaches checkpoints. The real-input rollout itself (u07–u10 list unit +
  checkpoint mini-pilot, `input` adds for u03/u05/u08/u09) remains as plan 050 left it.

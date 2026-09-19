# Plan 052 — u07 high-score-hall: full real-input treatment (rollout slice 1, list arm)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the full u04 end-state treatment to `unit-07-high-score-hall`.
**Branch:** `feature/plan-052-u07-real-input`. **Base:** main @ 741bde7.

## Motivation

Roll out the treatment u04 now carries (plans 050 + 051) to the rest of Book 1, author-directed, in the
design-003 §7 order. **u07 is slice 1** — the first LIST unit — chosen to exercise the untested list arm
(realistic fixed lists + the "read into a list" real-form idiom + list-vs-count naming). Authorities:
`docs/designs/003-book1-real-input.md` (real-input norm) and plan 051 (CP-light naming + numbered prompts).

## The treatment (the full u04 package, adapted for u07)

1. **Real-input hybrid forms** (design 003): every complete lesson task (put-it-together / Algorithm-Extension
   home) and every non-exempt exercise keeps its EXECUTABLE fixed-data form AND gains one `input()`-reading
   "real program" form — a `no-exec` `input()` CODE cell (+ `**Notice:**`) in `lesson.ipynb`; a MARKDOWN fenced
   ```python block``` in `solutions.ipynb` (input() banned in solutions code cells). Every non-exempt
   fixed-data exercise statement also gains a one-line `**Real version:**` cue (as u04 did); exempt exercises
   carry a one-line note saying why. u07 already has `input` in its concept union → **no metadata change**.
2. **Realistic data — grow only the small CORE lists to ≥4 (design 003 §3 v2 floor).** §3 v2: binding
   requirement is "data not *toy*"; ≈6–8 is the target for fresh lists; already-realistic (≥4) lists need not
   grow; build-up rungs + explicitly-framed "small fixed data" enrichment drills keep their small lists. Apply
   to u07:
   - **Lesson core lists are already realistic** (`[1200,850,990,1500]`, `[1500,1310,1200,990,850]`, …, ≥4) —
     unchanged.
   - **Enrichment drills stay small** (§3 v2 exemption): Algorithm-Extension Spotlights (`names=["Ada","Bo","Cy"]`,
     `scores=[3,9,5,7]`) + Ex10–22 drills (lesson 63 / ex 21 / sol 19 "small fixed data" framing) — unchanged.
   - **Grow the <4-element CORE exercise lists to ≥4** (core = Ex1–9 + Challenges, not enrichment/rungs):
     **Ex1** `[700,1250,980]`, **Ex7** & **Ex8** `[900,450,1200]`, **Challenge 2** `scores=[1200,990,1500]` +
     `second_scores=[1310,700,1050]` → each grown to ≥4 realistic scores, with **lockstep re-derivation** of that
     exercise's asserts + statement worked-example values + any teacher-notes number (Phase B drift check). The
     `≥4` test is per **working list** (Ex7 reaches 5 after its append; Ch2 merges to ≥8) — the executable
     source literal itself is grown to ≥4 so **no core fixed SOURCE/input dataset ships fewer than 4 values**.
     (Result-literal asserts may still be <4 — e.g. Ex9's `assert bonus_board == [300,450,275]` is fine because
     its *source* `waiting_scores` is 4-element; §3 governs source/input data, not computed results.)
3. **CP-light names (Light trim) — full u07 inventory.** "Untouched rungs" means data/pedagogy; **renames apply
   unit-wide** (incl. rung cells). u07's names are already clean and often meaningfully **paired**, so the trim
   is genuinely light:

   | Old | New | Note |
   |---|---|---|
   | `best_so_far` | `best` | drop verbose suffix (lesson rung 18 + wherever it appears) |
   | `position` | `i` | generic list-index loop counter; `i` is already u07's index elsewhere (lesson 69/71) — makes indices consistent. **Rename ONLY the identifier, never the English word "position(s)" (concept-prose in lesson 8/10/12/30/62, Ex15 statement, tn 6/70/78 must stay).** Identifier sites — CODE: lesson 27/29, sol 6/14, sol 31/35 (Ex15/Ex17 `for position in range`), while-index sol 18; MARKDOWN: Ex3/Ex7/Ex9 statement backticks (`` `position` ``, `scores[position]`, `position + 1`, `position = 0`), lesson Notice 28, teacher-notes 73–74. |

   **Kept verbatim** (domain-meaningful or paired — trimming would lose meaning or collide): `place` (a
   *ranking* term passed to `board_line`, not a generic index), `score`/`scores`/`names`/`board`/`kept`, the
   `_name`/`_score` pairs (`best_name`/`best_score`, `rookie_name`/`rookie_score`), the `raw_`/`clean_` pairs,
   the `_count`/`_total` pairs (`passer_`, `fit_`, `tip_`, `strict_`, `gold_count`), value-loop vars
   (`one_score`, `s`), and all other names (`champion`, `rookie`, `worst`, `average`, `budget`, `wait`,
   `my_score`, `new_score`, `player_name`, `threshold`, `midpoint`, `tier(s)`, …). **Default: any name not in
   the rename table is kept verbatim.** No new name shadows a builtin (`n`/`i`/`best` are clear).

   **Two-regime naming rule (rollout-wide, record for u08/u09/u10/checkpoint slices + a one-line teacher-notes
   remark):** *pre-list units* (u04) use the plural noun for the COUNT (there is no list); *list units (u07+)*
   use the plural noun for the LIST, with count `n` and index `i`. Students meet both conventions across u04→u07;
   the teacher-notes remark names this.
4. **Numbered per-iteration prompts** (plan 051): `f"Score {i + 1}: "` / `f"Name {i + 1}: "`, 1-based, never
   index 0. In-union: u07 `requires`/`practices` f-string + arithmetic, and lesson cell 29 **already** uses the
   exact idiom `f"…{position + 1}…"` (→ `{i + 1}` after rename). Fallback if ever contested: precompute
   `label = i + 1` then plain `{label}` (plan-051 precedent).

## Per-exercise real-form SHAPE table

| Shape | Exercises | Real-form |
|---|---|---|
| **read-into-list** | Ex1, Ex2, Ex5, Ex9, Ex10, Ex11, Ex12 (names), Ex13, Ex14, Ex16, Ex18, Ex19, Ex20, Ex21, Ex22, Challenge 1 | `n = int(input("How many scores? "))` + `for i in range(n):` reading one value per pass into the list (two-line append, below), then the unchanged body |
| **read-into-parallel-lists** | Ex15 (Champion by name), Ex17 (Rookie by name) | ONE `for i in range(n)` loop reading BOTH per pass: `names.append(input(f"Name {i + 1}: "))` then `scores.append(int(input(f"Score {i + 1}: ")))` — never two loops / `zip` |
| **read-into-list (one of two lists)** | Challenge 2 (merge two boards) | keep the first board FIXED; read `second_scores` with the `n`/`i` prologue, then the unchanged merge — preserves the "one loop to merge" goal |
| **single-read** (already `no-exec` interactive, reads ONE value) | Ex4 (add my score), Ex6 (guard one score), Ex7 (name + one score, append to fixed board) | statement is already the real program; real-form mirrors it with one/two `input(...)` reads, no list prologue and no `**Real version:**` cue |
| **exempt** (debug/predict — input would defeat it) | Ex3 (Read an IndexError / predict), Ex8 (Why did `best` become `None`) | NO real-form; statement carries a one-line note ("a trace/debug exercise — fixed data on purpose, no input version") |

Lesson: L1/L2/L3 put-it-togethers get read-into-list `no-exec` forms; the **find-extreme** Algorithm-Extension
home reads parallel `names`+`scores` in one loop; the **filter-into-list** home reads scores into a list.

## Real-form idiom (two-line append; read into a list)

Match u07's own append ladder (which appends a value held in a variable) — use the **two-line** form, not a
3-deep nested call:

```python
n = int(input("How many scores? "))
scores = []
for i in range(n):
    score = int(input(f"Score {i + 1}: "))
    scores.append(score)
# ...unchanged list logic below...
```

Everything is in u07's union (`for`/`range`/`loop-counter`, `input`, `int` [never_flag], `list-literal`/
`list-append`, `f-string`+`arithmetic`). The executable twin keeps its FIXED list; the real-form swaps the
literal list for this prologue and is otherwise line-for-line identical (design 003 §6). No `sys.stdin`.

## Per-notebook-kind forms (CI-forced, design 003 §2)

- **lesson.ipynb:** real-form = `no-exec` `input()` CODE cell + `**Notice:**` (concept-scan sees input() — u07
  already has it, no add). Executable fixed-data ladder unchanged.
- **solutions.ipynb:** real-form = markdown fenced ```python``` block after the executable asserted cell; the
  asserted fixed-data reference solution (≥3 non-vacuous assert cells/nb) stays the validated logic. A fenced
  block must not contain a line starting `## Exercise <digit>`.

## Phases

### Phase A — apply to u07 (lesson + exercises + solutions + teacher-notes)
Add real-input forms per the SHAPE table (lesson put-it-togethers + Algorithm-Extension homes as `no-exec`
cells; solutions markdown real-forms); add `**Real version:**` cues to non-exempt fixed-data exercise
statements + exempt notes to Ex3/Ex8; apply the two renames unit-wide (`best_so_far`→`best`, `position`→`i`);
add numbered prompts. Sweep `teacher-notes.md` for the renamed identifier. **Grow the <4-element CORE lists**
(Ex1, Ex7, Ex8, Challenge 2) **to ≥4** realistic scores, re-deriving that exercise's asserts + statement
worked-examples + teacher-notes numbers in lockstep. Markers + Algorithm-Extension "small fixed data" framing +
build-up rungs + all **already-≥4 and enrichment** lists untouched.

### Phase B — verification
- `ast.parse` + piped-run every real-form + executable twin; each real-form's RESULT line equals its
  fixed-data twin's output **modulo `input()` prompt text**; numbered prompts display 1..n never 0.
- **Drift check (for the grown cells Ex1/Ex7/Ex8/Ch2):** statement worked-example values == solution assert
  values == real-form piped output == teacher-notes numbers, all re-derived from the new lists. **Ex8 is
  real-form-exempt (debug/predict) — statement/asserts/teacher-notes legs only, no piped-output leg.** For
  unchanged cells, confirm the real-forms reproduce the existing twin values; no `**Real version:**` cue names
  a changed value.
- AST-level closure scan: no concept outside u07's union introduced (no `sys.stdin`; no new builtin/idiom).
- Assert NO old **identifier** (`best_so_far`; `position` as a code Name / backticked `` `position` `` /
  `scores[position]` / `position + 1` / `position = 0`) survives under the unit dir — code via AST, markdown via
  a grep for those identifier patterns. **The English word "position(s)" in concept-prose is NOT matched** (it
  stays; only the variable is renamed).
- `scripts/ci-local.sh` ALL GREEN (exec-lessons runs ladders/twins; exec-solutions runs asserted cells;
  concept-scan/prereq/coverage/pattern-marker/technique-spiral stay clean).

## Out of scope
- Any Book-1 entry other than u07. **Checkpoint-mini-pilot deferral:** design 003 §7 *SHOULD*-paired the first
  slice with a checkpoint mini-pilot; this plan does u07 alone and the checkpoint follows as plan 053 (author
  scope choice — smaller slices; SHOULD ≠ MUST; the 051 renumbering note already shifted the rollout to 052+).
- Growth is limited to the <4-element CORE source lists (treatment §2: Ex1/Ex7/Ex8/Ch2); already-≥4 core lists,
  enrichment drills, and build-up rungs are unchanged. **design 003 §3 amended to v2** (this plan) to codify the
  realistic-data policy — that amendment IS in scope; no other design change. Markers/rungs untouched. Phase B present.

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-19)
- **Verdict**: APPROVE
- Scoped to u07; closure-safe (read-into-list idiom `for i in range(n): scores.append(int(input(...)))` is
  entirely in u07's union — for/range/input/int/list-append all present); list-unit naming rule (plural=list,
  count=`n`, index=`i`) is the natural non-confusing mapping and resolves the plan-051 plural/scalar concern
  for the list arm; numbered prompts 1..n with arithmetic-in-f-string in-union; realistic-data limited to
  culminating cells (build-up rungs untouched); Phase B verification named. No new name shadows a builtin.

#### [sol] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
1. `[OPEN]` Should Fix: state how all 22 exercises + 2 Challenges get `**Real version:**` cues (fixed-data
   statements) or justified exemptions — coverage must be unambiguous.

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS
1. `[OPEN]` Should Fix: rename map ambiguity — resolve `place` (loop-index vs ranking term) vs `position`;
   name the main index; state "rungs untouched = data/pedagogy, renames apply unit-wide"; give value-loop
   vars + `_count`/`_total` pairs a keep disposition.
2. `[OPEN]` Should Fix: scope toy-list growth to CULMINATING instances only (not shared-ladder rungs); add a
   value-citing-PROSE sweep wherever data grows (the class the 051 gate caught — stale captions).
3. `[OPEN]` Nice: state the parallel-lists real-form reads both lists in ONE `for i in range(n)` loop.
4. `[OPEN]` Nice: record the design-003 §7 checkpoint-mini-pilot deferral as an author scope choice.
- Confirms: closure clean; naming rule sound + no builtin shadow; prompts 1..n; Phase B present (no REJECT).

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
1. `[OPEN]` Must Fix: no rename table / identifier inventory (plan 051 had one); u07 has many ambiguous-disposition
   names (`position`, `best_name`/`best_score`, `passer_count`/`passer_total`, `raw_name`/`clean_name`, …).
   Add renamed + kept-verbatim table + the statement rewordings it forces (Ex3/5/7/9/15/17).
2. `[OPEN]` Should Fix: add a per-exercise real-form SHAPE table — read-into-list / single-read (Ex4/6/7 already
   interactive, read ONE score) / exempt (Ex3 predict, Ex8 None-debug).
3. `[OPEN]` Should Fix: "culminating cells" undefined + collides with the "small fixed data" Algorithm-Extension
   header (lesson 63 / ex 21 / sol 19) and Ex10–22 drills' locked worked-example/assert/teacher-notes values.
   Define which cells grow; re-derive asserts + worked-examples + Notices + teacher-notes in lockstep.
4. `[OPEN]` Should Fix: find-extreme Spotlight (lesson 65–71) shares one list across rungs — grow uniformly
   (rewrite Notices) or leave; "grow only final rung" breaks continuity.
5. `[OPEN]` Should Fix: record the two-regime naming rule (pre-list units plural=count [u04]; list units u07+
   plural=list, count=`n`) for the u08/u09/u10/checkpoint slices + a one-line teacher-notes remark.
6. `[OPEN]` Nice: parallel-list real-forms (names+scores) must read BOTH per iteration in ONE loop.
7. `[OPEN]` Nice: prefer two-line append (`score = int(input(...))` / `scores.append(score)`) over the 3-deep
   nested call, to match u07's own append ladder.
8. `[OPEN]` Nice: cite lesson cell 29 (`f"...{position + 1}..."`) — the exact arithmetic-in-f-string idiom is
   already taught IN u07.
9. `[OPEN]` Should Fix: Phase B must add a drift check — statement worked-examples == solution asserts ==
   real-form piped output == teacher-notes numbers.
- Confirms: Phase B present (not REJECTable); scope clean; naming rule sound + no builtin shadow; closure passes.

### Round 1 — outcome: 4× APPROVE / APPROVE WITH NITS (no REJECT). Plan revised to fold all findings.

**Round 1 responses (plan revised in place; no implementation had begun):**
- → [FIXED] (fable#1 Must / glm#1): added the **rename table** (only `best_so_far`→`best`, `position`→`i`) +
  explicit **kept-verbatim inventory** (paired `_name`/`_score`, `_count`/`_total`, value-loop vars, `place`
  kept as a ranking term) + default keep rule; stated "rungs untouched = data/pedagogy; renames apply unit-wide".
- → [FIXED] (fable#2 / sol#1): added the **per-exercise real-form SHAPE table** (read-into-list /
  read-into-parallel-lists / single-read Ex4·Ex6 / exempt Ex3·Ex8) + `**Real version:**` cues on non-exempt
  fixed-data statements + exempt notes.
- → [FIXED] (fable#3/#4 / glm#2): **NO data growth for u07** — core data already realistic; the toy lists are
  deliberate "small fixed data" drills; growing forces the lockstep/prose-drift cascade for no gain. Removes the
  hazard entirely (no Notice/assert/worked-example/teacher-notes/prose re-derivation needed).
- → [FIXED] (fable#6 / glm#3): parallel-lists real-form reads BOTH lists in ONE `for i in range(n)` loop.
- → [FIXED] (fable#7): two-line append form (`score = int(input(...))` / `scores.append(score)`), matching u07's ladder.
- → [FIXED] (fable#5): two-regime naming rule recorded (pre-list plural=count; list units plural=list, count=`n`)
  + a one-line teacher-notes remark planned.
- → [FIXED] (fable#8 / glm confirms): cite lesson cell 29's `f"…{position + 1}…"` as the in-unit precedent.
- → [FIXED] (fable#9): Phase B drift check retained but simplified (data unchanged → confirm real-forms
  reproduce existing twin values; no cue names a changed value).
- → [FIXED] (glm#4): checkpoint-mini-pilot deferral recorded as an author scope choice in Out of scope.

Re-dispatching round 2 (plan materially expanded).

### Round 2 (2026-09-19) — re-review after revision 0dcae2d

#### [self] round 2 (2026-09-19)
- **Verdict**: APPROVE — rename table + kept-verbatim inventory added; per-exercise SHAPE table covers all
  22 + 2 (read-into-list / parallel Ex15·Ex17 / single-read Ex4·Ex6 / exempt Ex3·Ex8); NO data growth (core
  already realistic, drills deliberately small) removes the lockstep/prose cascade; parallel one-loop + two-line
  append + cite cell 29 + two-regime naming recorded; Phase B drift check retained. No new blocker.

### Round 3 (2026-09-19) — re-review after design-003 §3 v2 amendment (8066682)
#### [self] round 3 (2026-09-19)
- **Verdict**: APPROVE — design 003 §3 v2 makes u07's no-growth consistent with the governing design ([sol]#1
  resolved); Phase B markdown grep + rename markdown scope ([glm]#1/[fable]#2), Ex7 single-read ([fable]#1),
  Ch2 second_scores ([fable]#3) all folded. No new blocker.
#### [sol] round 3 (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: §3 v2 exempts only build-up rungs + explicitly-framed "small fixed data" enrichment, but
   **Ex8 is core practice** (not enrichment/rung) with a 3-element list `[900,450,1200]` — blanket no-growth is
   still inconsistent. Grow the small CORE lists to ≥4 (or narrowly reframe without weakening the rule).
   → Response (round 4): grow the <4-element CORE lists (Ex1 `[700,1250,980]`, Ex7/Ex8 `[900,450,1200]`, Ch2's
   two 3-lists) to ≥4 realistic scores with lockstep assert/worked-example re-derivation; enrichment Ex10–13 +
   Spotlight rungs stay small (§3 v2 exemption). `[FIXED — pending round 4]`

#### [glm] round 3 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — confirms §3 v2 sound + narrowly scoped; verified lesson core lists are
  realistic 4-value. Nits (== fable R3): 1. identifier-scope the markdown sweep (don't rename English
  "position(s)" prose); 2. rename row missing sol 31/35; 3. header v1→v2.

#### [fable] round 3 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — round-2 nits resolved; design 003 §3 v2 "sound and not over-broad".
1. `[OPEN]` Should Fix: `position`→`i` and the Phase-B "no old name" assert must be **identifier-scoped** — the
   English word "position(s)" is prose in many cells (lesson 8/10/12/28/30/60/62, Ex15 statement, teacher-notes
   6/70/78) and must NOT be renamed / must not fail the grep. Rename only backticked `` `position` ``,
   `scores[position]`, `position + 1`, `position = 0`, and code Names. Drop teacher-notes:78 (prose "same
   position") from the rename row; add solutions cells 31/35 (Ex15/Ex17 `for position in range`).
2. `[OPEN]` Nice: §3 v2's "≥4 real values" is per-UNIT, not per-cell (Ex7 → 4 after append, Ch2 → 6 merged);
   state so a content reviewer doesn't re-litigate those cells.
3. `[OPEN]` Nice: bump design 003 header Status `v1`→`v2` (changelog already records v2).

### Round 3 — outcome: REJECT (1 of 4, [sol] — core <4 lists). Fixed → round 4.
**Round 3 responses:** [sol]#1 [FIXED r4] grow core <4 lists Ex1/Ex7/Ex8/Ch2 to ≥4 (lockstep re-derivation;
enrichment/rungs exempt). [fable]#1 / [glm]#1 [FIXED] identifier-scoped rename + Phase-B sweep (English
"position(s)" prose untouched). [fable]#2 [FIXED] `≥4` clarified per working-list. [fable]#3 / [glm]#3 [FIXED]
design 003 header → v2. rename row: dropped tn:78 (prose), added sol 31/35. Re-dispatching round 4.

---

#### [sol] round 2 (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: "NO GROWTH" contradicts design 003 §3's explicit ≈6–8-element requirement for u07–u10
   while claiming no design amendment — either conform the exercise data OR amend the governing design.
   → Response: **amended design 003 §3 → v2** (binding requirement = "not toy"; ≈6–8 is the target for
   fresh lists; already-realistic units need not grow; drills keep small data). u07's no-growth now CONFORMS
   to amended §3 (its lists are already realistic ≥4-value; drills protected). `[FIXED]`

#### [glm] round 2 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — confirms no-growth "an acceptable, well-reasoned deviation"; SHAPE table
  complete; rename table resolves the ambiguity.
1. `[OPEN]` Nice: Phase B's no-old-name assert is AST/code-only, but `position` appears in markdown (Ex9
   statement backticks, teacher-notes 73–74/78) — add a plain-text sweep over the unit dir. → Response:
   Phase B now greps `.ipynb` (code+markdown) + `.md`; rename row lists the markdown sites. `[FIXED]`

#### [fable] round 2 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all 9 round-1 findings resolved (Ex3/Ex8 confirmed the only exemptions;
  no-growth accepted for u07 as a sound §3 reading; rename table, SHAPE table, parallel one-loop, two-line
  append, cell-29 cite, two-regime rule all present). New nits:
1. `[OPEN]` Should Fix: Ex7 is already `no-exec` interactive (reads a name + ONE score) → move it to the
   **single-read** row (not read-into-list); no list prologue / `**Real version:**` cue.
2. `[OPEN]` Should Fix: `position`→`i` also reaches STATEMENT markdown + teacher-notes (Ex3/Ex7/Ex9 statements,
   lesson Notice 28, teacher-notes 73–74); add these to the rename scope and make Phase B's "no old name" sweep
   a plain-text grep over `.ipynb` markdown + `.md` (AST can't see markdown).
3. `[OPEN]` Nice: Challenge 2 (two lists) — real-form reads `second_scores` with `n`/`i`, keeps the first board
   fixed (preserves the "one loop to merge" goal).
4. `[OPEN]` Nice: record one explicit sentence that u07 waives §3's "≈6–8 elements, ties where apt" target by
   author choice (signals u08/u09/u10 whether the target applies rollout-wide).

**Round 2 responses:** all folded — [sol]#1 [FIXED] via **design 003 §3 → v2** amendment (u07 no-growth now
conforms); [glm]#1 [FIXED] Phase B plain-text markdown+md grep; [fable]#1 [FIXED] Ex7 → single-read; [fable]#2
[FIXED] `position`→`i` markdown scope + Phase B grep (== [glm]#1); [fable]#3 [FIXED] Challenge 2 reads
`second_scores` (first board fixed); [fable]#4 [FIXED] subsumed by the §3 amendment (u07 conforms; the target
still applies rollout-wide to fresh lists). **Design 003 §3 amended → round 3 re-review (design changed).**

### Round 4 (2026-09-19) — re-review after core-list growth + identifier-scoping (2a904bd)
#### [self] round 4 (2026-09-19)
- **Verdict**: APPROVE — every core (Ex1–9 + Challenges) executable list is now ≥4 (grown Ex1/Ex7/Ex8/Ch2;
  lesson core already ≥4); enrichment/rungs stay small per §3 v2 → fully consistent with the governing design.
  Rename + Phase-B sweep identifier-scoped (English "position(s)" prose preserved); header v2. No new blocker.
#### [sol] round 4 (2026-09-19)
- **Verdict**: REJECT — substance (core-list growth) ACCEPTED; REJECT is on stale scope text only.
1. `[OPEN]` Must Fix: stale "No data growth"/"u07's no-growth conforms" text (Out-of-scope) + design v2
   changelog "Codifies u07's no-growth" contradict the revised treatment §2/Phase A that now grows. Remove/update.
   → [FIXED]: Out-of-scope now "growth limited to <4 core source lists"; design v2 changelog rewritten; no stale text.
2. `[OPEN]` Should Fix: narrow "no cell ships a 3-element core list" — Ex9's `assert bonus_board == [300,450,275]`
   is a 3-element RESULT literal (fine; its source is 4-element). → [FIXED]: reworded to "no core fixed
   SOURCE/input dataset < 4 values; result literals may be smaller".

#### [glm] round 4 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — round-3 nits verified resolved; core-list growth sound (closed set, lockstep
  + scoped drift check, no prose-drift return); [sol]'s Must-Fix (Ex8 core, 3-element) addressed.
1. `[OPEN]` Nice: Phase B drift chain names "real-form piped output" for all grown cells, but Ex8 is
   SHAPE-exempt (no real form) — add "(Ex8: statement/asserts/teacher-notes legs only)". → [FIXED].

#### [fable] round 4 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all round-3 nits resolved; verified the growth is bounded (grown literals
  occur only in their own statement+solution cells; no lesson/teacher-notes collision) so no cascade. Two Nice
  implementation cautions (honor at build time):
1. `[OPEN]` Nice: Ex8 solution has `[900,450,1200]` TWICE (reset step) — grow both literals identically.
2. `[OPEN]` Nice: value choices — avoid `1100` in Ex1 + cross-board duplicates in Ch2 (ties weaken the sort
   demo); re-derive Ch2's `assert len(...)` to the new merged length (8 if both grown to 4).

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

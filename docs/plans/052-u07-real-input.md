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
2. **Realistic data — NO GROWTH for u07 (deliberate).** design 003 §3 targets toy data (`n=3`, 2-element
   lists). u07's core lesson/exercises already use realistic score values (1200, 1500, …) in ≥4-element lists,
   and the only genuinely-small lists (`names=["Ada","Bo","Cy"]`, `scores=[3,9,5,7]`) live in the
   Algorithm-Extension Spotlights + Ex10–22, which are **explicitly framed as "small fixed data" enrichment
   drills** (lesson 63 / ex 21 / sol 19 headers) with locked worked-example values, asserts, Notices, and
   teacher-notes numbers. Growing them would fight that framing and force error-prone lockstep rewrites for no
   gain against the actual "toy data" concern. So **fixed data is unchanged**; the real-input forms carry the
   "reads real input" requirement. (If a future reviewer wants 6–8-element core lists, that is a separate
   change with its own drift check.)
3. **CP-light names (Light trim) — full u07 inventory.** "Untouched rungs" means data/pedagogy; **renames apply
   unit-wide** (incl. rung cells). u07's names are already clean and often meaningfully **paired**, so the trim
   is genuinely light:

   | Old | New | Note |
   |---|---|---|
   | `best_so_far` | `best` | drop verbose suffix (lesson rung 18 + wherever it appears) |
   | `position` | `i` | generic list-index loop counter (lesson 27/29, sol 6/14, while-index sol 18); `i` is already u07's index elsewhere (lesson 69/71) — makes indices consistent |

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
| **read-into-list** | Ex1, Ex2, Ex5, Ex7, Ex9, Ex10, Ex11, Ex12 (names), Ex13, Ex14, Ex16, Ex18, Ex19, Ex20, Ex21, Ex22, Challenge 1, Challenge 2 | `n = int(input("How many scores? "))` + `for i in range(n):` reading one value per pass into the list (two-line append, below), then the unchanged body |
| **read-into-parallel-lists** | Ex15 (Champion by name), Ex17 (Rookie by name) | ONE `for i in range(n)` loop reading BOTH per pass: `names.append(input(f"Name {i + 1}: "))` then `scores.append(int(input(f"Score {i + 1}: ")))` — never two loops / `zip` |
| **single-read** (already interactive, reads ONE value) | Ex4 (add my score), Ex6 (guard one score) | statement is already the real program; real-form mirrors it with one `int(input(...))`, no list prologue |
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
add numbered prompts. Sweep `teacher-notes.md` for the renamed variables. **No data growth.** Markers +
Algorithm-Extension "small fixed data" framing + build-up rungs + all fixed lists untouched.

### Phase B — verification
- `ast.parse` + piped-run every real-form + executable twin; each real-form's RESULT line equals its
  fixed-data twin's output **modulo `input()` prompt text**; numbered prompts display 1..n never 0.
- **Drift check:** since data is unchanged, statement worked-example values == solution assert values ==
  real-form piped output must already hold (no growth to re-derive) — confirm the real-forms reproduce the
  existing twin values, and that no `**Real version:**` cue names a value/variable that changed.
- AST-level closure scan: no concept outside u07's union introduced (no `sys.stdin`; no new builtin/idiom).
- Assert NO old name (`best_so_far`, `position` as a bare Name) survives anywhere under the unit dir (AST).
- `scripts/ci-local.sh` ALL GREEN (exec-lessons runs ladders/twins; exec-solutions runs asserted cells;
  concept-scan/prereq/coverage/pattern-marker/technique-spiral stay clean).

## Out of scope
- Any Book-1 entry other than u07. **Checkpoint-mini-pilot deferral:** design 003 §7 *SHOULD*-paired the first
  slice with a checkpoint mini-pilot; this plan does u07 alone and the checkpoint follows as plan 053 (author
  scope choice — smaller slices; SHOULD ≠ MUST; the 051 renumbering note already shifted the rollout to 052+).
- No data growth (see treatment §2); design 003 (no amendment); markers/rungs untouched. Phase B present.

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

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

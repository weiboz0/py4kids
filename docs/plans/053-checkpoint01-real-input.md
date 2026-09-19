# Plan 053 — checkpoint-01 real-input mini-pilot (non-unit markdown path)

**Status:** DRAFT — plan-review gate pending.
**Type:** Content — apply the real-input treatment to `book1/checkpoints/checkpoint-01-first-steps`.
**Branch:** `feature/plan-053-checkpoint01-real-input`. **Base:** main @ 199ec1c.

## Motivation

Rollout slice 2 (design 003 §7): the **checkpoint mini-pilot**, chosen to exercise the untested **non-unit
markdown / cell-lint / solution-policy path** before the remaining units. checkpoint-01 is the simplest
checkpoint — list-less, early (`requires: print, input, variable, if-statement, while-loop`), clean names —
so it isolates the checkpoint-path mechanics from list-arm / rename / growth complexity. Authorities:
`docs/designs/003-book1-real-input.md` (§2 form-by-kind — checkpoint row; §3 v2; §6 validation); the u04/u07
pilots (plans 050/052) for the established real-form style.

## The treatment (adapted for a checkpoint)

1. **Real-input forms in `solutions.ipynb` (markdown fenced ```python blocks``` under the mirrored
   `## Question N`), per design 003 §2 v3** (amended by this plan to record the placement). The student
   `checkpoint.ipynb` stays **solution-free** (Content Conventions) → **checkpoint.ipynb gets NO edits at all**;
   real-forms live ONLY in the paired solutions, exactly as units do. Where a Question's statement/starter
   already reads `input()` (Q3/Q5/Q7), that IS the real-program form and the solutions block is the model
   answer. This is the key non-unit-path check: markdown real-forms in a checkpoint's solutions are invisible to
   `_solution_policy_findings`/`cell-lint` (they scan code cells only) — 0 `input()` in solutions CODE cells;
   ≥3 non-vacuous assert cells (6 present, unchanged). **Real CI hazard to avoid: an UNFENCED `## Question <digit>`
   line in a new solutions markdown cell would break the `checkpoint_solutions` heading mirror** (fenced ones are
   stripped pre-scan, so harmless); keeping the real-form's own `## Question`-looking lines fenced is a
   design-§6 authoring rule, CI-inert here.
2. **No data growth.** checkpoint-01 is list-less; its data is single realistic scalars (`clues_found=4`,
   `stars=8`, `secret`), not toy `n=3`/2-element lists — design 003 §3 v2 satisfied, nothing to grow.
3. **No rename.** Names (`clues_found`, `clue_message`, `stars`, `bonus`, `total`, `secret`, `guess`,
   `clue_count`, `keep_guessing`, `clue`) are already clean/meaningful — CP-light yields no renames.
4. **No numbered prompts.** No question reads a *sequence* of values; the guess loops read a single running
   guess (`"Guess: "`/`"Guess again: "`) with no round index. Prompts stay as-is.
5. `input` is already in checkpoint-01's `requires` → **no metadata change**.

## Per-question SHAPE table

| Shape | Questions | Real-form (in solutions.ipynb) |
|---|---|---|
| **exempt** (predict / trace / debug / conceptual — input would defeat it) | Q1 (fix the `TypeError` — a read-the-traceback/`type-conversion` debug question; forcing `int(input())`+`str()` is an artificial round-trip and raw `input()` would remove the very error being graded — same class as u07 Ex3), Q2 (predict the output), Q4 (trace the if/elif chain), Q6 (naming + comment concept) | NO real-form; a one-line note in the SOLUTION ("predict/trace/debug/concept question — fixed data on purpose, no input version"). NO checkpoint.ipynb edit. |
| **single-read** (statement already reads `input()`; the question IS the real program) | Q3 (`clue_count = int(input("How many clues? "))`), Q7 (one-guess if/elif/else) | markdown fenced real-form in solutions = the input()-reading program the fixed-data stand-in stands in for |
| **iterative-read / condition-completion** (adapted oracle) | Q5 (complete the `while guess != secret:` condition; reads an initial guess + repeated guesses) | markdown fenced real-form = the completed loop; the fixed-data twin proves the **condition** (`keep_guessing = guess != secret` → `True`), NOT line-for-line output — see Phase B adapted oracle |

Q3/Q7 solutions use stand-ins (`int("6")`, `guess = 10`); their real-form is the input()-reading version. Q5's
real-form is the completed guess loop (prints "You found it!"), captioned as the completed loop so it isn't
read as the condition fragment. **Q1 is exempt → checkpoint.ipynb is untouched** (Q3/Q5/Q7 already carry
`input()`; Q1/Q2/Q4/Q6 exempt).

## Closure

Real-forms use only checkpoint-01's union (print, input, int/str, variable, comparison, if/elif/else, while,
f-string, string-concat, arithmetic). No `sys.stdin`, no list, no `+=`, no new concept. No metadata change.

## Phases

### Phase A — apply to checkpoint-01 (solutions.ipynb ONLY)
**No `checkpoint.ipynb` edits.** In `solutions.ipynb`: add markdown fenced real-forms under the mirrored
`## Question N` for Q3 + Q7 (single-read) and Q5 (completed loop, captioned); add a one-line exempt note under
Q1/Q2/Q4/Q6 ("…question — fixed data on purpose, no input version"). No cues in the student assessment. No data
growth, no rename, no numbered prompts, no teacher-notes change (no variable renamed). Keep every existing
solution CODE cell (the asserted twins) intact so the ≥3-assert floor + heading mirror hold; place each new
markdown cell AFTER the Question's code cell (never inject an UNFENCED `## Question` heading).

### Phase B — verification
- `ast.parse` + piped-run every markdown real-form. Q3/Q7: result line == fixed-data twin's output **modulo
  `input()` prompt text**. **Q5 adapted oracle** (design 003 §6(d) — fragment/condition-completion: its twin
  proves the CONDITION, not the loop output): the
  completed loop, piped a mismatching-then-matching guess sequence, terminates and prints "You found it!"; the
  asserted twin (`keep_guessing = guess != secret` → `True`) proves the condition the question grades.
- CLOSURE AST scan: no concept outside checkpoint-01's union; no `sys.stdin`.
- Non-unit-path checks: 0 `input()` in `solutions.ipynb` CODE cells; ≥3 non-vacuous assert cells (6);
  `checkpoint.ipynb` byte-unchanged (git diff empty for it). No NEW UNFENCED `## Question <digit>` heading in a
  solutions markdown cell (would break the `checkpoint_solutions` mirror); real-forms' own headings-like lines
  stay fenced (design-§6 authoring rule).
- `scripts/ci-local.sh` ALL GREEN (esp. checkpoint cell-lint / solution-policy / structure checks).

## Out of scope
- Any Book-1 entry other than checkpoint-01 (rollout continues: remaining units + checkpoints + projects,
  design 003 §7 order). **design 003 §2 amended → v3** (this plan) to record the checkpoint/brief real-form
  placement (solutions-only, mirrored heading) — that amendment IS in scope; cp02–cp04 + projects follow it.
  No data growth (list-less; §3 v2 satisfied), no rename, no numbered prompts. Phase B present.

## Plan Review

### Round 1 (2026-09-19) — [self] inline; [sol] gpt-5.6-sol; [glm] volcengine-plan/glm-5.3; [fable] Fable 5.

#### [self] (2026-09-19)
- **Verdict**: APPROVE
- Non-unit path handled correctly (real-forms in solutions.ipynb only; checkpoint.ipynb solution-free);
  SHAPE table covers all 7 questions (exempt Q2/Q4/Q6; single-read Q3/Q5/Q7; read-and-compute Q1); closure
  within checkpoint-01's union; input already in requires (no metadata); no growth/rename/numbered-prompts is
  correct for a list-less clean-named early checkpoint; Phase B verification present incl. the checkpoint
  cell-lint/solution-policy path + the `## Question <digit>` fenced-block guard.

#### [sol] (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: solutions-only placement contradicts design 003 §2's checkpoint row + plan-050's
   `## Question N` mapping — reconcile the authority conflict before implementation. → amend design 003 §2 (v3).
2. `[OPEN]` Must Fix: Q5 is not single-read (initial + repeated reads; twin prints `True`, completed loop prints
   "You found it!") — line-for-line/result-parity can't hold; reclassify + specify the adapted oracle (its
   unnumbered `Guess`/`Guess again` prompts are correct since the question forbids a counter).
3. `[OPEN]` Should Fix: Q1 → fixed-data debug exemption (int(input)+str() round-trip is artificial; raw input()
   removes the error being assessed). (== [fable]#1)
4. `[OPEN]` Nice: the fenced-heading guard uses `QUESTION_HEADING` (not `EXERCISE_HEADING`); fences are stripped
   pre-scan so a fenced `## Question <digit>` is harmless — fix the plan's wording.

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — verified non-unit mechanics sound (solution-policy/cell-lint scan code cells
  only; `QUESTION_HEADING` keys the checkpoint structure mirror; fences stripped pre-scan; 6 assert cells, 0
  code input()); SHAPE table matches notebooks; closure/no-growth/no-rename/no-prompts/no-metadata all correct.
1. `[OPEN]` Should Fix: design 003 §2 checkpoint-row placement unrecorded — add a §2 clarification / record the
   governing reading (cp02–cp04 re-litigate otherwise). (== [sol]#1/[fable]#3)
2. `[OPEN]` Should Fix: Q1 `**Real version:**` cue edits the graded assessment statement — drop it / constrain
   it. (== [fable]#1)
3. `[OPEN]` Nice: fenced-`## Question` guard is CI-inert for checkpoints (fences stripped); the real hazard is
   an UNFENCED heading breaking the mirror — re-attribute.
4. `[OPEN]` Nice: caption Q5's real-form as the completed loop (its twin stands in for the condition).

### Round 1 — outcome: REJECT (1 of 4, [sol]); all four converged. Fixed → round 2.
**Round 1 responses:**
- → [FIXED] design 003 §2 authority conflict ([sol]#1 Must / [glm]#1 / [fable]#3): **amended design 003 §2 → v3**
  — checkpoint/brief real-forms live in the paired solutions.ipynb under the mirrored heading; student
  checkpoint/brief stays solution-free; statement/starter that already reads input() IS the real-program form.
- → [FIXED] Q5 reclassified ([sol]#2 Must / [fable]#2): "iterative-read / condition-completion" with an adapted
  Phase-B oracle (twin proves the condition, not line-for-line; completed loop prints "You found it!").
- → [FIXED] Q1 → EXEMPT ([sol]#3 / [fable]#1 / [glm]#2): debug/traceback exemption; **checkpoint.ipynb gets NO
  edits** (no cue).
- → [FIXED] guard attribution ([sol]#4 / [glm]#3): fenced-`## Question` is a design-§6 authoring rule, CI-inert
  for checkpoints; real hazard = UNFENCED heading breaking the mirror.
- → [FIXED] Q5 caption ([glm]#4); Q3 inline-line fold + exempt-note-in-solutions-deliberate ([fable]#4) noted.
Re-dispatching round 2 (design §2 changed).

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS — non-unit mechanics confirmed sound (solution-policy scans code cells only;
  6 assert cells; `_markdown_heading_occurrences` strips fences so a fenced `## Question` won't trip
  checkpoint_structure). Closure/no-growth/no-rename/no-prompts/no-metadata all confirmed.
1. `[OPEN]` Should Fix: Q1 should be **EXEMPT**, not read-and-compute — Q1 grades `type-conversion` (`str()`
   fixes the TypeError); a cue that `clues_found` comes from `input()` invites `input(...)` (already str) →
   concat works with NO `str()`, defeating the grading, and the int()+str() real-form is a contrived round-trip.
   Make Q1 exempt (debug/traceback class, like u07 Ex3) → **checkpoint.ipynb gets NO edits at all**.
2. `[OPEN]` Should Fix: Q5's real-form (prints "You found it!") doesn't line-match its twin (prints `True`,
   the condition) — state Phase B's adapted criterion for Q5 (piped-run terminates on the matching guess +
   prints "You found it!"; the asserted twin proves the condition, not output).
3. `[OPEN]` Should Fix: reconcile with design 003 §2 checkpoint row explicitly — real-forms solutions-only;
   the §2 "under ## Question N" form is satisfied by the statement/starter when it already reads `input()`
   (Q3/Q5/Q7). Add a sentence (+ optional design 003 §9 line); cp02–04 copy this precedent.
4. `[OPEN]` Nice: Q3 solution markdown already states the full `int(input(...))` line inline — fold, don't
   duplicate. Exempt-note placement in solutions (not statement) is deliberate for checkpoints — say so.

### Round 2 (2026-09-19) — re-review after design §2 v3 + Q1-exempt + Q5-reclassify (e386103)
#### [self] round 2 (2026-09-19)
- **Verdict**: APPROVE — design 003 §2 v3 resolves the authority conflict (checkpoint real-forms solutions-only,
  mirrored heading; checkpoint.ipynb solution-free); Q1 exempt → checkpoint.ipynb untouched; Q5 reclassified
  with adapted oracle; guard attribution corrected. No new blocker.
#### [sol] round 2 (2026-09-19)
- **Verdict**: REJECT
1. `[OPEN]` Must Fix: Q1-exempt + §2 v3 sound, but Q5's adapted oracle conflicts with design 003 §6 (which
   unconditionally requires result-line parity + line-for-line twin) — amend §6 to define the
   condition-completion exception + its two-part proof. → [FIXED]: **design 003 §6(d) added (v3)** — twin proves
   the graded fragment; the completed real-form proves termination + result line. (== [fable] R2 nit, escalated.)

#### [glm] round 2 (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS — all 4 round-1 nits verified resolved (design §2 v3, Q1 exempt + checkpoint
  byte-unchanged, guard re-attribution against the code, Q5 caption). 2 Nice:
1. `[OPEN]` Nice: §9 revision history reads v1, v3, v2 (v3 inserted before v2) — reorder ascending. → [FIXED].
2. `[OPEN]` Nice: add a §6 condition-completion allowance so cp02–cp04 don't re-litigate. → [FIXED] via §6(d)
   (added after glm's e386103 review).

### Round 2 — outcome: REJECT (1 of 4, [sol]; §6 conflict). Fixed via design 003 §6(d) → round 3.
**Round 2 responses:** [sol]#1 [FIXED] design 003 **§6(d)** added — fragment/condition-completion exception
(twin proves the graded fragment; completed real-form proves termination + result line); Q5 Phase B cites it.
[fable] R2 nice == same §6(d) [FIXED]. [glm]#1 [FIXED] §9 reordered v1→v2→v3; [glm]#2 [FIXED] via §6(d).
Re-dispatching [sol] round 3 (design §6 changed).

#### [fable] round 2 (2026-09-19)
- **Verdict**: APPROVE WITH NITS — all 4 round-1 nits RESOLVED (Q1 exempt + checkpoint.ipynb byte-unchanged;
  Q5 adapted oracle; design §2 v3 sound + consistent with the "why markdown for non-lessons" para; Q3 fold +
  exempt-note-in-solutions). Guard attribution corrected. No new blocker.
1. `[OPEN]` Nice: design 003 §6(b)/(c) has no clause for condition/fragment-completion oracles (Q5's kind);
   add a one-line §6 addendum so cp02–cp04/projects don't re-derive it ("fragment-completion questions: the
   twin proves the graded fragment; the piped-run real-form proves termination + result line"). → will fold.

## Content Review
_(pending — 4-way.)_

## Post-Execution Report
_(pending.)_

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

### Round 3 (2026-09-19) — [sol] re-review after design §6(d) (7991d0b)
#### [self] round 3 (2026-09-19)
- **Verdict**: APPROVE — design 003 §6(d) makes Q5's condition-completion oracle design-sanctioned; plan now
  fully consistent with design 003 (§2 v3 placement, §3 v2 no-growth, §6d oracle). [glm]/[fable] nits (§9 order,
  §6 clause) folded. No open blocker.
#### [sol] round 3 (2026-09-19)
- **Verdict**: APPROVE — §6(d) design-sanctions Q5's two-part oracle, narrowly limited to fragment-grading;
  consistent with §2 v3 + §3 v2. No blocker.

### PLAN-REVIEW GATE CLOSED (2026-09-19) — 4-way consensus: [self]/[sol] APPROVE, [glm]/[fable] APPROVE WITH
NITS (all folded). Produced design 003 §2 v3 (checkpoint/brief placement) + §6(d) (fragment-completion oracle).

## Content Review

### Round 1 — Phase A (2026-09-19, commit 61bd69a). Roster: [self] inline; [sol]; [glm] glm-5.3; [fable].
#### [self] (2026-09-19)
- **Verdict**: APPROVE
- Verified: Q3/Q7 real-forms parity-match twins (Q7→"Too high!"); Q5 §6(d) oracle (piped 3,7 → "You found
  it!"; twin proves the condition); exempt notes on Q1/Q2/Q4/Q6 (in solutions, not the assessment);
  checkpoint.ipynb byte-unchanged (git diff empty); 0 `input()` in solutions CODE cells; 6 assert cells;
  closure within checkpoint-01's union; nbformat valid; ci-local ALL GREEN (checkpoint solution-policy/
  structure path passes with markdown real-forms — the mini-pilot's proof).
#### [sol] (2026-09-19)
- **Verdict**: APPROVE — no findings.

### CONTENT GATE CLOSED (2026-09-19) — 4-way: [self]/[sol] APPROVE, [glm]/[fable] APPROVE WITH NITS. All Nice
folded: exempt notes reworded age-appropriately (no "fixed data on purpose" jargon; Q6 tailored to naming) +
Q5 real-form blank line restored. No open blockers.

## Post-Execution Report

**Status: COMPLETE — checkpoint-01 real-input mini-pilot (rollout slice 2, non-unit path). 2026-09-19.**

### What shipped
The real-input treatment applied to `checkpoint-01-first-steps`, proving the **non-unit markdown path**:
- **solutions.ipynb only** (checkpoint.ipynb byte-unchanged — student assessment stays solution-free, design
  003 §2 v3): markdown `input()` real-forms under Q3 (one-line count read), Q5 (completed guess loop —
  §6(d) condition-completion oracle), Q7 (one-guess detective); one-line exempt notes under Q1 (debug/
  traceback), Q2 (predict), Q4 (trace), Q6 (naming/comment concept).
- No data growth (list-less realistic scalars), no rename (clean names), no numbered prompts (no sequence),
  no metadata change (`input` already in `requires`).

### Verification
- 6 solution code cells' asserts pass; the 3 real-forms parity-match (Q7 → "Too high!"; Q5 → "You found it!"
  with the twin proving the condition per §6(d); Q3 binds `clue_count`). 0 `input()` in solutions code cells;
  6 assert cells; checkpoint.ipynb byte-unchanged.
- `scripts/ci-local.sh` ALL GREEN — the checkpoint cell-lint / solution-policy / structure (heading-mirror)
  path passes with markdown real-forms. `pre-merge-guard` OK.
- **Content gate: 4-way → consensus** ([self]/[sol] APPROVE, [glm]/[fable] APPROVE-WITH-NITS, all Nice folded).
- Produced (plan-review) design 003 **§2 v3** (checkpoint/brief placement) + **§6(d)** (fragment-completion
  oracle) — cp02–cp04 + projects inherit both.

### Rollout
Slice 2 done. Remaining (design 003 §7): units u01 (text-only), u02, u03, u05, u06 (list-less); u08, u09, u10
(list); checkpoints cp02–cp04; projects. `input` metadata add needed for u03/u05/u08/u09. The non-unit
checkpoint path is now proven for cp02–cp04.

#### [glm] (2026-09-19, volcengine-plan/glm-5.3)
- **Verdict**: APPROVE WITH NITS
1. `[OPEN]` Nice: Q6 exempt note omits "fixed data on purpose" that the other three include — inconsistent
   wording. → will resolve together with [fable]#1 by rewording all four age-appropriately (Q6 tailored to
   naming).

#### [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS — blind-solved all 7 (match); ran 6 solution cells (asserts pass) + 3
  real-forms (Q3 binds 6; Q7 → Too high!/Too low!/Case closed!; Q5 terminates + "You found it!", twin proves
  the condition — §6(d)); exempt notes correct + solutions-only; non-unit path PASS (checkpoint.ipynb diff
  empty, 7 `## Question` headings intact, hygiene/structure/cell-lint/exec-solutions/concept-scan/prereq PASS);
  closure clean. (Pre-existing u02 DuplicateCellId warning, not this change.)
1. `[OPEN]` Nice: exempt-note wording "fixed data on purpose" is jargon for a 12-year-old — reword to "the
   numbers are typed into the code on purpose — there is no `input()` version". → will apply.
2. `[OPEN]` Nice: keep Q5's starter blank line between the initial read and `while` (cosmetic). → will apply.
#### [fable] (pending)

## Post-Execution Report
_(pending.)_

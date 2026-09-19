# Plan 050 — Book 1 Real-Input Norm (hybrid stdin form + realistic data)

**Goal:** Book-1 examples and exercises stop looking "fake." Two norms:
1. **Hybrid real-input form (Option A, user-chosen).** Keep the **executable fixed-data** worked examples
   (run live, students see output) AND add ONE consistent **`input()`-reading "real program"** form per
   complete task (each lesson "put it together") and per exercise. Uses `input()` (introduced u01),
   **NEVER** `sys.stdin` (that is Book 2).
2. **Realistic exec data (user-directed).** Culminating "put it together" cells and exercises use
   realistic, non-trivial data — no `n=3`, no 2-element lists — via **Handling (i)** (user-chosen):
   - **u07–u10 (lists from u07):** realistic FIXED lists (≈6–8 elements, real variety, ties where apt).
   - **u01–u06 (no `list` yet):** a realistic *fixed* dataset needs an ugly N-branch `if/elif`, which reads
     *more* fake — so the exec cell keeps a **modest** fixed dataset and the **`input()` real-program form
     carries the realism** (in u02–u06, an arbitrary count of values via a sentinel/count loop; **u01 stays
     fixed-count text prompts, no loop**). The one-increment build-up rungs **stay minimal**
     (realism applies to the put-it-together + exercises only — never the graduated rungs; that protects
     the plans 031–035 / 049 pedagogy).

**Non-goal (rejected option):** Book-2-style `sys.stdin.read()` + subprocess `judge-check` over `.in`/`.out`.
Book 1 stays a notebook course with **executable worked examples**; the real-input realism is the *added*
form + realistic exec data.

## The CI constraint that shapes the form (verified by all four reviewers, round 1)

An `input()` cell cannot be executed by CI (`nbclient` has no stdin; `tools/notebooks.py` `INTERACTIVE =
input(|sys.stdin`). Two checks matter, and they differ by notebook kind:
- **`_solution_policy_findings`** rejects `input()` in **any `solutions.ipynb` code cell regardless of
  `no-exec`** (units, checkpoints, projects). Only Book-2 stdin-model entries are exempt. → A `input()`
  reference solution **CODE cell is impossible** in Book 1 without a tooling change.
- **`cell-lint`** skips `no-exec` code cells **only for `kind=="unit"`**; checkpoint/project `no-exec` code
  cells are still compiled. **`concept-scan`** detects `input()` in any CODE cell (no `no-exec` filter).
- **Lessons** may carry a `no-exec` `input()` CODE cell — this is a live, green convention already
  (u04 lesson cells 20 and 40 are exactly that).

**Resolution (no tooling change):**
- **Lessons:** the real-program form is a **`no-exec` `input()` CODE cell** (proven convention) + a
  `**Notice:**`. `concept-scan` sees `input()` → units whose union lacks `input` get a General-Rule
  `practices: [input]` add (map + manifest). Verified set needing the add: **u03, u05, u08, u09** (u01/u02/
  u04/u06/u07/u10 already have it — u04, the pilot, needs none).
- **`solutions.ipynb`, `checkpoint.ipynb`, `brief.ipynb`:** the real-program form is a **markdown fenced
  code block** (NOT a code cell) — for `solutions.ipynb` this is required by `_solution_policy_findings`
  (bans `input()` in solution code cells); for `checkpoint.ipynb`/`brief.ipynb` by `cell-lint` (non-unit
  `no-exec` code cells are still compiled) + `concept-scan`. The exact plan-045 submission-wrapper precedent. Because it is markdown, `concept-scan`/`cell-lint`/solution-policy never
  touch it, so **no `input` metadata add is needed for checkpoints/projects**. The **executable
  reference solution stays a fixed-data code cell carrying ≥3 non-vacuous asserts** (run + verified by
  `exec-solutions`) — that is the VALIDATED logic; the markdown real-program form is a thin adapter over
  the same logic (fixed values → `input()`).

## Validation of the real-program forms (reviewer safeguard, round 1)

`no-exec` / markdown real-program code is never run by CI, so malformed or wrong code could pass silently.
Guardrails: (a) every real-program form is `ast.parse`-checked at authoring; (b) it is **run once with
piped fixed input** (`printf '…' | python prog.py`) and its **result line(s)** confirmed equal to the
paired executable fixed-data cell's output — compared *modulo the `input()` prompt text* (prompts print to
stdout), recorded in the slice's post-exec report; (c) the real form's logic is line-for-line the
fixed-data solution with the fixed values replaced by `input()` reads, so the CI-run fixed-data version is
the behavioral proof. **Drift:** if a later slice edits a fixed-data cell but not its markdown twin, the
pair diverges silently — the per-PR content gate re-checks the pairing (inherent to the no-tooling-change
resolution).

## Global Constraints

- **`input()` idiom only** (u01-native); NEVER `sys.stdin`. **u01 real-program forms are TEXT-ONLY** —
  `int()`/`str()` (type-conversion/int-type) are introduced **u02**, so u01 reads/prints strings only.
- **Per-unit input idiom** (closure-pinned in design 003): u01 = fixed-count prompts, **no loop**
  (sentinel-loop is u02); u02+ = sentinel / count loop; u07+ may read into a list.
- **Real-program form placement:** lesson → `no-exec` `input()` code cell; solutions/checkpoint/brief →
  **markdown fenced block**; executable fixed-data solution (code cell, ≥3 non-vacuous asserts) is retained
  and is the validated logic.
- **Realistic data** on put-it-together + exercises; **build-up rungs stay minimal**; list-less units use
  Handling (i); realistic fixed lists only u07–u10.
- **Executable worked examples preserved** (no exec→no-exec conversion). Metadata: no `introduces`/
  `requires`/marker/§3 change; the ONLY permitted change is the General-Rule `practices: [input]` add for
  **u03/u05/u08/u09** (map + manifest, kept in sync). Prereq-closure per unit.
- **Control-flow closure of the LESSON real-program forms (rollout risk — fable N2).** The `input`-only
  add set assumes each real form reuses control flow already in its unit's union. `int-type`/
  `type-conversion`/`sentinel-loop` are in `concept-scan`'s `never_flag`, so `int(input())` is safe
  everywhere — but **`while-loop` IS flaggable and is absent from u03/u06/u08/u09**. So those units' lesson
  real forms use a **`for`-loop** idiom (all four have `for-loop`; u03/u06/u09 also have `range-function`
  for a `for i in range(n)` read; **u08 lacks `range-function`** → `for` over a taught iterable — u08 has
  `list-literal`/`list-loop`/`list-append` — or fixed-count reads), NOT a sentinel `while`; add `while-loop`
  to a unit's `practices` only if a form genuinely needs it. (u04 pilot has both `input` and `while-loop`
  → unaffected.) Design 003 pins each unit's exact idiom. Each 051+ slice
  concept-scans its own forms before commit.
- **`solutions_structure` raw-markdown scan (N5).** A fenced real-form block inside a unit `solutions.ipynb`
  must NOT contain a line beginning `## Exercise <digit>` (that check matches raw markdown, un-fenced) —
  real code never does; noted so authors don't paste a heading-shaped comment.
- Branch `feature/plan-050-…`; no commits while a `[sol]` review is in flight; `GH_TOKEN=$(cat .gh-token)`;
  run `ci-local` FOREGROUND (`TMPDIR=/dev/shm bash scripts/ci-local.sh`). Do not touch Book 2 / governance.

## Out of scope

- Book-2-style subprocess judging / `.in`-`.out` fixtures / `judge-check` for Book 1.
- Converting existing executable teaching cells to `no-exec`; new checkpoint/project questions.
- A tooling change to `_solution_policy_findings` (the markdown-form resolution avoids needing one).

## Phases

**Plan 050 ships Phase A + Phase B (pilot u04) ONLY.** The rollout across the remaining 15 entries is
**subsequent plans (051+)**, each a slice through both gates — enumerated in design 003 §rollout so this
plan is not an open-ended umbrella (avoids plan-scope expansion). Dispatch per AGENTS.md.

### Phase A — Design 003 + conventions + CI-safety probe (docs, ships first)
1. Write `docs/designs/003-book1-real-input.md`: the two norms; the per-kind real-program form
   (lesson no-exec code cell; solutions/checkpoint/brief markdown); the validation guardrails; the
   realistic-data recipe + per-unit input idiom + u01 text-only boundary; the **enumerated rollout order**
   (u01–u03, u05, u06 list-less; u07–u10 lists; then the 4 checkpoints; then the 2 projects — first rollout
   slice includes one u07–u10 list unit, first checkpoint slice is a mini-pilot); the **u03/u05/u08/u09
   `input` `practices` adds**; the acceptance bar (reached unit-by-unit).
2. Probe (throwaway, reverted) covering **all three kinds** — a unit (lesson `no-exec` input() cell +
   solutions markdown real-form + fixed-data asserted solution), a **checkpoint** (markdown real-form +
   fixed-data solution), and a **project** (markdown real-form) — and confirm `exec-lessons`,
   `exec-solutions`, `_solution_policy_findings` (structure-check), `cell-lint` (incl. non-unit),
   `noexec-check`, `concept-scan`, `hygiene`, `manifest`/`prereq`/`coverage` all stay green. Ship a
   tooling change only if the probe forces it; expected: none (markdown-form resolution).
- **Acceptance (A):** design 003 committed; the three-kind probe green; no tooling change (or fault-tested).

### Phase B — PILOT: u04 quiz-show (full unit)
Apply both norms to u04 end-to-end: each L-section + Algorithm-Extension-home "put it together" gains a
`no-exec` `input()` real-program code cell + Notice (u04 already has `input` → no metadata add); exec
put-it-togethers use realistic-but-modest fixed data (list-less → Handling (i)); each u04 exercise keeps a
fixed-data asserted reference solution AND gains a markdown `input()` real-program form, statement
reworded to "reads its input." Build-up rungs untouched; markers/§3 untouched. Validate every real form
(ast.parse + piped-input run == fixed-data output). 4-way content gate; ci-local ALL GREEN.

### Phase V — Verification (named, mandatory)
`uv run pytest -q` green; `scripts/ci-local.sh` ALL GREEN (exec-lessons/exec-solutions run the fixed-data
cells; `input()` lesson cells `no-exec`-stripped; markdown real-forms inert; hygiene/cell-lint/noexec/
concept-scan/structure/manifest/prereq/coverage/PDF + pre-merge guard). **Real-program-form validation**
(ast.parse + piped-input == fixed-data output) recorded per slice. **Pedagogy (reviewer-enforced):** every
complete task has an executable fixed-data form AND a real-program `input()` form; put-it-together +
exercise data realistic where closure allows; build-up rungs one-increment; u01 text-only; no `sys.stdin`;
Book 2 green. **Acceptance:** design 003 + pilot u04 merged; ci-local ALL GREEN; `pre-merge-guard --pr` OK;
plan-review + content-review 4-way consensus. Rollout entries follow in plans 051+.

## Plan Review

### Round 1 (HEAD 034e9d1) — [glm] REJECT · [sol] REJECT · [fable] APPROVE WITH NITS

All three confirmed the lesson arm is CI-sound/proven, `input()` (not `sys.stdin`) is the right u01 idiom,
Handling (i) + build-up-rung exemption are sound, and Phase V is named. Blockers, all folded in this
revision:

- `[FIXED]` **B1 (all three): `input()` in a solutions code cell fails `_solution_policy_findings`
  regardless of `no-exec`** (empirically verified) → the exercise "solution reads input()" would red every
  slice; the unit-only probe gave a false green. Resolution: **markdown fenced real-program form** in
  solutions/checkpoint/brief (no tooling change; plan-045 precedent); executable fixed-data asserted
  solution retained as the validated logic.
- `[FIXED]` **B2 (all three): `int()`/`str()` are u02, not u01** → u01 real-program forms are TEXT-ONLY;
  per-unit input idiom pinned (u01 fixed prompts no-loop; u02+ sentinel/count loop).
- `[FIXED]` **checkpoint/project mapping (sol/glm): unspecified** → markdown real-program form under each
  `## Question N` (checkpoints) / `## Milestone N` (Book-1 project briefs — NOT `### Problem N`, which is
  Book-2); executable fixed-data solution retained; notebook mapping stated.
- `[FIXED]` **probe scope (sol/fable): unit-only** → Phase A probe now covers unit + checkpoint + project.
- `[FIXED]` **N1 metadata (glm/sol): entries lacking `input`** → verified only **u03/u05/u08/u09** need the
  General-Rule `practices:[input]` add (their lesson no-exec code cells); checkpoints/projects use markdown
  → no add. Enumerated; map+manifest synced.
- `[FIXED]` **no-exec/markdown real-form validation (sol/fable): could pass CI silently** → ast.parse +
  piped-input run == fixed-data output, recorded per slice; the fixed-data asserted cell is the CI proof.
- `[FIXED]` **scope/phasing (sol/glm/fable): "Phases C–…" not enumerated / plan-scope expansion risk** →
  050 ships A + B (pilot u04) only; rollout enumerated in design 003 as plans 051+ (first rollout slice
  includes a u07–u10 list unit; first checkpoint = mini-pilot).
- `[FIXED]` **fable nits:** exercise fixed-data check cells carry ≥3 non-vacuous asserts; u01
  "arbitrary input size" overclaim removed (u01 pre-loop → fixed prompts).

Round 2 re-dispatched to all three on the revised HEAD.

### Round 2 (HEAD e4319d9) — [glm]/[fable] APPROVE WITH NITS · [sol] REJECT (1 blocker)

All three verified B1's markdown-form resolution is sound *by mechanism* ([fable] ran an in-memory probe:
a markdown ```` ```python input() ```` block + fixed-data asserted cells passes structure-check/
concept-scan/cell-lint; the same as a code cell would fail), the 4-unit `input` add set (u03/u05/u08/u09)
is exactly right, u01 text-only is correct, Phase V is named, scope is clean. Findings, all folded:

- `[FIXED]` **[sol] blocker / [glm]+[fable] nit — project mapping.** Book-1 project briefs are
  `## Milestone N`-based (zero `### Problem N` — that's Book-2's project-03). Corrected: markdown real-form
  under `## Question N` (checkpoints) / `## Milestone N` (Book-1 briefs).
- `[FIXED]` **all three — citation:** "u04 cells 20/40/50" → "cells 20 and 40" (cell 50 is a markdown
  heading).
- `[FIXED]` **[glm] — attribution:** the `checkpoint.ipynb`/`brief.ipynb` markdown requirement is enforced
  by `cell-lint` (non-unit `no-exec` compiled) + `concept-scan`, not `_solution_policy_findings`
  (solutions-only). Reworded.
- `[FIXED]` **[glm]/[fable] — "arbitrary input size" contradiction:** scoped to u02–u06 (u01 fixed-count
  prompts, no loop).
- `[FIXED]` **[fable] N2 / [glm] risk — control-flow closure:** `while-loop` is `concept-scan`-flaggable and
  absent from u03/u06/u08/u09 → their lesson real forms use a for/count-loop idiom (not sentinel `while`),
  add `while-loop` only if needed; `int`/`type-conversion`/`sentinel-loop` are `never_flag`. New constraint.
- `[FIXED]` **[fable] — validation wording:** compare result line(s) *modulo prompt text*; drift caught by
  the per-PR content gate. **[fable] N5:** no `## Exercise <digit>` line inside a unit-solutions fenced
  real-form (raw-markdown scan). New constraint.

Round 3 re-dispatched to all three (the project-mapping blocker + nits folded).

### Round 3 (HEAD 518458e) — CONSENSUS: all four APPROVE / APPROVE WITH NITS ✅ — GATE CLOSED

- **[self] APPROVE.**
- **[sol] APPROVE** — round-2 blocker (project → `## Milestone N`) fixed and implementable; all six folds
  verified against the repo; no new blockers.
- **[fable] APPROVE** — no residual blockers, no nits; every empirical claim re-verified (the N2
  control-flow set is factually exact: `while-loop` absent from precisely u03/u06/u08/u09; u08's `for`/list
  idiom is within its union).
- **[glm] APPROVE WITH NITS** — all six items verified folded; one non-blocking wording nit `[FIXED]`:
  the u08 idiom line now says `for` over a taught iterable (u08 has list-literal/list-loop/list-append) or
  fixed-count reads, and defers the exact per-unit idiom to design 003.

**4-way consensus — no open blockers. Plan-review gate CLOSED.** Cleared to implement Phase A (design 003
+ three-kind CI probe) → Phase B (pilot u04); rollout entries in plans 051+.

## Content Review

### Round 1 — Phase B pilot u04 (2026-09-19)

Roster dispatched in parallel: [self] inline; [sol] `codex:codex-rescue` (--model gpt-5.6-sol --fresh, read-only);
[glm] `opencode:opencode-review`; [fable] Fable 5 (`Agent`, general-purpose), all read-only.

#### Review — [self] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
1. `[self]` Closure: AST-level scan of all 22 new real-forms (19 solutions markdown, 3 lesson `no-exec`) —
   NO `for`/`list`/`range`/`len`/`sum`/string-method/`def`; only input, int(input), `==` (incl. string),
   and/or/not, while, break, nested if, f-strings. Clean. Priority: (verified, no action).
2. `[self]` CI-safety: 0 solutions CODE cells contain `input()`; 0 markdown real-forms contain a
   `^## Exercise` line; `ci-local` ALL GREEN (exec-solutions runs the asserted twins incl. Ex11→40, Ex12→3).
   Priority: (verified, no action).
3. `[self]` Correctness: all 22 real-forms `ast.parse` + piped-run to their fixed-data twin's result line
   (modulo prompt text). Priority: (verified, no action).
4. `[FIXED-N/A]` Exemptions: Ex6 (paper-trace "Predict the score") and Challenge 2 (countdown) documented
   as no-input by design — input() would defeat a prediction / a countdown reads nothing. Justified.
   Priority: Nice to Have (rollout should keep this exemption class explicit in design 003 §4 — already implied).
5. `[OPEN]` Asymmetry (rollout note, not a u04 blocker): for the read-and-accumulate exercises whose student
   cell is `no-exec` (Ex11), the input() form IS the model answer; for the fixed-data ladder drills
   (Ex13–18) the student writes the fixed-data version and the real-form is shown only in the solution via a
   "Real version:" note. Both satisfy design 003 §8, but plans 051+ should standardize how prominently the
   real-form is offered to the student. Priority: Nice to Have.

#### Review — [sol] (2026-09-19 — codex gpt-5.6-sol, task-mu8q4hig-yacrlw)
- **Verdict**: REJECT
1. `[OPEN]` lesson.ipynb L1 (cell 20 `65f4180b`) and L3 (cell 42 `d3d0be05`) are complete `no-exec` input
   programs with no executable fixed-data twin of the same logic/result line; adjacent rungs are only partial
   build-ups. Violates design 003's both-forms requirement for the full pilot. Priority: Must Fix. (== [glm] #4, escalated)
2. `[OPEN]` exercises.ipynb Ex12 work cell (`u04-count-correct-work`) untagged though rewritten Ex12 requires
   an input-reading program (Ex11 cell 25 is `no-exec`). Priority: Should Fix. (== [fable]#1 / [glm]#1)
3. `[OPEN]` exercises.ipynb Ex11 (`u04-ex11`) says a "round" contains any number of "questions" but then
   defines `n` as rounds. Priority: Should Fix. (== [glm]#2)
4. `[OPEN]` exercises.ipynb Ex12 (`u04-count-correct-heading`) "not just 3 answers" leftover. Priority: Nice to Have. (== [fable]#2)
5. `[OPEN]` exercises.ipynb Ex16 (`bb5c58d03be5`) real note omits the leading count read. Priority: Nice to Have. (== [fable]#3 / [glm]#3)

### Round 1 — outcome: REJECT (1 of 4, [sol]). Fix → re-review (round 2).

**Round 1 responses (commit after e4df129):**
- → Response [FIXED] ([sol]#1 / [glm]#4 — Must Fix): added executable fixed-data twins for the L1 opening-round
  and L3 SUDDEN-DEATH put-it-togethers (fixed stand-in answers), each placed before its `no-exec` input form
  with a Notice; reworded the intro prose so "run it" now points at the runnable twin (fixes the prior
  run-a-no-exec-cell contradiction). Twins run: "Score 3 after 2 questions." / "Survived 3 sudden-death
  questions." — matching their input-version result lines. All three lesson sections + L1/L3 now carry BOTH forms.
- → Response [FIXED] ([sol]#2 / [fable]#1 / [glm]#1 — Should Fix): tagged Ex12 work cell `u04-count-correct-work` `no-exec`.
- → Response [FIXED] ([sol]#3 / [glm]#2 — Should Fix): Ex11 statement now "A quiz can have any number of rounds."
- → Response [FIXED] ([sol]#4 / [fable]#2 — Nice): Ex12 "not just 3 answers" → "not just the five answers in the checked example."
- → Response [FIXED] ([sol]#5 / [fable]#3 / [glm]#3 — Nice): Ex16 real-version note now mentions the leading count read.
- → Response [FIXED] ([self]#5 — Nice, rollout note): folded into design 003 §7 guidance for plans 051+ (no u04 change).

ci-local ALL GREEN after fixes; all 24 real-forms (19 solution md + 3 lesson input + 2 new lesson twins are
executable, validated) reproduce their twins. Re-dispatching all four for round 2 (lesson content changed materially).

#### Review — [glm] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
- Verified: all 22 real-forms run clean + reproduce twin result lines (Ex11→40, Ex12→3, asserts pass); no
  closure violations; exemptions justified; 0 input() in solutions code cells; no fenced real-form starts
  `## Exercise`; targeted hygiene/structure/noexec/cell-lint/exec-solutions/exec-lessons/manifest/prereq/
  coverage/concept-scan/stretch all PASS; blind solves matched.
1. `[OPEN]` exercises.ipynb Ex12 work cell 28 untagged while its statement is now input-native (sibling Ex11
   cell 25 is `no-exec`). Tag cell 28 `no-exec`. Priority: Should Fix. (== [fable] #1)
2. `[OPEN]` exercises.ipynb Ex11 cell 24: "A quiz round can have any number of questions" conflates questions
   with rounds; reword to "A quiz can have any number of rounds." Priority: Nice to Have.
3. `[OPEN]` Ex16 real-program note omits the leading count read (real-form opens with `n = int(input(...))`);
   sibling Ex13/14/15/17/18 notes mention it. Priority: Nice to Have. (== [fable] #3)
4. `[OPEN]` lesson.ipynb L1 (cell 20) and L3 (cell 40) put-it-togethers carry ONLY the `no-exec` input()
   form, with no executable fixed-data twin of the same task — unlike the newly paired L2/running-total/
   count. Pre-existing, but short of design 003's "both forms". Priority: Nice to Have.

#### Review — [fable] (2026-09-19)
- **Verdict**: APPROVE WITH NITS
- Verification: blind-solved Ex6/9/11/12/16/17/18 (all match); ran all 21 asserted cells (pass, incl. Ex11→40,
  Ex12→3); all 22 real-forms ast.parse + piped-run identical to twins; closure clean (u04 union only); 0
  solutions code cells with input(); 0 real-forms with `## Exercise`; exemptions (Ex6 trace, Challenge 2
  countdown) justified.
1. `[OPEN]` exercises.ipynb Ex12 answer cell (cell 28) missing `no-exec` tag — its rewrite to an input()
   "any n" program should carry the tag like Ex11's cell 25. Empty so CI passes today, but breaks the
   design-003 convention. Priority: Should Fix.
2. `[OPEN]` exercises.ipynb Ex12 statement trailing "not just 3 answers" is a leftover from the old
   fixed-data statement (twin now uses 5). Priority: Nice to Have.
3. `[OPEN]` exercises.ipynb Ex16 "Real version:" note omits that the real form first reads the answer count
   (its real-form opens with `n = int(input(...))`); sibling notes on Ex13/14/15/17/18 mention it. Priority: Nice to Have.

## Post-Execution Report

_(pending.)_

# Plan 049 — Book 1 Algorithm-Extension Lesson Enrichment (graduated worked examples)

**Goal:** Make each unit's `## Algorithm Extension` **lesson** section teach with the same
**graduated worked-example ladder** as the rest of the lesson (L1/L2/L3): a short run of executable
`code` rungs, each followed by a `**Notice:**`, building the pattern up one increment at a time and
ending in a worked "put it together" example — **before** students meet the extension drills. Today the
section (shipped by plan 048) introduces each pattern as a **prose-only "Pattern Spotlight"**, which is
inconsistent with the worked-example teaching used everywhere else in Book 1 (plans 031–035). This plan
adds the missing ladders at each pattern's **home** Spotlight.

**Relationship to plan 048 (progress-tracked, collision-safe):** plan 048 is being rolled out
concurrently by another session (it creates each unit's `## Algorithm Extension` section + drills,
unit-by-unit). This plan **follows** 048: a unit's lesson enrichment is authored **only after that
unit's 048 slice has merged to `main`** (so the two never edit the same `lesson.ipynb` at once). u04's
048 slice (Phase B, PR #59) is already merged — u04 is the pilot and can proceed now; the remaining
home units follow as their 048 slices land.

**Branch-refresh mechanics (mandatory per slice).** Because 049 is long-lived and 048 keeps merging,
each slice is authored on top of CURRENT `main`: at slice start, `git checkout main && git pull
--ff-only`, then cut a fresh `feature/plan-049-<unit>` branch (or rebase the 049 branch onto the
freshly-pulled `main`), and run the gate probe at that HEAD. **Concrete 048-gate probe (testable
"otherwise wait"):** the unit's `lesson.ipynb` on the just-pulled `main` must contain a `## Algorithm
Extension` cell AND a `### Pattern Spotlight: <name>` cell for each of the unit's home patterns (grep
the notebook JSON); if absent, that unit's 048 slice has not merged yet — skip it and take the next
ready unit / wait. This guarantees each 049 edit builds on 048's merged content and never races the file.

**Architecture:**
- **Scope = HOME Spotlights only.** A graduated ladder is *teaching*, and teaching happens where a
  pattern is introduced. Per `tools/patterns.py`, a lesson pattern marker exists **only for an
  introduced (home) pattern** (`_expected_markers`: `lesson.ipynb` → `introduced`), and it must live in
  prose. So the ladders attach to the home Spotlight of each of the 7 patterns:
  - **u04** — running-total, count-by-condition
  - **u06** — linear-search, transform-each
  - **u07** — find-extreme, filter-into-list
  - **u02** — sentinel-loop
  **Reappearance/reuse units (u05, u08, u09, u10) are unchanged** — their lesson Spotlight is a
  *retrieval* one-liner by design (§6: "Which pattern? Which variable is the so-far?"); adding a worked
  example there would defeat retrieval and re-teach. This is a deliberate, documented decision, not an
  omission. u01/u03 host no pattern content → exempt.
- **Ladder form (matches the rest of the lesson).** Immediately AFTER each home `### Pattern Spotlight:
  X` prose cell (which holds the `<!-- pattern: id -->` marker) — and before the next Spotlight/section,
  so when a unit has two homes each ladder sits between its Spotlight and the next — insert a ladder of
  executable `code` rungs, each followed by a `**Notice:**` markdown cell, then one worked "put it
  together" cell + a closing `**Notice:**`. Each rung adds exactly one idea, exactly like L1/L2/L3.
  **Rung count is completeness-driven, NOT capped** (plan 031 rule: as many rungs as the concept needs
  — 2 is typical; the harder patterns take more, e.g. linear-search gets 5 rungs and find-extreme 3, each
  + the put-it-together; never fewer than 2 + the put-it-together). The concrete one-increment rung sequence, fixed
  data, and expected output for ALL SEVEN home patterns are specified in **## Appendix — Ladder
  specifications** below (so within-unit closure + one-increment pacing are reviewable now, matching the
  implementation-ready detail of plans 031–035).
- **Marker + §3 untouched.** The `<!-- pattern: id -->` marker stays in its Spotlight prose cell
  (unchanged, still one-per-introduced, still in-prose). New cells go *after* it — no lesson-marker
  adjacency rule exists (only `exercises.ipynb` requires marker+1 = `## Exercise N`), so
  `pattern-marker`/`technique-spiral` are unaffected. **No pattern is added/dropped/reclassified;
  technique tags and `introduces`/`requires` are UNCHANGED.** The ONE metadata change a slice may make
  is a **regular-concept `practices` add under the General Rule** (map + manifest) *iff* a ladder rung
  makes `concept-scan` detect a regular concept not yet in the unit's union, introduced ≤ the unit and
  not in `introduces` — expected **none**, because ladders reuse the home unit's already-taught concepts.
  (This is the sole reconciliation of "metadata untouched" with the General Rule: technique/`introduces`/
  `requires` never change; a scanner-forced regular-concept `practices` add is the only permitted edit.)
- **Design amendment:** design 002 → **v9** — §6 "Spotlight cell" redefined so the **home** Spotlight in
  the lesson `## Algorithm Extension` carries a graduated worked-example ladder (code rungs + `**Notice:**`
  + a put-it-together cell) consistent with the rest of the lesson; the reappearance Spotlight stays a
  retrieval one-liner. + §13 revision entry. This v9 edit **adds a mandatory student-facing requirement**
  (it does not lift/restructure a constraint like v7/v8) — it is nonetheless in-scope for the plan-review
  gate and needs **no separate design review**, because it adds/drops/re-classifies **no §3 locus** and
  is fully specified + reviewed here. **Activation-during-migration (per plan 048's precedent):** v9
  describes the target end-state; a unit not yet enriched is NOT "violating" v9 — the requirement is met
  unit-by-unit as each home slice (B–E) merges, and the acceptance bar is reached when the last home
  slice lands. **In-class routing:** the home Spotlight's **pattern-naming prose stays read in-class**
  (as v8 already requires); the appended worked-example **ladder is enrichment** routed by teacher-notes
  (time-permitting / homework), so the 60–90 min pacing is unchanged — the ladder deepens the named
  pattern without becoming required in-class instruction.

**Spec:** `docs/designs/002-book1-algorithm-patterns.md` (amend to v9), `docs/plans/048-…md` (the thread
this enriches — sequence behind it), the Book-1 worked-example-ladder precedent (plans 031–035 —
code-rung + `**Notice:**` + put-it-together form), `tools/patterns.py`/`tools/notebooks.py`/
`tools/concept_scan.py` (CI semantics that must stay green).

## Global Constraints

- **Ladders TEACH one increment per rung**, `**Notice:**` after each, ending in a worked put-it-together
  cell — the exact form of L1/L2/L3 in the same lesson. No big-O/sorting/recursion/two-pointers (Book 2).
- **Executable + prereq-clean per unit** (exec-lessons runs them): fixed in-cell data, **no `input(` in
  any EXECUTABLE rung** (the SOLE exception is the u02 sentinel put-it-together, which is `no-exec` +
  interactive by design — see the u02 trap and the Appendix); ONLY concepts introduced ≤ the unit (honor
  each unit's closure exactly as plan 048's drills do — see plan 048's Global-Constraints trap list).
  Per-home-unit traps:
  - **u04** — `while`-only (no `for`/`range`/`list`); no `len`/`sum`/`sorted`/`.split()`; fixed values via
    `if/elif` on a counter.
  - **u06** — `for`/`in-operator`/`break`/`string-methods` OK; **no `ord`/`chr`** (letter values only via
    the lesson's `range(26)` alphabet scan); no `len` (u07) — use a manual `position` counter.
  - **u07** — `list`/`list-append`/`list-loop`/`len` OK; `find-extreme` seeds from the FIRST item (never
    `best = 0`); no `max`/`min`/`sorted`.
  - **u02** — `while`/`comparison`/`random-module` only. CRITICAL: **`accumulator` (`x = x + 1`) is
    NOT in u02's union** (first introduced in u04) and `concept-scan` detects it on any self-referential
    reassignment, so no executed rung may STEP a counter — the executable rungs teach the sentinel
    *condition* with `comparison` (True then False when the guess matches) plus one deterministic `while`
    rung that ends the loop with a plain `guess = secret` assignment (NOT `accumulator`). The
    interactive guessing loop is the **`no-exec` put-it-together** (matching the lesson's existing
    interactive PIT convention — u04 cells 20/40 are `no-exec`): `while guess != secret: guess =
    int(input(...))` is closure-clean (`input` in u02's `requires`, no `accumulator`, `while`/`comparison`
    introduced in u02) and, being `no-exec`, is skipped by `exec-lessons`. So u02 is the one home where
    the put-it-together is `no-exec`; its early rungs still execute.
  Rungs are state-independent (self-contained data), placed AFTER their Spotlight prose cell (and, when a
  unit has two homes, before the next Spotlight) — no earlier cell is affected; preserve/add cell `id`s
  on new cells (avoid nbformat MissingIDFieldWarning).
- **Scanner-derived `practices` (General Rule).** If a ladder rung makes `concept-scan` detect a concept
  not yet in the unit's union, add that exact registry id to `practices` (map + manifest) iff introduced
  ≤ the unit and not in `introduces` — recorded in the ledger. Expected: none (ladders reuse the home
  unit's already-taught concepts).
- **Do not touch:** the `## Algorithm Extension` **exercises**/drills (that is plan 048); the marker /
  §3 / `introduces` / `requires`; reappearance Spotlights; Book 2; governance files. No lesson gets a
  ladder before its 048 slice is on `main`. Branch `feature/plan-049-…`; no commits while a `[sol]`
  review is in flight; `GH_TOKEN=$(cat .gh-token)`; SOLUTIONS/worked-code authored per AGENTS.md
  dispatch (Codex); the content gate blind-reads each ladder for correctness + pedagogy.
- **Ledger contention.** 048 edits `book1/curriculum/pattern-ledger.md` on every slice; 049 writes it
  ONLY if a General-Rule regular-concept `practices` add genuinely fires (expected none). If it does, the
  slice must rebase onto current `main` first (per the branch-refresh mechanics) and re-apply the ledger
  row cleanly — never clobber a concurrent 048 ledger edit.

## Out of scope

- New patterns / drills / exercises; Book 2; reappearance-Spotlight worked examples (retrieval stays);
  re-opening plan 047/048 decisions; any `introduces`/`requires`/§3 change.

## Phases

Dispatch per AGENTS.md: design amendment + ladder authoring + teacher-notes → inline/Codex per the
worked-example precedent; the content gate blind-verifies each ladder. Each unit slice keeps `ci-local`
GREEN and `main` valid. **Ordering follows 048's per-unit merges** (048: B u04 ✓, D u06, E u07, I u02).

### Phase A — Design v9 + ladder conventions + CI/exec probe (docs, ships first)

1. Amend design 002 → **v9**: **update the top status header** (currently "APPROVED — v7") to v9; §6
   requires the home Spotlight in the lesson `## Algorithm Extension` to carry a graduated worked-example
   ladder (code rungs + `**Notice:**` + put-it-together), matching the rest of the lesson; reappearance
   Spotlight stays a retrieval one-liner; + §13 revision entry. No §3 change.
2. Probe (throwaway, reverted): insert a 3-cell ladder after a home Spotlight in u04's lesson and
   confirm ALL checks stay green — `pattern-marker` (marker still in-prose, one-per-introduced, no
   adjacency break), `technique-spiral`, `patterns-doc-check`, `concept-scan`, `exec-lessons` (rungs
   execute; exec order intact), `hygiene`/`cell-lint`. If any check needs a tweak, that tooling change
   ships in Phase A with fault fixtures; expected: none.
- **Acceptance (A):** design v9 committed; probe shows a home-Spotlight ladder passes every check incl.
  exec; no tooling change required (or it ships fault-tested).

### Phases B–E — one slice per HOME unit (author the ladders), gated on the unit's 048 slice

Per home unit, in a single slice: (a) confirm the unit's `## Algorithm Extension` lesson section is on
`main` (its 048 slice merged); (b) after each home `### Pattern Spotlight: X` cell, author its
graduated ladder — the completeness-driven rung sequence specified in the **## Appendix — Ladder
specifications** (executable rungs + `**Notice:**` each + a put-it-together cell) teaching that pattern's
loop shape on the Spotlight's own fixed data, prereq-clean; (c) if teacher-notes describe the extension,
note the home Spotlight now includes a worked build-up (enrichment, still teacher-routed); (d) keep every
check GREEN incl. `exec-lessons`; (e) no marker/§3/`introduces`/`requires` change — a scanner-forced
regular-concept `practices` add (map + manifest, General Rule) is the SOLE permitted metadata edit,
expected none (record "no scanner-derived add" or
the General-Rule add if one is genuinely triggered).

- **Phase B — u04 (running-total, count-by-condition):** 048 Phase B merged → **proceed now.**
- **Phase C — u06 (linear-search, transform-each):** after 048's u06 slice (048 Phase D) merges.
- **Phase D — u07 (find-extreme, filter-into-list):** after 048's u07 slice (048 Phase E) merges.
- **Phase E — u02 (sentinel-loop):** after 048's u02/project slice (048 Phase I) merges. **project-01
  gets VERIFICATION ONLY** — its `sentinel-loop` locus is a *reuse* Spotlight in `brief.ipynb` (048
  frames it as extension prose), not a home; this plan adds NO ladder and NO code cell to `brief.ipynb`,
  only confirms the reappearance prose stays retrieval-shaped.
- **Reappearance / reuse Spotlights get NO ladder (retrieval stays, design §6).** This covers: the
  reuse units **u05/u08/u09/u10**; any **practiced-only** Spotlight that appears inside a home unit
  (e.g. a `count-by-condition` reappearance in u06, or `running-total`/`transform-each` reappearances in
  u07 — those carry no lesson marker and stay retrieval one-liners even though the unit has its own home
  ladder for a *different* pattern); and **project-01**. As each such 048 slice merges, this plan only
  verifies the reappearance Spotlight is retrieval-shaped — no content change. **u01/u03 exempt** (no
  pattern content).

Per-slice acceptance: each home pattern's lesson Spotlight is followed by a graduated worked-example
ladder consistent with L1/L2/L3; rungs execute, prereq-clean, single-pass; marker still in-prose +
one-per-introduced; `ci-local` GREEN incl. the 3 pattern checks + `exec-lessons`; per-PR 4-way content
gate consensus.

### Phase V — Verification (named, mandatory)

`uv run pytest -q` green; `scripts/ci-local.sh` ALL GREEN (incl. the 3 pattern checks + concept checks +
notebook exec/hygiene/cell-lint + PDF + pre-merge guard). **Volume guardrail (plan-037 / design §7,
per PR):** a slice that trips >2× cells / >30% PDF pages / >25% wall-time requires an EXPLICIT
content-gate sign-off recorded in the PR. (A single cell exceeding **120 s** is a HARD `ci-local`
FAILURE, not a waivable growth threshold — split or lighten it; ladder rungs are tiny fixed-data cells,
so this should never trigger.) A home ladder adds ~5–8 cells to a lesson, so
watch the multi-home units (u04, u06, u07). **No CI check enforces ladder presence or quality** (no
tooling change ships): the graduated-ladder form, one-increment pacing, and correctness are
**content-gate-enforced** (reviewers blind-read each rung). **Pedagogy (reviewer-enforced):** every home
pattern's lesson Spotlight now teaches via a graduated ladder (rungs + Notices + put-it-together)
consistent with the rest of the lesson; reappearance Spotlights unchanged; no §3/marker/`introduces`/
`requires` drift (only a General-Rule regular-concept `practices` add if genuinely scanner-forced);
Book 2 stays green. **Acceptance:** design v9; all four home units enriched (as their 048 slices land);
3 pattern checks green; `ci-local` ALL GREEN; `pre-merge-guard --pr` OK; plan-review + per-PR
content-review 4-way consensus. **Rollout:** phased PRs (Phase A first; then B–E as 048 advances), each a
complete slice so `main` stays green.

---

## Plan Review

### Round 1 (HEAD bc9cb7f) — [glm]/[fable] APPROVE WITH NITS · [sol] REJECT

All three confirmed: HOME-only scope is correct + tool-verified (`_expected_markers` gives a lesson
marker only for introduced patterns, in-prose; no lesson adjacency rule); Phase V named; 048-sequencing
is a sound same-file collision strategy; CI-safe (ladders after the prose marker don't perturb
pattern-marker/technique-spiral; exec-lessons runs the rungs). Findings, all folded on this HEAD:

- **[sol] REJECT — 4 blockers, all `[FIXED]`:**
  - `[FIXED]` branch-refresh: added mandatory per-slice "checkout main && pull, fresh/rebased branch,
    re-probe at HEAD" mechanics (was only "verify on main").
  - `[FIXED]` metadata contradiction: stated technique tags + `introduces`/`requires` NEVER change; a
    regular-concept `practices` add is permitted ONLY under the General Rule (scanner-forced, expected
    none) — the sole reconciliation.
  - `[FIXED]` under-specified ladders: added **## Appendix — Ladder specifications** with concrete
    one-increment rung sequences + fixed data + exact expected output for ALL 7 patterns; replaced the
    hard "2–3 rungs" cap with completeness-driven counts (plan 031 rule, up to 4 for harder patterns).
  - `[FIXED]` v9 activation + volume: added the activation-during-migration clause (v9 met unit-by-unit,
    not "violated" pre-migration) and restored the plan-037 volume-signoff guardrail in Phase V.
- **[glm] APPROVE WITH NITS — all folded:** N1 volume guardrail (=sol) `[FIXED]`; N2 v9-framing +
  in-class routing `[FIXED]` (naming prose in-class, ladder is enrichment); N3 "after each Spotlight,
  before the next" wording `[FIXED]`; N4 per-unit prereq traps `[FIXED]`; N5 ladder quality is
  content-gate-enforced (no CI guard) `[FIXED]`; N6 actionable 048-gate grep probe `[FIXED]`; N7
  project-01 verification-only `[FIXED]`; N8 ledger contention note `[FIXED]`.
- **[fable] APPROVE WITH NITS — all folded:** f1 project-01 verification-only (no brief ladder)
  `[FIXED]`; f2 u02 sentinel needs a DETERMINISTIC in-cell driver (no `input`, no `no-exec`) `[FIXED]`
  (constraint + Appendix u02 spec); f3 v9 in-class routing `[FIXED]`; f4 ledger contention `[FIXED]`.
  Also folded sol's non-blocking point: the unchanged-reappearance list now explicitly covers
  practiced-only Spotlights inside home units (u06/u07) + project-01.

Round 2 re-dispatched to all three on the revised HEAD.

### Round 2 (HEAD 8dfe032/f45dbe5) — [glm]/[fable] APPROVE WITH NITS · [sol] REJECT

- **[glm] APPROVE WITH NITS** — all N1–N8 confirmed folded (hand-traced all 7 appendix outputs correct);
  sol's 4 blockers resolved; one residual **N9** (`[FIXED]` in f45dbe5): per-slice step (b) still said
  "2–3-rung" — now defers to the Appendix's completeness-driven count.
- **[fable] APPROVE WITH NITS** — all round-1 findings + sol blockers resolved (hand-traced all 7 outputs
  + closure vs coverage-map). Nits `[FIXED]` in f45dbe5: **f-N1** Appendix preamble now states the
  self-contained "restate prior + one line" rung convention; **f-N2** the two heaviest steps flagged for
  the content gate. **f-N3** (transform-each "`for` [u03]") cosmetic — no change.
- **[sol] REJECT** — reviewed 8dfe032 (before the f45dbe5 nit folds); surfaced real content bugs, all
  now `[FIXED]` in the v3 revision:
  - `[FIXED]` **metadata contradiction** — per-slice step (e) said "no manifest change" while permitting
    a General-Rule `practices` add: reworded to "no marker/§3/`introduces`/`requires` change; a
    scanner-forced regular-concept `practices` add is the SOLE permitted metadata edit, expected none."
  - `[FIXED]` **rung cap** — dropped the "up to 4" / "2–3-rung" cap language for plan-031's uncapped
    completeness-driven rule (linear-search + find-extreme now 3 rungs + PIT).
  - `[FIXED]` **linear-search not one-increment** — inserted an intermediate rung (R2 = walk every char
    with the `in` test, no stop) between the bare `in` and the scan-with-`break`.
  - `[FIXED]` **find-extreme incomplete** — the home now retains the WINNER'S NAME (`best_name` +
    `best_score` over parallel `names`/`scores`, `range(len())`), per the ledger's "Champion by name",
    not a bare numeric max.
  - `[FIXED]` **sentinel-loop closure violation (critical)** — `guess = guess + 1`/`tries = tries + 1`
    trip `accumulator`, which is NOT in u02's union (introduced u04). Rebuilt: executable rungs teach the
    sentinel CONDITION with `comparison` only (`guess != secret` True → False), and the interactive
    input-driven loop is the **`no-exec` put-it-together** (matching u04's no-exec PIT convention;
    closure-clean — `input` in u02, no `accumulator`). Constraint + u02 trap updated accordingly.
  - `[FIXED]` **120 s nit** — separated: >2×cells/>30%PDF/>25%wall-time need sign-off, but a cell >120 s
    is a HARD CI failure, not waivable.

All revised ladders re-executed to their stated outputs (linear-search False/True/False, 1, −1;
find-extreme `Bo 9`; sentinel `True`/`False`). Round 3 re-dispatched to [sol] (+ [glm]/[fable] to
re-confirm the appendix rewrites).

### Round 3 (HEAD 91d558b) — [fable] APPROVE · [glm] APPROVE WITH NITS · [sol] REJECT (2 [OPEN])

[fable] APPROVE (executed every snippet; confirmed the u02 no-exec PIT is *required*, and sol's rebuild
correctly supersedes fable's own round-1 f2 nit). [glm] APPROVE WITH NITS (ran `detect()` over all cells
— zero closure gaps; nits N-A..N-D). [sol] REJECT on two [OPEN] only (all else confirmed resolved). All
folded on this HEAD:

- `[FIXED]` **[sol] OPEN-1 / [glm] N-A** — linear-search R3 still bundled position-counter + conditional
  + `break`: SPLIT into R3 (add ONLY the `position` counter, no stop → prints `1`) and R4 (add ONLY
  `break` → `1`), so each rung is one idea; PIT unchanged (`myth` → `-1`). Content-gate flag reworded —
  the only remaining heavy step is the u04 running-total PIT; linear-search no longer bundles.
- `[FIXED]` **[sol] OPEN-2 / [glm] N-B** — stated the u02 `no-exec` interactive-PIT `input` exception in
  BOTH general rules: the Global-Constraints "no `input` in any EXECUTABLE rung (sole exception: u02
  sentinel PIT)" and the Appendix preamble "executable rungs are `input`-free — the one exception is the
  u02 sentinel put-it-together."
- `[FIXED]` **[glm] N-C** — added an executable deterministic `while` rung to u02 (R3: `guess = 1;
  secret = 7; while guess != secret: guess = secret; print(guess)` → `7`) so the loop shape IS
  CI-exercised (no `accumulator` — `guess = secret` is a plain assign); the interactive version stays the
  `no-exec` PIT.
- `[FIXED]` **[glm] N-D** — Phase A step 1 now updates design 002's top status header (v7 → v9) alongside
  the §6/§13 edits.

Re-executed: linear-search R3 → `1`, R4 → `1`; u02 R3 → `7`. Round 4 re-dispatched to all three.

### Round 4 (HEAD 2af052c) — [glm]/[fable] APPROVE WITH NITS · [sol] REJECT (1 [OPEN])

[glm] APPROVE WITH NITS (N-A..N-D confirmed folded, `detect()` clean, no regression; N-E cosmetic — no
change). [fable] APPROVE WITH NITS (executed every snippet; verified u02 R3 closure via the detector;
f4-N1/f4-N2 cosmetic). [sol] REJECT on ONE [OPEN]: linear-search R3 still bundled the position counter +
a new conditional (not "one new line"). Folded on this HEAD:

- `[FIXED]` **[sol] OPEN (linear-search one-increment)** — fully decomposed to 5 one-idea rungs:
  R1 `in`-test → R2 loop the test → **R3 add ONLY the `position` counter** (prints `0`/`1`/`2`, no
  conditional) → **R4 add ONLY recording the match** in a `found = -1` var via `if` (→ `1`) → **R5 add
  ONLY `break`** (→ `1`) → PIT (`myth` → `-1`). Re-executed: R3 `0/1/2`, R4 `1`, R5 `1`, PIT `-1`.
- `[FIXED]` **convention wording (sol's literalism)** — "adds exactly one new line" → "adds exactly ONE
  NEW IDEA (one concept; usually one line, occasionally two inseparable ones — a counter's init+increment,
  or recording a match via an `if`)", matching the plans 031–035 precedent [glm]/[fable] verified.
- `[FIXED]` **[fable] f4-N1** — the stale u02 "condition with `comparison` only" wording (Global trap +
  Appendix preamble) now names the executable `while` rung R3 (`guess = secret`, no `accumulator`).
- **[glm] N-E / [fable] f4-N2** — cosmetic (`print` placement) — WONTFIX; the split resolves the substance.

Round 5 re-dispatched to all three (linear-search is now 5 rungs).

### Round 5 (HEAD 9d46332) — CONSENSUS: all four APPROVE / APPROVE WITH NITS ✅ — GATE CLOSED

- **[self] APPROVE** — all findings folded; every ladder re-executed to its stated output.
- **[glm] APPROVE WITH NITS** — 5-rung linear-search verified rung-by-rung + `detect()` closure-clean;
  pytest 50 passed, all pattern/coverage/prereq checks PASS; no regression. Nit **N-F** (`[FIXED]`):
  line 46 "3 rungs" stale → "linear-search gets 5 rungs and find-extreme 3".
- **[fable] APPROVE** — executed every rung (R1 True, R2 F/T/F, R3 0/1/2, R4 1, R5 1, PIT −1); one idea
  per rung genuinely satisfied; no regression.
- **[sol] APPROVE WITH NITS** — the split resolves its round-4 one-increment objection; confirmed R4
  (found-init + guarded assign) is ONE idea under the corrected rule and the plan 031/034/035 precedent
  (inseparable init+update accepted). Only nit = N-F (`[FIXED]`).

**4-way consensus: all four APPROVE / APPROVE WITH NITS, no open blockers. Plan-review gate CLOSED.**
Cleared to implement (Phase A → Phase B u04 + Phase C u06, both 048-ready → Phases D/E as 048 advances).

## Content Review

_(4-way gate — pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

### Phase B — u04 (running-total + count-by-condition ladders) — CONSENSUS: all four APPROVE ✅

All three externals independently executed the 6 rungs — running-total 5/8/16, count-by-condition 1/1/2
— confirmed one-increment, closure-clean (while-only; `accumulator` in u04's union; no
`for`/`range`/`list`/`len`/`sum`/`.split`/`input`), markers unchanged/in-prose, manifest+coverage-map
byte-unchanged, and the L1/L2/L3 form. [glm] ran all 12 book1 checks PASS. [fable] + [sol] accepted the
running-total PIT bundling (its `while`+`if/elif` scaffold was already taught in the same lesson's
SUDDEN DEATH ladder).

- **[self] APPROVE** — ci-local ALL GREEN, exit 0.
- **[fable] APPROVE** — zero findings.
- **[sol] APPROVE** — zero findings.
- **[glm] APPROVE WITH NITS** — one Should-Fix `[FIXED]`: u04 teacher-notes line 21 still said "Read the
  two Pattern Spotlights ... here" though each Spotlight now carries a 6-cell enrichment ladder →
  reworded to "NAME the two patterns from their Spotlights (one-line hook each) in-class; the worked
  ladders that follow are enrichment (time-permitting / homework), 60–90 min budget unchanged" (design
  v9 in-class routing).

**Gate CLOSED — 4-way consensus, no open blockers.** Cleared to merge Phase B.

### Phase C — u06 (linear-search 5-rung + transform-each 3-cell ladders) — CONSENSUS: all four APPROVE ✅

All three externals executed the 9 rungs — linear-search True / F,T,F / 0,1,2 / 1 / 1 / −1, transform-each
H / HI / HI — confirmed one-increment (R3 counter only, R4 record-match only, R5 break only), closure-clean
(for/in/break/string-methods/accumulator; NO `len`/`ord`/`chr`/`.split`/`input`; manual `position`), markers
byte-unchanged/in-prose, manifest+coverage-map byte-unchanged, L1/L2/L3 form. [sol] verified the R4→R5
last-vs-first distinction with a multi-vowel witness (`idea`: R4 last=3 vs R5 first=0).

- **[self] APPROVE** — ci-local ALL GREEN.
- **[fable] APPROVE** — fresh-namespace execution; `concept-scan` 0 findings (no General-Rule add).
- **[sol] APPROVE** — zero findings.
- **[glm] APPROVE WITH NITS** — two Nice-to-Have: (1) `[FIXED]` R4 Notice now notes it keeps the LATEST
  match and R5's `break` keeps the FIRST (forward pointer for a curious multi-vowel probe); (2) R3's
  unused `ch` loop var — `[WONTFIX]` (cosmetic; the loop legitimately counts characters, Notice explains).

**Gate CLOSED — 4-way consensus, no open blockers.** Cleared to merge Phase C.

### Phase D — u07 (find-extreme "Champion by name" 4-rung + filter-into-list 3-cell) — CONSENSUS: all four APPROVE ✅

All three externals blind-solved the 7 rungs — find-extreme Ada 3 / Bo 9 / Cy 5 / Bo 9 (retains the
winner's NAME per design §3 / ledger "Champion by name", not a bare max), filter [9] / [9] / [9,5,7] —
confirmed one-increment, closure-clean (list/list-append/list-loop/range/len/comparison; NO
max/min/sorted; `best_name = names[i]` not accumulator), markers byte-unchanged/in-prose,
manifest+coverage-map byte-unchanged, L1/L2/L3 form.

- **[self] APPROVE** — ci-local ALL GREEN.
- **[fable] APPROVE** — zero findings (isolated + full-run execution).
- **[sol] APPROVE** — zero findings.
- **[glm] APPROVE WITH NITS** — two Nice-to-Have: (1) R3 (the `i`-index bridge) departs from strict
  restate-prior wording but is verbatim the Appendix's "index that ties name↔score" — `[WONTFIX]` (glm:
  "no change required"); (2) `[FIXED]` u07 teacher-notes now notes each naming Spotlight is followed by a
  worked-example ladder that is part of the enrichment (not required in-class).

**Gate CLOSED — 4-way consensus, no open blockers.** Cleared to merge Phase D. (u02 = Phase E, awaits
048 Phase I.)

## Post-Execution Report

_(appended per slice as it lands.)_

---

## Appendix — Ladder specifications (all 7 home patterns)

Each ladder is `code` rung → `**Notice:**` → … → a "put it together" `code` rung → closing `**Notice:**`,
placed right after the home `### Pattern Spotlight` prose cell. All rungs are executable (exec-lessons),
fixed-data, and within the unit's closure; **executable rungs are `input`-free — the ONE exception is the
u02 sentinel put-it-together, which is `no-exec` + interactive (uses `input`)**, matching the lesson's
existing interactive-PIT convention (u04 cells 20/40 are `no-exec`). Rung counts are completeness-driven
(plan 031); these are the authoring targets — the content gate confirms embodiment and may add a rung
where a step is too big. Expected outputs are exact. **Rung self-containedness (plans 031–035
convention):** each rung is a COMPLETE runnable cell — it RESTATES the prior rung's lines and adds exactly
ONE NEW IDEA (one concept per rung; usually one line, occasionally two that are inseparable — a counter's
`= 0` init plus its `+ 1` increment, or recording a match in a `found` variable via an `if`). The
shorthand below (e.g. R2 "add a second score → 8") means "the prior rung's code plus that one idea," NOT
a continuation cell depending on the prior rung's leftover state. The "→ output" shown is the full rung's
own output. **Content-gate flag:** the heaviest single step is the u04 running-total
put-it-together (introduces `while` + round counter + `if/elif` dispatch at once) — the gate should split
it into an extra rung if it reads as too big for one increment. (linear-search is now split
R1→R2→R3→R4→R5, one idea each — test → loop → counter → record-match → break —
so no single rung bundles counter + conditional + `break`.)

### u04 — running-total (`while`-only, no list)
- **R1** `total = 0` / `total = total + 5` / `print(total)` → `5`. *Notice:* start the running total at 0,
  then add the first score — the box holds 5.
- **R2** add a second score (`total = total + 3`) → `8`. *Notice:* each new score builds on the
  total-so-far, so it climbs to 8.
- **Put-it-together** `while round_number <= 3` with `if/elif` scores 5, 3, 8 feeding one `total` → `16`.
  *Notice:* the loop feeds one score per round into the same running total — 5, 8, 16.

### u04 — count-by-condition (`while`-only)
- **R1** `count = 0` / `score = 7` / `if score >= 5: count = count + 1` / `print(count)` → `1`.
  *Notice:* the counter moves only when the check passes (7 ≥ 5).
- **R2** a second check that FAILS (`score = 3`) → still `1`. *Notice:* 3 fails the test, so nothing is
  added — count each item once, bump only on a match.
- **Put-it-together** `while` over 7, 3, 8 counting `score >= 5` → `2`. *Notice:* one pass; 7 and 8 pass,
  3 does not, so 2.

### u06 — transform-each (`for` [u03], string-methods [u06]; no `ord`/`chr`)
- **R1** `result = ""` / `result = result + "h".upper()` / `print(result)` → `H`. *Notice:* transform one
  character and add it to the new string.
- **R2** a second manual append (`result = result + "i".upper()`) → `HI`. *Notice:* the same step applied
  again grows the transformed string.
- **Put-it-together** `word = "hi"` / `result = ""` / `for ch in word: result = result + ch.upper()` →
  `HI`. *Notice:* the loop applies the same transform to every character.

### u06 — linear-search (`for` + `break` + `in`, manual `position` counter; no `len`; 5 rungs — the hardest pattern, ONE idea per rung)
- **R1** `print("a" in "aeiou")` → `True`. *Notice:* `in` tests ONE character against the vowels.
- **R2** *(new idea: the loop)* `word = "cat"` / `for ch in word: print(ch in "aeiou")` → `False` /
  `True` / `False`. *Notice:* run the same `in` test on each character in turn — 'a' is the vowel.
- **R3** *(new idea: a position counter — no conditional, no stop)* `word = "cat"` / `position = 0` /
  `for ch in word: print(position)` … `position = position + 1` → `0` / `1` / `2`. *Notice:* a `position`
  counter, stepped once per character, tracks WHERE we are (`accumulator` is fine — introduced u04 ≤ u06).
- **R4** *(new idea: record the matching position)* add `found = -1` and, in the loop, `if ch in
  "aeiou": found = position`; after the loop `print(found)` → `1`. *Notice:* instead of printing every
  step, remember the index of the vowel in `found` (a `-1` stand-in for "none yet", no `None`).
- **R5** *(new idea: stop early — exactly one added line)* add `break` right after `found = position` →
  `1`. *Notice:* `break` STOPS at the FIRST vowel instead of scanning the rest; same index, less work.
- **Put-it-together** scan `word = "myth"` (no vowel) → `found` stays `-1` → `-1`. *Notice:* the loop
  falls through and the `-1` stand-in reports "not found" — a search returns early on a hit or ends with
  the not-found stand-in.

### u07 — find-extreme = "Champion by name" (argmax retaining the WINNER'S NAME; `list`, `range(len())`, comparison; seed from the FIRST item)
_The home embodiment (per the ledger) tracks `best_name` AND `best_score` together — NOT just a number —
so the pattern answers "who is the champion?", not merely "what is the top score?"._
- **R1** `names = ["Ada", "Bo", "Cy"]` / `scores = [3, 9, 5]` / `best_name = names[0]` / `best_score =
  scores[0]` / `print(best_name, best_score)` → `Ada 3`. *Notice:* seed the champion from the FIRST
  player — never `best_score = 0` (a real score could be lower / all-negative).
- **R2** compare the next player and update BOTH together: `if scores[1] > best_score: best_name =
  names[1]` … `best_score = scores[1]` / `print(best_name, best_score)` → `Bo 9`. *Notice:* a higher score
  crowns a new champion — update the name and the score as a pair, or the name drifts from the score.
- **R3** *(the index that ties name↔score)* show reading a player by position: `i = 2` / `print(names[i],
  scores[i])` → `Cy 5`. *Notice:* `names[i]` and `scores[i]` are the same player — the loop will walk `i`
  over both lists in step.
- **Put-it-together** `best_name = names[0]` / `best_score = scores[0]` / `for i in range(len(scores)): if
  scores[i] > best_score: best_name = names[i]` … `best_score = scores[i]` / `print(best_name,
  best_score)` over the three players → `Bo 9`. *Notice:* one pass keeps the highest-scoring player's NAME
  and score — the champion, not just the number.

### u07 — filter-into-list (`list-append`, comparison)
- **R1** `kept = []` / `kept.append(9)` / `print(kept)` → `[9]`. *Notice:* start an empty result list and
  append a keeper.
- **R2** check-before-append that FAILS (`score = 3` / `if score >= 5: kept.append(score)`) → `[9]`.
  *Notice:* 3 fails the test, so it is not kept — only matches are appended.
- **Put-it-together** `for s in [3, 9, 5, 7]: if s >= 5: kept.append(s)` → `[9, 5, 7]`. *Notice:* one pass
  copies just the qualifying scores into the new list.

### u02 — sentinel-loop (`while`/`comparison`; early rungs teach the CONDITION — NO `accumulator`; interactive put-it-together is `no-exec`)
_u02 has no `accumulator` (first introduced u04) and no counter may be stepped in an executed rung, so the
executable rungs teach the sentinel **condition** with `comparison` (R1/R2) and end the loop with a plain
`guess = secret` assignment in one executable `while` rung (R3, no `accumulator`); the real input-driven
loop is the `no-exec` put-it-together, matching the lesson's interactive-PIT convention (u04 cells 20/40
are `no-exec`)._
- **R1** `guess = 3` / `secret = 7` / `print(guess != secret)` → `True`. *Notice:* while the guess does
  NOT equal the secret, the condition is True — the loop keeps going.
- **R2** `guess = 7` / `secret = 7` / `print(guess != secret)` → `False`. *Notice:* the moment the guess
  matches, the condition is `False` and the loop STOPS — that match is the sentinel.
- **R3** *(the loop shape, executable + deterministic — no `accumulator`, no `input`)* `guess = 1` /
  `secret = 7` / `while guess != secret: guess = secret` / `print(guess)` → `7`. *Notice:* the `while`
  repeats as long as `guess != secret`; here one pass sets `guess` to the secret, the condition turns
  `False`, and the loop ends — the sentinel in action. (`guess = secret` is a plain assignment, NOT
  `accumulator`, so it stays inside u02's closure and runs under CI.)
- **Put-it-together** *(`no-exec` — interactive, not run by CI)* `import random` / `secret =
  random.randint(1, 10)` / `guess = 0` / `while guess != secret: guess = int(input("Guess: "))` /
  `print("Got it!")`. *Notice:* the real game — the loop repeats, reading a new guess each time, until the
  guess equals the secret (the sentinel that ends it). Interactive, so this cell is `no-exec`. *(Closure-clean: `input` in u02's `requires`, `random-module`/
  `while`/`comparison` in u02; NO `accumulator` — `guess = int(input(...))` reassigns from input, not
  from itself.)*

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
home units follow as their 048 slices land. Before each slice, verify on `main` that the unit's
`## Algorithm Extension` lesson section exists (its 048 slice merged) — otherwise wait.

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
  X` prose cell (which holds the `<!-- pattern: id -->` marker), insert a ladder of **2–3 executable
  `code` rungs**, each followed by a `**Notice:**` markdown cell, then one worked "put it together"
  cell — e.g. running-total: rung 1 = a single accumulator update on fixed values → rung 2 = the update
  inside a `while` loop → put-it-together = the running total over the Spotlight's fixed data, with a
  final `**Notice:**`. Each rung adds exactly one idea, exactly like L1/L2/L3.
- **Marker + §3 untouched.** The `<!-- pattern: id -->` marker stays in its Spotlight prose cell
  (unchanged, still one-per-introduced, still in-prose). New cells go *after* it — no lesson-marker
  adjacency rule exists (only `exercises.ipynb` requires marker+1 = `## Exercise N`), so
  `pattern-marker`/`technique-spiral` are unaffected. **No pattern is added/dropped/reclassified; no
  `introduces`/`practices`/`requires` change** — this is pure teaching enrichment.
- **Design amendment:** design 002 → **v9** — §6 "Spotlight cell" redefined so the **home** Spotlight in
  the lesson `## Algorithm Extension` carries a graduated worked-example ladder (code rungs + `**Notice:**`
  + a put-it-together cell) consistent with the rest of the lesson; the reappearance Spotlight stays a
  retrieval one-liner. + §13 revision entry. Constraint-restructuring only (no §3 locus change).

**Spec:** `docs/designs/002-book1-algorithm-patterns.md` (amend to v9), `docs/plans/048-…md` (the thread
this enriches — sequence behind it), the Book-1 worked-example-ladder precedent (plans 031–035 —
code-rung + `**Notice:**` + put-it-together form), `tools/patterns.py`/`tools/notebooks.py`/
`tools/concept_scan.py` (CI semantics that must stay green).

## Global Constraints

- **Ladders TEACH one increment per rung**, `**Notice:**` after each, ending in a worked put-it-together
  cell — the exact form of L1/L2/L3 in the same lesson. No big-O/sorting/recursion/two-pointers (Book 2).
- **Executable + prereq-clean per unit** (exec-lessons runs them): fixed in-cell data, **no `input(`**
  in any rung; ONLY concepts introduced ≤ the unit (u04 `while`-only, no `for`/`range`/`list`/`len`/
  `sum`/`.split()`; honor each unit's closure exactly as plan 048's drills do). Rungs are
  state-independent (self-contained data) and sit at the END of the lesson so no earlier cell is
  affected; preserve cell `id`s / add ids on new cells (avoid nbformat MissingIDFieldWarning).
- **Scanner-derived `practices` (General Rule).** If a ladder rung makes `concept-scan` detect a concept
  not yet in the unit's union, add that exact registry id to `practices` (map + manifest) iff introduced
  ≤ the unit and not in `introduces` — recorded in the ledger. Expected: none (ladders reuse the home
  unit's already-taught concepts).
- **Do not touch:** the `## Algorithm Extension` **exercises**/drills (that is plan 048); the marker /
  §3 / `introduces` / `requires`; reappearance Spotlights; Book 2; governance files. No lesson gets a
  ladder before its 048 slice is on `main`. Branch `feature/plan-049-…`; no commits while a `[sol]`
  review is in flight; `GH_TOKEN=$(cat .gh-token)`; SOLUTIONS/worked-code authored per AGENTS.md
  dispatch (Codex); the content gate blind-reads each ladder for correctness + pedagogy.

## Out of scope

- New patterns / drills / exercises; Book 2; reappearance-Spotlight worked examples (retrieval stays);
  re-opening plan 047/048 decisions; any `introduces`/`requires`/§3 change.

## Phases

Dispatch per AGENTS.md: design amendment + ladder authoring + teacher-notes → inline/Codex per the
worked-example precedent; the content gate blind-verifies each ladder. Each unit slice keeps `ci-local`
GREEN and `main` valid. **Ordering follows 048's per-unit merges** (048: B u04 ✓, D u06, E u07, I u02).

### Phase A — Design v9 + ladder conventions + CI/exec probe (docs, ships first)

1. Amend design 002 → **v9**: §6 requires the home Spotlight in the lesson `## Algorithm Extension` to
   carry a graduated worked-example ladder (code rungs + `**Notice:**` + put-it-together), matching the
   rest of the lesson; reappearance Spotlight stays a retrieval one-liner; + §13 entry. No §3 change.
2. Probe (throwaway, reverted): insert a 3-cell ladder after a home Spotlight in u04's lesson and
   confirm ALL checks stay green — `pattern-marker` (marker still in-prose, one-per-introduced, no
   adjacency break), `technique-spiral`, `patterns-doc-check`, `concept-scan`, `exec-lessons` (rungs
   execute; exec order intact), `hygiene`/`cell-lint`. If any check needs a tweak, that tooling change
   ships in Phase A with fault fixtures; expected: none.
- **Acceptance (A):** design v9 committed; probe shows a home-Spotlight ladder passes every check incl.
  exec; no tooling change required (or it ships fault-tested).

### Phases B–E — one slice per HOME unit (author the ladders), gated on the unit's 048 slice

Per home unit, in a single slice: (a) confirm the unit's `## Algorithm Extension` lesson section is on
`main` (its 048 slice merged); (b) after each home `### Pattern Spotlight: X` cell, author a 2–3-rung
graduated ladder (executable rungs + `**Notice:**` each + a put-it-together cell) teaching that pattern's
loop shape on the Spotlight's own fixed data, prereq-clean; (c) if teacher-notes describe the extension,
note the home Spotlight now includes a worked build-up (enrichment, still teacher-routed); (d) keep every
check GREEN incl. `exec-lessons`; (e) no marker/§3/manifest change (record "no scanner-derived add" or
the General-Rule add if one is genuinely triggered).

- **Phase B — u04 (running-total, count-by-condition):** 048 Phase B merged → **proceed now.**
- **Phase C — u06 (linear-search, transform-each):** after 048's u06 slice (048 Phase D) merges.
- **Phase D — u07 (find-extreme, filter-into-list):** after 048's u07 slice (048 Phase E) merges.
- **Phase E — u02 (sentinel-loop) + project-01:** after 048's u02/project slice (048 Phase I) merges.
- **Reuse units u05/u08/u09/u10:** NO lesson ladder (retrieval Spotlight stays per design §6). As each
  048 reuse slice merges, this plan only verifies the reappearance Spotlight is retrieval-shaped — no
  content change. u01/u03 exempt.

Per-slice acceptance: each home pattern's lesson Spotlight is followed by a graduated worked-example
ladder consistent with L1/L2/L3; rungs execute, prereq-clean, single-pass; marker still in-prose +
one-per-introduced; `ci-local` GREEN incl. the 3 pattern checks + `exec-lessons`; per-PR 4-way content
gate consensus.

### Phase V — Verification (named, mandatory)

`uv run pytest -q` green; `scripts/ci-local.sh` ALL GREEN (incl. the 3 pattern checks + concept checks +
notebook exec/hygiene/cell-lint + PDF + pre-merge guard). **Pedagogy (reviewer-enforced):** every home
pattern's lesson Spotlight now teaches via a graduated ladder (rungs + Notices + put-it-together)
consistent with the rest of the lesson; reappearance Spotlights unchanged; no §3/marker/manifest drift;
Book 2 stays green. **Acceptance:** design v9; all four home units enriched (as their 048 slices land);
3 pattern checks green; `ci-local` ALL GREEN; `pre-merge-guard --pr` OK; plan-review + per-PR
content-review 4-way consensus. **Rollout:** phased PRs (Phase A first; then B–E as 048 advances), each a
complete slice so `main` stays green.

---

## Plan Review

_(4-way gate — consensus = all four APPROVE / APPROVE WITH NITS, no open blockers.)_

## Content Review

_(4-way gate — pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

## Post-Execution Report

_(appended per slice as it lands.)_

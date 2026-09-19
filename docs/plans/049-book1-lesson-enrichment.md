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
  **Rung count is completeness-driven, NOT a fixed cap** (plan 031 rule: as many rungs as the concept
  needs — typically 2, up to 4 for a harder pattern like find-extreme's first-item seed or the sentinel
  stop-rule; never fewer than 2 + the put-it-together). The concrete one-increment rung sequence, fixed
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
- **Executable + prereq-clean per unit** (exec-lessons runs them): fixed in-cell data, **no `input(`**
  in any rung; ONLY concepts introduced ≤ the unit (honor each unit's closure exactly as plan 048's
  drills do — see plan 048's Global-Constraints trap list). Per-home-unit traps:
  - **u04** — `while`-only (no `for`/`range`/`list`); no `len`/`sum`/`sorted`/`.split()`; fixed values via
    `if/elif` on a counter.
  - **u06** — `for`/`in-operator`/`break`/`string-methods` OK; **no `ord`/`chr`** (letter values only via
    the lesson's `range(26)` alphabet scan); no `len` (u07) — use a manual `position` counter.
  - **u07** — `list`/`list-append`/`list-loop`/`len` OK; `find-extreme` seeds from the FIRST item (never
    `best = 0`); no `max`/`min`/`sorted`.
  - **u02** — `while`/`comparison` only; **the sentinel driver must be a deterministic in-cell value**
    (e.g. an arithmetic-stepped guess converging to a fixed secret), NOT `input()` — the rung executes
    under `exec-lessons`, so a `no-exec` tag is FORBIDDEN here (it would silently evade execution).
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
per PR):** a slice that trips >2× cells / >30% PDF pages / >25% wall-time (or any cell >120 s) requires
an EXPLICIT content-gate sign-off recorded in the PR — a home ladder adds ~5–8 cells to a lesson, so
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

## Content Review

_(4-way gate — pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

## Post-Execution Report

_(appended per slice as it lands.)_

---

## Appendix — Ladder specifications (all 7 home patterns)

Each ladder is `code` rung → `**Notice:**` → … → a "put it together" `code` rung → closing `**Notice:**`,
placed right after the home `### Pattern Spotlight` prose cell. All rungs are executable (exec-lessons),
fixed-data, `input`-free, and within the unit's closure. Rung counts are completeness-driven (plan 031);
these are the authoring targets — the content gate confirms embodiment and may add a rung where a step is
too big. Expected outputs are exact.

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

### u06 — linear-search (`for` + `break` + `in`, manual `position` counter; no `len`)
- **R1** `print("a" in "aeiou")` → `True`. *Notice:* `in` tests one character against the vowels.
- **R2** scan `word = "cat"` with a `position` counter, `break` at the first vowel → `1`. *Notice:* stop
  the instant a vowel is found; `position` holds its index.
- **Put-it-together** scan `word = "myth"` with `found = -1` stand-in (no `None`), `break` on a vowel →
  `-1`. *Notice:* no vowel, so the `-1` stand-in reports "not found" — search returns early on a hit or
  falls through to the stand-in.

### u07 — find-extreme (`list`, list-loop, comparison; seed from the FIRST item)
- **R1** `scores = [3, 9, 5]` / `best = scores[0]` / `print(best)` → `3`. *Notice:* seed `best` from the
  first item — never `best = 0` (a real score could be lower or all-negative).
- **R2** compare the next (`if scores[1] > best: best = scores[1]`) → `9`. *Notice:* keep the bigger of
  the two.
- **Put-it-together** `for s in scores: if s > best: best = s` over `[3, 9, 5]` → `9`. *Notice:* one pass
  keeping the biggest-so-far gives the maximum.

### u07 — filter-into-list (`list-append`, comparison)
- **R1** `kept = []` / `kept.append(9)` / `print(kept)` → `[9]`. *Notice:* start an empty result list and
  append a keeper.
- **R2** check-before-append that FAILS (`score = 3` / `if score >= 5: kept.append(score)`) → `[9]`.
  *Notice:* 3 fails the test, so it is not kept — only matches are appended.
- **Put-it-together** `for s in [3, 9, 5, 7]: if s >= 5: kept.append(s)` → `[9, 5, 7]`. *Notice:* one pass
  copies just the qualifying scores into the new list.

### u02 — sentinel-loop (`while`, comparison; DETERMINISTIC driver, no `input`, no `no-exec`)
- **R1** `guess = 3` / `secret = 7` / `print(guess != secret)` → `True`. *Notice:* the loop keeps going
  while the guess does not equal the secret.
- **R2** one step (`guess = guess + 1`) → `4`. *Notice:* each try moves the guess closer.
- **Put-it-together** `secret = 7` / `guess = 1` / `tries = 0` / `while guess != secret: guess = guess +
  1; tries = tries + 1` / `print(tries)` → `6`. *Notice:* the loop repeats until the sentinel condition
  (`guess == secret`) is met — a fixed driver, so it runs the same way every time (the graded exercise
  uses a real `input()` guess; the lesson rung stays deterministic so it executes under CI).

# Plan 048 — Book 1 Algorithm-Extension Consolidation + Loop-Mastery Drills

**Goal:** (1) **Consolidate** all algorithm-pattern content into an explicit **"Algorithm Extension"**
section at the end of each unit's `lesson.ipynb` and `exercises.ipynb` (migrating the plan-047 exercises
that currently sit interleaved among the core exercises), and (2) **expand** it with a large bank of
**simple, linear, single-pass loop drills** — counting, summing, searching, find-best, map, filter,
sentinel — with deliberate *repetition-with-variety* (the "until-threshold" matrix and its neighbours),
focused on the loop-light units (u04, u05, u06, u09, u10). The algorithm track becomes an explicit,
clearly-labelled **enrichment extension**, not interleaved core.

**Architecture:**
- **Student-facing structure (new):** every unit's `exercises.ipynb` ends with a `# Algorithm Extension`
  header; all pattern-tagged exercises (relocated from their interleaved positions) plus the new drills
  live there, as the last `## Exercise N` before the trailing `## Challenge` (stretch) cells. Numbering
  stays `## Exercise N` (so `structure-check`/`solutions_structure` heading-pairing and `stretch-check`
  are unaffected); the algo exercises are simply the highest-numbered core exercises. Each unit's
  `lesson.ipynb` gathers its pattern Spotlight(s) under a closing `## Algorithm Extension` markdown
  section. `<!-- pattern: id -->` markers stay immediately before their exercise/inside their Spotlight,
  so `pattern-marker`/`technique-spiral` are unaffected.
- **Enrichment framing:** the extension is end-of-lesson enrichment, **not required in-class**. This
  **relaxes design 002's "home is in-class" rule** (which reviewers repeatedly flagged); teacher-notes
  route the whole extension as time-permitting / homework / differentiation.
- **New drills:** mostly **unmarked** reps (the one-marker-per-technique-per-unit CI rule stands), plus a
  few **new tagged loci** where a unit currently lacks a pattern it can now host (running-total in
  u06/u08/u10; count-by-condition / linear-search / transform-each in u10) — each new locus satisfies
  the spiral (≥3 core), one marker, a catalog-consistent generation, and a ledger row.
- **Design amendment:** design 002 → **v8** (§6 student-facing form redefined as the Algorithm Extension
  section; the in-class-home requirement relaxed to extension-enrichment). Constraint-restructuring only;
  no §3 pattern locus is dropped or re-classified.

**Spec:** `docs/designs/002-book1-algorithm-patterns.md` (to be amended to v8 — the pattern-thread
authority), `docs/plans/047-book1-algorithm-patterns.md` (the shipped thread this restructures + extends),
`tools/patterns.py` / `tools/notebooks.py` / `tools/curriculum.py` / `tools/concept_scan.py` (the CI
semantics that must stay green), `docs/plans/037-book1-exercise-mastery.md` (Phase-V volume thresholds +
the ≥3/≥5 quantity goal + the "favor volume" preference). Reviewer proposal banks ([fable] + [sol],
2026-09-18) are captured in **## Appendix — Exercise inventory**.

## Global Constraints

- **Single-pass, linear algorithms ONLY.** No big-O/complexity, no sorting internals, no recursion, no
  two-pointers / prefix sums / graphs (all Book 2). Framing stays qualitative. Every drill is one loop
  over one sequence.
- **Deliberate repetition is the GOAL.** It is explicitly desired to add many exercises of the SAME shape
  with small data/threshold/theme/boundary variations, so students meet each loop job repeatedly. Favor
  volume + variety (see [[exercise-sets-favor-volume]]; no per-unit exercise-count ceiling — design 002
  v7).
- **Prereq closure per unit (hard).** Every exercise uses ONLY concepts introduced ≤ its unit. Documented
  traps that `practices` CANNOT fix: **u04** has no `for`/`range`/`list` (all loops are counter-bounded
  `while` on fixed/typed values); **`len`** is u07 (`builtin-functions`) — before u07 use a manual
  `position`/`count` counter; **never** `sum`/`sorted`/`abs`/`round`/`.count()`/`.index()`/`enumerate`/
  comprehensions/tuples-multi-return; **no `.split()`** (`str-split` is unregistered — use alternating
  lines or parallel files, not `"name,score"`); **no `None`/`continue`** (use a `"not found"`/`-1`
  stand-in or a `found` boolean); **`min` init** — seed from the first item / a `first = True` flag (never
  `best = 0`).
- **Scanner-derived `practices` (General Rule, plan-016/037/047 precedent).** When a new drill makes
  `concept-scan` detect a concept not yet in the entry's union, add that exact registry id to the entry's
  `practices` (map + manifest) iff it is introduced ≤ the entry, not in the entry's `introduces`, no
  `introduces`/`requires` change — recorded in the ledger + surfaced at the content gate. Anticipated adds
  are enumerated per unit in the Appendix.
- **Markers / tagging.** One `<!-- pattern: id -->` marker per technique per unit (CI rule). Extra reps of
  an already-tagged pattern are **unmarked** (their Spotlight prose may still ask "which pattern is
  this?"). A unit becomes a NEW tagged locus for a pattern only via: id in `practices` (map+manifest),
  exactly one comment-only marker immediately before the `## Exercise N` heading, regenerated
  `patterns.md` (committed == generated), a ledger row, and the spiral still ≥3 core.
- **Stretch preservation.** Never drop a unit below ≥2 `stretch`-tagged Challenge cells
  (`notebooks.py:538`). Relocations must not untag Challenges; new drills are core (non-stretch) unless
  explicitly a Challenge.
- **Numbering discipline.** Algo exercises are the last `## Exercise N` (before the `## Challenge` block).
  Renumber synced across `exercises.ipynb` ↔ `solutions.ipynb`; update every teacher-notes exercise-number
  reference on renumber; keep `## Exercise N` headings (do NOT invent `## Exercise A1`-style headings that
  `solutions_structure`'s `^## Exercise \d+` regex would miss).
- **No literal `input(` token in any solution cell** (`structure-check` flags it textually — including in
  comments); solutions use fixed stand-in data. `input()`-driven exercises are `no-exec`-tagged.
- **Volume guardrail.** Carry plan-037 Phase-V thresholds (>2× cells / >30% PDF pages / >25% wall-time =
  content-gate sign-off; 120 s/cell). u07/u08/u09 already carry the broadest core load — route their new
  reps mostly to the extension's own More-Practice tier and watch the 2×-cells budget.
- **Do not touch:** `introduces`/`requires` for regular concepts (technique tags + General-Rule
  scanner-derived `practices` only); Book 2 anything; governance files. Branch `feature/plan-048-…`; no
  commits while a `[sol]` review is in flight; `GH_TOKEN=$(cat .gh-token)`; SOLUTIONS authored per the
  AGENTS.md dispatch (Codex, separate from statements; the content gate blind-solves).

## Out of scope

- New algorithm *patterns* or Book 2 growth; big-O/sorting/recursion; a `patterns.yaml`; re-opening
  plan-037/047 coverage decisions. The 7 §3 patterns are fixed — this plan re-homes their exercises and
  adds reps, it does not add/drop/reclassify a pattern.

## Phases

Dispatch per AGENTS.md: design amendment + metadata/markers/teacher-notes + the relocation mechanics →
inline (curriculum architecture); new exercise STATEMENTS → Codex; SOLUTIONS → separate fresh Codex
session; the content gate blind-solves. Each unit slice keeps `ci-local` GREEN and `main` valid.

### Phase A — Design v8 + Algorithm-Extension conventions (docs/tooling, ships first)

1. Amend `docs/designs/002-…` to **v8**: §6 redefines the student-facing form as the end-of-notebook
   `# Algorithm Extension` section (lesson Spotlights + exercises gathered there); relax "home in-class"
   → "extension enrichment, routed by teacher-notes"; note the numbering/marker rules keep CI green. No
   §3 locus change → constraint-restructuring, no design re-review beyond the plan gate.
2. Confirm (with a probe, not a code change) that the CI checks are agnostic to a `# Algorithm Extension`
   header: `structure-check`/`solutions_structure` pair by `## Exercise N`; `pattern-marker` adjacency is
   marker→heading regardless of a preceding section header; `stretch-check` counts tagged cells anywhere.
   If any check needs a tweak to tolerate the section header, that tooling change is part of Phase A
   (Codex) with fault fixtures; expected: none needed.
- **Acceptance (A):** design v8 committed; a scratch probe shows a relocated-into-`# Algorithm Extension`
  arrangement passes all checks; no tooling change required (or the change ships fault-tested).

### Phases B–J — one vertical slice per unit (relocate 047 exercises + add new drills)

Per unit, in a single slice: (a) relocate that unit's pattern-tagged exercises (and their markers) into a
new `# Algorithm Extension` section at the end of `exercises.ipynb` (before `## Challenge`), renumbering
synced with `solutions.ipynb`; (b) gather the unit's lesson Spotlight(s) under a closing
`## Algorithm Extension` section in `lesson.ipynb`; (c) author the unit's NEW drills (per the Appendix) in
that section — new core exercises + any new tagged locus + General-Rule `practices` adds; (d) align
teacher-notes (reframe the algo block as enrichment, fix all renumbered refs, add unplugged traces for the
new-locus homes); (e) regenerate `patterns.md`; (f) keep every check GREEN.

- **Phase B — u04 quiz-show:** relocate Ex8/Ex9 (running-total, count-by-condition) into the extension;
  add the bounded-loop matrix (while-based, fixed/typed values, no list), two-counter count, conditional
  sum, signed accumulate, opening-streak, true user-sentinel (`no-exec`).
- **Phase C — u05 function-factory (lightest — most new volume):** its running-total home moves to the
  extension; add `count_bonus_stamps`/`count_wide_stamps`, `total_even_stamps`/`stamps_in_triangle`/
  `average_side`, `stamps_that_fit`/`width_used`/`stamps_to_pass`/`width_when_passed` (matrix in a
  function), `stamps_to_reach`/`stamps_scanned_for` (sentinel-in-function). Scanner-derived: `if-statement`,
  `comparison`, `break-statement`, `while-loop`.
- **Phase D — u06 secret-codes:** relocate transform-each/count/linear-search exercises; add running-total
  home (letter-value sum — a NEW `running-total` tagged locus), find-first-vowel index search, boolean
  digit search, multi-counter tally, star-the-vowels map, the matrix (letter-value budget, count doubles
  as a slice index).
- **Phase E — u07 high-score-hall:** relocate its five algo exercises into the extension; add the MIN/
  argmin family (rookie-by-name, best+worst, running-max), count-then-average, place/rank count,
  index/boolean search, numeric map, range/partition filters, the matrix over the waiting list + the
  `≥`-vs-`>` boundary drill. (Mostly More-Practice tier — u07 already heavy.)
- **Phase F — u08 word-wizard:** relocate its algo exercises; add running-total (total-of-tally — NEW
  locus), min/argmin (rarest/shortest word), two-counter known-vs-unknown, tally-by-derived-key,
  first-unknown search, the matrix (len-budget with an exact-hit boundary).
- **Phase G — u09 save-point:** relocate its algo exercises; add count + count-then-average (NEW
  `count-by-condition` locus), min-by-scanning with the init gotcha, line-number search, the matrix over
  save-file lines, filter-and-re-save.
- **Phase H — u10 pet-simulator (richest untapped — four NEW loci):** relocate Ex13/Ex14/Ex15; add
  count-by-condition (hungry pets), running-total (team hunger), linear-search (find pet by name),
  transform-each (roster of names) as NEW tagged loci, plus min/argmin over objects, mood tally, the
  matrix (feed-until-budget, downward total), filter-driven feeding.
- **Phase I — u02 number-detective + project-01:** relocate the sentinel-loop Spotlight/exercise into a
  lean extension section (u02 stays light — no new drills beyond the relocation); project-01 M1 Spotlight
  framed as extension prose. Keep u01–u02 lean per the standing exception.

Per-slice acceptance: the unit's algo content sits in a labelled `# Algorithm Extension` section;
pattern-tagged exercises still embody their design definition (content gate confirms); markers present +
adjacency-correct; new drills prereq-clean + single-pass; renumber synced exercises↔solutions↔teacher-notes;
`ci-local` GREEN incl. `technique-spiral`/`pattern-marker`/`patterns-doc-check`/`concept-scan`/`stretch`.

### Phase V — Verification (named, mandatory)

`uv run pytest -q` green; `scripts/ci-local.sh` ALL GREEN (memory-light groups) incl. the 3 pattern checks
+ inherited concept checks + notebook exec/hygiene/cell-lint + PDF (incl. the regenerated catalog) +
pre-merge guard. Volume budget recorded per unit (plan-037 disposition, per PR). **Proficiency/enrichment
(reviewer-enforced):** every unit has a coherent `# Algorithm Extension` section; each of the 7 patterns
still has its home + ≥3 core non-checkpoint reappearances; the new drills give each loop job (count / sum
/ search / find-best / map / filter / sentinel + the until-threshold matrix) multiple varied reps across
the light units. Book 2 stays green throughout.

**Acceptance criteria:** all algo content consolidated into per-unit Algorithm-Extension sections; the
loop-drill bank added (both boundary flavours of the until-threshold matrix + min family + conditional
sum + count-average + index/boolean search + object-loops); design v8; 3 checks green; catalog regenerated;
`ci-local` ALL GREEN; `pre-merge-guard --pr` OK; plan-review + per-PR content-review 4-way consensus.
**Rollout:** phased PRs by unit (Phase A first; then B–J), each a complete slice so `main` stays green.

---

## Plan Review

_(4-way gate — consensus = all four APPROVE / APPROVE WITH NITS, no open blockers.)_

### Review 1 — [self] (2026-09-18) → APPROVE WITH NITS

Scope matches the user's two directives (full lightest-units fill + consolidate all algo content into an
explicit end-of-notebook Algorithm-Extension section, migrating the merged 047 exercises). Named Phase V
present (ships unit content). Design-v8 amendment is in-scope and constraint-restructuring (no §3 locus
dropped/reclassified). Single-pass-only + prereq-closure traps + General-Rule adds + one-marker-per-
technique + stretch-preservation + numbering discipline are all carried from the 047 precedent. Phased by
unit so `main` stays green. NITS/risks for the external reviewers to pressure-test:
1. **Relocation CI-safety (biggest risk):** moving interleaved 047 exercises to the end + renumbering must
   keep `structure-check`/`solutions_structure` heading-pairing, `pattern-marker` adjacency, `stretch`
   counts, and `concept-scan` all green. Phase A's probe must prove a `# Algorithm Extension` header cell
   is inert to every check BEFORE any unit slice; if not, Phase A ships the tooling tolerance + fixtures.
2. **Marker adjacency after a section header:** confirm a `# Algorithm Extension` markdown cell sitting
   between the last core exercise and the first algo marker does not break the "marker immediately precedes
   the `## Exercise N` heading" rule (the marker still precedes its heading; the section header precedes
   the marker — should be fine, but verify in Phase A).
3. **Volume in u07/u08 (already 16 core):** the plan routes their new reps to the extension's More-Practice
   tier; confirm the plan-037 >2×-cells guardrail holds per unit and record the disposition.
4. **`min` init / no-`None` / no-`.split` traps** must be honored in every new drill (enumerated), else a
   genuine prereq violation `practices` can't fix.
Verdict: APPROVE WITH NITS (all addressable at implementation time). Awaiting [sol]/[glm]/[fable].

### Review 2 — [sol] (pending) · Review 3 — [glm] (pending) · Review 4 — [fable] (pending)

## Content Review

_(4-way gate — pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

## Post-Execution Report

_(Written before PR.)_

---

## Appendix — Exercise inventory (from the [fable] + [sol] reviews, 2026-09-18)

The authoritative per-unit exercise list — to be finalized inline (exact data + expected outputs) before
each unit slice, following the reviewer proposals. Highlights:

**Bounded-loop "until-threshold" matrix** (one loop, running total + a stop-rule; both boundary flavours
as distinct drills), per [fable]'s spec with exact datasets/answers:
- **S-fit** (sum not exceeding X — check-before-add, `<=`), **S-tip** (sum just exceeding X — add-then-check,
  `>`, name the tipping item), **C-fit** (count that fit ≤ X), **C-tip** (count until first > X).
- Placements + data: u04 scores 4,6,5,7,3 / X=12; u05 stamp sizes 10..30 / X=60 (in a function); u06
  letter-values of "secret" / budget 30 (count doubles as a slice index → prints the prefix); u07 waiting
  list [300,450,275,600] / 1000 (beside the existing Ex13); u08 word lengths / 12 (exact-hit boundary);
  u09 save-file lines 300,450,725,1350 / 1000 (no list); u10 Buddy hunger 8, snacks [2,4,3,5] (downward).
- **Neighbours (same skeleton, different "done yet?"):** just-reaching (`>=` vs `>`), until a sentinel
  value in the data, until the first item failing a test (streak/prefix), until the first N that pass,
  two-condition stop (`and`/`or`).

**Other jobs** (both reviewers): MIN/argmin family (u07 rookie-by-name/best+worst/running-max; u08 rarest/
shortest; u09 lowest-by-scan + init gotcha; u10 hungriest/least-hungry) — the book currently has zero min;
conditional sum + count-then-average; search returning an index vs a boolean vs "not found"; two-counter
tallies; numeric map; two-way partition; and u10 object-loops (count/sum/search/map as new tagged loci).

**Lightest units (priority for new volume):** u05 > u10 > u06 > u04; u07/u08/u09 reps route to the
extension's More-Practice tier (already at 16 core). Full proposal banks: [fable] ~89 items + matrix
supplement (exact data/answers) and [sol] ~36 items — both prereq-checked; consolidated here at slice time.

# Plan 048 — Book 1 Algorithm-Extension Consolidation + Loop-Mastery Drills

**Goal:** (1) **Consolidate** all algorithm-pattern content into an explicit **"Algorithm Extension"**
section at the end of each unit's `lesson.ipynb` and `exercises.ipynb` (migrating the plan-047 exercises
that currently sit interleaved among the core exercises), and (2) **expand** it with a large bank of
**simple, linear, single-pass loop drills** — counting, summing, searching, find-best, map, filter,
sentinel — with deliberate *repetition-with-variety* (the "until-threshold" matrix and its neighbours),
focused on the loop-light units (u04, u05, u06, u09, u10). The algorithm track becomes an explicit,
clearly-labelled **enrichment extension**, not interleaved core.

**Architecture:**
- **Student-facing structure (new):** every unit's `exercises.ipynb` ends with a `## Algorithm Extension`
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
- **New drills are UNMARKED extra-practice reps** (course-author decision, 2026-09-18): NO
  `<!-- pattern: id -->` marker, NO new technique `practices` tag, NO new §3 locus. The 7 patterns keep
  exactly the markers/loci they have from plan 047 (each already meets its ≥3 spiral), so design §3 is
  untouched. A drill's prose may still ask "which pattern is this?" for retrieval, but it adds no marker.
- **Bounded inventory:** the authoritative, capped per-unit drill list is
  `docs/proposals/048-loop-drill-inventory.md` (consolidated from the [fable]+[sol] reviews; ≈50 core
  drills, per-unit caps). Each slice finalizes its unit's exact list from that file — no open-ended pull.
- **Design amendment:** design 002 → **v8** — §6 student-facing form redefined as the end-of-notebook
  `## Algorithm Extension` section, and "home is in-class" relaxed to "extension enrichment routed by
  teacher-notes" (the lesson-side Spotlight that NAMES each pattern stays read in-class so later
  retrieval prose refers to a name every student met). Genuinely constraint-restructuring: **no §3 locus
  is added, dropped, or re-classified** — the new drills are unmarked, and §7's "running-total dropped
  from u08" note stands (u08 gets only an *unmarked* sum rep).

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
   `## Algorithm Extension` section (lesson Spotlights + exercises gathered there); relax "home in-class"
   → "extension enrichment, routed by teacher-notes" (the pattern-NAMING lesson Spotlight stays read
   in-class); + §13 revision entry. No §3 locus added/dropped/re-classified (drills are unmarked) →
   constraint-restructuring, no design re-review beyond the plan gate. **Activation:** v8 describes the
   target end-state; it is not "violated" by units not yet migrated — the migration completes unit-by-unit
   across Phases B–I, and v8's structure is the acceptance bar reached when the last slice merges.
2. Commit the bounded inventory `docs/proposals/048-loop-drill-inventory.md` (already drafted) so slices
   draw from a durable, capped source.
3. Confirm (with a probe, not a code change) that the CI checks are agnostic to a `## Algorithm Extension`
   header AND to relocation: `structure-check`/`solutions_structure` pair by `## Exercise N` (per-heading,
   not position); `pattern-marker` adjacency is marker→heading regardless of a preceding section header;
   `stretch-check` counts tagged cells anywhere; **`exec-solutions`/`exec-lessons`** still pass after a
   relocation (relocated cells must be state-independent — verify no later cell consumes a name a moved
   cell binds). If any check needs a tweak, that tooling change is part of Phase A (Codex) with fault
   fixtures; expected: none needed.
- **Acceptance (A):** design v8 committed; inventory committed; a scratch probe shows a
  relocated-into-`## Algorithm Extension` arrangement (with renumber) passes all checks incl. exec order;
  no tooling change required (or the change ships fault-tested).

### Phases B–I — one vertical slice per unit (relocate 047 exercises + add unmarked drills)

Per unit, in a single slice: (a) relocate that unit's pattern-tagged exercises (and their comment-only
markers) into a new **`## Algorithm Extension`** (H2, matching `## Challenge`) section at the end of
`exercises.ipynb`, positioned per the unit's own Challenge convention (047 documents it: some units put
the algo exercises as the last core `## Exercise N` before `## Challenge` cells; u08 uses `## Challenge N`;
u09/u10 Challenges are `stretch`-tagged `## Exercise N` — keep each unit's convention), renumbering synced
with `solutions.ipynb`; (b) gather the unit's lesson Spotlight(s) under a closing `## Algorithm Extension`
section in `lesson.ipynb` (a Spotlight for a *practiced-only* pattern must carry NO `<!-- pattern: id -->`
comment — `pattern-marker` only expects a lesson marker for an *introduced* pattern); (c) author the
unit's NEW drills from `docs/proposals/048-loop-drill-inventory.md` (up to the unit's cap) as **unmarked**
core exercises + General-Rule scanner-derived `practices` adds (regular concepts only); (d) align
teacher-notes (reframe the algo block as enrichment) AND fix EVERY renumbered exercise reference in
teacher-notes, in-notebook prose (lesson + exercises), and `book1/curriculum/pattern-ledger.md`; (e)
regenerate `patterns.md` (a no-op unless a marker moved) and refresh the ledger's exact-heading rows; (f)
keep every check GREEN.

Renumber scope (from [fable]'s audit — only these are interleaved and shift): u02 Ex3, u04 Ex8/9, u05 Ex7,
u07 Ex4/5/6/12, u08 Ex5/6/10; u06/u09/u10's pattern exercises already sit last (relocation there is mostly
adding the section header + new drills).

- **Phase B — u04 quiz-show:** relocate Ex8/Ex9 into the extension; add the ≤7 u04 drills (matrix
  fit/tip on 4,6,5,7,3, two-counter count, conditional sum, signed accumulate, opening-streak, user
  sentinel). `while`-only, no `for`/`range`/list.
- **Phase C — u05 function-factory (lightest):** relocate Ex7; add the ≤9 u05 function-packaged drills
  (count/sum/matrix/sentinel-in-function). Scanner-derived: `if-statement`, `comparison`, `break-statement`,
  `while-loop`. No list/string-index (data from `range`/formulae).
- **Phase D — u06 secret-codes:** relocate its transform-each/count/linear-search exercises; add the ≤8
  u06 drills (letter-value **unmarked** sum, first-vowel index search, boolean digit search, three-counter
  tally, star-the-vowels map, the matrix). Letter values come only from the lesson's `range(26)` scan;
  `ord`/`chr` forbidden.
- **Phase E — u07 high-score-hall:** relocate its **seven** algo exercises (Ex4, Ex5, Ex6, Ex12, Ex14,
  Ex15, Ex16) into the extension; add the ≤6 u07 drills (rookie-by-name/best+worst argmin, count-average
  with zero-guard, place/rank count, index/boolean search, matrix + `≥`-vs-`>` boundary) as **More-Practice**
  (u07 already 16 core — expect a plan-037 volume sign-off).
- **Phase F — u08 word-wizard:** relocate its algo exercises; add the ≤5 u08 **unmarked** drills
  (total-of-tally sum, rarest/shortest argmin, known-vs-unknown two-counter, first-unknown search, matrix)
  as More-Practice. (u08 running-total stays an unmarked rep — §7's "dropped from u08" note stands.)
- **Phase G — u09 save-point:** relocate its algo exercises; add the ≤7 u09 drills (count, count-average,
  min-by-scan + init gotcha, line-number search, matrix, filter-and-re-save) — all **unmarked**.
- **Phase H — u10 pet-simulator (richest untapped):** relocate Ex13/Ex14/Ex15; add the ≤9 u10 **unmarked**
  object-loop drills (count hungry, team-hunger sum, find-pet-by-name search, roster map, min/argmin, mood
  tally, feed-until-budget matrix, filter-feed, cheer-saddest). No new tagged loci.
- **Phase I — u02 number-detective + project-01:** relocate the u02 sentinel-loop Spotlight/exercise into a
  lean `## Algorithm Extension` section (no new drills — u02 stays lean); project-01 M1 Spotlight framed as
  extension prose.
- **u01 & u03 are EXEMPT:** they host no algorithm-pattern content (no §3 home or reappearance), so they
  get no Algorithm Extension section. The "every unit" acceptance clause means *every unit that hosts a
  pattern* — u01/u03 are out of scope and unchanged.

Per-slice acceptance: the unit's algo content sits in a labelled `## Algorithm Extension` section;
pattern-tagged exercises still embody their design definition (content gate confirms); markers present +
adjacency-correct; new drills unmarked, prereq-clean + single-pass; renumber synced across
exercises↔solutions↔teacher-notes↔prose↔ledger; `ci-local` GREEN incl. `technique-spiral`/`pattern-marker`/
`patterns-doc-check`/`concept-scan`/`stretch`; exec order preserved (relocated cells are state-independent).

### Phase V — Verification (named, mandatory)

`uv run pytest -q` green; `scripts/ci-local.sh` ALL GREEN (memory-light groups) incl. the 3 pattern checks
+ inherited concept checks + notebook exec/hygiene/cell-lint + PDF (incl. the regenerated catalog) +
pre-merge guard. **Volume budget (plan-037 disposition, per PR):** any slice exceeding >2× cells / >30%
PDF pages / >25% wall-time (or a cell >120 s) requires an EXPLICIT content-gate sign-off recorded in the
PR (not a silent "recorded") — u05 (11→~20 core) and u04 will very likely trip >2× cells, so a sign-off
is pre-expected there. **Proficiency/enrichment
(reviewer-enforced):** every unit has a coherent `## Algorithm Extension` section; each of the 7 patterns
still has its home + ≥3 core non-checkpoint reappearances; the new drills give each loop job (count / sum
/ search / find-best / map / filter / sentinel + the until-threshold matrix) multiple varied reps across
the light units. Book 2 stays green throughout.

**Acceptance criteria:** all algo content consolidated into per-unit Algorithm-Extension sections; the
loop-drill bank added (both boundary flavours of the until-threshold matrix + min family + conditional
sum + count-average + index/boolean search + object-loops); design v8; 3 checks green; catalog regenerated;
`ci-local` ALL GREEN; `pre-merge-guard --pr` OK; plan-review + per-PR content-review 4-way consensus.
**Rollout:** phased PRs by unit (Phase A first; then B–I; u01/u03 exempt), each a complete slice so
`main` stays green.

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
   counts, and `concept-scan` all green. Phase A's probe must prove a `## Algorithm Extension` header cell
   is inert to every check BEFORE any unit slice; if not, Phase A ships the tooling tolerance + fixtures.
2. **Marker adjacency after a section header:** confirm a `## Algorithm Extension` markdown cell sitting
   between the last core exercise and the first algo marker does not break the "marker immediately precedes
   the `## Exercise N` heading" rule (the marker still precedes its heading; the section header precedes
   the marker — should be fine, but verify in Phase A).
3. **Volume in u07/u08 (already 16 core):** the plan routes their new reps to the extension's More-Practice
   tier; confirm the plan-037 >2×-cells guardrail holds per unit and record the disposition.
4. **`min` init / no-`None` / no-`.split` traps** must be honored in every new drill (enumerated), else a
   genuine prereq violation `practices` can't fix.
Verdict: APPROVE WITH NITS (all addressable at implementation time). Awaiting [sol]/[glm]/[fable].

### Round 1 (2026-09-18) — verdicts on the draft (d572300)

- **[self] APPROVE WITH NITS** · **[fable] APPROVE WITH NITS** · **[glm] REJECT** · **[sol] REJECT**.
- All four converged on **B1**: the draft claimed "constraint-restructuring only" but added new §3 tagged
  loci (running-total u06/u08/u10; count/search/map u10), which design §3/§7 forbids a plan from doing
  (and reversed §7's "running-total dropped from u08"). [sol] added **B2** (u01/u03 unaddressed vs the
  every-unit contract) and **B3** (exercise bank unbounded / not committed). All CONFIRMED the relocation
  is CI-safe (no tooling change) and Phase V is properly named.

### v2 reconciliation (2026-09-18) — all findings folded (course author chose "unmarked reps")

- `[FIXED]` **B1:** new drills are now **UNMARKED extra-practice reps** — no new tagged loci, no §3 change;
  design v8 is genuinely §6 + in-class-relaxation only, and §7's u08 note stands (Architecture; Phases
  D/F/H reworded; v8 scope tightened).
- `[FIXED]` **[sol] B2:** u01/u03 explicitly EXEMPT (host no pattern content); the every-unit clause means
  every pattern-hosting unit; phases are B–I (label corrected).
- `[FIXED]` **[sol] B3 + [fable] N2:** committed the bounded, capped inventory
  `docs/proposals/048-loop-drill-inventory.md` (consolidates both banks; per-unit caps ≈50 core total) as
  the authoritative source; the Appendix now points to it.
- `[FIXED]` nits: `##` (not `#`) Algorithm-Extension header + per-unit Challenge conventions restated;
  Phase E marker count corrected to **seven** (Ex4/5/6/12/14/15/16); Phase-A probe includes exec-order;
  per-slice step (d)/(e) now refresh in-notebook prose + `pattern-ledger.md` exact-heading rows; forbid
  `ord`/`chr` + "no list/string-index in u05" + "for/range are u03, excluded by choice not closure" added
  to the constraints/inventory; "zero *scanned* min" clarified; v8 activation-with-migration clause;
  Phase V restates the explicit volume sign-off (u04/u05 pre-expected to trip >2× cells); lesson-side
  Spotlight for practiced-only patterns carries NO marker (pattern-marker only expects it for introduces).

### Round 2 (2026-09-18) — verdicts on v2 (7658c3d)

- **[glm] → APPROVE WITH NITS** — B1 substantively resolved (unmarked reps, §7 u08 note preserved); all
  round-1 nits addressed; only two stale-wording nits (Appendix "new tagged loci"; a couple of `#`
  Algorithm-Extension headers). No blockers.
- **[sol] → REJECT** — but ONLY on the same stale wording (Appendix "new tagged loci" line + remaining
  single-hash H1 Algorithm-Extension header refs at plan 12/186/214/216); B2/B3 confirmed resolved, all substantive
  nits addressed, relocation CI-safe + Phase V named re-confirmed. No scope/design blocker.

### v2.1 (2026-09-18) — stale-wording sweep ([glm]/[sol] round-2 nits)

- `[FIXED]` Appendix "u10 object-loops … as new tagged loci" → "as unmarked rep jobs".
- `[FIXED]` every H1 Algorithm-Extension header ref converted to the H2 form `## Algorithm Extension`
  (plan lines 12/186/214/216; inventory header rule) — H2 throughout, matching `## Challenge`.
- `[FIXED]` inventory's leftover self-correcting aside removed. No substantive change; B1/B2/B3 stay
  resolved. Remaining "tagged loci" strings are the legitimate general-rule text + the "No new tagged
  loci" assertions.

### Round 3 — [self] → APPROVE. [glm]/[fable] round-2/round-1 APPROVE-WITH-NITS stand (nits folded).

- **[sol] → REJECT (round 3)** — confirmed ALL substantive items resolved (B1/B2/B3; no §3 locus
  added/dropped/reclassified; §7 running-total-dropped-from-u08 note preserved; relocation CI-safe;
  Phase V named; no regressions "none found"). Its sole remaining objection: the negative grep still
  matched two single-hash literals — but those were in THIS Plan Review's own reconciliation prose
  (lines ~259/265) quoting the old header string to *describe* the fix, which [sol] itself called
  "historical review text rather than heading specifications." A grep artifact on the change-log, not
  a header defect.

### v2.2 (2026-09-18) — grep-artifact sweep ([sol] round-3)

- `[FIXED]` Reworded the two reconciliation-note lines (~259/265) so no single-hash `#`+"Algorithm
  Extension" literal remains anywhere in the plan or the inventory. Verified:
  `grep "# Algorithm Extension" | grep -v "## Algorithm Extension"` → empty in both files. No
  substantive change; B1/B2/B3 stay resolved. [sol] round-4 re-dispatched on v2.2.

### Round 4 — CONSENSUS (gate CLOSED)

- **[self] → APPROVE.**
- **[sol] → APPROVE (round 4)** — re-ran the negative grep on both `docs/plans/048-*.md` and
  `docs/proposals/048-*.md`: no single-hash literal remains. Confirmed v2.1→v2.2 is documentation-only
  (plan file only; proposal + design byte-unchanged). Re-confirmed the surviving contracts: unmarked
  reps (no new markers / technique `practices` tags / §3 loci), `## Algorithm Extension` H2 throughout,
  content phases B–I each carry a named Phase V, and the v8 amendment preserves §7's "running-total
  dropped from u08" decision.
- **[glm] → APPROVE-WITH-NITS** (round 2; nits folded into v2/v2.1).
- **[fable] → APPROVE-WITH-NITS** (round 1; nits folded).

**4-way consensus: all four APPROVE / APPROVE-WITH-NITS, no open blockers. Plan-review gate CLOSED.**
Cleared to implement (Phase A → Phases B–I → Phase V per slice).

## Content Review

_(4-way gate — pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

## Post-Execution Report

### Phase A — Design v8 + Algorithm-Extension conventions (docs/tooling) — DONE

- **Design 002 → v8** committed: §6 gains the `## Algorithm Extension` end-of-notebook structure bullet
  (H2 section, last core `## Exercise N` before `## Challenge`; lesson Spotlights gathered under a closing
  `## Algorithm Extension`; numbering + markers unchanged), and the teacher-notes bullet relaxes "home is
  always in-class" → "extension enrichment routed by teacher-notes" (pattern-*naming* Spotlight stays
  in-class). §13 gains the v8 entry. **No §3 locus added/dropped/re-classified; §7's "running-total
  dropped from u08" note preserved.**
- **Inventory** `docs/proposals/048-loop-drill-inventory.md` already committed (5839477) — the durable,
  capped source the slices draw from.
- **CI-safety + exec-order probe (no tooling change needed).** Static read of the tools confirmed the
  header is invisible to the heading/tag/marker checks: `notebooks.py` `EXERCISE_HEADING` matches only
  `^## Exercise \d+` and `SOLUTION_HEADING` requires the word "solution"; `patterns.py` `_exercise_link`
  requires `marker_index + 1` to be the `## Exercise N` cell, so the `## Algorithm Extension` header must
  (and does) sit *before* the marker. Dynamic probe: a real relocate+renumber of u05's running-total
  block (Ex7 → end under `## Algorithm Extension`, Ex8–11 → Ex7–10, moved → Ex11) in BOTH
  `exercises.ipynb` and `solutions.ipynb`, then reverted. Against that arrangement, ALL relevant checks
  PASS: `structure-check`, `stretch-check`, `hygiene-check`, `pattern-marker` (adjacency preserved),
  `technique-spiral` (≥3 spiral intact), `patterns-doc-check`, `concept-scan`, and **`exec-solutions`**
  (moved `def` cell is state-independent → exec order safe). Probe reverted; Phase A ships docs-only.
- **Slice note for B–I:** the relocation script must preserve each cell's `id` field (the throwaway probe
  omitted ids → a benign `nbformat` MissingIDFieldWarning); real slices copy/generate ids so notebooks
  stay normalized.

_(Phases B–I + Phase V report appended as each slice lands.)_

---

## Appendix — Exercise inventory (from the [fable] + [sol] reviews, 2026-09-18)

**The authoritative, bounded per-unit list is the committed `docs/proposals/048-loop-drill-inventory.md`**
(per-unit caps + the matrix datasets/answers + candidate drills, all UNMARKED). Each slice finalizes its
unit's exact exercises (data + expected outputs) from that file within its cap. Highlights below for
orientation:

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
tallies; numeric map; two-way partition; and u10 object-loops (count/sum/search/map as unmarked rep jobs).

**Lightest units (priority for new volume):** u05 > u10 > u06 > u04; u07/u08/u09 reps route to the
extension's More-Practice tier (already at 16 core). Full proposal banks: [fable] ~89 items + matrix
supplement (exact data/answers) and [sol] ~36 items — both prereq-checked; consolidated here at slice time.

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

### Phase B — u04 quiz-show (relocation + 7 unmarked drills)

**Round 1** — [self] APPROVE-WITH-NITS · [glm] APPROVE-WITH-NITS · [fable] APPROVE-WITH-NITS ·
**[sol] REJECT** (one [OPEN]). Blind-solve of Ex13–18 matched all four reviewers (Ex13 3/2, Ex14 18,
Ex15 4, Ex16 3, Ex17 10/2, Ex18 15/3); closure clean (`while`-only, no `for`/`range`/list/`len`/`sum`/
`.split()`, no `input(` in solutions); unmarked contract intact (only running-total/count marked, before
Ex11/Ex12); numbering 1–19 aligned; ledger resulting-core 19; volume 33→48 cells (1.455× < 2×, no
sign-off needed). Findings:

- `[FIXED]` **[sol] [OPEN]** — Ex19 gave no score sequence yet the solution asserted total 16 **and**
  count 3 (not blind-derivable). Statement now carries a *worked example* ("entering 5, 3, 8, then 0 adds
  3 scores for a total of 16"), so 16/3 are derivable; also added `int(input(...))`.
- `[FIXED]` **[glm]/[fable] [OPEN]** — teacher-notes stale renumber: the or-spellings "Accept either
  spelling" exercise moved old Ex10 → **Ex8**; the Common-mistakes reference updated 10 → 8.
- `[FIXED]` **[self]/[fable] [OPEN]** — exercises `## Challenge` intro "after the twelve core exercises"
  → number-free "after the earlier exercises" (u04 now has 19).
- `[FIXED]` **[glm]/[fable] nit** — Ex13–18 statements said "Create five … variables" but solutions
  inline via `if`/`elif` (the Ex11 running-total precedent); reworded to "step through the five fixed
  values …" to match, and unified "counter-controlled" → "counter-bounded" (the design/house term).
- `[FIXED]` **[fable] nit** — Ex19 solution used a counter-bounded loop; restructured to the true
  sentinel shape (`while True:` + `break` on the 0 entry) so it models what the interactive exercise asks.
- `[FIXED]` **[fable] nit** — teacher-notes running-total/count "routes" reworded ("name in class from
  the Spotlight; Exercise 11/12 is its home in the Algorithm Extension") and the in-class coverage claim
  qualified for those two enrichment homes.
- `[FIXED]` **[glm]/[fable] nit** — added a student-facing framing line under `## Algorithm Extension`
  (exercises + lesson): "Extra loop practice — optional enrichment …".
- `[FIXED]` **[fable] note** — Phase B post-execution report added below.

All book1 checks + exec-solutions/exec-lessons + PDF re-run GREEN after fixes.

**Round 2 — CONSENSUS (gate CLOSED).** [self] APPROVE · **[sol] APPROVE** (round 2: confirmed Ex19
worked example makes 16/3 blind-derivable + solution mirrors it; Ex13–18 unchanged answers; closure /
markers / numbering / stretch all intact) · [glm] APPROVE-WITH-NITS · [fable] APPROVE-WITH-NITS (their
nits folded). All four APPROVE / APPROVE-WITH-NITS, no open blockers. Cleared to PR + merge.

### Phase C — u05 function-factory (relocation + 9 unmarked function drills)

**Round 1** — [self] APPROVE · [glm] APPROVE-WITH-NITS · [fable] APPROVE-WITH-NITS · **[sol] REJECT**
(one [OPEN]). All four blind-solved Ex12–20 to the specified results (3, 12, 15, 2.5, 3/45, 4/70, 6, 4,
70); closure clean (functions; `for`/`range` or `while` (Ex18); no list/`len`/`sum`/`.split()`/`input(`);
General-Rule `practices` adds (`if-statement`, `elif-else`, `comparison`, `while-loop`, `break-statement`,
all introduced ≤ u05) synced in map+manifest, `concept-scan` clean; unmarked contract intact; numbering
1–20 aligned; volume 42→61 cells (1.45×, < 2×). Findings:

- `[FIXED]` **[sol] [OPEN]** (+ [glm]/[fable] nits) — stale running-total relocation references: the
  pattern-ledger locus row + count row (`"Exercise 7"` / "reuse Ex7" → **Ex11**), the ledger header
  "design 002 v7" → v8, and design 002 §3 catalog + §7 + §13-revision refs ("u05 Ex7" → **Ex11** where
  live; the v3 revision note neutralised to "running-total reuse"). Design status line bumped v7 → **v8**
  (the v8 amendment merged in Phase A had left the status marker at v7).
- `[FIXED]` **[fable] [OPEN]** — `exercises.ipynb` Ex10 prose self-referenced "reuse `stamp(size)` from
  Exercise 10" after the renumber → "from Exercise 9" (old Ex10 grid is now Ex9).
- `[FIXED]` **[fable] nit** — asset starter header comments said "Student starter for Exercise 10/11"
  (now off-by-one) → content-descriptive ("…for the stamp-grid/stamp-bands exercise"); filenames kept
  (stable identifiers, named exactly by the prose; renaming = disproportionate churn).
- `[FIXED]` **[fable] nit** — u05 teacher-notes "accumulator beat … sits with return-value" clause
  updated (the Spotlight now sits in the closing Algorithm Extension, Ex11).
- `[FIXED]` **[fable] nit (optional)** — added a one-line clarifier to Ex16/Ex17 ("Both functions use
  the same loop over the sizes; only the value you return differs").
- `[WONTFIX]` **[fable] nit** — loop var `i` (vs the unit's descriptive names): the plan mandates
  `for i in range(...)`; recorded, no change.

All book1 checks + exec-solutions/exec-lessons + PDF re-run GREEN after fixes.

**Round 2** — [self] APPROVE; [glm]/[fable] round-1 APPROVE-WITH-NITS stand (folded); **[sol] REJECT** —
original [OPEN] confirmed resolved (all stale v7/Ex7 refs gone; Ex12–20 blind-solve + all checks pass),
but flagged ONE regression the round-1 fix introduced:

- `[FIXED]` **[sol] [OPEN] (round 2)** — u05 teacher-notes twice called Exercise 11 "the running-total
  **home**", contradicting the source-of-record (running-total's home is **u04**; u05 is a **reuse**).
  Reworded both (teacher-notes.md:53 and the Algorithm-Extension list) to "the running-total pattern's
  reuse rep (home is Unit 04)". Docs-only; no CI impact.

**Round 3 — CONSENSUS (gate CLOSED).** [self] APPROVE · **[sol] APPROVE** (round 3: regression resolved —
no "running-total home" phrase remains; teacher-notes framing matches ledger/design; Ex12–20 unchanged,
numbering 1–20, unmarked contract intact, all read-only checks pass) · [glm] APPROVE-WITH-NITS ·
[fable] APPROVE-WITH-NITS (folded). All four APPROVE / APPROVE-WITH-NITS, no open blockers. Cleared to
PR + merge.

### Phase D — u06 secret-codes (header-only relocation + 8 unmarked character-scan drills)

**Round 1** — [self] APPROVE · [glm] APPROVE-WITH-NITS · [fable] APPROVE-WITH-NITS (no [OPEN]) ·
**[sol] REJECT** (2 [OPEN]). All four blind-solved Ex15–22 to spec (3; 5/1/2; pos 3; T/F; c*t/h*ll*; 6;
fit 3/27/"sec"; tip 4/45/"r"); closure clean (string scans; no `len`/`.split`/`ord`/`chr`/`sum`/lists;
letter values via the alphabet scan); NO renumber (Ex1–14 byte-identical to main); unmarked contract
intact (3 exercise markers before Ex12/13/14, 2 lesson markers; Ex15–22 unmarked); concept-scan clean
(no `practices` adds). Findings:

- `[FIXED]` **[sol] [OPEN] + [glm] nit** — ledger u06 resulting-core said 21 but the notebook has 22
  `## Exercise` headings. Reconciled to **22** (11 baseline + 3 real 047 adds, Ex12–14 — plan-047 logged
  +2, the pre-existing fable NIT-4 off-by-one — + 8 plan-048 drills).
- `[FIXED]` **[sol] [OPEN]** — u06 teacher-notes still routed the pattern exercises Ex12–14 as **in-class**,
  contradicting design v8 (the whole Algorithm Extension is enrichment; only the lesson-side naming
  Spotlight is in-class). Reframed like u04/u05: in-class core is now Ex1–11; the naming Spotlights are
  read in class (riding the L2 `in`/alphabet-scan and L3 `encode` ladders), and every Algorithm-Extension
  exercise (Ex12–22) runs as time-permitting / homework / differentiation.
- `[FIXED]` **[glm]/[fable] nit** — exercises `## Challenge` intro "after the fourteen in-class core
  exercises" → number-free "after the earlier exercises" (matches u04/u05).
- `[FIXED]` **[fable] N3 + [glm] micro-nit** — Ex18 `has_digit` solution rewritten to the taught
  found-flag idiom (`found = False … found = True; break … return found`, mirroring the Ex14/Ex17
  linear-search shape) with `assert has_digit(...)` / `assert not has_digit(...)` (dropped `== True`/`== False`).
- `[FIXED]` **[fable] N4** — Ex16/Ex21/Ex22 solution `print(a, b, c)` multi-arg prints → f-strings (the
  unit's own convention).
- `[FIXED]` **[fable] N1** — Ex21 prose `secret[:count]` → `"secret"[:count]` (a bare `secret` identifier
  would `NameError`; the slice is on the string literal).
- `[FIXED]` **[fable] N5** — the lesson `## Algorithm Extension` framing line now describes the gathered
  **Spotlights** (not "drills", which live in exercises).
- `[FIXED]` **[fable] N6** — teacher-notes pacing bullets now say the naming Spotlights are read in class
  and point to the Algorithm-Extension exercises (subsumed by the enrichment reframe).
- `[WONTFIX]` **[fable] N2** — leaving Ex17–20 statement function names unfixed / not re-worded: they
  blind-solved unambiguously for all four reviewers; changing already-verified statement wording adds risk
  for no correctness gain.

All book1 checks + exec-solutions/exec-lessons + PDF re-run GREEN after fixes.

**Round 2 — CONSENSUS (gate CLOSED).** [self] APPROVE · **[sol] APPROVE** (round 2: both [OPEN]s
resolved — ledger 11+3+8=22 consistent; in-class core = Ex1–11 with Ex12–22 enrichment matching v8 §6;
Ex15–22 re-derived, found-flag `has_digit`, numbering 1–22, closure/markers/concept-scan all pass) ·
[glm] APPROVE-WITH-NITS · [fable] APPROVE-WITH-NITS (folded). All four APPROVE / APPROVE-WITH-NITS, no
open blockers. Cleared to PR + merge.

### Phase E — u07 high-score-hall (relocate 7 pattern exercises + renumber + 6 list drills)

**Round 1** — [self] APPROVE · [fable] APPROVE-WITH-NITS (no [OPEN]) · **[glm] REJECT** (1 [OPEN]) ·
**[sol] REJECT** (3 [OPEN]). All four blind-solved Ex17–22 to spec (Zoe/650; 1050/720; 3/900.0; place 3;
fit 2/750; tip 3/1025/275); closure clean (list loops; `len`/`max`/`min`/`.append()`/`.sort()`; no
`sum`/`sorted`/`.split()`/`input`; min seeded from first item); the 16-exercise renumber verified aligned
across both notebooks + markers (Ex10–16) + design §3 + ledger + u04/u06 teacher-notes. Findings:

- `[FIXED]` **[glm]+[sol] [OPEN]** — stale cross-ref `unit-02-number-detective/teacher-notes.md:35`
  "unit-07 Exercise 12" (sentinel-loop) → **Exercise 13**. (My earlier sweep used the "unit 07" spelling
  and missed the "unit-07" hyphen form; glm's broader grep caught it. Confirmed no other hyphen-form
  stale refs remain for u04/u05/u07.)
- `[FIXED]` **[sol] [OPEN]** — Challenge 1 solution asserted `scores[:3] == [...]` — **list slicing**,
  untaught in u07 (`list-slice` is unregistered → undetected by concept-scan). Pre-existing on `main`
  (only in the assert; the solution logic already uses `scores[0/1/2]`); replaced with three list-index
  asserts. Closure fix folded into the slice.
- `[FIXED]` **[sol] [OPEN] + [fable] N3** — Ex19's required zero-passer branch was unverified; added a
  second guard-exercising assert (impossible pass mark → average 0).
- `[FIXED]` **[fable] N2** — Ex17 statement now says to seed `rookie_name`/`rookie_score` from the first
  item (never 0), plus a Common-mistakes bullet on seeding minima from the first item (Ex15/17/18).
- `[FIXED]` **[sol] nit 4** — Ex21/Ex22 worked-example variable names (`total_used`, `tipping_total`)
  drifted from the solutions' `fit_total`/`tip_total`; reworded to state values, no prescribed names.
- `[WONTFIX]` **[fable] N1** (lesson Spotlight order/pointer) — the closing-section order matches the
  exercise order (Ex15 find-extreme, Ex16 filter) and teacher-notes route the in-class timing; and
  **[glm] nits** (design §7 v7-era "u07→16" projection, superseded by the ledger's 22; defensive guards).

All book1 checks + exec-solutions/exec-lessons + PDF re-run GREEN after fixes.

**Round 2 — CONSENSUS (gate CLOSED).** [self] APPROVE · **[glm] APPROVE** (round 2: [OPEN] resolved, full
cross-ref sweep clean, no regressions) · **[sol] APPROVE** (round 2: all 3 [OPEN]s confirmed fixed — u02
ref = Ex13, no list-slice remains, Ex19 zero-guard asserted; Ex17–22 re-derived; numbering/markers/closure
all pass) · [fable] APPROVE-WITH-NITS (folded). All four APPROVE / APPROVE-WITH-NITS, no open blockers.
Cleared to PR + merge.

### Phase F — u08 word-wizard (relocate 5 pattern exercises + renumber + 5 dict/list drills)

**Round 1** — [self] APPROVE · **[glm] REJECT** (1 [OPEN]) · **[fable] REJECT** (2 [OPEN]) ·
**[sol] REJECT** (2 [OPEN]). All four blind-solved Ex17–21 to spec (total 6; rarest fox/1; known 2/unknown
1; fit 3/12 exact-hit; tip 4/18/"wizard"); closure otherwise clean; the 5-exercise relocation + renumber
verified aligned across notebooks + markers (Ex12–16) + design §3 + ledger + u04/u06 teacher-notes.
The three external reviewers converged on the same two [OPEN]s:

- `[FIXED]` **[glm] F1 + [fable] OPEN-2 + [sol] [OPEN]** — the More-Practice divider still read "Exercises
  12–16" (my relocation's reword regex assumed "12–14" and silently missed the "12–16" en-dash form).
  Corrected to "Exercises 9–11" + the Algorithm-Extension pointer sentence.
- `[FIXED]` **[fable] OPEN-1 + [sol] [OPEN]** — the Codex solutions used `+=` (augmented assignment) in
  Ex17/19/20/21 (7 lines) — **untaught in Book 1** (appears nowhere else; `concept-scan` doesn't model it,
  so reviewer-enforced). Rewritten to the taught long form `x = x + …`. (Verified u04–u07 drills used no
  `+=` — isolated to u08.)
- `[FIXED]` **[fable] nit-1** — Ex20 opened "Same words, same budget, different rule:" but is the first of
  the pair; removed (kept the contrast wording on Ex21).
- `[FIXED]` **[fable] nit-2** — Ex18 argmin seeding had no route on a dict; added a hint ("use a boolean
  `first_pair = True` and flip it after the first turn").
- `[FIXED]` **[fable] nit-3** — teacher-notes "routed to More-Practice/homework" → "the Algorithm
  Extension is routed as time-permitting / homework".
- `[NOTE]` **[fable] nit-4** — shipped both matrix flavours (S-fit + S-tip) instead of the "first-unknown
  search" candidate, within the ≤5 cap (finalized within cap; the search rep is covered by the relocated
  linear-search Ex15).

All book1 checks + exec-solutions/exec-lessons + PDF re-run GREEN after fixes.

**Round 2 — CONSENSUS (gate CLOSED).** [self] APPROVE · **[sol] APPROVE** (round 2: both [OPEN]s
confirmed — no `+=` remains, divider = 9–11; Ex17–21 re-derived) · **[glm] APPROVE-WITH-NITS** (round 2) ·
**[fable] APPROVE-WITH-NITS** (round 2). A cosmetic residual nit (Ex20 opener left lowercase after the
nit-1 edit) was capitalized ("Use …"). All four APPROVE / APPROVE-WITH-NITS, no open blockers. Cleared to
PR + merge.

### Phase G — u09 save-point (relocate 5 pattern exercises + renumber + 7 loop drills)

**Round 1** — [self] APPROVE · **[glm] REJECT** (3 [OPEN]) · **[fable] REJECT** (3 [OPEN]) ·
**[sol] REJECT** (3 [OPEN]). All four blind-solved Ex17–23 to spec (2; 2825/706.25; 450; pos 2; 2/750;
3/1475/725; 725); closure clean (no `+=`, long-form; no `sum`/`sorted`/`min`/`input`; Ex19 seeds from
`scores[0]`); `range-function` General-Rule-added to u09 `practices` (map+manifest) for Ex20's
`range(len)`; numbering 1–25 aligned; markers before Ex12–16; only transform-each cross-ref changed
(Ex3→Ex12). u09 is a **stateful file-I/O** unit, so the reviewers converged on exec-order defects:

- `[FIXED]` **[glm]/[sol] [OPEN]** — Ex14 (linear-search over `settings.txt`) was NOT self-contained: it
  relied on More-Practice Ex10 having written "Mina", so it failed on the in-class→extension path
  (`exec-solutions` passed only because top-to-bottom ran Ex10 first). Ex14 solution now re-saves its own
  `settings.txt` (Ada/Mina/Leo) first; verified it passes in isolation. teacher-notes self-containment
  claim corrected ("re-save the file they read").
- `[FIXED]` **[fable] [OPEN]** — Ex12 (transform-each) statement said "Expected output `[1375,910,1260]`"
  but a student reaches it with the ambient `savegame.txt` = `[300,450,725,1350]`; aligned the statement
  expected output AND the solution to `[300,450,725,1350]` (consistent with Ex13/15/16).
- `[FIXED]` **[glm]/[fable]/[sol] [OPEN]** — the **solutions** More-Practice divider still said
  "Exercises 10–16" → "9–11" (I'd fixed only the exercises copy).
- `[FIXED]` **[glm]/[fable]/[sol] [OPEN]** — Ex7 prose self-referenced "`load_scores` helper from
  Exercise 7" → **Exercise 6** (where the helper is now defined).
- `[FIXED]` **[fable] nit** — Ex19 seeding clarifier (why `0` is a safe *max* seed but a fatal *min*
  seed); en-dash alignment on the exercises divider.
- `[NOTE]` **[fable]/[glm] nit** — the drills use **inline score lists** (not the inventory's "file-line
  loops", and drop the filter-and-re-save candidate) to avoid the file-state fragility that bit Ex12; the
  five relocated reps + core Ex1–8 carry the file-reading skill. Accepted deviation, recorded here.

All book1 checks + exec-solutions/exec-lessons + PDF re-run GREEN after fixes; Ex14 verified
order-independent.

**Round 2** — [self] APPROVE · **[fable] APPROVE** · **[glm] APPROVE-WITH-NITS** (all 3 round-1 [OPEN]s
confirmed resolved) · **[sol] REJECT** — sole remaining [OPEN] was the teacher-notes:56–57 wording that
attributed the order-independent re-save to the *student exercises* rather than the *solutions*
(both glm's nit and sol's [OPEN]).

- `[FIXED]` teacher-notes:56–57 reworded: "In the **solutions**, each relocated file-reading exercise
  re-saves the file it reads first … so the solutions notebook validates cleanly regardless of order. The
  student exercises notebook is designed to be run top-to-bottom (as the whole stateful unit is) …".

**Round 3 — CONSENSUS (gate CLOSED).** [self] APPROVE · **[sol] APPROVE** (round 3: teacher-notes claim
correctly scoped to solutions; diff is docs-only) · [glm] APPROVE-WITH-NITS · [fable] APPROVE. All four
APPROVE / APPROVE-WITH-NITS, no open blockers. Cleared to PR + merge.

### Phase H — u10 pet-simulator (header-only relocation + 9 unmarked object-loop drills)

**Round 1** — [self] APPROVE · **[glm] APPROVE-WITH-NITS** · **[fable] REJECT** (1 [OPEN]) ·
**[sol] REJECT** (2 [OPEN]). All four blind-solved Ex16–24 to spec (2; 23; found; roster; Rex/8 & Mia/3;
mood tally; 2/2; −1/3/3; [3,3,2,5]); closure clean; numbering 1–26 aligned; markers before Ex13–15;
Ex25/26 stretch; no cross-ref changes (Ex13/14 unchanged). Notably I pre-fixed two Codex smells before
committing (a contrived nested `for pet in pets:` over a single Buddy, and `tipping_snack = None` — a
Book-1 closure trap) → single-loop, `tipping_snack = 0`. The reviewers then converged on the
statement↔solution mismatches those solution-fixes created:

- `[FIXED]` **[glm]/[fable]/[sol] [OPEN]** — Ex22/Ex23 *statements* still told students to make a `pets`
  list and use `for pet in pets:` (which forces the forbidden nested loop), contradicting the single-loop
  solutions. Reworded both statements to "make one `Pet` named Buddy … loop once over the snacks", and
  fixed the teacher-notes' `for pet in pets:` generalization.
- `[FIXED]` **[glm]/[sol] [OPEN]** — Ex16/17/21/24 statements say `__init__` stores "only" hunger/mood,
  but the solutions also stored an unused `name`. Minimized those four solution Pet classes to the stated
  single attribute (Pet(8)…, Pet("happy")…).
- `[FIXED]` **[fable] nit** — Ex23 statement now says "start `tipping_snack = 0`" (matching the solution's
  no-`None` seed).
- `[FIXED]` **[fable] nit** — ledger scanner-derived-`practices` invariant line extended with the plan-048
  adds (u05, u09 `range-function`, u10 `break-statement`); u10 teacher-notes "Practices reappearance"
  now names `break-statement`.
- `[FIXED]` **[glm]/[fable] nit (pre-existing)** — design §7's v7 count projections are stale vs the
  ledger; added a note pointing to the ledger as the authoritative post-048 count (u04 19 … u10 24).

All book1 checks + exec-solutions/exec-lessons + PDF re-run GREEN after fixes; each drill self-contained
(own `class Pet`), verified standalone.

**Round 2 — CONSENSUS (gate CLOSED).** [self] APPROVE · **[sol] APPROVE** · **[glm] APPROVE** ·
**[fable] APPROVE** — all three externals confirmed both [OPEN]s resolved (Ex22/23 statements + teacher-notes
single-loop; Ex16/17/21/24 Pet classes minimized) with no regression; drills verified self-contained
standalone; pytest 495 passed. Full 4-way APPROVE, no open blockers. Cleared to PR + merge.

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

### Phase B — u04 quiz-show — DONE (pending [sol] round-2 confirm + PR)

- **Relocation:** running-total + count-by-condition moved into a closing `## Algorithm Extension` H2
  section as Exercises 11–12 (markers preserved, adjacent to their headings); old More-Practice → Ex8–10;
  renumbered in document order across exercises↔solutions; lesson Spotlights gathered under a closing
  `## Algorithm Extension`.
- **New drills (unmarked, Ex13–19):** two-counter tally, conditional sum (≥5 → 18), signed accumulate
  (+2/−1 → 4), opening streak (`break` → 3), the until-threshold matrix pair on 4,6,5,7,3 ÷ 12
  (check-before-add 10/2 vs add-then-check 15/3), and a sentinel-until-0 drill (Ex19, `no-exec`,
  simulated solution → 16/3). All `while`-only, u04 closure clean. Statements + solutions authored by
  separate Codex (gpt-5.6-sol) sessions from the shared inventory spec; content gate blind-solved.
- **Metadata:** `concept-scan` needed **no** scanner-derived `practices` adds (drills reuse u04's
  existing concept union); manifest untouched. teacher-notes reframed (Algorithm Extension enrichment;
  every renumber ref fixed); pattern-ledger resulting-core 12 → 19 + plan-048 note.
- **Verification:** full book1 ci-local checks + exec-solutions/exec-lessons + PDF GREEN; book2 no
  regression. Volume 1.455× cells (< 2×) — no special volume sign-off required.

### Phase C — u05 function-factory — DONE (pending [sol] round-2 confirm + PR)

- **Relocation:** running-total moved into a closing `## Algorithm Extension` H2 section as Exercise 11
  (marker adjacent); old More-Practice → Ex7–10; lesson running-total Spotlight (marker-free — practiced,
  not introduced) gathered under a closing `## Algorithm Extension`.
- **New drills (unmarked, Ex12–20):** all function-packaged — count multiples of 3, sum evens,
  triangular sum, average (float), the matrix pair (`stamps_that_fit`/`width_used` 3/45 vs
  `stamps_to_pass`/`width_when_passed` 4/70 on sizes 10..30 ÷ 60), a `while` sentinel `stamps_to_reach`,
  and two parameterized drills (`count_jumbo_stamps`, `total_ribbon`). Loops are `for i in range(...)` or
  `while` (Ex18); no list/`len`/`sum`/`input`.
- **Metadata:** General-Rule scanner-derived `practices` added to map+manifest (introduced ≤ u05):
  `if-statement`, `elif-else`, `comparison`, `while-loop`, `break-statement`. teacher-notes reframed;
  ledger resulting-core 11 → 20; design/ledger version + exercise-number refs synced to v8/Ex11; u04
  cross-ref "Unit 05 exercise 7" → "11".
- **Verification:** full book1 ci-local checks + exec + PDF GREEN; book2 no regression. Volume 1.45×
  cells (< 2×) — no special volume sign-off required.

### Phase D — u06 secret-codes — DONE (pending [sol] round-2 confirm + PR)

- **Relocation (no renumber):** u06's pattern exercises already sat last (count-by-condition Ex12,
  transform-each Ex13, linear-search Ex14), so only a `## Algorithm Extension` H2 header was inserted
  before Ex12 in exercises + solutions; Ex1–14 unchanged. Lesson gathered its two introduced-pattern
  Spotlights (linear-search, transform-each; markers in-prose) under a closing `## Algorithm Extension`.
- **New drills (unmarked, Ex15–22):** count-a-letter, three-counter tally (letters/spaces/marks),
  first-vowel search (`break`), boolean digit search, star-the-vowels map, letter-value sum (alphabet
  scan), and the matrix pair on "secret" ÷ 30 (fit 3/27/"sec" vs tip 4/45/"r"). All `for`-over-string
  scans; no `len`/`ord`/`chr`/`sum`/`.split()`/lists; letter values via the `range(26)` alphabet scan.
- **Metadata:** `concept-scan` needed **no** scanner-derived `practices` adds (all concepts already in
  u06's union). teacher-notes reframed (in-class core = Ex1–11; Algorithm Extension Ex12–22 enrichment);
  ledger resulting-core reconciled to 22.
- **Verification:** full book1 ci-local checks + exec + PDF GREEN; book2 no regression. Volume 54→71
  cells (1.31×, < 2×).

### Phase E — u07 high-score-hall — DONE (pending [glm]+[sol] round-2 confirm + PR)

- **Relocation + renumber (16 exercises):** the seven pattern-tagged exercises relocated into a closing
  `## Algorithm Extension` H2 section as Ex10–16 (spiral order, markers adjacent); the nine non-algo
  exercises renumbered to Ex1–9; the In-Class-Pattern-Practice divider dropped, More-Practice divider
  reworded. Lesson gathered its find-extreme + filter Spotlights under a closing `## Algorithm Extension`.
- **New drills (unmarked, Ex17–22):** rookie-by-name (argmin), best+worst one-pass, average-of-passers
  (zero guard), "what place would I be?", and the matrix pair on the waiting list [300,450,275,600] ÷
  1000 (fit 2/750 vs tip 3/1025/275). All list loops; no `sum`/`sorted`/`input`; minima seeded from the
  first item.
- **Cross-refs (renumber):** u04/u06/u02 teacher-notes, design §3 catalog, and ledger rows all updated
  to the new numbering (running-total u07 Ex10, count Ex11, transform-each Ex12, sentinel Ex13;
  find-extreme/filter/linear-search unchanged at 15/16/14). teacher-notes reframed (in-class core Ex1–6,
  More-Practice Ex7–9, Algorithm Extension Ex10–22 enrichment). ledger resulting-core 16 → 22.
- **Verification:** full book1 ci-local checks + exec + PDF GREEN; book2 no regression. Volume 48→60
  cells (1.25×, < 2×). A pre-existing list-slice closure issue in Challenge 1's assert was fixed here.

### Phase F — u08 word-wizard — DONE (pending round-2 confirm + PR)

- **Relocation + renumber:** the five pattern-tagged exercises relocated into a closing `## Algorithm
  Extension` H2 as Ex12–16 (count-by-condition, find-extreme, transform-each, linear-search, filter;
  markers adjacent); non-algo renumbered to Ex1–11. u08 has no lesson pattern markers (all reuse) → lesson
  unchanged.
- **New drills (unmarked, Ex17–21):** total-of-tally (unmarked accumulator — u08 stays running-total-free
  per §7), rarest-word (argmin, seed from first pair), known-vs-unknown (two-counter), and the word-length
  matrix pair on owl/dragon/cat/wizard/sun ÷ 12 (exact-hit fit 3/12 vs tip 4/18/"wizard"). Dict-loop/items,
  `len`, `in`; no `sum`/`sorted`/`min`/`input`; **long-form accumulation only (no `+=`)**.
- **Cross-refs:** u04/u06 teacher-notes, design §3, ledger updated (count u08 Ex12, find-extreme Ex13,
  transform-each Ex14; linear-search/filter unchanged 15/16). teacher-notes reframed (in-class Ex1–8,
  More-Practice Ex9–11, Algorithm Extension Ex12–21 enrichment). ledger resulting-core 16 → 21.
- **Verification:** full book1 ci-local checks + exec + PDF GREEN; book2 no regression. Volume 44→55
  cells (1.25×, < 2×).

### Phase G — u09 save-point — DONE (pending round-2 confirm + PR)

- **Relocation + renumber:** the five pattern-tagged exercises relocated into a closing `## Algorithm
  Extension` H2 (transform-each Ex12, running-total Ex13, linear-search Ex14, find-extreme Ex15, filter
  Ex16); non-algo Ex4–12→Ex3–11; the two `stretch` Challenges → Ex24/25. Only transform-each renumbered
  (Ex3→Ex12); the other four kept 13–16. Lesson unchanged (no pattern markers).
- **Exec-order (stateful file-I/O unit):** each relocated file reader re-saves the file it reads first
  (savegame.txt, or settings.txt for linear-search) → order-independent; Ex12 aligned to the ambient
  `savegame.txt` = [300,450,725,1350]. New drills use inline score lists (no shared-file reads).
- **New drills (unmarked, Ex17–23):** count boss-saves, count-average, lowest-by-scan (argmin), position
  search, first-≥-target search, and the matrix pair on [300,450,725,1350] ÷ 1000 (fit 2/750 vs tip
  3/1475/725). Long-form accumulation (no `+=`).
- **Metadata:** General-Rule `practices` add `range-function` (map+manifest, introduced ≤ u09).
  Cross-refs: transform-each u09 Ex3→Ex12 (u06 tn, design §3, ledger). teacher-notes reframed (in-class
  Ex1–8, More-Practice Ex9–11, Algorithm Extension Ex12–23, Challenges Ex24–25). ledger resulting-core
  16 → 23.
- **Inventory deviation (recorded):** the drills use inline score lists rather than the inventory's
  "file-line loops", and drop the filter-and-re-save candidate (the matrix pair fills the ≤7 cap) — chosen
  to avoid file-state fragility; file-reading is carried by the five relocated reps + core Ex1–8.
- **Verification:** full book1 ci-local checks + exec + PDF GREEN; book2 no regression. Volume 43→58
  cells (1.35×, < 2×).

### Phase H — u10 pet-simulator — DONE (pending round-2 confirm + PR)

- **Relocation (header-only, no renumber):** u10's three pattern exercises (find-extreme Ex13,
  sentinel-loop Ex14, filter Ex15) already sat last, so a `## Algorithm Extension` H2 header was inserted
  before Ex13 (markers adjacent; Ex1–15 unchanged; Ex13/14 cross-refs unchanged). Stretch Challenges →
  Ex25/26. Lesson unchanged (no pattern markers).
- **New drills (unmarked, Ex16–24):** count hungry, team-hunger sum, find-by-name (found+`break`), roster
  map, hungriest & least (max & argmin), mood tally-by-key, feed-every-hungry filter-action, and the
  **downward** matrix pair (Buddy hunger 8, snacks 2/4/3/5 toward floor 0 → check-before-feed 2/2 vs
  feed-then-check −1/3, tipping snack 3). Each **self-contained** (own `class Pet` + inline pets),
  single-loop, long-form (no `+=`), no `None`.
- **Metadata:** General-Rule `practices` add `break-statement` (map+manifest). No cross-ref changes.
  teacher-notes reframed (in-class Ex1–8,12; Algorithm Extension Ex13–24 enrichment; Challenges Ex25–26);
  ledger resulting-core 15 → 24.
- **Verification:** full book1 ci-local checks + exec + PDF GREEN; book2 no regression. Volume 47→65
  cells (1.38×, < 2×).

_(Phase I + Phase V report appended as each slice lands.)_

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

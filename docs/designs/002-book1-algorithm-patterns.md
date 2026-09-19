# Design 002 — Book 1 Algorithm-Pattern Thread

**Status:** APPROVED — v9. v6 2-way design review CLOSED ([sol] APPROVE + [fable] APPROVE, 2026-09-18); **v7 (2026-09-18): user-directed relaxation — the ≤16 per-unit exercise-count cap is REMOVED** (no max exercise ceiling). This is a constraint-lifting edit only: no §3 locus is added, dropped, or re-classified, and the honest per-unit counts below are retained as *informative* pacing data, not a cap — so it does not reopen the design review. The §2 *conceptual* depth ceiling (no big-O/sorting/recursion) is unaffected. **v8 (2026-09-18, plan 048):** the algorithm track becomes the explicit end-of-notebook `## Algorithm Extension` enrichment section and "home in-class" is relaxed to enrichment routing (see §6/§13); still no §3 locus added/dropped/re-classified. **v9 (2026-09-18, plan 049): the HOME Spotlight in the lesson `## Algorithm Extension` must teach its pattern with a graduated worked-example ladder (code rungs + `**Notice:**` + a put-it-together), consistent with the rest of the lesson — the reappearance Spotlight stays a retrieval one-liner.** v9 adds a mandatory student-facing requirement but adds/drops/re-classifies no §3 locus (and no `introduces`/`requires` change), so it does not reopen the design review beyond the plan-049 gate; the target end-state is reached unit-by-unit as home units are enriched. Ready for the plan lifecycle.
**Scope:** Book 1 only. Book 2 inherits the technique ids via `dependency_baseline`; it grows its own.

## 0. Design ↔ plan boundary

This design fixes the **shape**: the pattern set, homes, forward-only closure-safe spiral, the reuse/
promote/new status of each locus (verified against the current notebooks), the tracking model, and the
CI additions in principle. The **plan** owns the fine mechanics: the exact ~28-row cell ledger
(entry → exact exercise heading → core/stretch → action → resulting unit core count), the precise
`pattern-marker` cardinality/adjacency rules, the catalog generator command + inputs, and the
per-check pytest fixtures. Items marked "(plan)" below are deliberately deferred, not omitted.

## 1. Motivation

Layer a small set of **named, reusable algorithm patterns** — the small *jobs* a concept does — through
Book 1, on top of plan-037's exercise depth. Intents: (1) concept mastery through real jobs;
(2) computational thinking — contrast how a task *feels* to a person vs. the explicit step-by-step state
a program needs; (3) spaced, *varied* repetition (the enforced spiral).

## 2. Scope & depth ceiling

- **Linear, single-pass patterns** + one gentle-efficiency idea students may act on: **"stop early"**
  (`break` when you've found it — `break` is introduced in u04).
- **Kept teacher-only** (not in student text): "one pass beats two" (it contradicts real Book 1
  exercises that legitimately loop then call `max()`). **Not used at all:** "short-circuit" (Book 2's).
- **NOT in Book 1** (Book 2's, per design 001): big-O/complexity, sorting internals, recursion,
  two-pointers, prefix sums, graph traversal, complete search. Framing stays qualitative.

## 3. The pattern catalog (7) + variations

Each pattern is a `kind: technique` concept (§4). `name` carries the kid + formal name together. Every
reappearance is **core** (never stretch) and in a unit ≥ the home (forward-only). Status per locus,
**verified against current notebooks**: **reuse** = existing core exercise re-framed under a Spotlight +
tagged; **promote** = existing *stretch* exercise moved to core *with the semantic edit named*; **new** =
net-new core exercise.

| id | name (kid + formal) | home | hook (softened, kid-true) | spiral — ≥3 core reappearances (status) |
|----|------|------|------|------|
| `running-total` | Running total (accumulate) | u04 | the program needs a *named box* holding the total-so-far, updated each step | u05 Ex11 `total_card_borders` (reuse), u07 Ex4 average (reuse), u09 read-and-sum (**new**) |
| `count-by-condition` | Counting by condition (count) | u04 | keep a counter; check each item once, bump it when it matches | u06 count-matches (**new**), u07 Ex5 above-threshold (reuse), u08 Ex5/7 **tally-by-key** (reuse; the *count-per-group* variation, named in the catalog) |
| `find-extreme` | Find the best (max / argmax) | u07 | keep the *best so far* while scanning — and remember *who*, not just the number | home = **champion-by-name** (parallel names/scores, keep `best_name`+`best_score`, **new**), u08 Ex6 most-common `best_word`/`best_count` (reuse), u09 best-so-far replacing `max()` (**new**), u10 Ex13 happiest-pet (**promote** — add `best_pet`, not just the number) |
| `linear-search` | Scan until found + stop early | u06 | check items one by one; `break` when found = stop working early | home anchors the lesson's `for position in range(26)` scan + a home exercise that adds the `break` (**new/adapt**), u07 loop+`break` search (**new**), u08 reverse-lookup value→key scan (**promote** — add the `break`; the CT contrast "the dict finds by *name* instantly; by *value* we're back to one-by-one"), u09 find-in-file (**new**) |
| `transform-each` | Do the same to each (map) | u06 | apply the *same step* to every item, producing a **new sequence** | u07 Ex6 (reuse), u08 Ex10 translate-each (reuse), u09 Ex3 line→int (reuse) |
| `filter-into-list` | Keep the ones that pass (filter) | u07 | build a **new** list of only the items that pass a test | home = clean filter (**new**); reappearances u08 (**new**), u09 (**new**), u10 (**new**) — all three. No other pre-capstone home exists (project-01 precedes u07; project-02 is the capstone; checkpoints don't tag), so all three are required. |
| `sentinel-loop` | Repeat until done (sentinel loop) | u02 | *you* know when you're done; the program must ask "done yet?" every pass | project-01 M1 `while choice != "q"` (reuse), u07 Ex12/13 while (reuse), u10 Ex14 `while happiness<10` (**promote**) — 3 pre-capstone entries. **u04 Ex8 excluded** (`while attempts<3` is a counter-bounded retry, not a sentinel — see the embodiment definition); Ex10's `while stops<3` likewise excluded. |

Variations named in the catalog (NOT separate patterns): **tally-by-key** (count per group,
`counts[w]=counts.get(w,0)+1` — the most Book-2-relevant Book 1 shape). (The earlier draft's `all-any`
is **dropped** — `all`/`any` are not in Book 1's taught builtins.)

**Embodiment definitions** (what a tagged exercise MUST contain — the content-gate's blind-solve test):
running-total = a `total` var updated in a loop; count-by-condition = a counter bumped under a condition
in a loop; find-extreme = an explicit best-so-far loop keeping the *winner* (name/object), NOT `max()`
alone; linear-search = a sequential scan + comparison + early `break` (NOT `in`/`.get()`/dict-index);
transform-each = a loop producing a *new* sequence; filter = a loop appending passing items to a *new*
list; sentinel-loop = a `while` on a sentinel/condition re-checked each pass (NOT a counter-bounded loop).

Every home's enabling concepts are introduced ≤ the home (co-introduced where same-unit): sentinel-loop
u02 (while/comparison u02); running-total & count u04 (accumulator u04; arith/if/comparison ≤u02);
linear-search u06 (for u03, break u04, comparison ≤u02, in-operator u06); transform-each u06 (for u03,
string-methods u06); filter & find-extreme u07 (list-append/list-loop u07, if/comparison ≤u06).

## 4. Tracking model — reuse the existing concept model (`kind: technique`)

No separate registry. The 7 patterns are `kind: technique` entries in the existing
`book1/curriculum/concepts.yaml`, `category: techniques` (the Book 2 precedent; the schema allows exactly
`{id, name, category}` + optional `kind` — **no new fields**, so no schema migration). The kid+formal
name lives in `name` (e.g. `name: "Running total (accumulate)"`). They are tagged through the **existing**
`introduces`/`practices` lists in each unit's `manifest.yaml` + `coverage-map.yaml`.

Inherited from `tools/curriculum.py` once valid ids/tags exist: exactly-one-home, pre-capstone ≥1
practice, checkpoint-taughtness, unknown-id/kebab/dup validation, manifest==map, cross-book uniqueness +
`dependency_baseline` (so Book 2 inherits the ids — the cross-book contract, free).

**`requires` semantics (corrected):** the inherited `prereq_findings` computes `requires ∪ practices −
seen` *before* adding the entry's own `introduces`, so **same-unit enabling concepts must NOT go in a
home's `requires`** (they are co-introduced; the safety property holds by co-introduction). Only
*earlier-unit* enablers, if any, go in `requires`. Intra-unit teaching order (Spotlight/exercise after
the enabling lesson beat) is a **content-gate duty**, not a CI claim. Enabling concepts are recorded as
**catalog prose**; `patterns-doc-check` asserts each is introduced ≤ the home.

**concept-scan:** technique ids are added to each book's dynamic `never_flag` profile (the existing
mechanism in `concept_scan.py` that already covers Book 2 techniques — NOT the module-level
`MANUAL_ONLY` set); scan stays silent on them, embodiment is reviewer-enforced.

## 5. New tooling (three additions, wired into `ci-local`; mechanics deferred to plan)

1. **`technique-spiral`** — the one new rule: each **Book-1-registered** pattern (scoped to Book 1's
   own technique ids / Book 1 CI invocation — a book-wide rule would wrongly fail Book 2's techniques)
   must be `practices`-tagged in **≥3 pre-capstone, non-checkpoint** entries. It also rejects a locus
   whose marked exercise is `stretch` (so "3 tags" can't be satisfied by stretch cells).
2. **`patterns-doc-check`** — `book1/reference/patterns.md`'s "where you'll meet it" table is generated
   from the map (committed == generated); the check also verifies every technique id appears with its
   name, hook, and enabling-concepts, and that each enabling concept is introduced ≤ the home. (plan:
   generator command + exact inputs.)
3. **`pattern-marker`** — every entry that tags a technique id has a matching `<!-- pattern: <id> -->`
   marker cell in that entry's notebooks, mapped **kind→notebook** like `concept_scan.entry_notebooks`
   (unit home: `lesson.ipynb` + the exercise; unit reappearance: `exercises.ipynb` above the tagged
   exercise; **project: `brief.ipynb`**). **Checkpoints do not tag** patterns (simplest — avoids a
   marker in student-facing assessment source). (plan: exact cardinality/adjacency/core-detection.)

Embodiment stays **tag + reviewer** (no AST `pattern-scan`). Markers are HTML comments → dropped by
nbconvert/pandoc, hidden in JupyterLab; hygiene/PDF unaffected.

## 6. Student-facing form

- **Algorithm-Extension section (v8).** Every unit that hosts pattern content gathers ALL of it — the
  pattern-tagged exercises **and** the extra unmarked loop-drill reps — into one explicitly-labelled
  `## Algorithm Extension` section (H2, matching `## Challenge`) at the END of `exercises.ipynb`, placed
  as the last core `## Exercise N` block immediately before the trailing `## Challenge` (stretch) cells
  (each unit keeps its own Challenge convention — some units number Challenges `## Challenge N`, others
  tag them as `stretch` `## Exercise N`). The unit's `lesson.ipynb` likewise gathers its pattern
  Spotlight(s) under a closing `## Algorithm Extension` markdown section. Numbering stays `## Exercise N`
  so `structure-check`/`solutions_structure` heading-pairing and `stretch-check` are unaffected; markers
  stay immediately before their exercise / inside their Spotlight so `pattern-marker`/`technique-spiral`
  are unaffected. The algo exercises are simply the highest-numbered core exercises. This is the
  student-facing home the design points to; it is reached unit-by-unit as each migration slice merges.
- **Spotlight cell** (recurring markdown + marker): home = a short lesson cell (names the pattern, its
  hook, "stop early" where relevant) **followed by a graduated worked-example ladder (v9): 2+ executable
  `code` rungs, each with a `**Notice:**`, adding one idea at a time and ending in a "put it together"
  cell — the same teaching form as the rest of the lesson (L1/L2/L3, plans 031–035)** — plus the
  authoring exercise. The pattern-*naming* prose stays read in-class; the ladder is teacher-routed
  enrichment. reappearance = a one-liner asking the student to *identify* the pattern ("Which pattern?
  Which variable is the 'so-far'?") — retrieval practice, NO ladder.
- **Variation axes** — each reappearance differs from every earlier one on ≥1 axis, recorded in its
  Spotlight: data type (numbers→strings→lists→dicts→file lines→objects), packaging
  (inline→function→method), twist (empty / tie / early-stop).
- **Catalog** — `book1/reference/patterns.md` (the `reference/` dir already exists, empty): the 7 patterns (name, hook, enabling
  concepts, generated home+reappearances table). Delivered to students via `scripts/build-pdf.sh`
  (pandoc, like `syllabus.md`).
- **teacher-notes** (in the content dispatch): the `## Algorithm Extension` section is **end-of-lesson
  enrichment, not required in-class (v8)** — teacher-notes route the whole extension as
  time-permitting / homework / More-Practice / differentiation. The **exception** that stays read
  in-class is the lesson-side Spotlight that first *names* each pattern, so later retrieval prose can
  refer to a name every student has met. (This relaxes the earlier "home is always in-class" rule, which
  reviewers repeatedly flagged now that the algo track is an explicit extension.) Add a **2-minute
  unplugged trace** per home (e.g. five face-down cards, flip one at a time, find the biggest).

## 7. Footprint, pacing & the reuse ledger (honest counts)

**No max exercise ceiling** (v7 user directive): the per-unit counts below are honest *pacing* data —
they inform teacher-notes routing (in-class vs. homework/More-Practice) and the Phase-V volume budget,
but no unit is capped at a fixed number of core exercises. The reuse ledger still reports each unit's
resulting core count so pacing stays visible; it no longer has to *prove* any unit stays ≤16.

Current post-037 core: u02 8, u03 10, u04 10, u05 11, u06 11, **u07 13, u08 14**, u09 12,
u10 12. Corrected against reality:
- **u09 is the heavy one:** best-so-far, find-in-file, read-and-sum, filter are **new** (Ex4 uses
  `max()`, Ex6 uses `in`, no exercise sums) → u09 12 → **15–16**.
- **u07 → 16:** champion-by-name + clean-filter home + loop-and-break search (3 new).
- **u08 → 16:** reverse-lookup promote (+1 core) + filter (+1 new). Running-total is **dropped** from
  u08 (no natural sum — avoids overflow).
- u06 11 → ~13 (count-matches new + linear-search & transform-each homes). u04 10 → ~11–12 (running-
  total + count-by-condition homes may adapt existing scoring exercises; **no sentinel-loop tag** —
  dropped). u10 12 → **15** (promote Ex13 + Ex14 + filter new). u05/u02 no net-new (reuse the running-total exercise; u02 gets
  one lean one-sentence Spotlight only).
- **Projected core counts: u07≈16, u08≈16, u09≈16, u10≈15** (current core counts + the §3 loci) — these
  are the natural landing points of the §3 loci, **not caps**; §3's per-locus reuse/promote/new statuses
  stand and no relocation is needed. The **plan's ~28-row ledger records each unit's resulting core
  count** at exact-cell fidelity (informative pacing data, no longer a ≤16 proof). With the ceiling
  lifted, a locus the design marked **reuse** purely to conserve unit budget MAY instead be authored as
  a distinct **new** rep where that teaches better — a plan-time call that still must not add, drop, or
  re-classify a §3 *locus* (the spiral is fixed); it only changes how an existing locus is realized, and
  any such choice is recorded in the ledger and confirmed at the content gate. Carry
  plan-037 Phase-V volume thresholds (>2× cells / >30% PDF pages / >25% wall-time = gate finding; 120 s
  per-cell exec) as the remaining pacing guardrail.
- Estimate **+12–16 net-new exercises** (rest is reuse-tag + 3 promotions).

## 8. Rollout

Inherited structural checks are green from PR-1. **Vertical slice per complete pattern:** a technique id
is added to `concepts.yaml` only when its home + all ≥3 core reappearances + catalog row land together —
so `main` is valid at every merge and `technique-spiral` is **never red** (one rule; no SKIP-until
needed). Phased PRs by term to keep the content gate's blind-solve tractable (batching = plan decision).
**Sequence the `filter-into-list` slice last** — its vertical slice touches u07+u08+u09+u10 together
(four units in one PR), so it is the largest/riskiest slice. The plan must
**design `pattern-marker` (§5.3) and `technique-spiral`'s stretch-rejection (§5.1) together** — the
latter needs the marker's tag→cell link to tell whether a locus is stretch.

## 9. Verification (named phase — required)

Ships content + tooling → named phase: `ci-local` ALL GREEN incl. `technique-spiral`,
`patterns-doc-check`, `pattern-marker`, and the inherited concept checks; pytest with discriminating
fault fixtures (duplicate home; practice-before-home; only-two-practices; checkpoint-only-third;
unknown id; manifest/map mismatch; stale catalog; **stretch-only embodiment**; missing marker); notebook
exec + hygiene + PDF (incl. the catalog); pre-merge guard. Embodiment confirmed at the content gate
(reviewers blind-solve each marked exercise vs. §3's definitions).

## 10. Boundary & cross-book contract

Book 1 owns "scan until found / stop early" on *small* strings & lists; **Book 2 U05 formally revisits**
linear search with binary/complete search + complexity (design 001). A follow-up amends design 001 §2's
prerequisite surface once these ids ship (not now). No contradiction with plan 037 (sits on its reps);
`pattern-marker` partially offsets 037's "listed-but-not-student-exercised" follow-up.

## 11. Out of scope
- Separate `patterns.yaml`; an AST `pattern-scan`; big-O/sorting/recursion; Book 2 pattern growth;
  re-opening plan-037 coverage.

## 12. Decisions resolved
- Intent = mastery + computational-thinking + spaced varied repetition.
- Ceiling = linear + "stop early" (teacher-only "one pass beats two"; no "short-circuit").
- Tracking = **`kind: technique`, `category: techniques`** in `concepts.yaml`; formal name folded into
  `name`; **no new schema fields**; same-unit enablers co-introduced (not in `requires`).
- Embodiment = tag + reviewer; exact cells via `<!-- pattern: id -->` markers; checkpoints don't tag.
- Spiral N = **≥3** core, non-checkpoint reappearances; `technique-spiral` scoped to Book 1.
- Pattern set = the 7 in §3 (forward-only, closure-safe, reality-checked loci) + tally-by-key variation.
- Homes: sentinel-loop u02; running-total + count-by-condition u04; linear-search + transform-each u06;
  filter-into-list + find-extreme u07.

## 13. Revision history
- **v1:** separate `patterns.yaml`; backward spirals; `in`-based / stretch embodiments.
- **v2:** reuse `kind: technique`; forward-only spiral; champion-by-name; sentinel-loop rename; markers;
  catalog; ledger mandate.
- **v3 (2026-09-18):** round-2 fixes — `category: techniques` + formal name in `name` (no new fields);
  corrected `requires` semantics (same-unit enablers co-introduced, not in `requires`); phantom reuse
  loci corrected against the notebooks (u05 running-total reuse; u09 read-and-sum/best-so-far/find-in-file new;
  u08 dropped from running-total; sentinel-loop → u04 Ex8 / promote u10 Ex14; find-extreme u10 add
  `best_pet`; linear-search u08 add `break`); `technique-spiral` scoped to Book 1 + rejects stretch loci;
  markers map kind→notebook incl. `brief.ipynb`, checkpoints don't tag; `all-any` dropped; footprint
  corrected (u09 heavy; u07/u08/u09 at ceiling → ledger must prove ≤16); design↔plan boundary (§0).
- **v4 (2026-09-18):** round-3 fixes — `filter-into-list` restored to all three reappearances
  (u08+u09+u10, each ≤16); **`sentinel-loop` drops the u04 Ex8 locus** (counter-bounded retry, violates
  the "NOT counter-bounded" embodiment) → 3 genuine entries (project-01/u07/u10); §7 relocation levers
  rewritten (no spare home); stale `reference/` note + filter-slice-last + marker↔spiral co-design.
- **v7 (2026-09-18):** user-directed relaxation — **removed the ≤16 per-unit exercise-count ceiling** (no
  max exercise ceiling). §7 reframed: honest counts retained as informative pacing data, the ledger's
  ≤16 *proof* mandate dropped (it now just records resulting counts), the dual-marker overflow lever
  removed (moot), and reuse loci may be realized as new reps where that teaches better (no §3 locus
  changes). §3 filter-into-list "each fits ≤16" note and §8 "16-core ceiling" rationale updated. The §2
  conceptual depth ceiling and plan-037 Phase-V volume thresholds are unchanged. Constraint-lifting only
  → no design re-review required.
- **v8 (2026-09-18):** user-directed restructuring (plan 048) — the algorithm track becomes an explicit
  end-of-notebook **`## Algorithm Extension`** enrichment section. §6 gains the Algorithm-Extension
  structure bullet (H2 section, last core `## Exercise N` before `## Challenge`; lesson Spotlights
  gathered under a closing `## Algorithm Extension`; numbering + markers unchanged so all CI checks stay
  agnostic), and the teacher-notes bullet **relaxes "home is always in-class" → "extension enrichment
  routed by teacher-notes"**, keeping only the pattern-*naming* lesson Spotlight in-class. Plan 048 also
  adds **unmarked** extra loop-drill reps (no `<!-- pattern: id -->` marker, no new technique `practices`
  tag): **no §3 locus is added, dropped, or re-classified**, and §7's "running-total dropped from u08"
  note stands (u08's sum rep is unmarked). Constraint-restructuring only → no design re-review beyond the
  plan-048 gate. The target end-state is reached unit-by-unit as Phases B–I merge; v8 is not "violated"
  by a not-yet-migrated unit.
- **v9 (2026-09-18):** user-directed enrichment (plan 049) — the **HOME** Spotlight in the lesson
  `## Algorithm Extension` must teach its pattern with a **graduated worked-example ladder** (executable
  `code` rungs + `**Notice:**` each + a put-it-together), the same form as L1/L2/L3 (plans 031–035),
  because plan 048 shipped the home Spotlights as prose-only, inconsistent with the rest of Book 1. §6
  "Spotlight cell" updated. The pattern-naming prose stays in-class; the ladder is teacher-routed
  enrichment (60–90 min pacing unchanged). Reappearance Spotlights stay retrieval one-liners (NO ladder);
  reuse units (u05/u08/u09/u10) + project-01 unchanged; u01/u03 exempt. Adds a mandatory student-facing
  requirement but **no §3 locus is added, dropped, or re-classified** and no `introduces`/`requires`
  change — so no design re-review beyond the plan-049 gate. Reached unit-by-unit as each home unit's
  slice merges (sequenced behind the corresponding plan-048 slice); homes = u04, u06, u07, u02.

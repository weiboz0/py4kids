# Design 002 — Book 1 Algorithm-Pattern Thread

**Status:** proposed — **v2** (rev. 2026-09-17 after a 2-way design review: `[sol]` REJECT + `[fable]`
APPROVE-WITH-CHANGES, both folded). Awaiting re-review → plan lifecycle.
**Scope:** Book 1 only. Book 2 inherits the technique ids automatically (see §4), but grows its own.

## 1. Motivation (unchanged)

Layer a small set of **named, reusable algorithm patterns** — the small *jobs* a concept does — through
Book 1, on top of plan-037's exercise depth. Three intents:
1. **Concept mastery through real jobs** (running total, counting, finding the biggest).
2. **Computational thinking** — each pattern contrasts how it *feels* to a person vs. the explicit
   step-by-step state a program needs.
3. **Spaced, varied repetition** — each pattern reappears in several later units in *different* contexts
   (the enforced "spiral").

## 2. Scope & depth ceiling

- **Linear, single-pass patterns** + one gentle-efficiency idea students may act on: **"stop early"**
  (`break` when you've found it). Book 1 owns `break` only.
- **Removed from student-facing text** (design-review): "one pass beats two" (it contradicts real Book 1
  exercises that legitimately loop then call `max()`; keep it as a *teacher discussion prompt* only) and
  "short-circuit" (that is Book 2 U02's concept).
- **NOT in Book 1** (Book 2's, per design 001): big-O/complexity, sorting internals, recursion,
  two-pointers, prefix sums, graph traversal, complete search. Computational-thinking framing stays
  qualitative, never asymptotic.

## 3. The pattern catalog (7) + variations

Each pattern carries a kid-facing `name`, a `formal_name` (for the Book 2 handoff), a home unit, a
softened hook, its enabling concepts (tracked via the normal `requires`), and a **forward-only,
closure-safe** spiral (every reappearance is in a unit ≥ the home and is a **core** — never stretch —
embodiment). "reuse" = an existing exercise re-framed under a Spotlight + tagged; "new/promote" = net-new
core exercise or a stretch→core promotion.

| id | name (formal) | home | hook (softened) | requires | spiral (≥3 core reappearances) |
|----|------|------|------|----------|------|
| `running-total` | Running total (accumulate) | u04 | the program needs a *named box* that holds the total-so-far and updates it each step | accumulator, arithmetic | u05 `total_up_to(n)` (range-based, **new**), u07 Ex4 average (reuse), u08 sum-counts (reuse), u09 read-and-sum (reuse) |
| `count-by-condition` | Counting by condition (count) | u04 | keep a counter; check each item once and bump it when it matches | accumulator, if-statement, comparison | u06 Ex8 (reuse), u07 Ex5 above-threshold (reuse), u08 count (reuse). *Variation:* **tally-by-key** (`counts[w]=counts.get(w,0)+1`, u08) — named in the catalog as a distinct "count per group", not a separate pattern |
| `find-extreme` | Find best (max/argmax) | u07 | keep the *best so far* while scanning — and remember *who*, not just the number | list-loop, comparison | **home = champion-by-name** (parallel names/scores, keep `best_name`+`best_score`, **new** — motivates why `max()` isn't enough), u08 Ex6 most-common (reuse), u09 best-so-far not `max()` (**new**), u10 Ex13 top-pet (**promote** to core) |
| `linear-search` | Scan until found + stop early | u06 | check items one by one; `break` when found = stop working early | for-loop, comparison, break-statement, in-operator | home anchors on the lesson's `for position in range(26)` scan (add the `break`), u07 loop+`break` search (**new**), u08 **reverse lookup** value→key scan (**promote** — the key CT contrast: "the dict finds by *name* instantly; by *value* we're back to one-by-one"), u09 find-in-file (**new**) |
| `transform-each` | Do the same to each (map) | u06 | apply the *same step* to every item, producing a **new sequence** | for-loop, string-methods | u07 Ex6 (reuse), u08 Ex10 translate-each (reuse), u09 Ex3 line→int (reuse) |
| `filter-into-list` | Keep the ones that pass (filter) | u07 | build a **new** list of only the items that pass a test | list-append, list-loop, if-statement | home = clean filter (**new**), u08 (reuse/new), u09 (reuse/new), u10 (reuse/new) |
| `sentinel-loop` | Repeat until done (sentinel loop) | u02 | *you* know when you're done; the program must ask "done yet?" every pass | while-loop, comparison | u04 (reuse), project-01 M1 (reuse), u07 Ex12/13 while (reuse), u10 Ex10 (reuse) |

Notes / design-review corrections folded:
- **Backward spirals removed** — the earlier draft's find-extreme→u05, filter-into-list→u06,
  transform-each→u03 all *preceded* their homes (and two broke concept closure). Gone.
- **`sentinel-loop`** is the renamed `loop-until` (u02's `while guess != secret` is a sentinel, not a
  threshold).
- Every home's `requires` are introduced ≤ the home (verified vs. `coverage-map.yaml`): sentinel-loop
  u02 (while/comparison u02); running-total & count u04 (accumulator u04, arith/if/comparison u02);
  linear-search u06 (for u03, break u04, comparison u02, in-operator u06); transform-each u06 (for u03,
  string-methods u06); filter/find-extreme u07 (list-append/list-loop u07, if/comparison ≤u06).
- **Embodiment definitions** (what a tagged exercise MUST contain, for the content gate to count it):
  running-total = a `total` variable updated inside a loop; count = a counter bumped under a condition
  in a loop; find-extreme = an explicit best-so-far loop keeping the winner (NOT `max()` alone);
  linear-search = a sequential scan + comparison + **early `break`** (NOT `in`/`.get()`/dict-index);
  transform-each = a loop producing a *new* sequence; filter = a loop appending the passing items to a
  *new* list; sentinel-loop = a `while` on a sentinel/condition re-checked each pass.

## 4. Tracking model — reuse the existing concept model (`kind: technique`)

Per the design review + author decision: **no separate `patterns.yaml`**. The 7 patterns are registered
as **`kind: technique`** entries in the existing `book1/curriculum/concepts.yaml` (the mechanism Book 2
already uses for greedy/two-pointers/etc., design 001 §5), with a `category: patterns` and a `formal_name`.
They are tagged through the **existing** `introduces`/`requires`/`practices` lists in each unit's
`manifest.yaml` + `coverage-map.yaml` — **no new schema fields** (this sidesteps the exact-key schema
gotcha entirely).

Inherited for free from `tools/curriculum.py`: exactly-one-home (`introduction_findings`), closure
(`prereq_findings`), pre-capstone practice (`practice_findings`), checkpoint-assesses-only-taught,
unknown-id + kebab + dup-id validation, manifest==map, and cross-book id uniqueness (so Book 2's
`dependency_baseline` inherits these ids — the cross-book contract, free). Patterns also fall under
plan-037's ≥3/≥5 **reviewer** proficiency bar automatically.

**Concept-scan:** technique ids are not AST-detectable, so they go in `concept_scan`'s `MANUAL_ONLY`
set (the design-001 precedent) — scan stays silent on them; embodiment is reviewer-enforced.

**`requires` semantics:** the enabling concepts ARE the pattern's `requires` (existing closure applies,
`≤` includes the home entry's own introductions; intra-unit order is a content-gate duty — §6). No
separate `requires_concepts` field; enabling concepts also appear as catalog prose.

## 5. New tooling (small — three additions, wired into `ci-local`)

Everything above is inherited. Only these are new (ported into `tools/`, registered, blocking,
book-level — the plan-016 pattern):
1. **`technique-spiral`** — the one genuinely new rule: every `kind: technique` concept must be
   `practices`-tagged in **≥3** pre-capstone entries (checkpoints do **not** count toward N — assessment
   isn't practice; they may still tag for honesty). Extends the inherited ≥1 practice rule.
2. **`patterns-doc-check`** — `book1/reference/patterns.md`'s "where you'll meet it" table is
   **generated from the map** and the check asserts committed == generated (no hand-sync drift); it also
   verifies every technique id + its `formal_name`/hook/home appear.
3. **`pattern-marker`** — every entry that `introduces`/`practices` a technique id has a matching
   `<!-- pattern: <id> -->` marker cell in that entry's notebooks (home: `lesson.ipynb` + the exercise;
   reappearance: `exercises.ipynb` immediately above the tagged exercise). This gives reviewers/CI the
   *exact* cell to inspect (fixes "which of 14 exercises earns the tag?"). Markers are markdown →
   hygiene/PDF unaffected.

Embodiment stays **tag + reviewer** (no AST `pattern-scan` — a pattern is a shape, not a token). CI
enforces the spiral/closure/marker/doc metadata; the 4-way content gate's blind-solve confirms each
marked exercise embodies its pattern against the §3 embodiment definitions.

## 6. Student-facing form

- **Spotlight cell** (recurring markdown, tagged with the marker): at the **home**, a short cell in the
  lesson + the authoring exercise naming the pattern, its hook, its `formal_name`, and the "stop early"
  note where relevant; at a **reappearance**, a one-liner that asks the student to *identify* the pattern
  ("Which pattern is this? Which variable is the 'so-far'?") — retrieval practice, not just relabeling.
- **Variation axes** — each reappearance must differ from every earlier one on ≥1 axis, recorded in its
  Spotlight: **data type** (numbers→strings→lists→dicts→file lines→objects), **packaging**
  (inline→function→method), **twist** (empty input / tie / early-stop). This is what makes the spiral
  reinforcement rather than repetition.
- **Catalog** — `book1/reference/patterns.md`: the 7 patterns (kid + formal name, hook, enabling
  concepts, and the generated home+reappearances table). **Delivered to students** — added to
  `scripts/build-pdf.sh` (pandoc, like `syllabus.md`), so it is genuinely "the one place to see the whole
  vocabulary."
- **teacher-notes** (part of the content dispatch): every touched unit names the **in-class** pattern
  appearance (the home is always in-class) and routes the rest to homework/More-Practice; each home
  gets a **2-minute unplugged trace** (e.g. five face-down index cards, flip one at a time, find the
  biggest) — the move that makes "step-by-step" land for 12-year-olds.

## 7. Footprint, pacing & the reuse ledger

Current post-037 core counts (ceiling 16): u02 8, u03 10, u04 10, u05 11, u06 11, **u07 13, u08 14**,
u09 12, u10 12. So u07 has ~3 slots and u08 ~2 — exactly where new pattern homes/embodiments are needed
(u07: champion-by-name, a clean filter, a loop+`break` search; u08: reverse-lookup promotion + a
filter). Everything else spreads +1–2 over u04/05/06/09/10. **Prefer stretch→core promotions** (u08
reverse-lookup, u10 top-pet) over net-new where they exist.

The **plan must open with a ~29-row ledger** (one row per home+reappearance): `entry, exact exercise
heading, core/stretch now, action (reuse-tag / promote / new), enabling concepts, resulting unit core
count`. The design fixes the *shape* (the §3 table); the ledger commits each row to a real cell and
proves no unit crosses 16 core. Carry plan-037 Phase-V volume thresholds (>2× cells / >30% PDF pages /
>25% wall-time = content-gate finding; 120 s per-cell exec).

Estimated **+12–20 net-new exercises** (range = how many reappearances land on existing cells vs. new);
justified only because u07/u08 sit at the ceiling and the rest spreads thin. u01 untouched; **u02 gets
one lean one-sentence Spotlight** for sentinel-loop (syllabus lean rule at the fragile point).

## 8. Rollout (must avoid a permanently-red blocking spiral check)

Structural checks are **inherited and green from PR-1** (home-uniqueness, closure, ≥1 practice,
manifest==map, unknown-id). The **new `technique-spiral` (≥3) rule is wired blocking only when the full
spiral exists** — either the final content PR, or landed earlier as a `SKIP (plan NNN)` line (the
AGENTS.md convention) until then. **Registry grows per PR**: a technique id is added to `concepts.yaml`
only when its home + all ≥3 core reappearances + catalog row land together (the "vertical slice per
complete pattern" both reviewers preferred) — so `main` is valid at every merge. Phased PRs by term to
keep the content gate's blind-solve tractable; the exact batching is a plan decision.

## 9. Verification (named phase — required)

Ships content + tooling → named phase: `ci-local` ALL GREEN incl. `technique-spiral`,
`patterns-doc-check`, `pattern-marker`, and the inherited concept checks; pytest with **discriminating
fault fixtures** (duplicate home; practice-before-home; only-two-practices; capstone-only-third;
unknown id; unmet same-entry requirement; manifest/map mismatch; stale catalog; stretch-only
embodiment; missing marker); notebook exec + hygiene + PDF (incl. the catalog); pre-merge guard.
Embodiment confirmed at the content gate (reviewers blind-solve each marked exercise vs. §3's
definitions).

## 10. Boundary & cross-book contract

- **Linear search ownership:** Book 1 owns "scan until found / stop early" on *small* strings & lists;
  **Book 2 U05 formally revisits it** (design 001) alongside binary/complete search + complexity. Record
  here; a follow-up amends design 001 §2's prerequisite surface once these ids ship (not now).
- No contradiction with plan 037 (this sits on its reps). The `pattern-marker` check partially offsets
  the "listed-but-not-student-exercised" follow-up 037 named.

## 11. Out of scope
- A separate `patterns.yaml` (rejected — reuse `kind: technique`).
- An AST `pattern-scan` heuristic (rejected — reviewer-enforced).
- Any big-O/sorting/recursion (§2).
- Book 2 pattern growth / re-opening plan-037 coverage.

## 12. Decisions resolved (2026-09-17)
- Intent = mastery + computational-thinking + spaced varied repetition.
- Ceiling = linear + "stop early" only (drop "one pass beats two"/"short-circuit" from student text).
- Tracking = **reuse `kind: technique`** in `concepts.yaml` (no new registry/fields).
- Embodiment = tag + reviewer (no AST scan); exact cells via `<!-- pattern: id -->` markers.
- Spiral N = **≥3** core reappearances; checkpoints don't count.
- Pattern set = the 7 in §3 (forward-only, closure-safe), + tally-by-key/all-any as named variations;
  u01 excluded, u02 lean.
- Homes: sentinel-loop u02; running-total + count-by-condition u04; linear-search + transform-each u06;
  filter-into-list + find-extreme u07.

## 13. Revision history
- **v1 (2026-09-17):** separate `patterns.yaml`; backward spirals; some stretch/`in`-based embodiments.
- **v2 (2026-09-17):** design-review reconciliation — reuse `kind: technique`; forward-only closure-safe
  spiral with embodiment definitions; champion-by-name find-extreme; softened hooks + sentinel-loop
  rename; ceiling text trimmed; marker cells + generated/delivered catalog; reuse-ledger mandated;
  vertical-slice rollout; discriminating fault tests; linear-search cross-book contract.

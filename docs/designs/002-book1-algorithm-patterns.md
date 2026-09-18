# Design 002 — Book 1 Algorithm-Pattern Thread

**Status:** proposed — **v3** (rev. 2026-09-18). Two design-review rounds folded (`[sol]`, `[fable]`);
v3 addresses the round-2 blockers (schema keys, `requires` semantics, phantom reuse loci). Awaiting
re-review → plan lifecycle.
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
| `running-total` | Running total (accumulate) | u04 | the program needs a *named box* holding the total-so-far, updated each step | u05 Ex7 `total_card_borders` (reuse), u07 Ex4 average (reuse), u09 read-and-sum (**new**) |
| `count-by-condition` | Counting by condition (count) | u04 | keep a counter; check each item once, bump it when it matches | u06 count-matches (**new**), u07 Ex5 above-threshold (reuse), u08 Ex5/7 **tally-by-key** (reuse; the *count-per-group* variation, named in the catalog) |
| `find-extreme` | Find the best (max / argmax) | u07 | keep the *best so far* while scanning — and remember *who*, not just the number | home = **champion-by-name** (parallel names/scores, keep `best_name`+`best_score`, **new**), u08 Ex6 most-common `best_word`/`best_count` (reuse), u09 best-so-far replacing `max()` (**new**), u10 Ex13 happiest-pet (**promote** — add `best_pet`, not just the number) |
| `linear-search` | Scan until found + stop early | u06 | check items one by one; `break` when found = stop working early | home anchors the lesson's `for position in range(26)` scan + a home exercise that adds the `break` (**new/adapt**), u07 loop+`break` search (**new**), u08 reverse-lookup value→key scan (**promote** — add the `break`; the CT contrast "the dict finds by *name* instantly; by *value* we're back to one-by-one"), u09 find-in-file (**new**) |
| `transform-each` | Do the same to each (map) | u06 | apply the *same step* to every item, producing a **new sequence** | u07 Ex6 (reuse), u08 Ex10 translate-each (reuse), u09 Ex3 line→int (reuse) |
| `filter-into-list` | Keep the ones that pass (filter) | u07 | build a **new** list of only the items that pass a test | home = clean filter (**new**); reappearances **new** in two of {u08, u09, u10} (see §7 — placed to respect ceilings) |
| `sentinel-loop` | Repeat until done (sentinel loop) | u02 | *you* know when you're done; the program must ask "done yet?" every pass | u04 Ex8 `while attempts<3` + `break`-when-accepted (reuse), project-01 M1 (reuse), u07 Ex12/13 while (reuse), u10 Ex14 `while happiness<10` (**promote** — the genuine sentinel; Ex10's `while stops<3` is a counted loop, not this) |

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

- **Spotlight cell** (recurring markdown + marker): home = a short lesson cell + the authoring exercise
  (names the pattern, its hook, "stop early" where relevant); reappearance = a one-liner asking the
  student to *identify* the pattern ("Which pattern? Which variable is the 'so-far'?") — retrieval
  practice.
- **Variation axes** — each reappearance differs from every earlier one on ≥1 axis, recorded in its
  Spotlight: data type (numbers→strings→lists→dicts→file lines→objects), packaging
  (inline→function→method), twist (empty / tie / early-stop).
- **Catalog** — `book1/reference/patterns.md` (dir to be created): the 7 patterns (name, hook, enabling
  concepts, generated home+reappearances table). Delivered to students via `scripts/build-pdf.sh`
  (pandoc, like `syllabus.md`).
- **teacher-notes** (in the content dispatch): name the **in-class** appearance (home is always
  in-class), route the rest to homework/More-Practice, and add a **2-minute unplugged trace** per home
  (e.g. five face-down cards, flip one at a time, find the biggest).

## 7. Footprint, pacing & the reuse ledger (honest counts)

Current post-037 core (ceiling 16): u02 8, u03 10, u04 10, u05 11, u06 11, **u07 13, u08 14**, u09 12,
u10 12. Corrected against reality:
- **u09 is the heavy one:** best-so-far, find-in-file, read-and-sum are all **new** (Ex4 uses `max()`,
  Ex6 uses `in`, no exercise sums) → u09 ~12 → **15–16**. §7 (not "+1–2").
- **u07 → ~16:** champion-by-name + clean-filter + loop-and-break search (3 new).
- **u08 → ~15–16:** reverse-lookup promote (+1 core) + at most one filter; running-total is **dropped**
  from u08 (no natural sum — avoids 17).
- u06 11 → ~13 (count-matches new + linear-search & transform-each homes). u04 10 → ~11–12 (homes may
  adapt existing scoring exercises). u10 12 → ~14 (promote Ex13 + Ex14). u05/u02 no net-new (reuse Ex7;
  u02 gets one lean one-sentence Spotlight only).
- **Ceiling risk:** u07/u08/u09 land AT ~16. The **plan's ~28-row ledger must prove each unit ≤16**; if
  any exceeds, a `filter-into-list` reappearance relocates (e.g. off u08 to u10) or drops to homework.
  Carry plan-037 Phase-V volume thresholds (>2× cells / >30% PDF pages / >25% wall-time = gate finding;
  120 s per-cell exec).
- Estimate **+12–16 net-new exercises** (rest is reuse-tag + 3 promotions).

## 8. Rollout

Inherited structural checks are green from PR-1. **Vertical slice per complete pattern:** a technique id
is added to `concepts.yaml` only when its home + all ≥3 core reappearances + catalog row land together —
so `main` is valid at every merge and `technique-spiral` is **never red** (one rule; no SKIP-until
needed). Phased PRs by term to keep the content gate's blind-solve tractable (batching = plan decision).

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
  loci corrected against the notebooks (u05 Ex7 reuse; u09 read-and-sum/best-so-far/find-in-file new;
  u08 dropped from running-total; sentinel-loop → u04 Ex8 / promote u10 Ex14; find-extreme u10 add
  `best_pet`; linear-search u08 add `break`); `technique-spiral` scoped to Book 1 + rejects stretch loci;
  markers map kind→notebook incl. `brief.ipynb`, checkpoints don't tag; `all-any` dropped; footprint
  corrected (u09 heavy; u07/u08/u09 at ceiling → ledger must prove ≤16); design↔plan boundary (§0).

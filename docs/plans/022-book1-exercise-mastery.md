# Plan 022 — Book 1 exercise mastery (proficiency completeness) Implementation Plan

**Goal:** Ensure every concept each Book-1 unit `introduces`/`practices` is ACTIVELY EXERCISED by
students in a student-facing `exercises.ipynb` cell, with enough depth to build proficiency — closing
the exercise-coverage and depth gaps a four-layer audit (10 units + 4 checkpoints + 2 projects, plus a
Sol second opinion) found, so no concept is assessed at a checkpoint/project without upstream authoring
practice.

**Architecture:** Content changes to student-facing `exercises.ipynb` + their matching
`solutions.ipynb` across the affected Book-1 units, plus two small project fixes and three small
checkpoint/manifest reconciliations. Grouped into phases by curriculum locality (so each phase is one
coherent reviewer gate). This plan is the complement to plan 016: 016 made manifests match what content
*uses* (used→listed, via the `concept-scan` CI check); 022 makes what students *do* match what is
taught/assessed (listed/taught→student-exercised). Exercise **statements** and **solutions** are
authored by Codex (GPT-5.6-sol) in separate sessions per the AGENTS.md dispatch table; this plan
supplies the per-exercise spec + acceptance, not the notebook JSON.

**Spec:** this plan (audit-derived); `docs/designs/000-project-design.md` (§1 structure, §4
verification); `book1/curriculum/concepts.yaml` (concept registry) and
`book1/curriculum/coverage-map.yaml` (arc contract); plan `016-hygiene-practice-completeness.md` (the
`concept-scan` check + the unit-05 `accumulator` tag this plan revisits); the 16 audit reports in the
session scratchpad (`audit-unit-01.md` … `audit-project-02.md`) are the finding provenance.

## Audit provenance & verdict reconciliation

Two independent audits ran. The Claude pass (10 units + 4 checkpoints + 2 projects) rated 1 STRONG /
7 ADEQUATE / 2 WEAK against a bar of "introduced concepts covered." The Sol (GPT-5.6-sol) second
opinion applied a stricter bar — ANY `introduces`/`practices` tag not student-authored is a coverage
failure — and rated **8 units WEAK (02, 03, 05, 06, 07, 08, 09, 10), unit-04 STRONG, unit-01
ADEQUATE**. This plan adopts **Sol's stricter bar** (it matches the user's "guarantee mastery" goal),
so scope already covers every Sol-WEAK unit. The two audits AGREE on all systemic gaps; Sol adds three
items folded in below: the `input` false-practice reconciliation (units 07–10), the unit-03 Ex5
full-program rewrite (flagship), and a flag that unit-05 Ex6's solution may be incomplete vs. its
statement (verify in Phase 2).

## Global Constraints

- **This is a CONTENT plan.** It ships changed student-facing exercises and their solutions in
  already-shipped Book-1 units/projects — so per AGENTS.md it carries a **named verification phase**
  (Phase V) and goes through BOTH the 4-way plan-review gate and the 4-way content-review gate before
  PR. It introduces NO new units/projects/checkpoints and adds NO new concepts to any `introduces`
  list.
- **The proficiency bar (the definition of done for every added/modified exercise):** a concept is
  "actively exercised" only when a STUDENT-facing `exercises.ipynb` code cell requires the student to
  *author or complete* code that uses it — not when it appears only in the lesson, only in a
  `solutions.ipynb` cell, only inside an `assert` (CI self-check), or only in a `stretch`/Challenge
  cell. Reading/tracing/predicting counts as active use ONLY for concepts the unit deliberately keeps
  trace-only (documented per unit below); everything else needs authoring.
- **Self-containedness is law (unchanged).** Every new/modified exercise may use ONLY concepts
  introduced ≤ that entry in `coverage-map.yaml` (prereq closure). No forward references. Nothing
  assessed downstream may rely on a concept this plan has not made student-exercised upstream.
- **Content conventions (unchanged, enforced):** student notebooks contain NO solutions and NO executed
  outputs; solutions run top-to-bottom clean with fixed seeds and are `assert`-backed; interactive
  `input()` cells stay `no-exec` and solutions substitute fixed values; turtle work stays in `.py`
  assets (headless notebooks) — new turtle exercises use the existing predict/trace/repair/author-on-
  paper pattern, never a turtle window in a cell. Datasets from seeded scripts only.
- **Stretch rule (unchanged):** every unit keeps ≥1 `stretch`-tagged ("Challenge") exercise and core
  content never depends on stretch. New core exercises added by this plan must NOT be tagged `stretch`
  — the whole point is to move proficiency-critical practice OUT of stretch into core.
- **Grow the exercise SET (primary lever for mastery).** The default remediation is to ADD new core
  exercises, not to minimally edit existing ones. Each under-practiced concept gets **≥2 authoring
  reps with genuine variety** (typically one guided/scaffolded + one independent, in a different
  context — not the same task reskinned), and each touched unit gains a small "more practice" cluster
  so its core count meaningfully increases. Proficiency comes from volume + variety of active
  authoring, so err toward more exercises. This lengthens notebooks — acceptable.
  - **Exception — units 01 & 02 stay lean.** The syllabus binds units 01–02 to short exercise sets
    (heaviest introduction load at the most fragile point). There, add the MINIMUM new exercises
    needed to close the named gaps (one solid authoring rep per gap), not a large cluster. All other
    units (03–10) and the projects take the full "grow the set" treatment.
  - Each new exercise still obeys every constraint above (self-contained, non-stretch for core,
    assert-backed headless solution, no forward refs) and keeps the unit's project-first framing.
- **Lesson parity:** if a target concept is genuinely not taught in the unit's `lesson.ipynb` (audit
  found this ONLY for unit-05 `accumulator`), the fix is EITHER add a minimal lesson beat + a core
  exercise, OR reconcile the manifest (drop the tag) — decided per Phase 2 below; do not add an
  exercise for an untaught concept without a matching lesson beat.
- **Manifest/map honesty (interacts with plan 016):** where this plan adds real student practice for a
  concept, the existing `practices`/`introduces` tags already cover it (016 made them
  used-complete), so most phases change NO metadata. Two reconciliations are explicit (Phase 2
  `accumulator`, Phase 8 checkpoint-02 `turtle-drawing`) and each keeps `practices ∩ introduces` empty
  and closure intact, and must keep the `concept-scan` check GREEN.
- **`input` false-practice reconciliation (Sol):** units 07–10 (and any other) list `input` in
  `practices`, but their exercises forbid students from writing it (notebooks must run input-free —
  documented design). This is dishonest metadata. Per unit, EITHER (a) drop `input` from `practices`
  (map + manifest) if it is genuinely never student-authored, OR (b) add a student-authored `input()`
  line the exercise requires (with a `no-exec` tag + an executable fixed-value fallback beside it) so
  the tag is earned. Constraint: keep `concept-scan` GREEN — if `input` still appears in the unit's
  lesson/solution code cells it stays "used" and must remain listed, so option (a) is only valid when
  the scanner does not detect `input` usage in that unit. Decide per unit in Phase 8; default (b) for
  units where input is pedagogically load-bearing, (a) where it is vestigial.
- **Do not touch:** `introduces`/`requires` lists; teacher-notes learning-goal claims except to align
  them with new exercises; any Book-2 content; the governance files (CLAUDE.md,
  docs/development-workflow.md, docs/content-review-gate.md, docs/architecture/decisions.md).
- Process (standing): branch is `feature/plan-022-book1-exercise-mastery`; no commits while a `[sol]`
  review is in flight; every `gh` call uses `GH_TOKEN=$(cat .gh-token)`; codex content prompts for
  SOLUTIONS run in a SEPARATE fresh session that never sees the statement-authoring outline.

## Out of scope

- **New automated "listed-but-not-student-exercised" CI check.** The durable guarantee against this
  class of gap is a tool check (analogous to 016's `concept-scan`) that flags any `introduces`/
  `practices` concept never appearing in a student-facing `exercises.ipynb` code cell. It is the
  natural fast-follow (proposed **plan 023, tooling**) but is deliberately OUT of scope here: building
  it well needs the same false-positive care 016's scanner required (trace-only concepts, `stretch`
  exclusion, input/`no-exec` handling, OOP method exemptions), and bundling it would make this content
  plan un-reviewable. For THIS plan the proficiency bar is enforced by per-phase acceptance +
  reviewer duty + the content gate's blind-solve, exactly as AGENTS.md prescribes pre-tooling.
- Rewriting checkpoints/projects wholesale. The audit found all checkpoints correct and self-contained;
  their proficiency risk is upstream, fixed by the unit phases. Only the three named minor
  checkpoint/project touches (Phases 7–8) are in scope.
- Reworking the difficulty ramp, project hooks, or teacher-notes pacing where the audit found them
  sound (all units).

## Phases

Dispatch per AGENTS.md: exercise STATEMENTS and SOLUTIONS to Codex (GPT-5.6-sol), solutions in a
separate fresh session; teacher-notes alignment inline; manifest reconciliations inline. Each unit
phase's deliverable is: the target concepts made student-exercised in core, matching solutions
`assert`-backed and headless, teacher-notes aligned, and the unit's `ci-local` slice green.

Each numbered item in Phases 1–7 means "add one or more NEW core exercises" (per the "Grow the
exercise SET" constraint: ≥2 authoring reps per concept, with variety), except units 01 & 02 where each
item is the single minimum authoring rep needed. Modifying an existing exercise is allowed only when
the audit named it specifically (e.g. unit-06 Ex7, unit-09 Ex5); otherwise prefer adding.

Per-phase acceptance (applies to EVERY phase below unless it says otherwise):
- Each named target concept is actively exercised in a NON-stretch `exercises.ipynb` cell (proficiency
  bar above), with ≥2 varied authoring reps (units 01–02: ≥1), and the unit's core exercise count
  increases accordingly.
- Matching `solutions.ipynb` cells run top-to-bottom clean (fixed seeds / `no-exec` inputs) with
  `assert` self-checks that would catch the intended mistake.
- `manifest-check` / `coverage-check` / `prereq-check` PASS; `concept-scan` GREEN; notebook
  execution + hygiene PASS for the touched notebooks.
- Unit keeps ≥1 `stretch` exercise; no core exercise depends on stretch; no forward references.

### Phase 1 — unit-03-turtle-art-studio (WEAK → target ADEQUATE+)

Audit: `f-string` (MISSING from statements), `turtle-drawing` (active use only in stretch),
`loop-counter` (never used in an expression), `float-type` (real decimal never engaged). Sol flagship:
Ex5 only edits two values in an existing asset — students never AUTHOR a turtle program.

0. **FLAGSHIP — rewrite Ex5 into a full authored polygon program (Sol's highest-priority fix).**
   Replace the "edit `n`/`side_length` in the asset" exercise with one where the student AUTHORS a
   complete polygon program (as a headless `.py`-style plan / the existing author-command pattern):
   turtle setup + drawing (`penup`/`pendown`/`color`), a `for` over `range(n)`, a counter that DRIVES
   behavior (e.g. `pensize(side_number + 1)`), and `angle = 360 / n` for a non-clean `n`. This single
   rewrite makes `turtle-basics`, `turtle-drawing`, `for-loop`, `range-function`, `loop-counter`, and
   `float-type` all student-authored at once. Keep it core (not stretch); provide a headless,
   assert-backed solution.
1. **turtle-drawing → more core reps.** Beyond the flagship, add a second "pen plan" exercise
   (headless, author-command-strings pattern) — a different shape/color spec — so `turtle-drawing` has
   ≥2 varied authoring reps and is not carried by the flagship alone.
2. **loop-counter → expression use.** Add/modify an exercise that USES the counter value in an
   expression (the lesson's headline `turtle.pensize(side_number + 1)`), e.g. "write the line that
   makes each side one step thicker using `side_number`", or a trace that asks the `pensize` for side
   0 vs side 3.
3. **float-type → real decimal.** Add a prediction row for `n = 7` (`angle = 360 / 7` → `51.428571…`)
   plus a one-line "why can't this be a whole number, what breaks if we round to 51?" (mirrors the
   teacher-notes discussion prompt). Ensure at least one exercise's `assert` exercises a non-terminating
   float, not a clean `72.0`.
4. **f-string → required by a statement.** Change one worded-answer exercise (e.g. Ex1) so the
   STATEMENT requires an f-string report (`print(f"{straight_sides} sides of {side_length} steps")`),
   not only the solution.
5. Align teacher-notes if pacing changes. Acceptance: the four concepts above are student-exercised in
   core; `f-string` (already in unit-03 `practices` via 016) now honored by a statement.

### Phase 2 — unit-05-function-factory (WEAK → target ADEQUATE+) + `accumulator` reconciliation

Audit: `accumulator` (never taught OR exercised — only a solution CI-scaffold line; 016 tagged it from
that usage), `nested-loops` (never authored in an exercise), `scope` (trace-only, never authored),
`return-value` (authored only once).

1. **accumulator — DECISION (judgment fork, raise at plan-review gate):** EITHER (a) add a minimal
   lesson beat (a running `total` over N stamp sizes) + a core exercise that authors
   `total = total + size` and returns it — the pedagogically richer option, pairs naturally with
   `return-value`; OR (b) drop `accumulator` from unit-05's `practices` (map + manifest) and rely on
   its genuine home in unit-04 (introduced) / unit-06/07 (practiced). Default recommendation: **(a)**,
   because CP2 Q2/Q8 and project-01 M4 make accumulator load-bearing right after unit-05, so students
   need the authoring rep here. Whichever is chosen, `concept-scan` stays GREEN and
   `practices ∩ introduces` stays empty.
2. **scope → authoring.** Add a scope-repair exercise: a broken snippet that prints a local after the
   call (NameError); student fixes it by RETURNING the value and storing it outside — the exact repair
   `lesson l3-traceback` promises. Turns scope from trace-only into authoring.
3. **return-value → composition.** Add an exercise that authors `perimeter(side)` returning `4*side`
   and then USES the returned value in a further computation or feeds one function's return into
   another (the lesson's `polygon_points → polygon` shape). Gives return a second authoring rep in a
   composition context.
4. **nested-loops → authored (headless).** Add a core exercise where the student writes BOTH `for`
   lines of a grid-of-stamps plan (outer rows, inner columns, calling `stamp(size)`) and predicts the
   total call count — headless, per the turtle convention.
5. **Verify unit-05 Ex6 solution completeness (Sol flag) — possible pre-existing defect.** Sol
   reported Ex6's solution omits the completed turtle function + call plan relative to its statement;
   the Claude pass saw only a `petal`/`petal_shape` naming inconsistency vs. the asset. Read
   `unit-05/solutions.ipynb` Ex6 against its statement and asset: if the notebook solution genuinely
   fails to satisfy the statement, FIX it (assert-backed, headless) — if it is the intended headless
   stub deferring drawing to the `.py` asset, document that in the solution cell so it is not misread.
   Treat as errata-grade if it is a real gap.
6. Align teacher-notes. Acceptance as above; if 1(b) chosen, note the metadata diff explicitly.

### Phase 3 — Term-1 units 01 & 02 (string-concat, arithmetic, boolean-as-value)

Audit unit-01: `string-concat` proficiency rests on one buried line. Audit unit-02: `arithmetic`
(incl. `//`/`%`) in ZERO core exercises (stretch only), `boolean` only implicit, `str()` never, `elif`
single-touch.

1. **unit-01 string-concat → core, f-string-free.** Add a short core exercise that is concatenation-
   only (explicitly "do NOT use an f-string here"): join a fixed greeting + a `name` variable + a
   punctuation literal with `+` to print `Hello, <name>!`, forcing management of `+` and interior
   spaces.
2. **unit-02 arithmetic → core.** Add a non-stretch "range width" exercise: given `low`/`high`, print
   the span (`high - low`), the midpoint (`(low + high) // 2`), and use `%` to report even/odd —
   giving `+ - // %` required practice and seeding the halving idea the Challenges use.
3. **unit-02 boolean → stored/printed value.** Add a one-line exercise that stores and prints a boolean
   (`print(guess == secret)` as `True`/`False`) before the verdict, so boolean is exercised as a value,
   not only as a condition. (This same boolean-as-value beat recurs in Phases 4–5; keep the wording/
   pattern consistent across units.)
4. (Optional, MINOR) unit-02: fix Challenge-2 statement's `high`/`low`/`correct` vs numeric `1`/`2`/`3`
   inconsistency (a documentation fix flagged by the audit).
5. Align teacher-notes. Acceptance as above.

### Phase 4 — units 04 & 06 (author `or`; boolean-as-value; active traceback-reading; `elif`)

Audit unit-04: `or` read/replaced but never authored. Audit unit-06: `boolean`-as-value implicit only;
`error-messages` fix handed to student; `elif` never exercised; `int-type` single touch.

1. **unit-04 author `or`.** Add a short core exercise requiring the student to WRITE an `or` rule from
   scratch (e.g. accept `"true"` or `"True"`), restoring `and`/`or`/`not` authoring symmetry. Highest-
   value unit-04 fix.
2. **unit-06 boolean-as-value.** Add/extend an exercise that stores + prints a boolean
   (`is_vowel = letter in vowels; print(is_vowel)`).
3. **unit-06 active traceback-reading (the systemic `error-messages` pattern — canonical template).**
   Rework Ex7 so the student first RUNS the buggy `encode("zoo", 3)`, copies the LAST line of the
   traceback, and names the failing operation BEFORE applying `% 26`. This is the repeatable
   "run-broken → read-traceback → fix" template reused in Phases 5–6.
4. **unit-06 elif.** Add one `elif` touch (e.g. classify a char as vowel / `y` / consonant with
   `if…elif…else`), closing the `elif` half of `elif-else`.
5. Align teacher-notes. Acceptance as above.

### Phase 5 — units 07 & 08 (sort-returns-None, while, concat/str, boolean, traceback)

Audit unit-07: `.sort()`-returns-`None` mental model never exercised (the unit's own #1 common
mistake), `while-loop` (practices, no exercise), `error-messages` (no exercise), `max`/`min` single
touch, negative index & ascending `.sort()` never. Audit unit-08: `string-concat` + `type-conversion`
MISSING (f-strings crowd them out), `boolean` implicit, `error-messages` shallow.

1. **unit-07 sort-returns-None.** Add an exercise: "predict what `best = scores.sort()` prints, then
   fix it so `best` holds the sorted board" — exercises the unit's headline mental model.
2. **unit-07 while-loop.** Add an arcade-themed `while` exercise (e.g. a bonus threshold that doubles
   until it passes the champion score), honoring the `practices` tag.
3. **unit-07 error-messages (traceback template).** "Write `scores[len(scores)]`, predict the error,
   then rewrite to safely print the last score" — closes `error-messages` AND forces a negative-index
   (`scores[-1]`) use.
4. **unit-07 max/min + ascending sort (MINOR).** Fold a second `max`/`min` touch and one plain
   ascending `.sort()` into an existing exercise/challenge.
5. **unit-08 string-concat + type-conversion → core.** Add a "print a scoreboard" exercise that
   REQUIRES `word + " => " + str(count)` using `+` and explicit `str()` (NOT an f-string), directly
   mirroring lesson cell 27 and closing both MISSING gaps at once.
6. **unit-08 boolean-as-value** (`known = word in translations; print(known)`) and **traceback for
   Ex11** (read the actual `KeyError` before applying `.get`).
7. Align teacher-notes. Acceptance as above.

### Phase 6 — units 09 & 10 (files: error-messages/branch/edge; OOP: list-index/integration/pass_time)

Audit unit-09: `error-messages` MISSING (FileNotFoundError only demoed), `if-statement` trivial always-
true, no edge cases (`"w"` vs `"a"`, missing file), 6/8 exercises near-verbatim lesson copies. Audit
unit-10: `list-index` near-MISSING, no integrative full-`Pet` exercise, `pass_time` unpracticed,
`dict-literal` shallow, `error-messages` passive.

1. **unit-09 error-messages.** Add a study/`no-exec` exercise showing a `FileNotFoundError` traceback
   where the student names the missing file and writes the one-line "save before load" / existence-
   check fix (keeps notebooks runnable while making the concept active).
2. **unit-09 real branch.** Extend the `if "Ada" in info` exercise to `if…else` and have the student
   also test a NAME NOT PRESENT, so both paths execute.
3. **unit-09 edge case.** Add a `"w"` vs `"a"` exercise: save the same list twice with `"w"`, confirm
   the file did not grow, contrast with what `"a"` would do — the unit's #1 listed mistake.
4. **unit-09 transfer.** Vary at least one early copy-of-lesson exercise (a different score list /
   settings dict) so ≥1 core exercise requires transfer, not transcription.
5. **unit-10 list-index → statement.** Extend Ex5 (or add a step): after the loop, student writes
   `pets[0].name` and `pets[1].status()` explicitly, turning the indexing now hidden in solution
   asserts into student-authored code.
6. **unit-10 integrative full-class (the capstone-prep fix).** Add a core "Run a Pet Day" exercise:
   student defines the FULL `Pet` (all four methods incl. `pass_time`), makes a pet, runs a fixed
   `feed → play → pass_time → status` sequence, `assert` on final hunger/happiness. Closes the
   integration gap AND gives `pass_time` its only student rep.
7. **unit-10 dict + traceback (MINOR).** Deepen Ex6 (feed from two different foods + add a third dict
   entry); add a run-then-read step to the `AttributeError` Ex8.
8. Align teacher-notes. Acceptance as above.

### Phase 7 — project-01 & project-02 (author the load-bearing concepts; grade OOP + integration)

Audit project-01 (STRONG): `return` pre-supplied in both required game functions — students never
author it in a required path. Audit project-02 (capstone, ADEQUATE): graded path never exercises class
METHODS (Hero has only `__init__`); integration/synthesis is a TODO, not a graded milestone;
list-index only in asserts; traceback under-prepared.

1. **project-01.** Remove the `return` line from ONE required milestone's game function so the student
   must author `return` in a required (non-stretch) path — demonstrating the return-vs-print hinge the
   teacher notes call the #1 project bug. Keep the reference + rubric aligned.
2. **project-02.** (a) Make the graded path require ≥1 class METHOD on `Hero` (not only `__init__`) and
   its call — mirroring the unit-10 integrative fix. (b) Promote the "assemble the four scaffolds into
   one coherent program" synthesis step from a TODO into a named, rubric-scored milestone. (c)
   Optionally require one student-authored `list-index` in the graded path. Keep the exemplar/reference
   correct (`seed(4)` reproducibility) and self-contained.
3. Align each project's `teacher-notes.md` / rubric. Acceptance: reference solutions run clean with
   fixed seeds; rubric lines match the new required work; no new concept introduced.

### Phase 8 — checkpoint & manifest reconciliations (MINOR, inline)

Audit: CP2 `manifest.yaml` over-claims `turtle-drawing` in `practices` (Q7 only reads forward/right =
`turtle-basics`); CP3 Q6 `elif`/`else` is dead code at runtime (`"plum"` always present) so branching
can't be verified; CP3 Q8 hands both the `KeyError` name and the `.get` fix (does not assess traceback
reading despite the tag).

1. **CP2 metadata:** remove `turtle-drawing` from checkpoint-02's `practices` in BOTH `coverage-map.yaml`
   and `manifest.yaml` (surgical, identical order), keeping `turtle-basics`. Verify `manifest-check`/
   `coverage-check`/`prereq-check`/`concept-scan` all PASS after.
2. **CP3 Q6:** adjust the data so the `elif`/`else` branch is reachable (a key that is absent on one
   path), so the branch logic actually executes and the solution's `assert` proves it.
3. **CP3 Q8:** either (a) keep it as a `.get` fix drill but stop claiming it assesses traceback reading
   (align teacher-notes), or (b) make the student read the actual `KeyError` first — consistent with
   the Phase 4–6 traceback template. Default: **(b)** for consistency.
4. **`input` false-practice reconciliation (Sol) — units 07–10.** For each of units 07, 08, 09, 10
   apply the per-unit decision from Global Constraints: run `concept-scan` to see whether `input` is
   detected as used in that unit's cells; where it is NOT, either drop `input` from `practices`
   (map + manifest, surgical) OR ensure the unit's Phase (4–6) added a genuine student-authored
   `input()` rep so the tag is earned. Record the per-unit choice. Verify `manifest-check`/
   `coverage-check`/`prereq-check`/`concept-scan` PASS after.
- Checkpoint edits (1–3) are the ONLY checkpoint changes; all four checkpoints otherwise stay as
  shipped (their proficiency risk is resolved upstream by Phases 1–6). Item 4 is unit-manifest metadata
  grouped here for one clean reconciliation pass.

### Phase V — Verification (NAMED, mandatory)

Mechanical (authoritative — `scripts/ci-local.sh` is the gate, design §4):
- `uv run pytest -q` green (incl. any curriculum tests); ruff clean.
- `scripts/ci-local.sh` **ALL GREEN**: registry+lint, unit tests, **notebook execution + hygiene**
  (every touched `exercises.ipynb`/`solutions.ipynb`/checkpoint/project notebook executes clean with no
  stored outputs in student cells and clean assert-backed solutions), `manifest-check`/`coverage-check`/
  `prereq-check`, `concept-scan` (STILL zero used-but-unlisted across all 16 entries after the two
  metadata reconciliations), stretch-check, PDF build, pre-merge guard.
- `bash scripts/pre-merge-guard.sh --pr` OK.

Proficiency (reviewer-enforced, the plan's raison d'être — Phase V acceptance is NOT met without this):
- For EVERY concept named in Phases 1–8, a reviewer confirms it is now actively exercised in a
  NON-stretch student `exercises.ipynb` cell (the proficiency bar), and that each such exercise's
  solution `assert` would catch the intended mistake.
- Confirm no `introduces`/`requires` changed; the two metadata reconciliations keep closure +
  `practices ∩ introduces` empty; the `accumulator` decision (Phase 2) is recorded.
- Confirm every touched unit keeps ≥1 `stretch` exercise and no core exercise depends on stretch, and
  no new forward references were introduced.

**Acceptance criteria:** all Phase 1–8 target concepts student-exercised in core (proficiency bar);
solutions assert-backed + headless clean; two metadata reconciliations applied (map == manifest);
`ci-local.sh` ALL GREEN incl. `concept-scan`; `pre-merge-guard --pr` OK; plan-review + content-review
4-way consensus with no `[OPEN]` blockers.

---

## Plan Review

_(4-way gate — [self] / [sol] / [glm] / [fable]. To be conducted before any implementation.)_

## Content Review

_(4-way gate — conducted pre-PR after implementation. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

## Post-Execution Report

_(Written before PR.)_

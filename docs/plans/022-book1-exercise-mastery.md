# Plan 022 — Book 1 exercise mastery (proficiency completeness) Implementation Plan

**Goal:** Ensure every concept each Book-1 unit `introduces`/`practices` is ACTIVELY EXERCISED by
students in a NON-stretch `exercises.ipynb` cell (or is a documented trace-only exemption), with enough
depth to build proficiency — closing the exercise-coverage and depth gaps a four-layer audit (10 units
+ 4 checkpoints + 2 projects, plus a Sol second opinion) found, so no concept is assessed at a
checkpoint/project without upstream authoring practice.

**Architecture:** Content changes to student-facing `exercises.ipynb` + their matching
`solutions.ipynb` (and a few `.py` turtle assets) across the affected Book-1 units, plus two project
fixes and a metadata-reconciliation set. Grouped into phases by curriculum locality. This plan is the
complement to plan 016: 016 made manifests match what content *uses* (used→listed, via `concept-scan`);
022 makes what students *do* match what is taught/assessed (listed/taught→student-authored). Exercise
**statements** and **solutions** are authored by Codex (GPT-5.6-sol) in separate sessions per the
AGENTS.md dispatch table; this plan supplies the per-exercise spec + acceptance, not notebook JSON.

**Spec:** this plan (audit-derived); `docs/designs/000-project-design.md` (§1 structure, §4
verification); `book1/curriculum/concepts.yaml`; `book1/curriculum/coverage-map.yaml`; plan
`016-hygiene-practice-completeness.md` (the `concept-scan` check + the unit-05 `accumulator` tag this
plan revisits); the CI tools `tools/curriculum.py` (`coverage-check`/`prereq-check`/`manifest-check`),
`tools/concept_scan.py`, `tools/notebooks.py` (`cell-lint`/`ASSET_REF`/`exec-solutions`),
`tools/fake_turtle.py` (`turtle-check`); the 16 audit reports in the session scratchpad
(`audit-unit-01.md` … `audit-project-02.md`, `audit-sol-book1.md`) are the finding provenance.

## Audit provenance & verdict reconciliation

Two independent audits ran. The Claude pass (10 units + 4 checkpoints + 2 projects) rated 1 STRONG /
7 ADEQUATE / 2 WEAK against a bar of "introduced concepts covered." The Sol (GPT-5.6-sol) second
opinion applied a stricter bar — ANY `introduces`/`practices` tag not student-authored is a coverage
failure — and rated **8 units WEAK (02, 03, 05, 06, 07, 08, 09, 10), unit-04 STRONG, unit-01
ADEQUATE**. This plan adopts **Sol's stricter bar**, and Phase V enforces it over each unit's COMPLETE
`introduces ∪ practices` union (not just the named remediation targets), so a concept cannot slip
through by being un-listed as a phase target.

## Global Constraints

- **This is a CONTENT plan.** It ships changed student-facing exercises + solutions in already-shipped
  units/projects, so per AGENTS.md it carries a **named verification phase** (Phase V) and goes through
  BOTH the 4-way plan-review and 4-way content-review gates before PR. It adds NO new concepts to any
  `introduces` list and ships NO new units/projects/checkpoints.
- **The proficiency bar (definition of done for every concept):** a concept is "actively exercised"
  only when a STUDENT-facing `exercises.ipynb` code cell (or a student-authored `.py` asset) requires
  the student to *author or complete* code that uses it — NOT when it appears only in the lesson, only
  in a `solutions.ipynb` cell, only inside an `assert` (asserts are `concept-scan`-exempt and don't
  count as practice), or only in a `stretch`/Challenge cell. Reading/tracing/predicting counts as
  active use ONLY for concepts a unit **deliberately keeps trace-only**, and every such exemption MUST
  be listed explicitly in that unit's phase (see the per-phase "Exemptions" lines). A second exemption
  type — **justified-peripheral count-exemption** — covers concepts where meeting the ≥3/≥5 count is
  pedagogically unreasonable (e.g. `error-messages`: staging many run-a-traceback exercises is
  artificial, and it is practiced across many units): such a concept may sit BELOW its count bar with a
  written justification in the phase + Phase V inventory, but must still have ≥1 genuine authoring rep.
- **Quantity goal (concept-scaled depth — the plan's headline target, set by the author).** Growth is
  measured per CONCEPT, not per unit:
  - **Baseline: every concept** in a unit's `introduces ∪ practices` union appears in **≥3** distinct
    student-authored (non-stretch) exercises.
  - **Essential concepts: ≥5.** Each unit designates its ESSENTIAL (core/load-bearing) concepts — the
    exact set is LISTED in the target table below (for units 03–10 it is that unit's `introduces`
    spine). These reach **≥5** distinct student-authored exercises. (Not every introduced concept is
    essential — peripheral introduced concepts sit at the ≥3 baseline — this keeps concept-dense units
    within the pacing budget.)
  - "Distinct authoring exercise per concept": one exercise counts once toward EVERY concept it makes
    the student author (exercises are multi-concept, so spine concepts hit ≥5 quickly and the real lift
    is bringing thin `practices` concepts to ≥3). Reading/tracing does NOT count except for a listed
    trace-only exemption; `assert`-only and stretch-only uses do NOT count. MINOR "fold into an existing
    exercise" items still produce a real authoring rep and DO count.
  - **Applies to units 03–10.** **Units 01 & 02 are the lean exception** (syllabus binds them to short
    sets at the most fragile point): they target ≥1 rep per concept + closing named gaps, NOT the
    ≥3/≥5 depth target; this exception is recorded, not silently taken.
  - **This quantity goal is the SOLE authority on rep counts.** The per-phase items below enumerate
    WHICH concepts/exercises to author (the gaps to close), NOT how many reps each concept gets — any
    "≥1"/"≥2"/"a rep" figure inside a phase item is an illustrative floor SUPERSEDED by this bar. The
    implementer (Codex) authors enough varied exercises, distributing multi-concept reps and fold-ins,
    to satisfy ≥3/≥5 (with documented exemptions); the plan does not pre-enumerate all ~40 exercises —
    that is Codex's authoring job, verified at Phase V + the content gate (the AGENTS.md model). Where a
    phase item's number and this bar differ, THIS BAR GOVERNS.
- **Pacing budget (growth must not exceed class time).** Targets are the per-unit **before → after
  core count** in the table below. The budget is measured against the unit's ACTUAL lesson count from
  its `teacher-notes.md` (units are multi-lesson: e.g. unit-03 = 3 lessons, unit-07 = 2), NOT a single
  60–90 min session. Extra depth reps land in a **labelled "More Practice"** area (a markdown label,
  NOT a heading level — exercises stay `## Exercise N` so `EXERCISE_HEADING`/`solutions_structure`
  checks pass); teacher-notes name which reps are in-class vs. homework, allocated across the unit's
  lessons; **≥1 rep of each concept sits on the in-class path** (so no proficiency-critical rep is
  de-facto skippable like stretch). Hard ceiling: **no unit exceeds ~16
  core exercises**, and each `solutions.ipynb` must run within the `exec-solutions` 120 s per-notebook
  timeout (Phase V records before/after counts + `ci-local` duration).
  - Every new exercise still obeys all constraints (self-contained, non-stretch for core, assert-backed
    headless solution, no forward refs) and keeps the unit's project-first framing.
- **Self-containedness is law.** Every new/modified exercise may use ONLY concepts introduced ≤ that
  entry in `coverage-map.yaml` (prereq closure). No forward references. In particular: file-existence
  checks (`os.path`/`pathlib`/`try`/`except`) are UNTAUGHT in Book 1 and forbidden; `round()` /
  `builtin-functions` is introduced unit-07 and must not appear in a code cell before then (keep any
  "why can't we round?" beat prose-only).
- **Content conventions (enforced):** student notebooks contain NO solutions and NO executed outputs;
  solutions run top-to-bottom clean with fixed seeds and are `assert`-backed; interactive `input()`
  cells stay `no-exec` and solutions substitute fixed values; turtle work lives in `.py` assets run
  from the terminal (headless notebooks) — solution/notebook cells must NOT `import turtle` (they run
  un-stubbed under `exec-solutions`); `____` placeholders live only in markdown/comments, never in code
  cells (`cell-lint` runs ruff F82); any `assets/*.py` referenced by a cell MUST exist (`ASSET_REF`)
  and must `py_compile` + draw a **closed** shape (`turtle-check`: final position == first pen-down
  position and heading ≡ 0 mod 360) unless the file carries a `# turtle-check: open-path` comment.
- **Turtle nav is limited to `forward`/`backward`/`left`/`right`** (+ `penup`/`pendown`/`pensize`/
  `color`). `tools/fake_turtle.py` does NOT stub `goto`/`setheading`/`stamp`/`circle`/`begin_fill`/…,
  so authored `.py` assets must reposition via `penup`+`backward` patterns (the `l1_cards.py`/
  `l3_stamps.py` precedent), never `goto` — `turtle-check`-green is stricter than `concept-scan`-green
  here.
- **Any deliberately-broken/raising snippet (the `error-messages` traceback reps in Phases 4–6, 8 AND
  the Phase 2.2 scope-repair NameError):** the actual RAISING line must live in **markdown** (or a
  `no-exec`-tagged STUDENT exercise cell), NEVER in a `solutions.ipynb` code cell — `exec-solutions`
  runs solution notebooks in full with no `no-exec` filtering and `try/except` is untaught, so a
  raising line would crash CI; also, a bare undefined-name line in a student CODE cell trips
  `cell-lint` ruff F82 unless the cell is `no-exec`-tagged (and `no-exec` does NOT exempt CHECKPOINT
  cells from `cell-lint`, so CP3 Q8's `KeyError` line must be markdown or F82-clean, e.g. `d["zzz"]`).
  Solutions record the diagnosis/fix as code + `assert`; the traceback text is shown in markdown
  (hygiene forbids stored outputs).
- **Stretch rule:** every touched unit keeps ≥1 `stretch` ("Challenge") exercise and core never depends
  on stretch. New CORE exercises added here must NOT be `stretch` — the point is to move
  proficiency-critical practice OUT of stretch into core.
- **Metadata reconciliations (this plan's full, enumerated set — supersedes any "two" wording).** Each
  is surgical (map entry + matching manifest, identical order), keeps `practices ∩ introduces` empty
  and closure intact, and must keep `concept-scan` + `coverage-check` + `prereq-check` GREEN:
  1. **CP2:** DROP `turtle-drawing` from `checkpoint-02` `practices` — AND (2) ADD it to unit-05
     `practices` (see below). (Dropping from CP2 ALONE fails `coverage-check`: CP2 is the only
     pre-capstone practicer of `turtle-drawing`; `practice_findings` would report "only the capstone
     practices turtle-drawing". [fable] B1.)
  2. **unit-05:** ADD `turtle-drawing` to `practices` (introduced unit-03; unit-05 already `requires`
     it). The genuine pen/color AUTHORSHIP that earns this tag lives in the NEW Phase 2.4 grid program
     (not Ex6, whose `penup()/pendown()` are given lines with only blanks to fill) — the content gate
     looks for the authorship there. requires∩practices overlap is allowed (project-01 precedent).
  3. **unit-09:** ADD `elif-else` to `practices` (introduced unit-02) — required because Phase 6.2 adds
     an `if…else` branch and `concept-scan` flags `elif-else` on any non-empty `orelse`. [fable] B3.
  4. **units 07, 08, 09, 10:** DROP `input` from `practices` (Sol false-practice finding). Verified
     RED-safe by [glm] and [fable]: `input(` appears in ZERO code cells of these units' lesson/
     exercises/solutions/assets (only markdown prompts), and `input` stays practiced pre-capstone in
     CP1, project-01, and unit-06 (whose lesson genuinely uses it), so both `concept-scan` and
     `coverage-check` stay GREEN. Decision is (a)=drop for all four (fork answer below).
  5. **CP1:** `string-concat` — CP1 lists it in `practices` but Q1 only has the student REPLACE a broken
     concat with an f-string, so the tag is unearned. **Binding action: amend CP1 Q1 so the student
     authors a `+` concatenation** (see Phase 8.5 — single committed disposition, not a fork).
- **General rule — 016-style scanner-derived `practices` additions are PRE-AUTHORIZED** for this plan:
  when adding a required exercise makes `concept-scan` detect a concept not yet listed, the implementer
  MAY add that concept to the entry's `practices` (map + manifest) provided it is introduced ≤ the
  entry (closure), is NOT in the entry's `introduces`, and no `introduces`/`requires` changes. This
  gives implementers a sanctioned path (used by reconciliations 2–3) instead of an un-owned scan
  failure. The enumerated set 1–5 is the ANTICIPATED COMPLETE set — no additional scanner-derived
  additions are expected, because the plan's new exercises author concepts already in each entry's
  union. Should the scanner nonetheless flag a new one, the addition is bounded by the closure rule
  above, MUST be surfaced in that PR's description AND the content-review gate (not merely the
  post-execution report), and requires reviewer sign-off — it is not a silent license to expand
  metadata. Note the scanner observes lessons, exercises, solutions, AND assets — not only the
  newly-required exercise.
- **Do not touch:** `introduces`/`requires` lists; Book-2 anything; governance files (CLAUDE.md,
  docs/development-workflow.md, docs/content-review-gate.md, docs/architecture/decisions.md).
- Process (standing): branch `feature/plan-022-book1-exercise-mastery`; no commits while a `[sol]`
  review is in flight; every `gh` call uses `GH_TOKEN=$(cat .gh-token)`; codex SOLUTION prompts run in
  a SEPARATE fresh session that never sees the statement-authoring outline.

## Resolved judgment forks (plan-review consensus)

- **accumulator (Phase 2.1) → (a) BINDING:** add a minimal lesson beat + a core authoring exercise;
  do NOT drop the tag (option (b) is scan-unsafe — the Challenge-2 solution's
  `petals_drawn = petals_drawn + 1` is detected by `visit_Assign`). [glm]/[sol]/[fable].
- **input (units 07–10) → (a):** drop the `practices` tag for all four (reconciliation 4). [glm]/[fable].
- **CP3 Q8 → (b):** make the student read the actual `KeyError` before applying `.get`. [fable].
- **CP2 turtle-drawing → (ii):** drop from CP2 + add to unit-05 (reconciliations 1–2). [fable].

## Out of scope

- **New automated "listed-but-not-student-exercised" CI check** — the durable guarantee against this
  class of gap (analogous to 016's `concept-scan`), deliberately deferred to **plan 023 (tooling)**:
  building it needs the same false-positive care (trace-only concepts, `stretch` exclusion, `input`/
  `no-exec` handling, OOP method exemptions, asset authorship) and bundling it would make this content
  plan un-reviewable. For THIS plan the bar is reviewer-enforced (Phase V union inventory + content-gate
  blind-solve), per AGENTS.md pre-tooling prescription. **Risk acknowledged:** until 023 lands nothing
  automatically prevents regression — recorded as a named follow-up in the post-execution report.
- Rewriting checkpoints/projects wholesale (all checkpoints are correct + self-contained; risk is
  upstream). Reworking ramps/hooks/pacing where the audit found them sound.

## Implementation & gate batching

To keep the content gate's 4-way blind-solve tractable, implementation ships as **two PRs, each through
its own content-review gate**: **PR-A = Term 1–2** (Phases 1, 2, 3 **plus Phase 8.1's atomic
CP2-drop + unit-05-add of `turtle-drawing`**, which must ship together with the unit-05 content that
earns it) and **PR-B = Term 3–4** (Phases 4–7 + Phase 8 items 2–6). Both PRs share this one plan file;
each carries its own post-execution report + content-review section. (Non-blocking structure; a single
PR is permissible if the gate roster prefers it.)

## Phases

Dispatch per AGENTS.md: exercise STATEMENTS and SOLUTIONS to Codex (GPT-5.6-sol), solutions in a
separate fresh session; teacher-notes alignment inline; metadata reconciliations inline.

Per-phase acceptance (EVERY phase unless noted):
- Each named target concept is actively exercised in NON-stretch cells (proficiency bar). **Quantity
  goal met (units 03–10):** every concept in the unit's union reaches **≥3** distinct student-authored
  exercises, and each **essential** concept (listed in the phase) reaches **≥5** (counted per Global
  Constraints; MINOR fold-ins count). **Units 01–02 (lean exception):** ≥1 rep per concept + named gaps
  closed. The unit's core count moves from its stated before→after, keeps a 60–90 min in-class core
  path, and stays ≤16 core.
- Matching `solutions.ipynb`/asset cells run clean (fixed seeds / `no-exec` inputs) with `assert`
  self-checks that would catch the intended mistake.
- `manifest-check` / `coverage-check` / `prereq-check` PASS; `concept-scan` GREEN; notebook execution +
  hygiene + `cell-lint` + `ASSET_REF` + `turtle-check` (where assets change) PASS.
- Unit keeps ≥1 `stretch`; no core depends on stretch; no forward references; trace-only exemptions
  listed.

**Per-unit core-count targets & essential concepts** (current core measured 2026-09-08; essential = ≥5
reps, all other union concepts ≥3; units 01–02 lean = ≥1). Targets are the pacing envelope (≤16 core);
Phase V enforces the per-concept rep counts.

| Unit | core now → target | Essential concepts (units 03–10: ≥5 reps) |
|------|------------------|------------------------------|
| 01 (lean¹) | 6 → 7 | print, variable, input, string-concat, f-string |
| 02 (lean¹) | 6 → 8 | int-type, arithmetic, comparison, if-statement, elif-else, while-loop, type-conversion |
| 03 | 6 → 10 | turtle-basics, turtle-drawing, for-loop, range-function, loop-counter |
| 04 | 7 → 10 | accumulator, logical-ops, conditional-nesting, break-statement |
| 05 | 6 → 11 | def-function, parameters, return-value, scope |
| 06 | 7 → 11 | string-index, string-slice, string-methods, in-operator |
| 07 | 9 → 13 | list-literal, list-index, list-append, list-loop, list-sort |
| 08 | 11 → 14 | dict-literal, dict-access, dict-loop |
| 09 | 8 → 12 | file-read, file-write, with-statement |
| 10 | 8 → 12 | class-def, init-method, attributes, methods |

¹ **Units 01–02 lean exception:** the "Essential concepts" column is illustrative only — the ≥5/≥3 bar
does NOT apply; these units target ≥1 rep per concept + closing named gaps (syllabus short-set rule).

### Phase 1 — unit-03-turtle-art-studio (WEAK) — target core 6 → 10 (table authoritative)

Gaps: `f-string` (MISSING from statements), `turtle-drawing` (stretch-only), `loop-counter` (never in
an expression), `float-type` (real decimal never engaged). Sol flagship: Ex5 only edits two asset
values — students never AUTHOR a turtle program.

0. **FLAGSHIP — rewrite Ex5 into a student-AUTHORED complete polygon program.** Student writes a real
   `assets/`-style `.py` (run from the terminal like Ex1), authoring turtle setup + drawing
   (`penup`/`pendown`/`color`/`pensize`), a `for` over `range(n)`, a counter that DRIVES behavior
   (`pensize(side_number + 1)`), and `angle = 360 / n`. Ship the reference as `assets/solutions_ex5.py`
   with `n = 7` (closes within `turtle-check` tolerance). The notebook cell asserts the numeric parts
   (angle value, counter values, `pensize` for side 0 vs side 3) — NOT the drawing. Codex constraints:
   referenced asset must exist (`ASSET_REF`), must `py_compile` + draw a closed shape (`turtle-check`),
   starter template cannot contain `____` in code cells or be move-free (`cell-lint`). This one rewrite
   makes `turtle-basics`, `turtle-drawing`, `for-loop`, `range-function`, `loop-counter`, `float-type`
   all student-authored.
1. **turtle-drawing more reps (essential → ≥5 AUTHORING; `.py` assets, not notebook cells).** Add pen/
   color authoring touches (different shape/color specs) as student-authored `.py` assets — turtle code
   must NOT live in notebook code cells (`GUI_IMPORT`/un-stubbed execution). `turtle-drawing` is
   essential, so distribute ≥5 authoring reps across the flagship + these assets.
2. **loop-counter expression reps (essential → ≥5 AUTHORING).** `loop-counter` is essential; beyond the
   flagship, add focused exercises that AUTHOR the counter in an expression (`pensize(side_number + 1)`,
   `forward(side_number * 10)`, etc.) — a trace does NOT count toward the bar; distribute the reps
   across the polygon exercises to reach ≥5.
3. **float-type real decimal.** A prediction row for `n = 7` (`angle = 360 / 7` → `51.428571…`); the
   "why can't this be a whole number / what breaks if we round to 51?" beat stays **prose-only** (no
   `round()` call — would flag `builtin-functions`, untaught here).
4. **f-string required by a statement.** Change one worded-answer exercise so the STATEMENT requires an
   f-string report (`print(f"{straight_sides} sides of {side_length} steps")`).
- Trace-only exemptions (unit-03): none required after the flagship (all `introduces`/`practices` now
  authored). Note the audit's Ex4/Ex5 cross-lesson ordering nit as WONTFIX (both taught by unit end).

### Phase 2 — unit-05-function-factory (WEAK) — target core 6 → 11 (table authoritative)

Gaps: `accumulator` (never taught OR exercised — only a solution CI-scaffold line), `nested-loops`
(never authored), `scope` (trace-only), `return-value` (authored once), `import-statement` (asset-run
only). Adds `turtle-drawing` to `practices` (reconciliation 2).

1. **accumulator — option (a), BINDING.** Add a minimal lesson beat (a running `total` over N stamp
   sizes) + a core exercise that authors `total = total + size` and returns it. (Do NOT drop the tag.)
2. **scope authoring.** A scope-repair exercise: a broken snippet that prints a local after the call
   (NameError); student fixes it by RETURNING the value and storing it outside (the repair
   `lesson l3-traceback` promises) — turns scope from trace-only into authoring.
3. **return-value composition.** Author `perimeter(side)` returning `4*side`, then USE the returned
   value in a further computation or feed one function's return into another (`polygon_points →
   polygon` shape) — a 2nd authoring rep in a composition context.
4. **nested-loops + import-statement + turtle-drawing (authored, headless `.py`).** A grid-of-stamps
   program the student authors: starts with a student-written `import turtle` line, both `for` lines
   (outer rows, inner columns) calling `stamp(size)`, and pen/color authoring; predicts the total call
   count. Ship reference as an `assets/*.py` (verified by `turtle-check`); the notebook asserts the
   numeric count. This earns `nested-loops`, `import-statement`, and the newly-added `turtle-drawing`
   in one authored artifact.
5. **unit-05 Ex6 solution note (resolves Sol's flag — NOT errata).** [fable] verified Ex6's solution
   (cell 13) satisfies its statement (cell 17: on-paper blanks + recorded counters/size/distance +
   explanation; solution supplies 90, `*5`, `*40`) — it is the intended headless stub. Action: add a
   one-line note in the solution cell so it is not misread. No code change.
6. Align teacher-notes; record the two metadata adds (reconciliations 2).
- Trace-only exemptions (unit-05): `range-function` may remain fill-in/traced (the flagship/grid author
  the loop bodies; audit rated it "filled, not authored" — acceptable) — listed here per the bar.

### Phase 3 — Term-1 units 01 & 02 (LEAN: minimum reps only) — target core 01: 6 → 7, 02: 6 → 8

Gaps unit-01: `string-concat` rests on one buried line. unit-02: `arithmetic` (incl. `//`/`%`) in ZERO
core exercises, `boolean` implicit only, `str()` never, `elif` single-touch (CP1 grades it hard).

1. **unit-01 string-concat (1 core rep, f-string-free).** A concatenation-only exercise (explicitly "do
   NOT use an f-string"): join a fixed greeting + `name` + a punctuation literal with `+` to print
   `Hello, <name>!`.
2. **unit-02 arithmetic + elif + str (1 combined core rep, kept lean).** A "range width" exercise:
   given `low`/`high`, print the span (`high - low`), midpoint (`(low + high) // 2`), and use `%` for
   even/odd; classify the span three ways with `if/elif/else`; and include a `+`/`*` precedence line
   and a `str()` use in the printed message. Closes `arithmetic` (`+ - // %`), the CP1-graded `elif`
   and precedence, and the `str()` direction in one lean exercise.
3. **unit-02 boolean-as-value (1 core rep).** Store + print a boolean (`print(guess == secret)`) before
   the verdict.
4. **(MINOR)** unit-02: fix Challenge-2's `high`/`low`/`correct` vs numeric `1`/`2`/`3` inconsistency.
5. Align teacher-notes.
- Trace-only exemptions (unit-01/02): none.

### Phase 4 — units 04 & 06 — target core 04: 7 → 10, 06: 7 → 11 (table authoritative)

Gaps unit-04: `or` never authored. unit-06: `boolean`-as-value implicit; `error-messages` fix handed;
`elif` never exercised; `int-type` single touch.

1. **unit-04 author `or` (≥1 core rep; unit-04 is STRONG so this is a single targeted add).** Require
   the student to WRITE an `or` rule from scratch (e.g. accept `"true"` or `"True"`).
2. **unit-06 boolean-as-value (≥2 reps).** Store + print a boolean (`is_vowel = letter in vowels;
   print(is_vowel)`), plus a second combining two checks.
3. **unit-06 active traceback-reading — CANONICAL TEMPLATE (≥2 reps).** Rework Ex7 so the student RUNS
   the buggy `encode("zoo", 3)`, copies the LAST traceback line, and names the failing op BEFORE
   applying `% 26`; add a second small run-broken→read→fix rep. This template is reused in Phases 5–6.
4. **unit-06 elif (≥1 rep).** Classify a char vowel/`y`/consonant with `if…elif…else`.
5. **(MINOR)** unit-06 int-type 2nd touch: call `encode` with two different shifts (3 and 5) and
   compare — fold into an existing exercise.
6. Align teacher-notes.
- Trace-only exemptions (unit-04/06): none.

### Phase 5 — units 07 & 08 — target core 07: 9 → 13, 08: 11 → 14 (table authoritative)

Gaps unit-07: `.sort()`-returns-`None` never exercised, `while-loop` (no exercise), `error-messages`
(no exercise), `max`/`min` single touch, negative index & ascending `.sort()` never, `boolean`
implicit. unit-08: `string-concat` + `type-conversion` MISSING, `boolean` implicit, `error-messages`
shallow, dict key-only iteration never.

1. **unit-07 sort-returns-None (≥1 core rep).** "Predict what `best = scores.sort()` prints, then fix
   it so `best` holds the sorted board."
2. **unit-07 while-loop (≥2 reps).** An arcade `while` exercise (bonus threshold doubles until it passes
   the champion score) + one more `while` rep.
3. **unit-07 error-messages (traceback template, ≥1 rep).** "Write `scores[len(scores)]`, predict the
   error, then rewrite to safely print the last score" — closes `error-messages` AND forces a negative
   index (`scores[-1]`).
4. **unit-07 boolean-as-value + max/min + ascending sort (MINOR folds into existing CORE exercises,
   not challenges).** `print(new_score in scores)`; a 2nd `max`/`min` touch; one plain ascending
   `.sort()` rep.
5. **unit-08 string-concat + type-conversion → core (≥2 reps).** A "print a scoreboard" exercise
   REQUIRING `word + " => " + str(count)` with `+` and explicit `str()` (NOT an f-string), + a second
   varied concat/`str()` rep.
6. **unit-08 boolean-as-value** (`known = word in translations; print(known)`) **+ traceback for Ex11**
   (read the actual `KeyError` before `.get`) **+ (MINOR) dict key-only loop** (`for word in
   translations:`), folded in.
7. Align teacher-notes.
- Exemptions (unit-07/08): **count-exemption** — `error-messages` (both units) may sit below ≥3 with
  ≥1 genuine authoring rep (traceback-reading exercises are inherently limited; practiced across
  06–10); justify in Phase V. No trace-only exemptions.

### Phase 6 — units 09 & 10 — target core 09: 8→12, 10: 8→12. Adds unit-09 `elif-else` (recon. 3)

Gaps unit-09: `error-messages` MISSING, `if-statement` trivial always-true, no edge cases, 6/8 near-
verbatim lesson copies. unit-10: `list-index` near-MISSING, no integrative full-`Pet`, `pass_time`
unpracticed, `dict-literal` shallow, `error-messages` passive.

1. **unit-09 error-messages (traceback template).** A study/`no-exec` exercise showing a
   `FileNotFoundError` traceback; student names the missing file and writes the **"save before load"
   ordering fix** (NO existence check — `os.path`/`pathlib`/`try/except` are untaught, forward-ref).
1b. **unit-09 f-string authoring ([sol] blocker).** `f-string` is a unit-09 `practices` tag but Ex4 only
   asks for a "friendly message" and only the SOLUTION uses an f-string — the exact "listed-but-
   solution-only" pattern this plan targets. Add a core exercise (or amend Ex4's statement) that
   REQUIRES a student-authored f-string reporting loaded data (e.g. `print(f"{name} — high score
   {score}")`), so the tag is earned in a student cell.
2. **unit-09 real branch (adds `elif-else` tag, recon. 3).** Extend the `if "Ada" in info` exercise to
   `if…else` and test a name NOT present so both paths execute. Add `elif-else` to unit-09 `practices`
   (introduced unit-02) so `concept-scan` stays GREEN.
3. **unit-09 edge case ("w" vs "a").** Save the same list twice with `"w"`, confirm no growth, contrast
   with `"a"`. Use a DISTINCT filename (or place so downstream file-state asserts in Ex3/4/8/9/10 still
   hold — the unit's cells chain on file mutations). Any NEW run-time save file must be added to
   `.gitignore` (currently only `unit-09-save-point/savegame.txt` + `settings.txt` are ignored), else
   `ci-local`/`pre-merge-guard` sees an untracked file.
4. **unit-09 transfer.** Vary ≥1 early copy-of-lesson exercise (different score list / settings dict).
5. **unit-10 list-index → statement.** Extend Ex5: after the loop, student writes `pets[0].name` and
   `pets[1].status()` explicitly.
6. **unit-10 integrative full-class (capstone-prep).** A core "Run a Pet Day": student defines the FULL
   `Pet` (all four methods incl. `pass_time`), runs `feed → play → pass_time → status`, asserts final
   hunger/happiness. Closes integration + gives `pass_time` its only student rep.
7. **(MINOR)** unit-10 dict depth (feed from two foods + add a third entry) + run-then-read the
   `AttributeError` in Ex8 — folded into existing exercises.
8. Align teacher-notes.
- Exemptions (unit-09/10): **count-exemption** — `error-messages` may sit below ≥3 with ≥1 authoring
  rep (as in 07/08). No trace-only exemptions.

### Phase 7 — project-01 & project-02

project-01 (STRONG): `return` pre-supplied in both required game functions. project-02 (capstone):
graded path never exercises class METHODS (Hero has only `__init__`); integration/synthesis is a TODO,
not graded; `list-index` only in asserts; traceback under-prepared.

1. **project-01.** Remove the `return` line from ONE required milestone's game function so the student
   authors `return` in a required (non-stretch) path. Keep reference + rubric aligned.
2. **project-02.** (a) Require ≥1 student-authored class METHOD on `Hero` with a parameter + return as a
   graded RUBRIC line — the reference's `Hero.take_damage(self, amount)` (returns `self.health`) is the
   parameter+return exemplar (NOT `describe`/`move`, which are module-level functions, per [fable]);
   closes the "no graded methods" gap AND the audit's manifest-honesty note that `def-function`/
   `parameters`/`return-value` are solution-only. (b) Promote the "assemble the four scaffolds into one
   coherent program" synthesis
   step from a TODO into a named, rubric-scored milestone. (c) Require one student-authored `list-index`
   on the graded path. Traceback readiness is declared resolved upstream by Phase 6 (state so in the
   rubric). Keep the exemplar correct (`seed(4)` reproducibility) + self-contained.
3. Align each project's teacher-notes/rubric. Acceptance: references run clean with fixed seeds; rubric
   lines match new required work; no new concept introduced.

### Phase 8 — checkpoint & metadata reconciliations (MINOR, inline; item 1 ships with PR-A)

1. **CP2 + unit-05 turtle-drawing (reconciliations 1–2) — ships in PR-A** (atomic with the unit-05
   content that earns it): DROP `turtle-drawing` from checkpoint-02 `practices` AND ADD it to unit-05
   `practices` (both surgical, map+manifest). Verify `coverage-check` no longer reports capstone-only,
   and `manifest`/`prereq`/`concept-scan` PASS. (Items 2–6 ship in PR-B.)
2. **CP3 Q6:** adjust the data so the `elif`/`else` branch is reachable (a key absent on one path) so
   the branch executes and the solution's `assert` proves it.
3. **CP3 Q8 → (b):** make the student read the actual `KeyError` first (traceback template).
4. **input false-practice (reconciliation 4):** DROP `input` from `practices` in units 07, 08, 09, 10
   (pure metadata + teacher-notes alignment; decision (a), RED-safe per Global Constraints). Record per
   unit.
5. **CP1 string-concat (reconciliation 5) — BINDING SINGLE ACTION ([sol] blocker).** CP1 Q1 currently
   shows broken concatenation as prose and has the student REPLACE it with an f-string, so the
   `string-concat` `practices` tag is unearned. **The action is: amend CP1 Q1 so the student AUTHORS a
   `+` concatenation** (feasible — `string-concat` is introduced unit-01, and Phase 3.1 adds upstream
   authoring practice). This is the committed disposition; the alternative (dropping the tag) is NOT
   taken because concat is genuinely a CP1-appropriate skill. Verify `manifest`/`coverage`/`concept-scan`
   PASS after.
6. **unit-09 elif-else (reconciliation 3):** applied in Phase 6.2; re-verify here.
- Checkpoints otherwise stay as shipped (proficiency risk resolved upstream by Phases 1–6).

### Phase V — Verification (NAMED, mandatory)

Mechanical (authoritative — `scripts/ci-local.sh` is the gate, design §4):
- `uv run pytest -q` green; ruff clean.
- `scripts/ci-local.sh` **ALL GREEN**: registry+lint, unit tests, notebook execution + hygiene +
  `cell-lint` + `ASSET_REF` + `turtle-check`, `manifest-check`/`coverage-check`/`prereq-check`,
  `concept-scan` (zero used-but-unlisted across all entries after the reconciliation set),
  stretch-check, PDF build, pre-merge guard. `bash scripts/pre-merge-guard.sh --pr` OK.
- **Volume budget (numeric pass/fail, not just "recorded"):** record before→after core counts per
  touched unit and notebook cell/PDF-page counts + `ci-local` duration. FAIL the phase if: any unit
  exceeds **16 core exercises**; any notebook cell exceeds the `exec-solutions` **120 s per-CELL**
  timeout (`NotebookClient(timeout=120)`, `notebooks.py`) — a hard CI limit; or the PDF build fails.
  If any touched notebook's **cell count grows > 2×**, the built **PDF page count grows > 30 %**, or
  total `ci-local` wall-time grows **> 25 %**, that is a **content-gate finding requiring explicit
  reviewer sign-off** before merge (not a silent pass, and not an auto-fail) — the reviewer confirms
  the growth is pedagogically warranted, not bloat.

Proficiency (reviewer-enforced — Phase V is NOT met without this):
- **Whole-union inventory with rep COUNTS (not target-only, not just ≥1):** for EACH touched unit, a
  reviewer walks the COMPLETE `introduces ∪ practices` union and records, per concept, the COUNT of
  non-stretch student-authored exercises that use it. Bar: **≥3** for every concept, **≥5** for each
  listed essential concept (units 03–10); **≥1** for units 01–02. A concept below its bar must be
  either raised, OR carry one of the two listed exemptions (with justification): a **trace-only
  exemption** (concept kept trace-only) or a **justified-peripheral count-exemption** (≥1 genuine
  authoring rep but below the count bar, e.g. `error-messages`). No concept left below bar and
  unexplained. (This is why Phase V exceeds the named remediation list — [sol] blocker 2 + the
  quantity goal.)
- Each added exercise's solution `assert` would catch the intended mistake; ≥1 rep of each concept is
  on the in-class path; any conditional scanner-derived `practices` addition is listed in the
  post-execution report.
- No `introduces`/`requires` changed; the enumerated reconciliation set applied (map == manifest,
  closure + `practices ∩ introduces` empty); every touched unit keeps ≥1 stretch, no core depends on
  stretch, no new forward references.

**Acceptance criteria:** all Phase 1–8 targets student-exercised in core (proficiency bar) AND every
touched unit's full union inventoried; solutions assert-backed + headless clean; the enumerated
metadata reconciliations applied; `ci-local.sh` ALL GREEN incl. `concept-scan`; `pre-merge-guard --pr`
OK; plan-review + (per-PR) content-review 4-way consensus with no `[OPEN]` blockers; plan-023 recorded
as a named follow-up in the post-execution report.

---

## Plan Review

_(4-way gate — [self] / [sol] / [glm] / [fable]. Consensus = all four APPROVE / APPROVE WITH NITS, no
open blockers.)_

### Round 1 (2026-09-08)

- **[self] → APPROVE WITH NITS.** Spec-coverage checklist passed; folded two self-nits (unit-02
  `elif`+`str`, unit-05 `import-statement`) before external review.
- **[glm] → REJECT (1 blocker + nits).** Blocker: unit-05 `import-statement` orphan gap. Nits:
  accumulator (b) scan-unsafe; Phase 6.1 existence-check forward-ref; unit-07 boolean implicit; unit-02
  `elif`; CP1 concat overclaim; verified `input` drop RED-safe for 07–10.
- **[sol] → REJECT (4 blockers).** (1) audit-gap inventory incomplete (unit-05 import, unit-06 int-type,
  unit-07 boolean, unit-09 f-string). (2) Phase V verified only named targets, not each unit's full
  `introduces ∪ practices` union. (3) accumulator fork (b) not scan-safe. (4) grow-the-set had no
  pacing/load acceptance. Nits: Phase 5.4 "challenge" vs core; "two reconciliations" count wrong;
  budget notebook/PDF growth.
- **[fable] → REJECT (4 blockers, all small edits; "expected to flip to APPROVE").** B1 CP2
  `turtle-drawing` drop breaks `coverage-check` (only pre-capstone practicer) → drop-from-CP2 +
  add-to-unit-05. B2 Phase 6.1 existence-check is a forward-ref → "save before load" only. B3 unit-09
  `if/else` flips `concept-scan` RED → add `elif-else` reconciliation + pre-authorize scanner-derived
  adds. B4 accumulator (b) not metadata-only + input decision mis-ordered → commit (a), decide input now.
  Plus CI-grounded nits: unit-03 flagship should author a real `.py` verified by `turtle-check`; keep
  `round()` prose-only; Ex6 is intended stub not errata; per-unit pacing/labelled sections; project-02
  manifest-honesty disposition; list trace-only exemptions; gate-load batching by Term.

### Round-1 reconciliation (2026-09-08)

Round-2 plan (above) folds ALL blockers and nits: CP2/unit-05 `turtle-drawing` swap
(reconciliations 1–2, fixes [fable] B1); unit-09 `elif-else` add + pre-authorization rule ([fable] B3);
"save before load" only ([glm]/[fable] forward-ref); accumulator (a) binding + input decided now
(all); Phase V whole-union inventory + pacing/volume budget ([sol] blockers 2 & 4); unit-05
`import-statement` + unit-06 `int-type` + unit-07 `boolean` + the enumerated reconciliation-count fix
([sol]/[glm] gaps); unit-03 flagship authored-`.py`/`turtle-check` spec + `round()` prose-only + Ex6
note + trace-only exemption lists + project-02 disposition + Term-batched PRs ([fable] nits). All four
plan-review fork answers adopted. **Re-dispatching [sol]/[glm]/[fable] for round-2 confirmation.**

### Round 2 (2026-09-08)

- **[self] → APPROVE.**
- **[fable] → APPROVE WITH NITS (no blockers).** Mechanically applied the full reconciliation set +
  a simulated unit-09 `if/else` to a scratch copy and ran the real checkers: coverage/prereq/manifest/
  concept-scan all GREEN; reproduced the CP2-drop-only and unit-09-without-elif-add FAILs (confirming
  those fixes necessary). 7 CI-grounded nits: cite `Hero.take_damage` (not `describe`/`move`); turtle
  nav limited to `forward/back/left/right` (fake_turtle stub surface); grid must close or carry
  `# turtle-check: open-path`; traceback RAISING lines in markdown not solution cells; ASSET_REF +
  second turtle rep must be a `.py` asset; "More Practice" a label not a heading; "Phase 8 except 8.1".
- **[glm] → APPROVE WITH NITS (no blockers).** Re-verified all reconciliations against the tools
  (drop-only vs drop+add coverage FAIL; unit-09 zero current `orelse`; zero `input(` in 07–10 cells;
  pre-authorization rule bounded + CI-safe). 3 nits: PR-8.1-in-PR-A wording; recon-2 rationale should
  point authorship at Phase 2.4 (not Ex6); Phase 5.4 boolean must place real authorship in core +
  Phase V confirm unit-07 boolean.
- **[sol] → REJECT (2 blockers + 3 nits).** Confirmed round-1 blockers 2–4 resolved + metadata CI-clean.
  Remaining: (B1) unit-09 `f-string` has no remediation action (listed practice, solution-only); (B2)
  CP1 `string-concat` disposition non-binding ("or note"). Nits: numeric volume ceiling (not just
  "record"); enumerate conditional scanner-derived adds; before→after counts for units 01/02/04.

### Round-2 reconciliation (2026-09-08)

Round-3 plan (above) folds everything: **[sol] B1** → new Phase 6.1b (unit-09 f-string authoring rep);
**[sol] B2** → Phase 8.5 now BINDING (author concat or drop the tag); [sol] nits → numeric volume
budget in Phase V (≤16 core, 120 s exec-solutions, PDF, >25% wall-time flag), scanner-derived adds
enumerated in post-exec, and a per-unit core-count + essential-concept table (covers 01/02/04);
**[fable] nits** → `Hero.take_damage` cited, turtle-nav + grid-closure + traceback-in-markdown + ASSET
constraints added to Global Constraints, "More Practice" as a label, Phase 8.1→PR-A; **[glm] nits** →
recon-2 rationale re-pointed to Phase 2.4, Phase 5.4 authorship + Phase V unit-07 boolean, 8.1-in-PR-A.
**Also folds the author's ≥3/≥5 quantity goal** (baseline ≥3 per union concept, ≥5 per listed essential
concept; units 01–02 lean) into Global Constraints, per-phase acceptance, the target table, and Phase V.
**Re-dispatching [sol]/[glm]/[fable] for round-3 confirmation** (the quantity goal is a new,
author-directed scope change all three should see for CI/pacing feasibility).

### Round 3 (2026-09-08)

- **[self] → APPROVE.**
- **[fable] → APPROVE WITH NITS (no blockers).** Verified all 7 round-2 nits folded; re-ran the full
  reconciliation set (incl. CP1-drop option) GREEN; simulated the flagship polygon under the real stub
  (n=7 closes). Nits: per-item specs not re-scaled to ≥3/≥5 + no "peripheral count exemption" category;
  120 s is per-CELL not per-notebook; scope-repair NameError is a raising snippet outside the traceback
  rule's stated scope; phase headers vs table; essential text vs table; Phase 6.3 new file gitignore;
  Phase 1.1 `.py` asset.
- **[glm] → APPROVE WITH NITS (no blockers).** Verified its 3 round-2 nits folded + all reconciliations
  CI-safe. Nits: newly-added tags (`turtle-drawing` u05, `elif-else` u09, `boolean` u07) each get ~1
  locus but owe ≥3 under Phase V — name the loci or exempt; phase-header vs table coherence; lean-unit
  essential-cell annotation; recon-item-5 cross-ref Phase 8.5 binding.
- **[sol] → REJECT (3 blockers).** (1) Phase 8.5 still an either/or fork, not a single binding
  disposition. (2) Per-item specs contradict the ≥3/≥5 bar (Phase 1 "2 turtle-drawing" + a
  non-counting trace; Phase 5 while "≥2"/error "≥1") → re-author loop. (3) Phase headers disagree with
  the table (ambiguous targets). Confirmed the quantity goal is CI-safe and FEASIBLE within ≤16
  (u03 46 incidences ≈4.6/ex; u07 82 ≈6.3/ex) and that units are multi-lesson. Nits: numeric cell/PDF
  ceiling; bound scanner-derived adds in-plan; per-unit in-class timing.

### Round-3 reconciliation (2026-09-08)

Round-4 plan (above) folds all three [sol] blockers + the remaining [fable]/[glm] nits:
- **[sol] B1 (8.5 binding)** → Phase 8.5 + reconciliation-item-5 now a SINGLE committed action (amend
  CP1 Q1 so the student authors a `+` concatenation); the drop alternative removed.
- **[sol] B2 + [fable]/[glm] "per-item vs bar"** → new governing statement: **the quantity goal is the
  SOLE authority on rep counts**; per-item "≥1/≥2" figures are illustrative floors superseded by the
  bar; the plan enumerates WHICH concepts/exercises (Codex authors the counts, verified at Phase V +
  content gate). Added a **justified-peripheral count-exemption** category (e.g. `error-messages`);
  Phase 1.2 trace no longer counts (loop-counter needs authored reps); u07/u08/u09/u10 `error-messages`
  count-exemptions listed.
- **[sol] B3 (headers vs table)** → all phase headers reconciled to the table (table declared
  authoritative): P1 6→10, P2 6→11, P4 04 7→10/06 7→11, P5 07 9→13/08 11→14, P6 09 8→12/10 8→12.
- **[sol] nits** → Phase V numeric cell/PDF-page ceilings (>2× cells / >30% pages flag), scanner-derived
  adds bounded in-plan (anticipated set is complete; extras need PR + gate sign-off), pacing tied to
  each unit's real lesson count (multi-lesson).
- **[fable] nits** → 120 s corrected to per-CELL; traceback rule extended to "any deliberately-broken
  snippet" incl. Phase 2.2 + CP3 Q8 cell-lint note; essential text aligned to the table; Phase 1.1 is a
  `.py` asset; Phase 6.3 gitignore.
- **[glm] nits** → newly-added-tag loci covered by the count-exemption + governing statement; lean-unit
  essential cells annotated (footnote ¹); recon-item-5 cross-refs Phase 8.5.
**Re-dispatching [sol] for round-4 confirmation** ([fable]/[glm] already APPROVE-W-NITS with their nits
now folded; no new material change affects their verdicts).

### Round 4 (2026-09-08)

- **[self] → APPROVE.**
- **[glm] → APPROVE WITH NITS (carried; round-3 nits folded).**
- **[fable] → APPROVE WITH NITS (carried; round-3 nits folded).**
- **[sol] → REJECT (1 blocker + 2 nits).** Blocker: I added the count-exemption category in Global
  Constraints but Phase V's inventory still accepted only "raise or trace-only exemption" — so
  count-exemptions (e.g. `error-messages`) could not satisfy verification (self-contradiction). Nits:
  Phase 3 header lacked its table targets; volume >2×/>30% were flags, not enforceable.

### Round-4 reconciliation (2026-09-08)

Round-5 plan (above) fixes all three: **blocker** → Phase V now explicitly accepts BOTH a trace-only
exemption AND a justified-peripheral count-exemption for below-bar concepts; **nit 1** → Phase 3 header
now carries "01: 6 → 7, 02: 6 → 8"; **nit 2** → the >2× cell / >30% PDF / >25% wall-time thresholds are
now a content-gate finding requiring explicit reviewer sign-off before merge (enforceable, not a silent
pass). **Re-dispatching [sol] for round-5** ([glm]/[fable] APPROVE-W-NITS carried — no change touches
their concerns).

### Round 5

- **[self] → APPROVE.** The lone round-4 contradiction is resolved (Phase V accepts count-exemptions);
  header + volume nits closed. No open blockers.
- **[sol] → (pending round-5)**
- **[glm] → APPROVE WITH NITS (carried).**
- **[fable] → APPROVE WITH NITS (carried).**

## Content Review

_(4-way gate — conducted pre-PR after implementation, per PR. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`.)_

## Post-Execution Report

_(Written before PR; records plan-023 as a named follow-up.)_

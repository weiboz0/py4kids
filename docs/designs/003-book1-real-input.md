# Design 003 — Book 1 Real-Input Norm

**Status:** APPROVED — v2 (v1: plan-050 gate CLOSED, 2026-09-19; v2: plan-052 §3 realistic-data policy,
2026-09-19). Authority for the Book-1 "real-input" norm. Book 1 only; Book 2 is unaffected (it is already
stdin-first/subprocess-judged).

## 1. Motivation

Book-1 examples and exercises use fixed toy data (`n = 3`, 2-element lists) and never read real input, so
programs look fake. This design makes two things the norm, **without abandoning executable worked
examples** (the plans 031–035 / 049 pedagogy) and **without** Book-2's `sys.stdin.read()` + subprocess
judging (explicitly rejected by the course author after comparing options):

1. **Hybrid real-input form.** Every *complete task* (each lesson "put it together") and every exercise
   keeps its **executable fixed-data** form (runs live in the notebook — students see output) **and** gains
   one consistent **`input()`-reading "real program"** form. The idiom is **`input()`** (introduced u01),
   never `sys.stdin`.
2. **Realistic exec data.** Culminating put-it-together cells and exercises use realistic, non-trivial
   data — no `n = 3`, no 2-element lists.

## 2. The form, by notebook kind (CI-forced)

An `input()` cell cannot execute under CI (`nbclient` has no stdin; `tools/notebooks.py`
`INTERACTIVE = \binput\s*\(|\bsys\.stdin\b`). The safe form differs by kind:

| Where | Real-program `input()` form | Executable/validated form |
|---|---|---|
| **lesson.ipynb** | a **`no-exec` `input()` CODE cell** + a `**Notice:**` (proven: u04 lesson cells 20 & 40) | the fixed-data worked-example ladder (unchanged) |
| **solutions.ipynb** | a **markdown fenced ```python block``` (NOT a code cell)** | the fixed-data reference solution **code cell with ≥3 non-vacuous asserts** (run by `exec-solutions`) |
| **checkpoint.ipynb** | markdown fenced block under the `## Question N` | fixed-data solution (in the paired solutions.ipynb) |
| **brief.ipynb** (projects) | markdown fenced block under the `## Milestone N` (Book-1 briefs are milestone-based — **not** `### Problem N`, which is Book-2) | fixed-data solution |

**Why markdown for non-lessons:** `_solution_policy_findings` bans `input()` in ANY `solutions.ipynb`
code cell *regardless of `no-exec`* (units/checkpoints/projects); `cell-lint` compiles non-unit `no-exec`
code cells; `concept-scan` reads all code cells. Markdown fenced blocks are read by none of these (they
scan `cell_type == "code"` only) — this is the plan-045 submission-wrapper precedent. A lesson `no-exec`
`input()` code cell is fine (solution-policy is solutions-only; cell-lint exempts `no-exec` for
`kind=="unit"`).

## 3. Realistic data (Handling (i))

- **u07–u10 (lists from u07):** culminating exec cells use realistic FIXED lists. The **binding requirement
  is that data not be *toy*** (`n=3`, 2-element lists, tiny placeholder values); **≈6–8 elements with real
  variety (ties where apt) is the target for lists being built fresh.** A unit whose culminating lists
  **already hold realistic multi-element data** (≥4 real values — e.g. real scores) satisfies the requirement
  and **need not be grown** — growing already-realistic data forces lockstep rewrites of asserts /
  worked-examples / Notices / teacher-notes for no real gain, so it is not required. Enrichment drills
  **explicitly framed as "small fixed data"** keep their small lists (an extension of the
  build-up-rungs-minimal rule). The `input()` real-forms carry arbitrary-count realism regardless.
- **u01–u06 (no `list` yet):** a realistic *fixed* dataset would need an ugly N-branch `if/elif` — reads
  *more* fake. So the exec cell keeps a **modest** fixed dataset and the **`input()` real-program form
  carries the realism** (u02–u06: an arbitrary count of values; **u01: fixed-count text prompts, no loop**).
- **Build-up rungs stay minimal** (one increment each) — realism applies to the put-it-together +
  exercises only, never the graduated build-up rungs (protects the 031–035 / 049 one-increment pedagogy).

## 4. Prereq closure — per-unit input idiom

- `input` is u01; **`int()`/`str()` (int-type/type-conversion) are u02** → **u01 real-program forms are
  TEXT-ONLY** (read/print strings; no `int()`).
- **u01:** fixed-count prompts, **no loop** (sentinel-loop is u02).
- **u02–u06:** sentinel / count loop. Control-flow caveat: `while-loop` is `concept-scan`-flaggable and is
  **absent from u03/u06/u08/u09**; their lesson real forms use a **`for`** idiom (u03/u06/u09 have
  `range-function` → `for i in range(n)`; **u08** lacks it → `for` over a taught iterable [u08 has
  list-literal/list-loop/list-append] or fixed-count reads), not a sentinel `while`. (`int-type`/
  `type-conversion`/`sentinel-loop` are in `never_flag`, so `int(input())` is always safe.)
- **u07–u10:** may read into a list.

## 5. Metadata

- No `introduces`/`requires`/marker/§3 change. The ONLY change: a General-Rule `practices: [input]` add
  (map + manifest, in sync) for the **4 units whose union lacks `input`** and get a lesson `no-exec`
  `input()` code cell: **u03, u05, u08, u09** (u01/u02/u04/u06/u07/u10 already have `input`).
  Checkpoints/projects use markdown real-forms → no add (cp02/cp03/cp04 need none). `input` is category
  `io`, not a technique → the add cannot trip prereq/practice/technique-spiral checks.
- If a lesson real-form genuinely needs a control-flow concept absent from its unit (e.g. `while-loop`),
  add THAT id too under the General Rule — but §4 avoids this by choosing in-union idioms.

## 6. Validation of real-program forms

`no-exec` / markdown code is never CI-run, so: (a) `ast.parse` every real-program form at authoring;
(b) run it once with piped fixed input (`printf … | python`) and confirm its **result line(s)** equal the
paired fixed-data cell's output *modulo `input()` prompt text* (prompts print to stdout) — record in the
slice's post-exec report; (c) keep the real form line-for-line the fixed-data solution with fixed values
replaced by `input()` reads, so the CI-run asserted fixed-data cell is the behavioral proof. Drift (a slice
edits the fixed-data cell but not its twin) is caught by the per-PR content gate. In unit `solutions.ipynb`,
a fenced real-form must not contain a line starting `## Exercise <digit>` (`solutions_structure` scans raw
markdown).

## 7. Rollout (plans 051+)

Plan 050 ships **design 003 + the u04 pilot** only. Remaining 15 entries roll out unit-by-unit in
subsequent plans, each through both 4-way gates, `ci-local` GREEN per slice:

1. **Units, list-less (Handling (i)):** u01 (text-only, no loop), u02, u03, u05, u06. (`input` add: u03, u05.)
2. **Units, lists (realistic fixed lists):** u07, u08, u09, u10. (`input` add: u08, u09.)
3. **Checkpoints:** cp01–cp04 (markdown real-forms; no `input` add).
4. **Projects:** project-01, project-02 (markdown real-forms under `## Milestone N`).

**The first rollout plan (051) SHOULD include one u07–u10 list unit** (to exercise the list arm) **and the
first checkpoint slice is a mini-pilot** (to exercise the non-unit cell-lint/markdown path) — because the
u04 pilot only covers the list-less unit arm.

## 8. Acceptance

Reached unit-by-unit as each slice merges. A unit/checkpoint/project satisfies design 003 when every
complete task has BOTH an executable fixed-data form (CI-run, asserted where applicable) AND a real-program
`input()` form (no-exec code cell in lessons; markdown elsewhere), put-it-together + exercise data is
realistic where closure allows, build-up rungs stay one-increment, u01 is text-only, no `sys.stdin`,
and `ci-local` is ALL GREEN. Book 2 stays green throughout.

## 9. Revision history
- **v1 (2026-09-19):** created for plan 050; 4-way plan-review gate CLOSED (3 rounds — resolved: the
  `input()`-in-solutions policy → markdown real-forms; u01 int/str boundary; project `## Milestone N`
  mapping; the 4-unit `input` add set; control-flow closure; real-form validation).
- **v2 (2026-09-19, plan 052):** §3 realistic-data policy clarified — the binding requirement is
  "not toy"; ≈6–8 elements is the target for lists built fresh, but a unit already using realistic
  multi-element lists (≥4 real values) need not be grown, and "small fixed data" enrichment drills keep
  their lists. Under this policy a unit grows only its <4-element core SOURCE lists (u07 [plan 052]: Ex1/Ex7/
  Ex8/Challenge 2), leaving already-realistic core lists + enrichment/rung data untouched; the govern is
  source/input data, not computed result literals.

# Design 003 — Book 1 Real-Input Norm

**Status:** APPROVED — v6 (v1: plan-050 gate CLOSED; v2: plan-052 §3 realistic-data policy; v3: plan-053 §2
checkpoint/brief placement + §6d oracle; v4: plan-056 §5 input-add per-unit-audit-contingent + §1/§8 reads-nothing/generator exemption + §7 reconciled;
v5: plan-057 §1/§8 full exemption taxonomy [reads-nothing/generator + debug/fix-the-error + predict/trace];
v6: plan-059 §1 fixed-reference-fixture exemption + §4 pair-split dict-read idiom, 2026-09-19). Authority for the Book-1 "real-input" norm. Book 1 only; Book 2 is unaffected (it is already
stdin-first/subprocess-judged).

## 1. Motivation

Book-1 examples and exercises use fixed toy data (`n = 3`, 2-element lists) and never read real input, so
programs look fake. This design makes two things the norm, **without abandoning executable worked
examples** (the plans 031–035 / 049 pedagogy) and **without** Book-2's `sys.stdin.read()` + subprocess
judging (explicitly rejected by the course author after comparing options):

1. **Hybrid real-input form.** Every *complete task* (each lesson "put it together") and every exercise
   that **processes input-shaped data** keeps its **executable fixed-data** form (runs live in the
   notebook — students see output) **and** gains one consistent **`input()`-reading "real program"** form.
   The idiom is **`input()`** (introduced u01), never `sys.stdin`.
2. **Realistic exec data.** Culminating put-it-together cells and exercises use realistic, non-trivial
   data — no `n = 3`, no 2-element lists.

**Exemptions — which tasks get NO real-program form (v5).** The both-forms rule (clause 1, §8) applies only
to tasks that **process input-shaped data**. A task is EXEMPT (executable form only, plus a
`**No real version:**` note naming the class) when it falls in one of **four** settled classes (classes 1–3
applied across u01–u06; class 4 added in v6 for u08):
1. **Reads-nothing / generator** — produces output *without reading any external input*: a **turtle
   drawing**, a random **generator** (dice roller), a **countdown**, a **fixed printed card/receipt**. There
   is nothing to read. A unit whose lesson capstones are *all* this class (e.g. u03, all turtle drawings)
   adds **no lesson `input()` cell and no metadata** (§5); its real-forms — where an exercise *does* process
   input-shaped data — live only in `solutions.ipynb` markdown.
2. **Debug / fix-the-error** — the graded task is *repairing* the code (a wrong literal, a missing parameter,
   a scope/`NameError` fix); the fix IS the answer, and reading input does not dissolve it. **Exception:** if
   the repair *itself* is to read input (e.g. u02 Ex4, where `int(input())` was the fix), it is NOT exempt —
   it is a single-read real task.
3. **Predict / trace** — the graded task is predicting or hand-tracing the *fixed* output ("trace on paper",
   "predict the exact output"); replacing the fixed values with `input()` would defeat the prediction.
4. **Fixed-reference-fixture (v6)** — the input-shaped data is a **pre-authored dict/table used as reference or
   lookup data**, and the graded skill is a **transform or report *over* that fixture** (format it, merge two,
   flip it, total it, find its extreme) rather than *obtaining* it, AND reconstructing the fixture from input
   would require out-of-union control flow (e.g. a unit lacking `range-function`/`while-loop`). Then the task
   is exempt (executable-only). **Designated-demonstrator rule:** so the structure-read idiom (§4) is *shown at
   least once* rather than never, the plan **names ≥1 representative fixture task per fixture value-type** to
   carry a structure-read real-form (e.g. u08: one string-valued phrasebook walk + one int-valued tally
   find-extreme); every other fixture task is class-4 exempt. (The designated demonstrators are a coverage
   choice, not a property of the task — sibling tasks of the same shape are exempt.) (Origin: u08 word-wizard,
   plan 059, user-ratified "split"; wording per the 4-way gate.)

A **hybrid** task (one part input-shaped, one part exempt — e.g. u03 Ex2/Ex4: a compute-authoring program +
a prediction table) gets a real-form for the input-shaped part and a `**No real version:**` note for the
exempt part, each cue labeled by which half it governs.

## 2. The form, by notebook kind (CI-forced)

An `input()` cell cannot execute under CI (`nbclient` has no stdin; `tools/notebooks.py`
`INTERACTIVE = \binput\s*\(|\bsys\.stdin\b`). The safe form differs by kind:

| Where | Real-program `input()` form | Executable/validated form |
|---|---|---|
| **lesson.ipynb** | a **`no-exec` `input()` CODE cell** + a `**Notice:**` (proven: u04 lesson cells 20 & 40) | the fixed-data worked-example ladder (unchanged) |
| **solutions.ipynb** | a **markdown fenced ```python block``` (NOT a code cell)** | the fixed-data reference solution **code cell with ≥3 non-vacuous asserts** (run by `exec-solutions`) |
| **checkpoint.ipynb** | markdown fenced block in the **paired `solutions.ipynb`** under the mirrored `## Question N` (the student `checkpoint.ipynb` stays solution-free — Content Conventions); where a Question's statement/starter **already reads `input()`**, that statement IS the real-program form and the solutions block is the model answer | fixed-data solution (in the paired solutions.ipynb) |
| **brief.ipynb** (projects) | markdown fenced block in the **paired `solutions.ipynb`** under the mirrored `## Milestone N` (Book-1 briefs are milestone-based — **not** `### Problem N`, which is Book-2); the student `brief.ipynb` stays solution-free | fixed-data solution |

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
- **Read-into-list / read-into-dict idioms (v6):** a unit reading a *variable-count* structure must use an
  idiom in its union. With `range-function` → `for i in range(n)`; with a sentinel and `while-loop` → sentinel
  loop; **lacking BOTH `range` and `while` (u08)** → read one line and split: a **list** via
  `items = input("...").split()`, a **dict** via the **pair-split** idiom `for pair in input("...").split():`
  then `parts = pair.split(":")` / `d[parts[0]] = parts[1]` (or `int(parts[1])`) — **no assignment-unpacking**
  (statement-level `k, v = …` is never taught in Book 1). **`.split()` is NOT the `string-methods` concept**
  (that is upper/lower/strip/replace) — it is its own **`str-split`**, which must be registered + **introduced in
  the unit's union** before use (introduced u08, plan 059). A unit lacking `str-split` (and `range`/`while`) uses
  **fixed-count reads** instead (`items = [input(...), input(...), …]`; `d[input(...)] = input(...)` ×N).

## 5. Metadata

- No `introduces`/`requires`/marker/§3 change. The `practices: [input]` add (map + manifest, in sync) applies
  **only to a unit whose union lacks `input` AND that actually gets a lesson `no-exec` `input()` CODE cell**
  (concept-scan reads code cells; markdown real-forms are invisible). Candidate set was u03/u05/u08/u09, but
  the add is **contingent on the per-unit audit finding a lesson input() code cell**, not automatic:
  - **u03 (plan 056): NO add** — u03's lesson is all turtle-DRAWING (no compute capstone to pair), so its
    real-forms live ONLY in `solutions.ipynb` markdown (invisible to concept-scan); no u03 code cell uses
    `input`, so no metadata change. (u05/u08/u09 decided in their own plans by the same audit.)
  Checkpoints/projects use markdown real-forms → no add. `input` is category `io`, not a technique → any add
  cannot trip prereq/practice/technique-spiral checks. (`int-type`/`type-conversion` are `never_flag` too, so a
  markdown `int(input())` never forces a metadata change.)
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

(d) **Fragment / condition-completion exception (v3).** When a question grades a FRAGMENT — a boolean
condition, a single line — rather than a full program, (b)/(c) are adapted: the asserted fixed-data twin
validates the **graded fragment** (e.g. `keep_guessing = guess != secret` → `True`), and the piped-run
**completed** real-form validates **termination + result line** (e.g. the guess loop prints `"You found
it!"`). The twin need not be line-for-line the completed program; the real-form block is captioned as the
completed program so it is not misread as the fragment. (Origin: checkpoint-01 Q5, plan 053.)

## 7. Rollout (plans 051+)

Plan 050 ships **design 003 + the u04 pilot** only. Remaining 15 entries roll out unit-by-unit in
subsequent plans, each through both 4-way gates, `ci-local` GREEN per slice:

1. **Units, list-less (Handling (i)):** u01 (text-only, no loop), u02, u03, u05, u06. (`input` add: **per the
   §5 per-unit audit**, not automatic — u03 gets **none** (all-drawing lesson; solutions-markdown-only).)
2. **Units, lists (realistic fixed lists):** u07, u08, u09, u10. (`input` add: per the §5 per-unit audit.)
3. **Checkpoints:** cp01–cp04 (markdown real-forms; no `input` add).
4. **Projects:** project-01, project-02 (markdown real-forms under `## Milestone N`).

**The first rollout plan (051) SHOULD include one u07–u10 list unit** (to exercise the list arm) **and the
first checkpoint slice is a mini-pilot** (to exercise the non-unit cell-lint/markdown path) — because the
u04 pilot only covers the list-less unit arm.

## 8. Acceptance

Reached unit-by-unit as each slice merges. A unit/checkpoint/project satisfies design 003 when every
complete task **that processes input-shaped data** has BOTH an executable fixed-data form (CI-run, asserted
where applicable) AND a real-program `input()` form (no-exec code cell in lessons; markdown elsewhere) —
while **the §1 exempt classes (reads-nothing/generator, debug/fix-the-error, predict/trace,
fixed-reference-fixture) have the executable form only, with a `**No real version:**` note naming the class** — put-it-together + exercise
data is realistic where closure allows, build-up rungs
stay one-increment, u01 is text-only, no `sys.stdin`, and `ci-local` is ALL GREEN. Book 2 stays green
throughout.

## 9. Revision history
- **v6 (2026-09-19, plan 059):** §1 added a fourth exempt class — **fixed-reference-fixture** (a task that
  transforms/reports over a pre-authored dict/table used as lookup data, where rebuilding the fixture from
  input needs out-of-union control flow), with a **designated-demonstrator rule** (the plan names ≥1
  representative fixture task per value-type to carry a structure-read real-form; the rest exempt). §4 added
  the range/while-less **read-into-list (`.split()`) / read-into-dict (pair-split)** idioms and clarified that
  **`.split()` is its own concept `str-split`** (NOT the `string-methods` upper/lower/strip/replace concept),
  which must be registered + introduced in the unit's union (introduced u08); fixed-count reads are the fallback
  where `str-split` is absent. User-ratified teaching `.split()` in u08 (option b) + the exempt/demonstrator
  split; the 4-way gate ratifies wording.
- **v5 (2026-09-19, plan 057):** §1/§8 codified the **full exemption taxonomy** — the three settled classes a
  task may be exempt under (reads-nothing/generator; debug/fix-the-error, unless the fix itself reads input;
  predict/trace), plus the hybrid rule. Makes explicit the convention applied across u01–u04 (the reviewer
  gate had split on whether debug/predict tasks were exempt because v4 named only the reads-nothing class).
- **v1 (2026-09-19):** created for plan 050; 4-way plan-review gate CLOSED (3 rounds — resolved: the
  `input()`-in-solutions policy → markdown real-forms; u01 int/str boundary; project `## Milestone N`
  mapping; the 4-unit `input` add set; control-flow closure; real-form validation).
- **v2 (2026-09-19, plan 052):** §3 realistic-data policy clarified — the binding requirement is
  "not toy"; ≈6–8 elements is the target for lists built fresh, but a unit already using realistic
  multi-element lists (≥4 real values) need not be grown, and "small fixed data" enrichment drills keep
  their lists. Under this policy a unit grows only its <4-element core SOURCE lists (u07 [plan 052]: Ex1/Ex7/
  Ex8/Challenge 2), leaving already-realistic core lists + enrichment/rung data untouched; the govern is
  source/input data, not computed result literals.
- **v4 (2026-09-19, plan 056):** (§5) the `practices:[input]` add is **contingent on a per-unit audit
  finding a lesson `no-exec` `input()` CODE cell**, not automatic for the u03/u05/u08/u09 candidate set. u03 is
  all turtle-drawing (real-forms in solutions markdown only, invisible to concept-scan) → NO metadata add.
  (§1/§8) codified the **reads-nothing/generator exemption**: a task that produces output without reading
  external input (turtle drawing, generator, countdown, fixed printed card) has no real-program form and
  satisfies the norm with its executable form alone; the both-forms rule applies only to input-shaped tasks.
  (§7) reconciled the rollout `input`-add notes to defer to the §5 per-unit audit (u03 gets none).
- **v3 (2026-09-19, plan 053):** (§2) checkpoint + brief rows clarified — the real-program form lives in the
  PAIRED `solutions.ipynb` under the mirrored `## Question N` / `## Milestone N` (the student
  checkpoint/brief stays solution-free, per Content Conventions); where a Question/Milestone statement or
  starter already reads `input()`, that IS the real-program form and the solutions block is the model answer.
  (§6d) added a fragment/condition-completion validation exception (twin proves the graded fragment; the
  completed real-form proves termination + result line). Codifies plan 053's checkpoint-01 placement + Q5
  oracle; cp02–cp04 + projects follow both.

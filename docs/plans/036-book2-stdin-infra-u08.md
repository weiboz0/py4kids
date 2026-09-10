# Plan 036 — Book 2 stdin-first re-architecture: judge harness + design amendment + U08 pilot

**Goal:** Replace Book 2's `solve(data: str) -> str` inline-assert contract with a **stdin-first,
subprocess-judged** model (reference solutions are real contest `.py` scripts that read stdin and
print stdout, verified by a new `judge-check` harness against committed `.in`/`.out` fixtures), and
prove it end-to-end by re-authoring **U08 Prefix Sums** to the new model WITH the graduated
worked-example-ladder + completeness standard. This is the infra + design-amendment + first pilot
unit; U06 greedy follows in plan 037, then rollout.

**Why (user direction):** Book 2 lessons are too brief (one full solver per concept, no graduated
build) and the `solve(data)` wrapper is an extra abstraction barrier — real contest code reads stdin.
The user chose (AskUserQuestion, 2026-09-10): re-architect to stdin-first with a subprocess judge;
graduated algorithm-build ladders (tiny case → mechanism → full solver "Put it together" + edge rung
+ complexity note); pilot 2 units then roll out; full scope = units + checkpoints + capstone
(completeness pass across the rollout). Reference solutions stored as `assets/*.py` + fixtures, with
`solutions.ipynb` kept as a no-exec display mirroring each script.

**Architecture:** The map confirmed **no tool hard-codes `solve(`** — the contract is pure content
convention enforced only by `_solution_policy_findings` (≥3 non-vacuous asserts) + the kernel raising
on a failed assert. `turtle_findings` (`tools/fake_turtle.py:152-217`) is the subprocess-judge
precedent. So the change is tractable: add a `judge-check` that runs each solution `.py` via
`subprocess.run([python, script], stdin=<case.in>, ...)` and token-compares stdout to `<case.out>`;
extend `concept-scan` to scan those `.py` for taught-concept closure (allowing `input`/`sys.stdin`/
`print`); stop requiring/executing `solve()`-assert solution cells for book2; amend design-001 §3.

**Tech stack:** Python verification package (`tools/`), `scripts/ci-local.sh`, Jupyter notebooks,
committed `.in`/`.out` fixtures.

## The new stdin-first judge contract (replaces design-001 §3)

- **Reference solution = a runnable `.py` script** per problem, in the entry's `assets/` dir. It reads
  the whole input from stdin (`data = sys.stdin.read()` or line-wise `input()`), computes, and
  `print`s the exact output. Real contest code — no `solve()` wrapper required (a solver MAY still
  define helper functions; what matters is stdin→stdout).
- **Fixtures = committed `.in`/`.out` pairs** per problem: `assets/<pid>/1.in`+`1.out` (the stated
  sample) and `assets/<pid>/2.in`+`2.out`, … (≥1 crafted edge/larger case). **≥2 cases per problem**
  (non-vacuous discipline: a case whose decisive value is last / boundary, so a wrong solver fails —
  same mutation-kill bar as the old crafted asserts, now as files).
- **`judge-check` (new tool)** runs each `assets/*.py` × each fixture pair: pipe `<k>.in` to stdin,
  capture stdout, **token-compare** (`out.split() == expected.split()`) for whitespace tolerance;
  FAIL on mismatch, nonzero exit, or timeout. Deterministic (no `random`). Generous timeout (Big-O is
  taught, not CI-enforced — keep fixtures modest so a correct solver finishes well under the limit).
- **Lessons** show the full solver as a **`no-exec` cell mirroring its `.py`** (input()/sys ⇒ must be
  `no-exec`, already enforced by `noexec-check`), with a run line `python assets/<pid>.py <
  assets/<pid>/1.in` — the Book-1 turtle UX. The ladder's EARLY rungs stay **executable notebook
  cells on literal tiny data** (no stdin) so lessons still show live output under `exec-lessons`.
- **`solutions.ipynb`** stays (keeps `structure-check` required-files stable) as a teacher-facing,
  all-`no-exec` notebook that shows + explains each reference `.py` (mirrors it statement-for-
  statement, same discipline as Book-1 turtle cells; reviewers diff them).
- **Complexity** is still taught in teacher-notes (not CI-enforced). **Submission** is now the
  reference form itself (no separate wrapper needed).

## The Book-2 worked-example-ladder + completeness standard (established here)

For each concept a unit INTRODUCES (a technique), replace the single full solver with a graduated
build, each rung followed by a one-line `**Notice:**` naming the SINGLE new thing:

1. **rung 1 — the core idea on a tiny case**: an executable notebook cell operating on literal data
   (e.g. `nums = [3, 1, 4, 1, 5]`), hand-traceable, printing the key intermediate. ONE increment.
2. **rung 2 — the mechanism**: one step up on the same literal data (e.g. build the structure once,
   answer ONE query). ONE increment.
3. **rung 3 — generalize**: loop / parameterize the mechanism (still literal data or a small list).
4. **Put it together — the full solver**: the real stdin `.py` (shown as a `no-exec` cell), with its
   fixtures judged by `judge-check`. This is where input parsing enters.
5. **completeness rung(s)**: the edge cases the technique must handle (shown as an extra fixture + a
   lesson note), AND — where the technique has a FAILURE MODE — a **counterexample** showing when the
   naive/greedy/obvious approach is WRONG (a paradigm-unit requirement; e.g. greedy-by-wrong-key).
6. **complexity note**: a markdown `**Complexity:**` line stating the Big-O and why it is fast enough.

Governing bar (user's priority): **COMPLETENESS** (cover the realistic variations + the failure mode)
+ **GRADUAL PACING** (exactly one increment per rung). Rung count follows difficulty. Early rungs obey
all Book-2 closure rules (see below); the full solver obeys them too but may read stdin.

## Global Constraints (closure + tooling specifics — reviewer-enforced where noted)

- **U08 Prefix Sums** introduces `prefix-sum` (technique, reviewer-enforced); requires `list-literal,
  list-append, loop-counter, accumulator, grid-2d, nested-loops`; practices the parsing/house set.
  Ladder: 1D cumulative (tiny list → build prefix[] once → one range query `prefix[r+1]-prefix[l]` →
  loop many queries) then 2D (inclusion-exclusion) as its own ladder; full solvers = stdin `.py`.
  Completeness: the extra-zero sentinel (prefix[0]=0), whole-array and single-element range edges.
- **Closure / scanner rules (carry over from the solve() era — STILL apply to the `.py` solvers and
  the lesson rungs):** allowed builtins ONLY `{len, min, max, sorted, sum, abs, round}`; banned &
  scanner-blind (AST-grep): `+=`, comprehensions (`ListComp/SetComp/DictComp/GeneratorExp`), chained
  comparison (`a < b < c`), list-repetition `[x]*n`, ternary `a if c else b` (`IfExp`), `nonlocal`/
  `global`, `.pop`/`.join`/`.index`/`.count`/`.find`, `del`, `itertools`/`Counter`. House style
  `x = x + 1`. One-concat-per-statement for output (`out = out + piece`, CPython O(n)). **NEW allowed
  for stdin solvers:** `input`, `sys`, `sys.stdin.read()` (`.read`/`.readline`/`.readlines` already in
  `TAUGHT_METHODS`), `print`, `.split()` (str-split), `int()`/`str()` (type-conversion).
- **Lessons** open project-first (contest-problem hook). Early ladder rungs are executable (literal
  data); the stdin solver cell is `no-exec`. `manifest.lessons` == coverage-map lessons (unchanged:
  U08 stays 2); no syllabus figure change.
- **Fixtures convention:** `assets/<pid>/<k>.in` + `<k>.out`; `<pid>` = `l1`,`l2`,… for lesson
  solvers and `ex1`…`exN` for exercise reference solutions; ≥2 cases each; outputs are exact strings.

## Phases

### Phase A — `judge-check` tool + `concept-scan` over `.py` + `ci-local` wiring

- **Create `tools/judge.py`** with `judge_findings(root, book, unit=None)` (modeled on
  `turtle_findings`): for each entry dir under the book, for each `assets/*.py`, for each fixture pair
  `assets/<pid>/<k>.in`+`<k>.out`, run `subprocess.run([sys.executable, script], stdin=<in bytes>,
  capture_output=True, text=True, timeout=…, cwd=repo root, check=False)`; FAIL on nonzero/timeout/no
  output; token-compare stdout to expected; FAIL with a diff-ish message on mismatch. Require **≥1
  `.py` with ≥2 fixture pairs** per authored entry that has an `assets/` dir (entries without
  `assets/` are skipped — tolerate a partial book, like the other per-entry checks). Register
  `"judge-check": judge_findings` in `tools/checks.py`; add to `UNIT_ONLY`/entry iteration as
  appropriate.
- **Extend `concept-scan`** to also scan each entry's `assets/*.py` (parse with `ast`, run the same
  `detect()` closure) so real contest code is held to taught-concepts; **allow `input` and `sys`** for
  `.py` solvers (add `input` to the scanner's recognized/never-flag set or map to `input-parse`; `sys`
  import → `import-statement`, exempt like the precedented no-exec wrapper `import sys`). Verify the
  banned-token AST greps still fire on the `.py`.
- **Retire the book2 `solve()`-assert path:** `_solution_policy_findings` (≥3 asserts) and
  `exec-solutions` should no longer REQUIRE executable assert cells for book2 entries that use the new
  `assets/`+`judge-check` model. Make `solutions.ipynb` permitted to be all-`no-exec` display;
  `exec-solutions` must not execute (and hang on) `no-exec`/stdin display cells. Keep `exec-lessons`
  (the literal-data ladder rungs still run).
- **Wire `judge-check` into `scripts/ci-local.sh`** for book2 (after the existing per-entry checks).
- **Tests:** add `tools/` unit tests for `judge_findings` (a passing fixture set, a wrong-output
  FAIL, a timeout/nonzero FAIL) using a tiny temp entry.

### Phase B — design-001 §3 amendment + standard

Rewrite `docs/designs/001-book2-algorithms.md §3` from the `solve(data)` inline-assert contract to the
stdin-first subprocess-judge contract above (fixtures in `assets/`, `judge-check`, `.py` solvers,
`solutions.ipynb` as display, lessons' executable-literal rungs + no-exec stdin solver). Record the
Book-2 ladder/completeness standard (this plan's section) there or in the plan as the reusable
reference for the rollout. (design-001 is a design doc, not a governance file — amendable here.)

### Phase C — U08 Prefix Sums re-author (the end-to-end pilot)

Re-author `book2/units/unit-08-prefix-sums/`:
- `lesson.ipynb`: 1D and 2D prefix-sum ladders (executable literal-data rungs + Notices), the full
  stdin solvers as `no-exec` cells mirroring `assets/l1.py`/`assets/l2.py`, completeness (sentinel +
  range edges), and `**Complexity:**` notes (O(n) build / O(1) query; O(R·C) build / O(1) 2D query).
- `assets/`: `l1.py`,`l2.py` (lesson solvers) + `ex1.py`…`exN.py` (exercise reference solutions), each
  reading stdin / printing stdout, each with `assets/<pid>/{1,2,…}.in`+`.out` fixtures (≥2, non-vacuous
  incl. a decisive-last / boundary case per the Book-2 mutation-kill discipline).
- `exercises.ipynb`: statements unchanged in shape (`## Exercise N`, Sample Input/Output, Constraints;
  ≥8, ≥2 stretch) — re-point "submit" to running the `.py` with piped input.
- `solutions.ipynb`: all-`no-exec` display mirroring each `.py` + short explanation.
- `teacher-notes.md`: 5 unit headings; pacing re-synced to the ladders (U08 stays 2 lessons);
  per-exercise Big-O; the concept→core-practice matrix.
- `manifest.yaml`: add nothing to concepts (prefix-sum unchanged); `lessons: 2` unchanged.

### Phase D — Verification (named verification phase)

`scripts/ci-local.sh` ALL GREEN including the new `judge-check`: registry/lint, unit tests (incl. the
new `judge_findings` tests), `exec-lessons` (U08 literal-data rungs run clean; stdin solver cells
`no-exec`), `judge-check` (every U08 `assets/*.py` passes its fixtures), `concept-scan` (closure over
lesson + `.py`, stdin constructs allowed, banned AST-greps clean), `coverage`/`prereq`, manifest==map,
structure/hygiene/noexec/cell-lint, Book-1 PDF build (book1-only — unaffected), pre-merge guard.
**Closure + completeness audit (primary content-review duty):** each ladder one-increment with a
focused Notice; full solver framed "Put it together"; fixtures non-vacuous + mutation-killing; no
banned/untaught construct in any `.py` or rung; stdin solvers correct on the stated samples; lessons
project-first; `## Pacing` == lessons.

## Out of scope

- U06 greedy (plan 037, the paradigm pilot) and the remaining 12 units / 4 checkpoints / capstone
  (rollout plans after both pilots merge). Any Book-1 change. Governance files.
- **Verification-phase note:** ships a reworked unit WITH a named verification phase (Phase D) plus
  new tooling covered by new `tools/` unit tests.

## Post-Execution Report

_(filled at Phase D)_

## Plan Review

_(4-way plan-review gate — consensus before implementation)_

## Content Review

_(4-way content-review gate — consensus before PR)_

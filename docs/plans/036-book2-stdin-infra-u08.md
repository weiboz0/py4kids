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

### Phase A — `judge-check` + `source-policy` checker + per-entry switch + `ci-local` wiring

**A1 — `tools/judge.py` `judge_findings(root, book, unit=None)`** (modeled on `turtle_findings`,
iterating `content_dirs` — units + checkpoints + projects):
- **BOOK-SCOPED to `book2`** (GLM blocker): return `[]` immediately for any `book != "book2"`. The
  "new-model = `assets/` + `.py`" detector is indistinguishable from Book-1 turtle assets, so running
  this on Book 1 would try to judge 22 turtle scripts (no `fake_turtle` stub → fail) and break the
  `CHECK_NAMES`-parametrized Book-1 suites. `source_policy_findings` (A5) is book-scoped the same way.
  This book1/unknown-book `[]` is an **intentional documented no-op** (NOT the fail-closed-on-missing-
  root convention — these checks simply don't apply outside book2); note it at the return site.
- **Expected-solver PID derivation, per entry kind** (so a MISSING solver is caught, not just a
  present one — Sol B2): a **unit** derives `exN.py` from each `## Exercise N` in `exercises.ipynb`
  plus lesson solvers `l1.py`…`l{manifest.lessons}.py` (derive from `manifest.lessons` / `## Lesson N`
  headings — NOT circularly from which `.py` the lesson references, glm N2); a **checkpoint** derives
  `qN.py` from each `## Question N`; a **project** derives `pN.py` from each `### Problem N` in
  `brief.ipynb` (the capstone's heading level — NOT `## Milestone N`, which groups problems). **All
  heading regexes MUST be end-unanchored** (follow the house `EXERCISE_HEADING` pattern) — real
  headings are decorated, e.g. `### Problem 1 — Checkpoint Ledger *(prefix sums)*`; a `$`-anchored
  regex derives zero PIDs and resurrects the fail-open (fable N1). FAIL any expected-but-missing
  `.py`. **Reserved-stem rule (fable N2):** any `assets/*.py` whose stem matches `(l|ex|q|p)\d+` is
  ALWAYS a solver (fixtures + judged + mirrored), never silently demoted to a helper. A `.py` whose
  stem does NOT match that pattern is a **helper module**: still source-policy-scanned (A5) and
  parse-checked, but not fixture-required and not run standalone.
- For **every** solver `.py` (a derived PID), require **≥2 matched fixture pairs**
  `assets/<pid>/<k>.in`+`<k>.out`; FAIL a solver with <2 pairs, an `.in` with no matching `.out` (or
  vice-versa), and an orphan fixture dir with no `.py`.
- Run each case: `subprocess.run([sys.executable, str(script)], input=<case>.in.read_text(),
  text=True, capture_output=True, timeout=JUDGE_TIMEOUT_S, cwd=<repo root>, check=False)` — note
  **`input=` (a string), NOT `stdin=`**, with `text=True` (Sol BLOCKER 1). FAIL on nonzero exit,
  timeout, or empty output (**`stdout.strip() == ""`** so a trailing-newline-only output is
  unambiguous, fable N6); else **token-compare** `stdout.split() == expected.split()`, FAIL with a
  short diff on mismatch. `JUDGE_TIMEOUT_S = 30` (module constant); keep fixtures modest so a correct
  solver finishes well under it. Entries without `assets/` are skipped (partial-book tolerant).
- **Mirror check:** for each solver `<pid>.py`, exactly ONE display source must equal the `.py`
  **modulo whitespace = per-line trailing-whitespace strip + trailing-blank-line strip (NOT full
  whitespace collapse)** (fable N3). The target: an `exN`/`qN` PID → the CODE cell under that
  `## Exercise N`/`## Question N` in `solutions.ipynb`; a project `pN` → the CODE cell under
  `## Problem N` in the project `solutions.ipynb` (note: brief uses `### Problem N` but the project
  `solutions.ipynb` uses `## Problem N`, and `project_solutions_findings` has no code-cell-under-
  heading enforcement, so the mirror check must target it — glm N1); a lesson `lN` → its `no-exec`
  display cell in `lesson.ipynb`. The lesson's ladder-rung cells (partial excerpts on literal data)
  are NOT mirror targets. This kills the display-vs-`.py` drift nit class across the rollout without
  false-positiving on partial rungs.
- **turtle-check footgun (fable N4):** `turtle_findings` globs ALL `assets/*.py`; a manual
  `py4kids-tools --book book2 turtle-check` would run U08's stdin solvers under the stub and block on
  `sys.stdin.read()`. While in Phase A, have `turtle_findings` skip any script with no `import turtle`
  (or book-scope it to book1).
- Register `"judge-check": judge_findings` in `tools/checks.py`; it is **NOT** in `UNIT_ONLY_CHECKS`
  (checkpoints/projects gain `assets/` in rollout). Update the registry inventory test
  (`tuple(CHECKS) == CHECK_NAMES`) and the missing-root/selector matrices (both pass because the check
  returns `[]` for book1).

**A2 — per-entry new-vs-old switch (the correctness-continuity linchpin).** Detection: an entry is
**new-model** iff it has an `assets/` dir containing ≥1 `.py`. For a new-model book2 entry, **skip the
ENTIRE `_solution_policy_findings`** (not only the ≥3-assert sub-finding but also its `input()`/GUI/
`random` bans at `tools/notebooks.py:264-270` — the no-exec display cells legitimately mirror stdin
`input()`/`sys` code) AND have `exec-solutions` skip the entry outright (it has no `no-exec` filter
and would hang on stdin display cells); correctness comes from `judge-check`. An **old-model** entry
(no `assets/`) is unchanged — `exec-solutions` + ≥3 asserts exactly as today, so the 13 un-migrated
units + 4 checkpoints + capstone stay verified throughout the rollout. Add `no-exec` filtering to
`exec-solutions` too (harmless — no current `solutions.ipynb` carries a `no-exec` cell). Scope every
exemption to **book2 + assets-model**; update `tests/test_tools.py` (the policy tests near :1525,
:2103) and add **both-direction** tests (assets entry exempt incl. an `input()` display cell;
assets-less book2 entry STILL requires ≥3 asserts).

**A3 — `noexec-check` stdin extension.** `INTERACTIVE` (`tools/notebooks.py:46`) matches only
`input(`; extend it to also match `sys.stdin` so a lesson solver cell reading `sys.stdin.read()` is
forced `no-exec` (else `nbclient` silently returns `""` and the cell "executes clean" on garbage —
GLM #2 / fable N3). Still guards `lesson.ipynb` (where the mirror solver cell lives).

**A4 — `concept-scan` over `.py` is VERIFY-not-build.** `concept_scan` already yields `assets/*.py`
(`tools/concept_scan.py:447-449`) and `input`→baseline, `import sys`→`import-statement`,
`.read`→`file-read`, `.split`→`str-split`, `int()/str()`→`type-conversion` all resolve with zero gaps
(glm/fable verified via `detect()`). So this is a verification step (run the scan on the `.py`,
confirm no gaps), not new code. **Do NOT claim an automated banned-token check here** — that is A5.

**A5 — NEW `tools/source_policy.py` `source_policy_findings` (replaces the nonexistent "AST greps"
Sol BLOCKER 3 flagged). BOOK-SCOPED to `book2`** (return `[]` otherwise — same reason as A1). An
explicit AST checker over executable lesson rungs + every `assets/*.py` (solvers + helpers), FAILing:
- **Structural bans** (scanner-blind, repeatedly reviewer-caught in Book 2): chained comparison
  (`ast.Compare` with >1 comparator), list/str repetition (`ast.BinOp` `Mult` with a `List`/`Str`
  operand), ternary (`ast.IfExp`), `global`/`nonlocal` (`ast.Global`/`ast.Nonlocal`), `del`
  (`ast.Delete`), augmented assign (`ast.AugAssign`, e.g. `+=`), comprehensions
  (`ListComp`/`SetComp`/`DictComp`/`GeneratorExp`).
- **Import bans:** `import itertools`, `from collections import Counter` (but `from collections import
  deque` is ALLOWED — taught U10; `import sys` ALLOWED).
- **Banned methods:** `.pop`, `.join`, `.index`, `.count`, `.find` (attribute-call names).
- **Builtins:** enforce a **pinned allowlist** (a precise set, NOT an open-ended one) — a call to a
  NAME that is a Python builtin but not in the allowlist FAILs; a call to a name DEFINED in the same
  file (user helper) or imported is NOT a builtin and is exempt. **Pin the allowlist by auditing
  current Book 2** so it does not false-positive on valid existing content: it MUST include at least
  `{len, min, max, sorted, sum, abs, round}` (the free set) ∪ `{input, print, range, int, str}` (stdin
  + conversions) ∪ `{set}` (set-literal/ops constructor, used in U04/U13 — Sol MAJOR 2) ∪ `{deque}`
  (from the allowed import). The implementer derives the FINAL set empirically: run a draft over ALL
  current `book2` lesson cells, and any builtin that surfaces must be deliberately added-or-confirmed-
  banned before ship (no `...`). Everything else (`enumerate`/`zip`/`map`/`filter`/`all`/`any`/
  `reversed`/`list`/`dict`/`tuple`/…) is rejected unless the audit shows a legitimate existing use.
- **Parse failures surface as findings (glm minor):** `source_policy_findings` `ast.parse`s every
  `assets/*.py` INCLUDING non-PID helper modules; a `SyntaxError` must be reported as a FAIL (a helper
  never imported by a runnable solver is otherwise unchecked since `judge-check` never runs it).
- The SHIPPED checker contains a **precise literal allowlist with NO ellipsis**, reject-by-default
  (sol nit); the `{…}` above is the lower bound the implementer confirms/extends via the audit.
- Ship a **mutation fixture per ban** (a tiny snippet that must FAIL) AND — critically — a
  **full-current-Book-2 clean regression**: `source_policy_findings(root, "book2")` over the whole
  existing book MUST return `[]` (proves zero false-positives on shipped content before wiring it into
  `ci-local`). Register + wire into `ci-local` for book2 (book1 retro-coverage is out of scope here).

**A6 — `layout`/`ASSET_REF` existence extension.** The referenced-asset existence + py-compile check
is currently `uses_turtle`-guarded (`tools/notebooks.py:331-357`); extend the existence check to ANY
entry with an `assets/` dir so a notebook referencing a missing `assets/l2.py` FAILs `structure-check`
(compile is redundant with `judge-check` execution). Apply it in the unit, checkpoint, AND project
layout checks (not just `layout_findings`) so migrated checkpoints/projects are covered too.

**A7 — wire into `scripts/ci-local.sh`** (book2): add `judge-check` and `source-policy` after the
existing per-entry checks.

**A8 — tests:** `judge_findings` — pass; wrong-output FAIL; nonzero FAIL; timeout FAIL; **missing
expected script** FAIL for a unit (`exN`), a checkpoint (`qN`), AND a **project** (`pN`) — the
project fixture uses a **decorated `### Problem N — title *(tag)*` heading** so an over-strict
`$`-anchored regex cannot pass (fable N1); a solver with **0 or 1 case** FAIL; **missing `.in`/`.out`
counterpart** FAIL; **orphan fixture dir** FAIL; a second **untested solver** FAIL; mirror-drift FAIL
for an exercise cell AND a **project `## Problem N` cell** (glm N1); a non-`(l|ex|q|p)\d+` helper
`.py` is NOT fixture-required but a helper `SyntaxError` FAILs; **`judge_findings(root,"book1")`
returns `[]`** (book-scope).
`source_policy` — one mutation fixture per ban (each FAILs); a clean sample (passes);
**`source_policy_findings(root,"book2")` over the whole current book returns `[]`** (full-book clean
regression, Sol MAJOR 2); **`(root,"book1")` returns `[]`** (book-scope). Policy exemption — both
directions (A2). Registry inventory (`tuple(CHECKS)==CHECK_NAMES`) + missing-root/selector matrices
updated (book1-parametrized rows pass since both new checks return `[]`).

### Phase B — amend ALL binding contract references + standard

Amending only §3 leaves stale binding claims elsewhere that U08 would immediately violate (Sol MAJOR
4/5). Update every binding reference in `docs/designs/001-book2-algorithms.md`:
- **§3** — rewrite to the stdin-first subprocess-judge contract above (`.py` solvers reading stdin,
  `.in`/`.out` fixtures in `assets/`, `judge-check`, `solutions.ipynb` as no-exec display, lessons'
  executable-literal ladder rungs + no-exec stdin "Put it together" solver).
- **§4** — the unit file-set line wrongly says `solutions.ipynb` holds "`solve` functions + asserts"
  and teacher-notes has "six headings incl `## Rubric`". Correct both: solutions are the no-exec
  display + `assets/` `.py`; unit teacher-notes are the **5** `NOTES_HEADINGS` (verified against
  `tools/notebooks.py:38-45`; `## Grading` is checkpoints, `## Rubric` is projects).
- **§7 / §11** — update any remaining `solve(data)`/inline-assert binding language. Also fix §4's
  **checkpoint** bullet, which says `## Problem N` while the tooling enforces `## Question N` (fable
  N5 — correct it while rewriting §4).
- **`book2/syllabus.md:14`** — independently declares the old contract binding; rewrite to the new
  contract. The staged-transition note should also acknowledge `book2/syllabus.md:28`'s U01 row still
  naming "the `solve()` contract" (fine during the transition; reconcile as entries migrate — fable
  N5).
- Add a short **staged-transition note** (old-model entries keep `solve()`+asserts until migrated;
  the per-entry `assets/` switch is the boundary) so the half-migrated book is internally consistent.
- Record the **Book-2 ladder/completeness standard** (this plan's section) as the reusable rollout
  reference. (design-001 + syllabus are content/design docs, not governance files — amendable here.)

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
- `solutions.ipynb`: all-`no-exec` display mirroring each `.py` (each `## Exercise N` gets a CODE
  cell — `solutions_structure_findings` requires it) + short explanation; source must match the `.py`
  (the A1 mirror check enforces this).
- `teacher-notes.md`: the 5 unit `NOTES_HEADINGS`; pacing re-synced to the ladders (U08 stays 2
  lessons); per-exercise Big-O; the concept→core-practice matrix; a note that the `[x]*n`
  list-repetition ban means pre-sized 2D prefix arrays are built with append-loops (so the verbose 2D
  rungs don't surprise — fable pedagogy caution).
- `manifest.yaml`: add nothing to concepts (prefix-sum unchanged); `lessons: 2` unchanged.

### Phase D — Verification (named verification phase)

`scripts/ci-local.sh` ALL GREEN including the new checks: registry/lint, unit tests (incl. the new
`judge_findings` + `source_policy` tests + the policy-exemption both-direction tests), `exec-lessons`
(U08 literal-data rungs run clean; stdin solver cells `no-exec`), `judge-check` (every U08
`assets/*.py` passes ≥2 fixtures; expected-script set complete; mirror matches), `source-policy` (no
banned construct in any rung or `.py`), `concept-scan` (closure over lesson + `.py`; stdin constructs
resolve), `coverage`/`prereq`, manifest==map, structure/hygiene/noexec/cell-lint, Book-1 PDF build
(book1-only — unaffected), pre-merge guard. The 13 un-migrated units + 4 checkpoints + capstone stay
GREEN on the OLD path (no `assets/` ⇒ `exec-solutions` + asserts unchanged). **Closure + completeness
audit (primary content-review duty):** each ladder one-increment with a focused Notice; full solver
framed "Put it together"; fixtures non-vacuous + mutation-killing (decisive-last/boundary case per
problem); banned constructs now MECHANICALLY enforced by `source-policy` (reviewers still sanity-check);
stdin solvers correct on the stated samples; lessons project-first; `## Pacing` == lessons.

## Out of scope

- U06 greedy (plan 037, the paradigm pilot) and the remaining 12 units / 4 checkpoints / capstone
  (rollout plans after both pilots merge). Any Book-1 change. Governance files.
- **Verification-phase note:** ships a reworked unit WITH a named verification phase (Phase D) plus
  new tooling covered by new `tools/` unit tests.

## Post-Execution Report

_(filled at Phase D)_

## Plan Review

### Round 1 (HEAD 683f1a7) — [self] APPROVE WITH NITS

- **Tooling soundness ✓** — `judge-check` mirrors the proven `turtle_findings` subprocess model;
  stdin-pipe + token-compare is standard. Named verification Phase D present. design-001 is amendable
  (not governance).
- **CRITICAL implementation clarification (the #1 correctness-continuity risk):** retiring the
  `solve()`/assert path must be **CONDITIONAL and per-entry**, NOT global. The switch = "entry has an
  `assets/` dir containing ≥1 `.py`" ⇒ NEW model (judge-check verifies it; `exec-solutions` and
  `_solution_policy_findings` SKIP it; its `solutions.ipynb` may be all-`no-exec`). An entry WITHOUT
  `assets/` ⇒ OLD model (keep `exec-solutions` + ≥3-asserts exactly as today). This is essential
  because plan 036 migrates ONLY U08 — the other 13 units + 4 checkpoints + capstone still carry
  `solve()`+asserts and MUST stay verified by `exec-solutions` throughout the rollout. `exec-solutions`
  must not execute a new-model entry's `no-exec` stdin display cells (it has no `no-exec` filter), so
  it must skip new-model entries entirely, not just their no-exec cells.
- **concept-scan ✓ with work** — extending `detect()`/closure to `assets/*.py` and allowing
  `input`/`sys`/`sys.stdin.read` (add `input` to the recognized/allowed set; `import sys` exempt like
  the precedented wrapper) while keeping the banned-token AST-greps (ternary/comprehension/`+=`/
  chained-compare/list-repetition/`.pop`/`.join`) firing on the `.py` — real but bounded tooling.
- **cell-lint ✓ for the pilot** — U08 is a `kind:unit`, whose `no-exec` cells are cell-lint-exempt;
  self-contained stdin display cells define all their names (no F821). Flag for later checkpoint/
  project batches where the exemption is unit-only.
- **Nits / watch-items:** (a) make the per-entry new-vs-old switch explicit in Phase A (above);
  (b) `judge-check` timeout value + a fixture-size guidance (keep correct solvers well under it);
  (c) confirm `structure-check` tolerates an `assets/` dir on a book2 unit (book1 turtle units prove
  it does); (d) reviewers may prefer splitting infra (Phase A/B) from content (Phase C) — I coupled
  them so U08 proves the harness end-to-end, with `tools/` unit tests giving infra independent
  coverage; open to splitting if consensus wants it.

### Round 1 (HEAD 683f1a7) — [glm] APPROVE WITH NITS · [fable] APPROVE WITH NITS · [sol] REJECT

All three confirmed the direction is sound (no tool hard-codes `solve(`; `judge-check` mirrors the
`turtle_findings` precedent; `concept-scan` already scans `assets/*.py` and stdin resolves with zero
gaps; named Phase D present; no split needed). Findings (blockers + must-fixes), all `[FIXED]` in the
revised plan:

1. `[FIXED]` **[sol B1] subprocess call invalid** — `stdin=<bytes>`+`text=True` is wrong. → Phase A1
   now uses `subprocess.run([py, script], input=<case>.in.read_text(), text=True, …)`.
2. `[FIXED]` **[sol B2 / glm #3 / fable] judge-check fail-open** — "1 `.py` with 2 fixtures/entry" let
   other solvers ship unverified. → A1 requires EVERY `.py` to have ≥2 matched pairs, derives the
   expected `exN`/`qN`/`lN` script set from headings (missing script FAILs), and rejects orphan
   fixtures; A8 adds the one-fault tests.
3. `[FIXED]` **[sol B3 / glm #5 / fable] banned-construct check didn't exist** — the plan claimed "AST
   greps" that `detect()` does not perform. → Built as the real **A5 `source-policy` AST checker**
   (chained-compare, `[x]*n`, ternary, `global`/`nonlocal`, `del`, `+=`, comprehensions,
   itertools/Counter, banned methods, non-allowed builtins) with a mutation fixture per ban; Phase D
   reworded from "greps" to this mechanical check.
4. `[FIXED]` **[sol M4] doc amendment incomplete** — §3 alone left old-contract bindings in §4/§7/§11
   and `book2/syllabus.md:14`. → Phase B now amends all of them + adds a staged-transition note.
5. `[FIXED]` **[sol M5] teacher-notes heading conflict** — verified tooling requires 5 for units
   (`NOTES_HEADINGS`), so U08's 5 is correct; design §4's "six incl `## Rubric`" is STALE → amended in
   Phase B (and its stale "solutions = solve+asserts" line).
6. `[FIXED]` **[glm #1 / fable N1] `_solution_policy_findings` also bans `input()`** (not just
   asserts) — must waive the WHOLE policy for new-model entries. → A2 waives the entire policy + has
   `exec-solutions` skip new-model entries; both-direction tests added; scoped book2+assets-only.
7. `[FIXED]` **[glm #2 / fable N3] `noexec-check` misses `sys.stdin`** — my "already enforced" claim
   was false. → A3 extends `INTERACTIVE` to match `sys.stdin`.
8. `[FIXED]` **[glm #6 / fable N4] `ASSET_REF` existence check is turtle-only** — → A6 extends it to
   any entry with an `assets/` dir.
9. `[FIXED]` **[fable N5 / sol NIT] registration** — A1: `judge-check` iterates `content_dirs`, NOT
   `UNIT_ONLY_CHECKS`; registry-inventory + selector tests updated.
10. `[FIXED]` **[fable N2 / self] mirror drift** — A1 adds a display-cell-vs-`.py` mirror check
    (kills the drift nit class across the whole rollout).
11. `[FIXED]` **[glm #8] solutions mirror cells must be CODE cells** (`solutions_structure_findings`)
    and **[fable pedagogy]** `[x]*n` ban → 2D prefix via append-loops — both noted in Phase C.
12. `[FIXED]` **[glm #4] concept-scan over `.py` already implemented** — A4 reworded to verify-not-
    build.

### Round 2 (HEAD cb7c1e8) — [glm] REJECT · [sol] REJECT · [fable] (rate-limited, pending)

Round-1 fixes all verified closed (subprocess `input=`, per-script ≥2-fixtures, doc list, 5-heading
unit contract). Two new blocking findings, both `[FIXED]`; [fable]'s run hit a fable-5 session limit
(no verdict — re-dispatched round 3):

1. `[FIXED]` **[glm blocker] `judge-check`/`source-policy` not book-scoped** — as written they'd run
   over Book-1's 22 turtle `assets/*.py` (no `fake_turtle` stub → fail) and break the
   `CHECK_NAMES`-parametrized Book-1 suites. → A1 + A5 now return `[]` for any `book != "book2"`; A8
   adds `(root,"book1")==[]` tests; registry/selector matrices pass.
2. `[FIXED]` **[sol blocker] project solver discovery fails open** — derivation covered only
   `## Exercise`/`## Question`; the capstone uses `### Problem N`, so a migrated capstone missing
   `p8.py` would pass. → A1 now derives `pN.py` from `### Problem N` (projects), `exN`/`qN` for
   units/checkpoints, with a missing-project-solver test (A8).
3. `[FIXED]` **[sol major] `source-policy` builtin policy unpinned + would false-positive** — it
   omitted `set`, which U04/U13 validly call. → A5 now pins the allowlist (incl. `set`, `deque`,
   stdin/conversion builtins), distinguishes user-defined/imported calls from builtins, and A8
   mandates a **full-current-Book-2 clean regression** (`source_policy_findings(root,"book2")==[]`)
   before wiring into ci-local.
4. `[FIXED]` **[glm nits]** mirror-check target pinned to the `solutions.ipynb` exercise cell /
   lesson `lN` display cell (not partial ladder rungs); helper `.py` (non-PID) allowed (source-policy-
   scanned, not fixture-required); A6 existence extension applied to checkpoint/project layout too.

### Round 3 (HEAD 06f8052) — [sol] APPROVE WITH NITS · [glm] APPROVE WITH NITS · [fable] APPROVE WITH NITS

All round-2 blockers verified resolved. [glm] and [fable] independently AUDITED the real book2 tree:
the only builtins used are `{abs,int,len,max,min,print,range,set,sorted,str,sum}` (all in the pinned
allowlist), a draft `source-policy` over all book2 returns **0** hits (full-book clean regression
achievable), `.pop` ban ≠ U10's `.popleft`, book-scoping keeps every book1 suite green, and PID
headings match reality (`## Question N` / `### Problem N`). Non-blocking round-3 nits — all `[FIXED]`:

- `[FIXED]` **[fable N1] decorated headings** — all PID regexes end-unanchored (house
  `EXERCISE_HEADING` pattern); A8 project fixture uses a decorated `### Problem N — title *(tag)*`.
- `[FIXED]` **[fable N2 / glm N2] reserved-stem + lesson PID** — any `(l|ex|q|p)\d+` stem is always a
  solver (never a silent helper); lesson `lN` derived from `manifest.lessons`/`## Lesson N`, not
  circular references.
- `[FIXED]` **[fable N3] mirror "modulo whitespace"** defined (per-line trailing strip + trailing
  blank-line strip).
- `[FIXED]` **[glm N1] project mirror target** — `pN` mirrors the `## Problem N` cell in the project
  `solutions.ipynb` (which `project_solutions_findings` doesn't enforce); A8 adds the test.
- `[FIXED]` **[fable N4] turtle-check footgun** — `turtle_findings` skips scripts with no
  `import turtle` so book2 stdin solvers aren't run under the stub.
- `[FIXED]` **[glm N3] book-scope no-op** documented at the return site (not fail-closed-on-missing-
  root). **[glm minor]** source-policy surfaces helper `SyntaxError` as a FAIL.
- `[FIXED]` **[fable N5] stale prose** — Phase B also fixes design §4's `## Problem N`→`## Question N`
  and notes `syllabus.md:28`. **[fable N6]** empty output = `stdout.strip()==""`. **[sol]** shipped
  allowlist is a precise literal set (no ellipsis).

**CONSENSUS — plan-review gate CLOSED:** [self] APPROVE WITH NITS · [sol] APPROVE WITH NITS · [glm]
APPROVE WITH NITS · [fable] APPROVE WITH NITS. No open blockers. Cleared for implementation.

## Content Review

_(4-way content-review gate — consensus before PR)_

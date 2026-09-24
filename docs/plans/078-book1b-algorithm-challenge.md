# Plan 078 — Book 1b Algorithm Challenge (end-of-book capstone)

**Goal:** Ship `book1b/projects/project-01-algorithm-challenge` — a non-themed, integrative
mini-CP problem set — and take Book 1b **out of `buildout`**, activating the full
practice-coverage anchor. This is the FINAL plan for Book 1b.

**Spec:** `docs/designs/005-book1b-concept-first.md` §3 (the single project entry), §4 (registry /
buildout removal), §6 (coverage + the `practice_findings` anchor).

## Global constraints (verbatim)

- Book 1b is `prereq_policy: fastforward`, but **the project keeps the STRICT per-entry allowed set**
  (`concept_scan.py:933-940` — the fastforward whole-catalog union is `kind == "unit"` only). So every
  scanner-DETECTED concept in the project's cells MUST appear in the entry's `requires ∪ practices`,
  exactly like a checkpoint.
- **`project` structure is CI-enforced** (`structure-check` runs for Book 1b; `structure_findings` is not
  book-gated): `PROJECT_REQUIRED_FILES` = `manifest.yaml`, `brief.ipynb`, `solutions.ipynb`,
  `teacher-notes.md`. `brief.ipynb` needs **3–6 sequential `## Milestone N` headings**, a
  `## Make it yours` heading, and a `## Requirements checklist` heading, and NO `# … Solution` heading
  (`project_milestone_findings`, notebooks.py:779-816). `teacher-notes.md` needs
  `PROJECT_NOTES_HEADINGS` = the standard notes set **+ `## Rubric`** (NOT `## Grading` — that is the
  checkpoint heading), notebooks.py:50.
- **Manifest schema:** `blueprint_version: 1` with `concepts` = EXACTLY `{introduces, requires,
  practices}` (strict-equality `manifest_findings`, notebooks.py:39-42/462). **Do NOT add `auxiliary`.**
- Tool-subset pins (unchanged from 075–077): string methods ⊆ {upper,lower,strip,replace}; list methods
  ⊆ {append,sort} (**`.copy()` is NOT allowed** — copy a list via `sorted(x)` or a build loop); dict
  methods ⊆ {items,keys,values,get}; file methods ⊆ {read,readlines,readline,write,close}; builtins ⊆
  {len,min,max,sum,sorted,abs,round} with NO `key=`.
- **Dict iteration:** iterate with the single-variable form `for key in d:` + `d[key]`/`.get(...)`.
  **Do NOT use the two-variable `for k, v in d.items()` form** — for-target unpacking would trip the
  tier-C tuple-assignment ban (Plans 076/077 carved `.items()` out, but this plan sidesteps the question
  entirely by prescribing the single-variable idiom). Ordinary `a, b = ...` multiple assignment is banned.
- **No string `+` concatenation** (`visit_BinOp` detects `str + …` as scanner concept `string-concat`,
  which is NOT in the contract): write file lines with f-strings, e.g. `f.write(f"{word}\n")`.
  **No `in` membership tests** (`word in counts`) — tally/lookups use `.get`; membership would detect the
  `in-operator` concept, also not in the contract.
- Content-gate/AST-audit bans (NOT scanner-flagged in Book 1b schema-v1, so reviewer + Phase-E audit
  enforced): NO comprehensions, tuple/multiple assignment, step slices, `ord`/`chr`, `import math`,
  inheritance, dunder methods beyond `__init__`, decorators.
- File problems are SELF-CONTAINED (write the scratch file before reading it) and use git-ignored scratch
  names. Add a `book1b/projects/project-01-algorithm-challenge/*.txt` glob to `.gitignore`.
- Student-facing `brief.ipynb` is solution-free with NO executed outputs and unique cell ids; no
  `input()`. `solutions.ipynb` runs top-to-bottom clean, function/class form, **≥3 distinct asserted
  cases per problem** (`_solution_policy_findings` needs ≥3 assert cells overall; the per-problem rigor is
  a content-gate rule). No randomness (no seeding needed).
- **Value-distinctness (STRICT — audit before authoring):** every worked-sample / fixture input must be
  distinct from each other AND from any lesson/exercise/checkpoint the student has already seen. Known
  collisions to AVOID: `count_primes(10/20)` and the `2..20` prime count (cp03 / U05); the
  `["red","blue","red"]` word list (cp04); U09's palindrome exercise; U04's digit-sum drill; U11's
  `word_counts`. Codex MUST grep existing Book 1b notebooks for each chosen fixture before finalizing.

## Scope

1. **Coverage-map entry** `project-01-algorithm-challenge` (kind `project`, LAST entry; `introduces: []`).
2. **Project directory**: `manifest.yaml`, `brief.ipynb` (11 problems in 4 milestones, solution-free),
   `solutions.ipynb` (worked, asserted), `teacher-notes.md`.
3. **Syllabus**: add the project as a shipped-table row; update the roadmap prose line.
4. **Buildout removal**: drop `buildout: true` from the `book1b` entry in `books.yaml`; update
   `tests/test_books.py:23` to assert the finished state; sweep the now-stale "in buildout" comments at
   `tests/test_books.py:20`, `scripts/ci-local.sh:61`, and the `book1b/curriculum/coverage-map.yaml:2-6`
   header ("Book 1b is in buildout…").
5. **`.gitignore`**: add the project scratch-`.txt` glob.

## The problem set (11 problems in 4 milestones; 9 core + 2 Challenge)

Non-themed, algorithmic, integrative. Each is function/class form with a precise **Specification** +
worked sample (input→exact output). Inputs are distinct across problems and audited against shipped
Book 1b content. The 2 Challenge problems (P4, P5) are cell-tagged `stretch` (rendered "Challenge") in
both `brief.ipynb` and `solutions.ipynb`.

**Milestone 1 — Number algorithms**
1. **nth_prime(k)** — the k-th prime (1-indexed): a `while` counter over candidates; test each candidate
    with an inner `for d in range(2, candidate):` loop that `break`s on a found divisor (2 is prime by the
    empty-range base case). `nth_prime(1)`→2, `nth_prime(5)`→11, `nth_prime(10)`→29. (nested-loops,
    break-statement, `%`, count-by-condition.)
2. **reverse_digits(n)** — reverse the digits of a non-negative int arithmetically
    (`rev = rev * 10 + n % 10`; `n = n // 10`). `reverse_digits(1234)`→4321, `reverse_digits(1200)`→21,
    `reverse_digits(0)`→0. (while, `//`/`%`, accumulator.)

**Milestone 2 — Lists & searching**
3. **top_three(scores)** — the three largest values, descending, as a list. Sort with `sorted(scores)`
    (ascending), then read the last three by index in reverse order (`s[n-1], s[n-2], s[n-3]`; NO
    `.copy()`, NO `[::-1]`). ≥3 values guaranteed. `top_three([4,9,1,7,3])`→[9,7,4],
    `top_three([5,5,2,8])`→[8,5,5], `top_three([10,20,30])`→[30,20,10]. (list-sort, list-index.)
4. **[Challenge] merge_sorted(a, b)** — merge two ascending lists into one ascending list with a
    two-index walk (`while i < len(a) and j < len(b)`, then drain each remainder). `merge_sorted([1,4,6],
    [2,3,5])`→[1,2,3,4,5,6], `merge_sorted([],[2,9])`→[2,9], `merge_sorted([1,2],[])`→[1,2].
    (logical-ops, list-index, list-append.)
5. **[Challenge] binary_search(nums, target)** — the index of `target` in a **sorted list of distinct
    values**, else `-1` (`while lo <= hi`, `mid = (lo + hi) // 2`). `binary_search([1,3,5,7,9],7)`→3,
    `binary_search([1,3,5,7,9],4)`→-1, `binary_search([2,4,6,8,10,12],2)`→0. (while, `//`, comparison.)

**Milestone 3 — Text, tallies & files**
6. **count_substring(text, part)** — count OVERLAPPING occurrences of `part` in `text` by walking every
    start index `for i in range(len(text) - len(part) + 1):` and comparing the slice `text[i:i+len(part)]`
    with `part`. `count_substring("cocoon","co")`→2, `count_substring("aaaa","aa")`→3,
    `count_substring("mississippi","ss")`→2. (string-slice, linear-search, count-by-condition;
    case-sensitive — no `.lower()`.)
7. **word_counts_from_file(path)** — SELF-CONTAINED: write one word per line, then read and tally into a
    dict with `.get`, iterating lines with `for line in f:` + `.strip()`. Fresh fixtures (NOT
    red/blue/red), e.g. `["fern","moss","fern","ivy","moss","fern"]`→`{"fern":3,"moss":2,"ivy":1}` (+ two
    more distinct fixtures). (file-read/write, with, dict-access `.get`, string-methods.)
8. **most_common_word(path)** — SELF-CONTAINED: build the tally, then return the single word with the
    highest count by iterating `for key in counts:` and tracking the best (find-extreme). Distinct
    fixtures from #7, single clear winner each. `most_common_word` over a file written from
    `["kite","yoyo","kite","kite","yoyo"]`→`"kite"` (+ two more distinct single-winner fixtures).
    (dict-loop single-var, find-extreme, comparison.)
9. **group_by_parity(nums)** — return `{"even": [...], "odd": [...]}` preserving order (`n % 2`, append
    into the right list). `group_by_parity([1,2,3,4])`→`{"even":[2,4],"odd":[1,3]}`,
    `group_by_parity([0,7,10])`→`{"even":[0,10],"odd":[7]}` (`0`→even),
    `group_by_parity([])`→`{"even":[],"odd":[]}`. (dict-literal with list values, `%`.)

**Milestone 4 — Objects & pipelines**
10. **class RunningTally** — `__init__(self)` starts an empty list attribute; `add(self, value)` appends
    and returns **the number of values stored so far**; `total(self)` returns `sum`; `highest(self)`
    returns `max`; `describe(self)` returns the f-string `f"{count} values, total {total}, highest {highest}"`.
    Worked sample: `t = RunningTally()`; `t.add(5)`→1, `t.add(9)`→2, `t.add(0)`→3; then `t.total()`→14,
    `t.highest()`→9, `t.describe()`→`"3 values, total 14, highest 9"`. Asserts construct-then-check across
    ≥3 states, always calling `add` at least once before `highest`/`describe` (`max([])` raises).
    (class-def/init/attributes/methods, list-append, builtins, f-string.)
11. **running_totals_to_file(in_path, out_path)** — SELF-CONTAINED: read integers (one per line) from
    `in_path`, write their running totals to `out_path` (one f-string line each), and return the list of
    running totals. `[5,3,2]`→writes `"5\n8\n10\n"`, returns `[5,8,10]` (+ two more fixtures).
    (file-read/write, with, running-total/accumulator, transform-each.)

## Coverage-map entry (contract)

Append AFTER `checkpoint-05-files-and-objects` (must be the last entry):

```yaml
- id: project-01-algorithm-challenge
  kind: project
  title: "Project 1 — Algorithm Challenge"
  lessons: 2
  introduces: []
  requires: [def-function, parameters, return-value, for-loop, while-loop, nested-loops, if-statement,
             elif-else, comparison, boolean, logical-ops, arithmetic, list-index, list-sort, dict-access,
             file-read, file-write, with-statement, class-def, init-method, attributes, methods]
  practices: [def-function, parameters, return-value, variable, for-loop, while-loop, nested-loops,
              break-statement, range-function, if-statement, elif-else, comparison, boolean, logical-ops,
              arithmetic, int-type, list-literal, list-index, list-append, list-loop, list-sort,
              string-index, string-slice, string-methods, string-literal, dict-literal, dict-access,
              dict-loop, file-read, file-write, with-statement, class-def, init-method, attributes,
              methods, type-conversion, f-string, accumulator, running-total, count-by-condition,
              find-extreme, linear-search, transform-each, builtin-functions]
```

`manifest.yaml` mirrors this entry's `introduces`/`requires`/`practices` exactly, with
`blueprint_version: 1`, `provenance: original`, `lessons: 2`, and NO `auxiliary` key.
**Phase E reconciles the `practices` set to the ACTUAL scan** (add/drop so it exactly covers every
detected concept and carries no untaught method). The anchor does not need the project's own practices,
but the strict scan requires the tag set to cover every detected concept.

## Tooling pins (enforcement tiers)

- (A) **CI-enforced by concept-scan** (must be tagged if used): method subsets + builtins set above;
  `class-def`/`init-method`/`attributes`/`methods`/`with-statement`; slices → `string-slice`;
  `nested-loops`; `break-statement`; `logical-ops` (`and`/`or`); `list-sort` (`sorted`/`.sort`);
  **`accumulator`** (scanner-detected, `concept_scan.py:248` — NOT manual).
- (B) MANUAL_ONLY (`never_flag`; declaration + reviewer-verified): the OTHER technique concepts
  (`running-total`/`count-by-condition`/`find-extreme`/`linear-search`/`transform-each`), plus
  `list-index`/`list-loop`/`dict-access`/`dict-loop`/`string-index`/`int-type`/`variable`/
  `type-conversion`.
- (C) NOT scanner-flagged but BANNED (Phase-E static AST/grep audit): comprehensions, tuple/multiple
  assignment, step slices, `ord`/`chr`, `import math`, inheritance, dunders beyond `__init__`, decorators.
- Project scan is STRICT (allowed = introduces∪requires∪practices∪baseline; NO fastforward union).

## Phases

- **Phase A — Contracts.** Coverage-map entry + `manifest.yaml` (this CREATES the project directory) +
  `.gitignore` glob + syllabus row/prose. Gate: `coverage-check` + `prereq-check` GREEN. **NOTE:** because
  the directory now exists, `practice_findings` (the coverage anchor) is ACTIVE from this phase (it keys on
  directory existence, not on `buildout`); it is GREEN because all 62 concepts are already practiced by
  U01–U13 + cp01–cp05 (`known ⊆ pre_capstone`, pre-verified). Do NOT run full `structure-check` here
  (brief/solutions/teacher-notes not yet authored).
- **Phase B — Brief (Codex, statements).** `brief.ipynb`: 4 `## Milestone N` headings, 11 `### Problem N`
  problems, `## Make it yours`, `## Requirements checklist`; solution-free, unique ids, no executed
  outputs, no `input()`; P4/P5 cell-tagged `stretch`. Codex greps shipped notebooks to confirm every
  fixture is fresh.
- **Phase C — Solutions (SEPARATE fresh Codex).** `solutions.ipynb`: function/class form, ≥3 distinct
  asserted cases per problem, self-contained file problems, within all tool subsets and the dict
  single-var idiom; P4/P5 tagged `stretch`.
- **Phase D — Teacher-notes (inline).** `teacher-notes.md` with `PROJECT_NOTES_HEADINGS` (Goals / Pacing /
  Common mistakes / Discussion prompts / Differentiation / **Rubric**) + a per-problem value inventory
  that NAMES the scratch files used by P7/P8/P11.
- **Phase E — Buildout removal + VERIFICATION.** Drop `buildout: true` from `books.yaml`; update
  `tests/test_books.py:23` → `assert books[1].get("buildout", False) is False`; sweep the stale
  "in buildout" comments (`tests/test_books.py:20`, `scripts/ci-local.sh:61`). Reconcile the project
  `practices` to the actual scan. Run `scripts/ci-local.sh` — the now-active strict
  `introduction_findings` (all 62 introduced) + `lesson_budget` lower bound (`[30,60]`; pre-project total
  41.5 + project 2 = 43.5) + `practice_findings` anchor must all be GREEN, plus the full project
  structure/hygiene/scan/exec.
  Static AST/grep audit for the tier-C bans. `pytest tests/` GREEN. Post-execution report.

## Value plan

Every worked sample above uses distinct inputs, audited against shipped Book 1b notebooks (avoid the known
collisions listed under Global constraints). Solutions assert each problem's listed cases plus, where
noted, two additional distinct fixtures; file problems (#7/#8/#11) write distinct scratch files per case.
No two problems share an input tuple. No randomness (no seeding needed).

## Out of scope

- No new concepts (`introduces: []`); no changes to `concepts.yaml` (the catalog stays content-identical
  to Book 1 — a `variant_of` invariant).
- No governance-file edits. `books.yaml` and `tests/test_books.py` are registry/test files, not
  governance files (per AGENTS.md the governance set is AGENTS.md / development-workflow.md /
  content-review-gate.md / architecture/decisions.md).
- No `concept_minimum` change (design §4 removes only the `buildout` flag on completion).
- **Verification phase present** (Phase E) — this plan ships a project entry, so the named verification
  phase is required and included.

## Plan Review

4-way plan-review gate. Verdicts tagged `[self]`/`[sol]`/`[glm]`/`[fable]`.

### Round 1 — verdicts (HEAD a0d7fee)

- `[self]` APPROVE WITH NITS — dict-iteration idiom (S1) + stretch-tagging (S2).
- `[glm]` APPROVE WITH NITS — anchor + buildout-removal verified PASS computationally; missing
  `nested-loops`/`list-sort` practices; Phase-A anchor wording; pin problem 3 to `sorted()`; stale comments.
- `[sol]` **REJECT** — invalid v1 manifest (`auxiliary`); missing project structure (milestones/Rubric);
  strict-scan omits `nested-loops`/`list-sort`/`logical-ops` and mis-tiers `accumulator`; value-dup
  (count_primes vs cp03, red/blue/red vs cp04); dict `.items()` unpacking ambiguity.
- `[fable]` **REJECT** — solved all 11 within pins (all correct); count_primes verbatim cp03 dup; project
  structure omissions (CI-fatal); v1 manifest `auxiliary`; strict-scan concept gaps; tiering + naming nits.

Consensus: **NOT reached** (2 REJECT). All findings converge; folded below.

### Round 1 — fold (this rewrite)

- `[FIXED]` **count_primes verbatim cp03 dup** → replaced with `nth_prime(k)` (fresh values) (`[fable]`/`[sol]`).
- `[FIXED]` **project structure** → 4 `## Milestone N` + 11 `### Problem N` + `## Make it yours` +
  `## Requirements checklist`; teacher-notes `## Rubric` (not Grading) (`[fable]`/`[sol]`).
- `[FIXED]` **manifest schema** → `blueprint_version: 1`, NO `auxiliary` (`[fable]`/`[sol]`).
- `[FIXED]` **strict-scan coverage** → added `nested-loops`/`list-sort`/`logical-ops`/`break-statement` to
  the contract; corrected tier note: `accumulator` is scanner-DETECTED (tier A) (`[sol]`/`[glm]`/`[fable]`).
- `[FIXED]` **more value-dups** → `word_counts` fixture `red/blue/red` (cp04) replaced with fern/moss/ivy;
  `is_palindrome` (U09 dup) → `count_substring`; `digit_sum` (U04 dup) → `reverse_digits`; `word_counts`
  → `word_counts_from_file` (U11 name collision); Codex greps every fixture before authoring (`[sol]`/`[fable]`).
- `[FIXED]` **dict `.items()` unpacking** → prescribe single-var `for key in d:` + `d[key]`/`.get`; state
  the tuple-assignment ban explicitly (`[self]`/`[sol]`/`[fable]`).
- `[FIXED]` **Phase-A anchor wording** → anchor activates on directory existence in Phase A (not dormant /
  not buildout-gated); green because coverage already complete (`[glm]`/`[sol]`).
- `[FIXED]` **problem 3 `.copy()` trap** → pinned to `sorted(scores)` (`.copy()` not in the list pin) (`[glm]`).
- `[FIXED]` **Challenge tiering** → P4 `merge_sorted` + P5 `binary_search` are the two Challenges; #10/#11
  core (`[fable]`/`[glm]`); P4/P5 cell-tagged `stretch` (`[self]` S2).
- `[FIXED]` **binary_search / RunningTally specs** → distinct sorted values; ≥1 `add` before
  `highest`/`describe`; `add` returns "number of values stored so far" (`[fable]`).
- `[FIXED]` **stale buildout comments** swept in Phase E (`[fable]`/`[glm]`/`[sol]`).

### Round 2 — verdicts (HEAD 6334ec1)

- `[self]` APPROVE — S1/S2 folded; rewrite addresses every converging r1 finding.
- `[glm]` APPROVE WITH NITS — all r1 nits folded + re-verified computationally (anchor green,
  buildout-removal green, all 22 `requires` introduced before the project, manifest consistent). New nits:
  Phase-E arithmetic typo (`41.5+2=43.5`), coverage-map header also needs the sweep. **Both folded.**
- `[fable]` APPROVE WITH NITS — re-solved all 11 within pins (outputs verified), fixture-collision grep
  0 hits for the new fixtures, all r1 blockers confirmed resolved. New nits: `"banana"` is a shipped U09
  input (→ `"cocoon"`); `string-concat`/`in-operator` are scanner-detected (pin f-string writes + ban
  `in`); name the parity fixtures; specify `nth_prime` loop bound. **All folded.**
- `[sol]` **REJECT** — 4 of 5 r1 blockers RESOLVED; the 5th (value-distinctness) still flagged `"banana"`
  (U09) — **now fixed to `"cocoon"`**. New `[OPEN]`: P8/P10 lacked concrete worked samples — **now added**
  (`most_common_word(...)`→"kite"; `RunningTally.describe()`→"3 values, total 14, highest 9"). Both NITs
  (arithmetic, coverage-map header) already folded.

Consensus: **NOT reached** (1 REJECT). All findings folded (this commit); round 3 confirms `[sol]`.

### Round 2 — fold

- `[FIXED]` `"banana"` (U09 collision) → `"cocoon"` in `count_substring` (`[fable]`/`[sol]`).
- `[FIXED]` P8/P10 concrete worked samples added (`[sol]` `[OPEN]`).
- `[FIXED]` pins: no string-`+` concat (f-string writes), no `in` membership (scanner-detected concepts
  kept out of the contract) (`[fable]`).
- `[FIXED]` `nth_prime` inner-loop bound (`for d in range(2, candidate)`); named `group_by_parity`
  fixtures (`[fable]`).
- `[FIXED]` Phase-E arithmetic (`41.5+2=43.5`); coverage-map header added to the stale-comment sweep
  (`[glm]`/`[sol]`).

### Round 3 — verdicts (HEAD a7ec976) — CONSENSUS

- `[self]` APPROVE.
- `[fable]` APPROVE — all new samples solve-verified (`cocoon`/`kite`/`yoyo` grep 0 hits; `RunningTally`
  14/9/3; parity + `nth_prime` confirmed); no new issues.
- `[sol]` APPROVE — both r2 items RESOLVED (value-distinctness `cocoon`; P8/P10 worked samples); no new blocker.
- `[glm]` — round-2 APPROVE WITH NITS carried forward; all its nits folded, its concerns structural and
  unaffected by the r2 fixture/sample additions.

**Consensus: REACHED** — all four APPROVE / APPROVE-WITH-NITS, no open blockers. Plan-review gate PASSED;
cleared for implementation.

## Content Review

4-way content-review gate. Findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`; all `[OPEN]` resolve before merge.

### Round 1 — verdicts (HEAD 4fcf8ec)

- `[self]` APPROVE — structure/concept-scan/ci-local/pytest/AST-audit green; brief↔solutions consistent.
- `[fable]` APPROVE WITH NITS — executed solutions (all asserts pass), blind-solved all 11, value-distinctness
  grep 0 hits, full tool-pin/tier-C AST audit clean. Nits: P7/P8/P11 spec read/write wording; P10 f-string
  method-name note; P3 idiom hint; solutions P4/P5 headings.
- `[glm]` APPROVE WITH NITS — anchor+buildout green; **manifest honesty verified** (33 detected concepts all
  in-contract; 11 manual techniques all genuine; no over-claim). Nits: post-exec arithmetic typo
  (45.5→43.5); same P7/P8/P11 wording.
- `[sol]` **REJECT** — 2 Must-Fix (all blind solves otherwise correct; concept-scan/structure/coverage/AST
  PASS): (1) P7/P8/P11 specs describe a write-then-read *function* but the solutions' functions only read
  (self-containedness is at the CELL level); (2) P4's `[1,2]` fixture collides with U10 `keep_approved` and
  repeats within P4.

Consensus: **NOT reached** (1 REJECT). All findings folded (this commit); round 2 confirms `[sol]`.

### Round 1 — fold

- `[FIXED]` **P7/P8/P11 self-containedness** (`[sol]` MF1 / `[fable]` / `[glm]`): reworded the specs so the
  FUNCTION only reads (P11 reads in / writes out) and the CELL does the fixture setup; updated the
  Requirements checklist to state cell-level self-containedness. Matches the U12 convention + the solutions.
- `[FIXED]` **P4 `[1,2]` collision** (`[sol]` MF2): brief sample `merge_sorted([1,2],[])`→`[3,8,9],[]`; solution
  fixtures → `[3,8,9]+[]` and `[2,6,6]+[6,10]` (all grep 0 hits); teacher-notes value plan updated.
- `[FIXED]` post-exec arithmetic typo 45.5→43.5 (`[glm]`).
- `[FIXED]` P10 f-string method-call note added to teacher-notes Common mistakes (`[fable]`).
- `[FIXED]` P3 idiom hint (`ordered[len(ordered)-1]`) added to the brief spec (`[fable]`).
- `[FIXED]` solutions P4/P5 headings now read "— Challenge" (`[fable]`).

ci-local: ALL GREEN after fold.

### Round 2 — verdicts (HEAD 433e748)

- `[self]` APPROVE — both `[sol]` Must-Fix folded; ci-local GREEN.
- `[fable]` APPROVE — P4 fixture swap executes clean (hand-traced `[2,6,6]+[6,10]=[2,6,6,6,10]`, grep 0
  collisions); all r1 nits confirmed folded; full book1b CI slice PASS; no regressions.
- `[sol]` **REJECT** — MF2 (P4) RESOLVED; MF1 residual: the reworded checklist said "the function, which
  only reads," inaccurate for P11 (whose function writes `out_path`). No new blockers.
- `[glm]` — round-1 APPROVE WITH NITS carried forward (its `[OPEN]` arithmetic typo fixed; wording nit
  folded; manifest-honesty/anchor verification unaffected by the fold).

Consensus: **NOT reached** (1 REJECT — a one-line checklist wording residual). Folded; round 3 confirms `[sol]`.

### Round 2 — fold

- `[FIXED]` checklist (brief `p01b029`): "the function, which only reads" → names each function precisely
  (`word_counts_from_file`/`most_common_word` read; `running_totals_to_file` reads input, writes output)
  (`[sol]` MF1 residual). structure-check + hygiene-check PASS.

### Round 3 — verdicts (HEAD b8449b8) — CONSENSUS

- `[self]` APPROVE.
- `[sol]` APPROVE — checklist now accurate; both r1 Must-Fix remain resolved; structure/concept-scan/exec PASS.
- `[fable]` — round-2 APPROVE carried forward (the r2 fold was a one-line checklist wording fix).
- `[glm]` — APPROVE WITH NITS carried forward (all nits folded).

**Consensus: REACHED** — all four APPROVE / APPROVE-WITH-NITS, no open blockers. Content-review gate PASSED;
cleared for PR.

## Post-Execution Report

**Status: implemented, ci-local ALL GREEN + pytest 664 passed (2026-09-23). Content-review gate next.**

- **Phase A:** coverage-map entry `project-01-algorithm-challenge` (last, kind `project`) + `manifest.yaml`
  (v1, no `auxiliary`) + `.gitignore` project scratch glob + syllabus row/prose; coverage-map header
  swept. Creating the manifest activated the `practice_findings` anchor (directory existence) —
  `coverage-check` + `prereq-check` GREEN, confirming all 62 concepts practiced pre-capstone.
- **Phase B (Codex):** `brief.ipynb` — 4 `## Milestone N`, 11 `### Problem N`, `## Make it yours`,
  `## Requirements checklist`; solution-free, unique ids, no outputs; P4/P5 tagged `stretch`. Codex swapped
  two fixtures for freshness: `mississippi`→`possession` (U09), `ivy`→`larch` (U11).
- **Phase C (SEPARATE fresh Codex):** `solutions.ipynb` — 11 problems, function/class form, ≥3 asserted
  cases each; self-contained file problems; single-var dict iteration; f-string writes.
- **Reconciliation (inline):** the parallel Phase C authored from the plan specs, so its fixtures
  mismatched the brief. Aligned solutions to the brief's fresh fixtures and audited ALL extra fixtures
  against shipped Book 1b content (grep): P6 `mississippi`→`possession`; P7 `ivy`→`larch`, and the extra
  fixtures `red/blue/gold`→`maple/birch/cedar` and `owl/newt`→`wren/finch` (all shipped collisions);
  P8 extras `ant/bee`+`sun/moon/star`→`seal/crane`+`heron/ibis/koi` (all shipped). Also simplified P11's
  over-engineered manual digit-parser to the taught `int(line.strip())` (kept the fixtures, incl. a
  negative). concept-scan PASS; all 11 solution cells execute with every assert passing.
- **Phase D (inline):** `teacher-notes.md` with `PROJECT_NOTES_HEADINGS` (Goals/Pacing/Common
  mistakes/Discussion prompts/Differentiation/**Rubric**) + a per-problem value inventory naming the
  scratch files.
- **Phase E:** dropped `buildout: true` from `books.yaml`; `tests/test_books.py:23` →
  `assert books[1].get("buildout", False) is False` (+ comment); swept stale "buildout" comments in
  `scripts/ci-local.sh` and the coverage-map header. `TMPDIR=/dev/shm bash scripts/ci-local.sh` →
  **ALL GREEN** with the now-active strict `introduction_findings` (62/62), `lesson_budget` lower bound
  (43.5 ∈ [30,60]), and `practice_findings` anchor. `pytest tests/` → **664 passed**. Static tier-C
  AST/grep audit (comprehensions / tuple-assign / step-slice / ord-chr / import-math / inheritance /
  dunder>__init__ / decorators / `.copy()` / `.items()`-unpack): **VIOLATIONS NONE**. Working tree clean;
  every scratch `.txt` gitignored.

No deviations from the approved plan beyond the fixture reconciliation and the P11 simplification (both
quality fixes within scope). **This closes Book 1b:** all 13 units, 5 checkpoints, and the end-of-book
Algorithm Challenge ship; the book has left `buildout` with the full practice-coverage anchor GREEN.

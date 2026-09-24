# Plan 078 — Book 1b Algorithm Challenge (end-of-book capstone)

**Goal:** Ship `book1b/projects/project-01-algorithm-challenge` — a non-themed, integrative
mini-CP problem set — and take Book 1b **out of `buildout`**, activating the full
practice-coverage anchor. This is the FINAL plan for Book 1b.

**Spec:** `docs/designs/005-book1b-concept-first.md` §3 (the single project entry), §4 (registry /
buildout removal), §6 (coverage + the `practice_findings` anchor).

## Global constraints (verbatim)

- Book 1b is `prereq_policy: fastforward`, but **the project keeps the STRICT per-entry allowed set**
  (`concept_scan.py:933-940` — fastforward whole-catalog allowance is `kind == "unit"` only). So every
  scanner-DETECTED concept in the project's cells MUST appear in the entry's `requires ∪ practices`,
  exactly like a checkpoint.
- Tool-subset pins (unchanged from 075–077): string methods ⊆ {upper,lower,strip,replace}; list methods
  ⊆ {append,sort}; dict methods ⊆ {items,keys,values,get}; file methods ⊆ {read,readlines,readline,
  write,close}; builtins ⊆ {len,min,max,sum,sorted,abs,round} with NO `key=`.
- Content-gate/AST-audit bans (NOT scanner-flagged in Book 1b schema-v1, so reviewer + Phase-E audit
  enforced): NO comprehensions, tuple/multiple assignment, step slices, `ord`/`chr`, `import math`,
  inheritance, dunder methods beyond `__init__`, decorators.
- File drills are SELF-CONTAINED (write the scratch file before reading it) and use git-ignored scratch
  names. The `.gitignore` book1b block already globs `book1b/units/**` scratch `.txt`; add a
  `book1b/projects/project-01-algorithm-challenge/*.txt` glob.
- Student-facing `brief.ipynb` is solution-free with NO executed outputs and unique cell ids; no
  `input()`. `solutions.ipynb` runs top-to-bottom clean, function/class form, **≥3 distinct asserted
  cases per problem**, seeds fixed where randomness is used (no randomness is planned here).
- Values-distinctness rule: each problem's worked-sample inputs distinct from each other and from any
  lesson/exercise the student has seen.

## Scope

1. **Coverage-map entry** `project-01-algorithm-challenge` (kind `project`, LAST entry; `introduces: []`).
2. **Project directory**: `manifest.yaml`, `brief.ipynb` (11 problems, solution-free), `solutions.ipynb`
   (worked, asserted), `teacher-notes.md`.
3. **Syllabus**: add the project as a shipped-table row; update the roadmap prose line.
4. **Buildout removal**: drop `buildout: true` from the `book1b` entry in `books.yaml`; update
   `tests/test_books.py` (line 23) to assert the finished state.
5. **`.gitignore`**: add the project scratch-`.txt` glob.

## The problem set (11 problems: 9 core + 2 Challenge)

Non-themed, algorithmic, integrative. Each is function/class form with a precise **Specification** +
worked sample (input→exact output). Distinct inputs per problem.

1. **count_primes(n)** — count primes ≤ n (n ≥ 0). Nested loop + `%` primality; count-by-condition.
   `count_primes(10)`→4, `count_primes(1)`→0, `count_primes(20)`→8.
2. **digit_sum(n)** — sum the digits of a non-negative int with a `while` loop + `//`/`%`.
   `digit_sum(1234)`→10, `digit_sum(0)`→0, `digit_sum(9080)`→17.
3. **top_three(scores)** — the three largest values, descending, as a list (sort a copy ascending, take
   the last three by index in reverse order; ≥3 values guaranteed).
   `top_three([4,9,1,7,3])`→[9,7,4], `top_three([5,5,2,8])`→[8,5,5], `top_three([10,20,30])`→[30,20,10].
4. **is_palindrome(text)** — case-insensitive palindrome test; compare `text[i]` with `text[len-1-i]`
   over the first half (`.lower()`, `string-index`, no reverse builtin).
   `is_palindrome("Racecar")`→True, `is_palindrome("hello")`→False, `is_palindrome("Noon")`→True.
5. **merge_sorted(a, b)** — merge two ascending lists into one ascending list (two-index walk + `append`).
   `merge_sorted([1,4,6],[2,3,5])`→[1,2,3,4,5,6], `merge_sorted([],[2,9])`→[2,9],
   `merge_sorted([1,2],[])`→[1,2].
6. **word_counts(path)** — SELF-CONTAINED: write one word per line, then read and tally into a dict with
   `.get`. `["red","blue","red"]`→{"red":2,"blue":1} (+ two more distinct fixtures).
7. **most_common_word(path)** — SELF-CONTAINED: build the tally, then return the word with the highest
   count (find-extreme over `.items()`). Distinct fixtures from #6; single clear winner each.
8. **binary_search(nums, target)** — index of `target` in a sorted list, else `-1` (`while` + `//`
   midpoint). `binary_search([1,3,5,7,9],7)`→3, `binary_search([1,3,5,7,9],4)`→-1,
   `binary_search([2,4,6,8,10,12],2)`→0.
9. **class RunningTally** — `__init__(self)` starts an empty list attribute; `add(self, value)` appends
   and returns the running count; `total(self)`/`highest(self)`/`describe(self)` (f-string) report from
   the attribute. Assert construct-then-check across ≥3 states.
10. **[Challenge] running_totals_to_file(in_path, out_path)** — SELF-CONTAINED: read numbers from
    `in_path`, write their running totals to `out_path` (one f-string line each), and return the list of
    running totals. `[5,3,2]`→writes `"5\n8\n10\n"`, returns `[5,8,10]` (+ two more fixtures).
11. **[Challenge] group_by_parity(nums)** — return `{"even":[...], "odd":[...]}` preserving order (`%`,
    dict with list values). `group_by_parity([1,2,3,4])`→{"even":[2,4],"odd":[1,3]} (+ two fixtures).

## Coverage-map entry (contract)

Append AFTER `checkpoint-05-files-and-objects` (must be the last entry):

```yaml
- id: project-01-algorithm-challenge
  kind: project
  title: "Project 1 — Algorithm Challenge"
  lessons: 2
  introduces: []
  requires: [def-function, parameters, return-value, for-loop, while-loop, if-statement, elif-else,
             comparison, boolean, arithmetic, list-index, dict-access, file-read, file-write,
             with-statement, class-def, init-method, attributes, methods]
  practices: [def-function, parameters, return-value, variable, for-loop, while-loop, range-function,
              if-statement, elif-else, comparison, boolean, arithmetic, int-type, list-literal,
              list-index, list-append, list-loop, string-index, string-slice, string-methods,
              string-literal, dict-literal, dict-access, dict-loop, file-read, file-write,
              with-statement, class-def, init-method, attributes, methods, type-conversion, f-string,
              accumulator, running-total, count-by-condition, find-extreme, linear-search,
              transform-each, builtin-functions]
```

`manifest.yaml` mirrors this entry (same `introduces`/`requires`/`practices`; `blueprint_version: 1`,
`provenance: original`, `lessons: 2`, plus an `auxiliary: []`).
**Final `practices` set is reconciled to the actual scan in Phase E** (add/drop to exactly match detected
concepts; the anchor does not need the project's own practices, but the strict scan requires the tag set
to cover every detected concept and carry no untaught method).

## Tooling pins (enforcement tiers) — reused from 075–077

- (A) CI-enforced by concept-scan: method subsets + builtins set above; `class-def`/`init-method`/
  `attributes`/`methods`/`with-statement` detected; slices → `string-slice`.
- (B) MANUAL_ONLY (declaration + reviewer-verified, never scanner-detected): the technique concepts
  (`accumulator`/`running-total`/`count-by-condition`/`find-extreme`/`linear-search`/`transform-each`),
  plus `list-index`/`list-loop`/`dict-access`/`string-index`/`int-type`/`variable`/`type-conversion`.
- (C) NOT scanner-flagged but BANNED (Phase-E static AST/grep audit): comprehensions, tuple-assignment,
  step slices, `ord`/`chr`, `import math`, inheritance, dunders beyond `__init__`, decorators.
- Project scan is STRICT (allowed = introduces∪requires∪practices∪baseline; NO fastforward union).

## Phases

- **Phase A — Contracts.** Coverage-map entry + `manifest.yaml` + `.gitignore` glob + syllabus row/prose.
  Gate: `coverage-check`/`prereq-check` GREEN with the project entry present (buildout STILL on, so the
  anchor stays dormant until the directory is authored; verify the entry parses and requires-closure holds).
- **Phase B — Brief (Codex, statements).** `brief.ipynb`: 11 problems, solution-free, unique ids, no
  executed outputs, no `input()`.
- **Phase C — Solutions (SEPARATE fresh Codex).** `solutions.ipynb`: function/class form, ≥3 distinct
  asserted cases per problem, self-contained file problems, within all tool subsets.
- **Phase D — Teacher-notes (inline).** `teacher-notes.md` with the full heading set (Goals / Pacing /
  Common mistakes / Discussion prompts / Differentiation / Grading) + a per-problem value inventory.
- **Phase E — Buildout removal + VERIFICATION.** Drop `buildout: true` from `books.yaml`; update
  `tests/test_books.py:23` to `assert books[1].get("buildout", False) is False`. Reconcile the project
  `practices` set to the actual scan. Run `scripts/ci-local.sh` — the **now-active** `practice_findings`
  anchor (`known ≤ pre_capstone`) plus strict `introduction_findings`/`lesson_budget` lower bound must all
  be GREEN. Static AST/grep audit for the tier-C bans. `pytest tests/` GREEN. Post-execution report.

## Value plan

Every worked sample above uses distinct inputs. Solutions assert each problem's listed cases plus, where
noted, two additional distinct fixtures (file problems #6/#7/#10 write distinct scratch files per case).
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
_(4-way plan-review gate — filled before implementation.)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_

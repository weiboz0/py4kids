# Plan 075 — Book 1b Unit 09 (Strings) + Unit 10 (Lists)

**Origin:** Book 1b buildout ("full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (U09/U10 rows), §5 (fastforward), §6 (coverage),
§7 (mini-CP exercises, **function form** from U07 on), §"seven technique concepts" (search/transform in U09,
find-extreme/filter in U10 as ordinary concepts — no algorithm-pattern-thread authority).
**Templates:** Book 1b U07/U08 (function-form units, teacher-notes); U01–U08 conventions.

## Scope

Two concept-family units, NO checkpoint (checkpoints fall after U03/U05/U08/U11 — cp04 is plan 076), NO
turtle practice sites (U09/U10 are text/data, not drawing). Function form throughout (design §7). Book 1b
stays `buildout: true`.
- **U09 Strings** — introduces `string-index`, `string-slice`, `string-methods`, `in-operator`,
  `transform-each`, `linear-search`. Domains: palindrome, vowel count, Caesar cipher (via alphabet + mod),
  char frequency.
- **U10 Lists** — introduces `list-literal`, `list-index`, `list-append`, `list-loop`, `list-sort`,
  `find-extreme`, `filter-into-list`. Domains: min/max/sum, filtering, prefix sums, sorting.

## Coverage-map entries (contracts)

**unit-09-strings** — `kind: unit`, `title: "Strings — indexing, slicing, methods, and search"`, `lessons: 3`
- introduces: `[string-index, string-slice, string-methods, in-operator, transform-each, linear-search]`
- requires: `[def-function, parameters, return-value, for-loop, range-function, if-statement, comparison,
  boolean, arithmetic, variable, print, string-literal]`
- practices: `[f-string, string-concat, accumulator, count-by-condition, loop-counter, builtin-functions,
  int-type, type-conversion, elif-else, comment, naming]`

**unit-10-lists** — `kind: unit`, `title: "Lists — build, index, loop, sort, find, and filter"`, `lessons: 3`
- introduces: `[list-literal, list-index, list-append, list-loop, list-sort, find-extreme, filter-into-list]`
- requires: `[def-function, parameters, return-value, for-loop, range-function, if-statement, comparison,
  boolean, arithmetic, variable, print]`
- practices: `[builtin-functions, in-operator, accumulator, running-total, count-by-condition, loop-counter,
  f-string, int-type, float-type, comment, naming]`

Closure: U09/U10 requires ⊆ U01–U07 (def/params/return U07, for/range U05, if/elif U03, comparison/boolean/
arithmetic/type-conversion U02, variable/print/string-literal/f-string U01). U10 practices `in-operator`
(introduced U09, ≤U10). No self-practice. After this plan: 39 → 52 introduced-once (adds 6 + 7; 10 remain:
dicts 3 / files 3 / objects 4).

### Design §6 practice-coverage record
U10 practices U09's `in-operator` (membership tests in filters/searches). Both units practice the U07
`builtin-functions` — U09 via `len` (finally taught for real, per the plan-074 preview), U10 via
`len`/`min`/`max`/`sum`/`sorted` on lists. Every `practices` tag has a named site in the outline (below);
no unit lists its own introductions in `practices`.

## Tooling pins (CI-verified — the risk areas)

- **String methods are the taught subset ONLY: `upper`, `lower`, `strip`, `replace`** (concept_scan.py:63
  `STRING_METHODS`). Do NOT use `split`/`join`/`find`/`index`/`count`/`startswith`/`endswith`/`format`/
  `title`/`isdigit`/etc. — the scanner flags any other `.name(...)` as an untaught method
  (concept_scan.py:50-64, `.index` "nearly leaked into unit-06").
- **List methods are `append` and `sort` ONLY.** No `insert`/`remove`/`pop`/`extend`/`index`/`count`/
  `reverse`. `list-sort` is `list.sort()` (in place); `sorted(...)` is the builtin (returns a new list).
- **Built-ins now available: `len`, `min`, `max`, `sum`, `sorted`** (BUILTINS, concept_scan.py:64) — `len`
  on strings/lists, `min`/`max`/`sum`/`sorted` on lists (U10). Still NO other builtins.
- **NO `ord`/`chr`** (untaught, not in BUILTINS) — the Caesar cipher shifts via an **alphabet string** +
  `linear-search` for a letter's position + `%` (mod) + `string-index`, never character codes.
- **NO dicts (U11), files (U12), classes (U13)**; no tuple/multiple assignment; no comprehensions
  (`[... for ...]`) — build lists with `append` in a `for` loop (`transform-each`/`filter-into-list` are
  written as explicit loops, not comprehensions).
- Function form: solutions define the function + assert **several distinct input cases**; ≥3 non-vacuous
  assert cells per `solutions.ipynb`; no `input()` in graded/solution cells; unique cell ids; student
  notebooks solution-free with NO executed outputs.

## Teaching outlines

### U09 Strings (3 lessons, problem-first, function form)
- **L1 — Reach into a string (`string-index`, `string-slice`).** A string is a sequence of characters; `s[0]`
  is the first, `s[-1]` the last; `s[a:b]` is a slice (stop excluded, echoing `range`). `len(s)`. Hooks:
  first/last initial, a substring.
- **L2 — Clean and test (`string-methods`, `in-operator`).** The taught methods `upper`/`lower`/`strip`/
  `replace` (case-fold before comparing; trim input; swap a substring); `"a" in word` membership. A
  **palindrome** check (compare a cleaned string to its reverse-by-slice or index-walk) and a **vowel count**
  (`count-by-condition` with `ch in "aeiou"`).
- **L3 — Transform and search (`transform-each`, `linear-search`).** Build a NEW string character by
  character in a loop (`transform-each` via `+`/accumulator) — a **Caesar cipher** using an alphabet string:
  find each letter's position with a `linear-search` loop, shift by `(pos + k) % 26`, index back into the
  alphabet. A `linear-search` that returns the first index of a target (or -1). A **char-frequency** count.
60-min cut per lesson in teacher-notes (Caesar is the natural L3 cut casualty → stretch).

### U10 Lists (3 lessons, problem-first, function form)
- **L1 — Build and read (`list-literal`, `list-index`, `list-append`, `list-loop`).** `[3, 1, 2]`; `nums[0]`;
  `nums.append(x)`; `for x in nums`. Build a list with `append` in a loop; `len(nums)`; `sum(nums)`.
- **L2 — Order and choose (`list-sort`, `find-extreme`).** `nums.sort()` (in place) vs `sorted(nums)` (new
  list); `min`/`max` builtins vs a hand-written **find-extreme** loop (track the best so far); why the loop
  generalizes (find the longest word, the highest score).
- **L3 — Filter and combine (`filter-into-list`).** Build a new list of the items that pass a test
  (`filter-into-list` via `append` inside an `if` in a loop — NOT a comprehension); **prefix sums** (a running
  total appended each step). Put it together (e.g. keep the above-average scores).
60-min cut per lesson in teacher-notes.

## Value plan
Distinct input cases per exercise, distinct from lesson examples and each other (plan-072/073/074 rule);
list the (function, sample inputs) inventory in each unit's teacher-notes so the gate can check.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: 2 coverage-map entries (7-key) + 2 unit manifests + 2 syllabus rows; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): U09 + U10 lesson.ipynb + exercises.ipynb. Per unit ≥8 exercises, core ≤7, ≥2 `stretch` (notebooks.py:583-587 floor + plans-071–074 convention). Pin: function form; string methods = upper/lower/strip/replace ONLY; list methods = append/sort ONLY; builtins len/min/max/sum/sorted; NO ord/chr, NO comprehensions, NO dicts/files/classes/tuple-assignment.
### Phase D — solutions (SEPARATE fresh Codex): U09/U10 solutions.ipynb (function form: define + assert several distinct cases; ≥3 assert cells; NO forbidden methods/builtins). Verify `exec-solutions`.
### Phase E — teacher-notes (inline, both) + verification: full `TMPDIR=/dev/shm bash scripts/ci-local.sh`
ALL GREEN (registry/lint, unit tests, notebook exec+hygiene, manifest/prereq/coverage/stretch, concept-scan,
PDF, pre-merge-guard). Static audit: no string/list methods outside the taught subsets; no `ord`/`chr`; no
comprehensions; no tuple assignment. Scope allowlist = this plan + the U09/U10 trees + coverage-map + syllabus.

## Out of scope
- U11–U13, cp04/cp05, Algorithm Challenge — plans 076+. No tooling/stub changes; no governance/Book-1/2 changes.
- No dicts/files/classes; string/list methods limited to the taught subsets; no comprehensions; no `ord`/`chr`.
- **Verification phase:** Phase E is the named verification phase (both units → required).

## Plan Review

### Round 1 (2026-09-23)
**[self] APPROVE.** Closure: U09/U10 requires ⊆ U01–U07; U10 practices `in-operator` (U09) ≤U10; no
self-practice; 39→52 introduced-once, no duplicate introductions. Named verification phase (E) covers both
units. Risk areas pinned in Phase C: string methods = upper/lower/strip/replace only; list methods =
append/sort only; builtins len/min/max/sum/sorted; NO ord/chr (Caesar via alphabet + linear-search + mod);
NO comprehensions (build lists with append loops); function form.
_(Awaiting [sol]/[glm]/[fable].)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(Filled before shipping.)_

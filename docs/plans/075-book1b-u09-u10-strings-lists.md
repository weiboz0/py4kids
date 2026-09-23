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
U10 practices U09's `in-operator` (membership in filters/searches). Named sites for every practice tag:
- **U09** — `builtin-functions` (`len` in palindrome/vowel-count), `count-by-condition` (vowel count,
  `count_char`), `accumulator`/`string-concat` (the `transform-each` string builder), `loop-counter` (the
  index-walk `range` loops), `f-string` (result reports), `int-type` (counts/positions), `type-conversion`
  (`str()` in a report), `elif-else` (a classify-the-char branch), `comment`/`naming` (throughout).
- **U10** — `builtin-functions` (`len`/`min`/`max`/`sum`/`sorted`), `in-operator` (membership filter),
  `accumulator`/`running-total` (prefix sums), `count-by-condition` (count items passing a test),
  `loop-counter` (index loops/argmax), `f-string`, `int-type`, `float-type` (the average in above-average
  filtering), `comment`/`naming`.
No unit lists its own introductions in `practices`.

## Tooling pins (with their ACTUAL enforcement — corrected per [sol]/[glm] r1)

Three tiers of enforcement — do not conflate them:

**A. CI-enforced by `concept-scan` (a violation FAILS ci-local):**
- **String methods = the taught subset ONLY: `upper`, `lower`, `strip`, `replace`** (`STRING_METHODS`,
  concept_scan.py:62). Any other `.name(...)` (`split`/`join`/`find`/`index`/`count`/`startswith`/`title`/
  `isdigit`/…) is flagged "untaught method" (concept_scan.py:50-64, 438-441 — `.index` "nearly leaked into
  unit-06").
- **List methods = `append`, `sort` ONLY** (TAUGHT_METHODS, concept_scan.py:52). No `insert`/`remove`/`pop`/
  `extend`/`index`/`count`/`reverse` (all flagged untaught).
- **Detected concepts:** `string-slice`/list-slice → `string-slice` (Subscript+Slice, :337-340 — the scanner
  CANNOT tell string from list slices, so a **list slice scans as `string-slice`**); `string-methods`
  (:398-399); `in-operator` (:201-204); `list-literal` (:292-294); `list-append`/`list-sort`/`sorted`
  (:400-403, 451-452). Builtins map to `builtin-functions`.

**B. MANUAL_ONLY — declared + reviewer-verified, NOT scanner-detected** (concept_scan.py:40-42, and the four
technique concepts are `never_flag`, concepts.yaml:34-40): **`string-index`, `list-index`, `list-loop`**
(a subscript `s[i]` emits no index concept; `for x in items` emits only `for-loop`), plus `transform-each`/
`linear-search`/`find-extreme`/`filter-into-list`. Their introductions are credited by the manifest/
coverage-map tag (curriculum.py at-most-once check), not by detection — so the coverage claim is honest, but
reviewers (not CI) confirm the concept is genuinely present.

**C. NOT flagged by Book 1b's schema-v1 scan at all — enforced by the content-gate reviewers + my Phase-E
static audit (grep/AST), NOT ci-local:** `ord`/`chr` (bare calls, no detector); **comprehensions**
(`[… for …]` / set / dict / generator — `add_feature` no-ops against the 62-concept catalog); **tuple/multiple
assignment**. The stricter source policy is Book-2-only (source_policy.py). So these MUST be caught by review
and the Phase-E audit — do NOT rely on the scanner.

**Positive rules:** built-ins available = `len`, `min`, `max`, `sum`, `sorted` (+ the already-taught `abs`/
`round`), nothing else (BUILTINS, concept_scan.py:63); `len` on strings (U09) and lists (U10), `min`/`max`/
`sum`/`sorted` on lists (U10). Caesar shifts via an **alphabet string** + `linear-search` + `%` (mod) +
`string-index` — never `ord`/`chr`. `transform-each`/`filter-into-list` are explicit `append` loops, never
comprehensions. **NO list slices in U10** (they scan as `string-slice`, which U10 does not introduce).
NO dicts (U11)/files (U12)/classes (U13).
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
  **palindrome** check by **index-walk** (`for i in range(len(s) // 2): if s[i] != s[len(s)-1-i]: return False`)
  — uses only `string-index` + `for`/`range` + `len`; do NOT teach `s[::-1]` (step slices are never
  introduced; if shown at all, only as an aside after the loop). A **vowel count** (`count-by-condition` with
  `ch in "aeiou"`).
- **L3 — Transform and search (`transform-each`, `linear-search`).** CORE (independent of Caesar, so the cut
  never leaves these concepts unpractised): a simple **`transform-each`** that builds a NEW string char by
  char in a loop (`remove_vowels`/`double_letters`/`censor` via `+`/`string-concat` accumulator), and a CORE
  **`linear-search`** `position(text, ch)` (return `i` inside the loop, `-1` after). Then **char frequency**
  as `count_char(text, ch)` (count-by-condition) plus a printed alphabet-scan table (a 26×n nested loop —
  NOT a frequency map; a map needs dicts, U11). "Most common letter" is `find-extreme` (U10) — keep it out of
  U09 core (offer as a stretch, tagging `find-extreme` in practices via fastforward, or defer to U10).
  **Stretch — Caesar cipher**, written HELPER-FIRST composing the core pieces: `position(alphabet, ch)`
  (linear-search) then `shift(message, k)` = `message.lower()`, for each char shift a letter by
  `(pos + k) % 26` and index back into the alphabet, passing non-letters through unchanged (the `-1` branch);
  `k >= 0`. (The one-nested-loop-with-inline-mod version is too hard — that is why Caesar is stretch, not core.)
60-min cut per lesson in teacher-notes (Caesar is the L3 cut casualty → already stretch).

### U10 Lists (3 lessons, problem-first, function form)
- **L1 — Build and read (`list-literal`, `list-index`, `list-append`, `list-loop`).** `[3, 1, 2]`; `nums[0]`;
  `nums.append(x)`. Teach BOTH loop forms: `for x in nums` (value) AND `for i in range(len(nums))` (index —
  needed for argmax and "compare with the previous item"). Build a list with `append` in a loop; `len(nums)`;
  `sum(nums)`.
- **L2 — Order and choose (`list-sort`, `find-extreme`).** `nums.sort()` (in place, returns `None`) vs
  `sorted(nums)` (new list) — pin the **`scores = nums.sort()` → `None` trap** (the U10 twin of U07's
  print-vs-return). `min`/`max` builtins vs a hand-written **find-extreme** loop: seed `best = nums[0]`
  (NOT `0` — negative-value trap), assume "the list has at least one item" (state it in every extreme/average
  spec). The loop earns its keep via **argmax** — the position of the max, or the longest word — since
  `max(words, key=len)` is untaught, so "longest word" is unsolvable without the index loop.
- **L3 — Filter and combine (`filter-into-list`).** Build a new list of the items that pass a test
  (`filter-into-list` via `append` inside an `if` in a loop — NOT a comprehension); **prefix sums** (a running
  total appended each step — `running-total` from U04). Put it together (e.g. keep the above-average scores,
  using `sum`/`len` for the average → `float-type`).
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
PDF, pre-merge-guard). **Static AST/grep audit (the real enforcement for the tier-C forms ci-local does NOT
catch in Book 1b):** no `.method` outside `{upper,lower,strip,replace,append,sort}`; no builtins outside
`{len,min,max,sum,sorted,abs,round,print,int,float,str,range}`; no `ord`/`chr`; no comprehensions
(`ListComp`/`SetComp`/`DictComp`/`GeneratorExp`); no tuple/multiple assignment; no step slices (`s[::…]`);
no list slices in U10; Caesar uses the alphabet+linear-search+`%` form (no `ord`/`chr`). Scope allowlist =
this plan + the U09/U10 trees + coverage-map + syllabus.

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

**[fable] APPROVE WITH NITS; [glm] APPROVE WITH NITS; [sol] REJECT.** All agree the contract closes (39→52,
no dupes/self-practice) and the domains are achievable; the REJECT is on my inaccurate CI-enforcement claims.
Folded:
- `[FIXED]` ([sol]/[glm]) rewrote §Tooling pins into three enforcement tiers: **A** CI-enforced by
  concept-scan (methods subsets; slice/method/in-operator/list-literal/append/sort detection; a list slice
  scans as `string-slice`); **B** MANUAL_ONLY (`string-index`/`list-index`/`list-loop` + the four technique
  concepts — declared/reviewer-verified, not detected); **C** NOT scanner-flagged in Book 1b (`ord`/`chr`,
  comprehensions, tuple assignment) → enforced by reviewers + my Phase-E static audit. Fixed citations
  (`STRING_METHODS`:62, `BUILTINS`:63). Pinned "no list slices in U10".
- `[FIXED]` ([sol]/[glm]) Phase-E static audit strengthened to grep/AST for the tier-C forms (the real
  enforcement) + methods/builtins outside the taught sets + step slices + U10 list slices.
- `[FIXED]` ([fable]1-2) U09 L3 gains CORE `transform-each` (`remove_vowels`/`double`/`censor`) + CORE
  `linear-search` (`position`) independent of Caesar; Caesar is stretch, helper-first (`position`+`shift`,
  lowercase, k≥0, non-letters pass through).
- `[FIXED]` ([fable]3) palindrome via index-walk, not `s[::-1]`.
- `[FIXED]` ([fable]4/[glm]) char frequency = `count_char(text, ch)` + a printed alphabet-scan table (no
  frequency map/dict); "most common letter" kept out of U09 core (find-extreme is U10).
- `[FIXED]` ([fable]5) U10 find-extreme: `best = nums[0]`, "≥1 item", argmax variant, `sort()`→`None` trap.
- `[FIXED]` ([fable]6) U10 L1 teaches both loop forms.
- `[FIXED]` ([fable]7) §6 record now names a site for every practice tag.

### Round 2 (2026-09-23) — re-dispatched [sol]/[glm]/[fable].
**CONSENSUS — [self] APPROVE; [sol] APPROVE; [glm] APPROVE; [fable] APPROVE.** All r1 blockers/nits resolved
(tooling claims corrected to true enforcement tiers; Phase-E audit is the explicit enforcement for the
forms ci-local misses; all pedagogy pins folded). No open findings. **Plan-review gate PASSED.**
Phase-C authoring notes ([fable] r2): if the "most common letter" stretch is written in U09, add
`find-extreme` to U09 practices then; ensure the `elif-else` practice site lands in a CORE exercise (tier-B/C
tags are reviewer-verified, not CI-detected).

## Content Review

### Round 1 (2026-09-23) — [self] APPROVE; [glm] APPROVE WITH NITS; [fable] APPROVE WITH NITS; [sol] REJECT.
Blind solves matched ([fable] 14/14, [glm] 18/18); all tooling PASS; reviewers confirmed NO tier-C forms
(ord/chr/comprehensions/tuple-assignment/step-slices/list-slices) and only the taught method/builtin subsets.
One REJECT ([sol]) on two P2 metadata items. Dispositions (folded):
- `[FIXED]` ([fable] Should Fix) U09 lesson now teaches `for ch in text` (string iteration — the first
  non-`range` for-loop in Book 1b) before its first use, with the value-vs-index contrast; and explains
  method chaining (`strip().lower()`).
- `[FIXED]` ([fable]/[glm]) U10 solutions Ex1 returns `[scores[0], len(scores), sum(scores)]` directly (was a
  loop over a list literal).
- `[FIXED]` ([fable]/[glm]) U10 lesson adds a sentence that `in` tests whole-item list membership (vs U09's
  substring/char membership).
- `[FIXED]` ([glm]) U10 Ex9 worked input changed (was `["green","blue","gold"]`, 2/3 shared with the lesson).
- `[FIXED]` ([fable] Should Fix) U10 teacher-notes gain the silent-wraparound trap (`range(len)` vs
  `range(1,len)` → `scores[-1]` wraps) and the `//`-average trap.
- `[FIXED]` ([sol]1/[fable]6b) U09 Differentiation no longer previews `find-extreme` ("most common vowel");
  reworded to within-U09 extensions (case-insensitive / ignore punctuation) — keeps U09 self-contained, so
  `find-extreme` stays out of U09 practices.
- `[FIXED]` ([sol]2/[glm]) U09 value-plan Ex7/Ex9 now enumerate concrete inputs
  (`count_char("pepper","z")`, `print_alphabet_scan("Bee")`; `position(…,"q")`, `shift("Code 9!",2)` etc.).
- `[FIXED]` ([fable]6) U09 teacher-notes drift (Pacing L3 → `double_letters`; "letter→count map needs a
  dictionary"); ([fable]7) Caesar foregrounded in the U09 hook.
- `[WONTFIX]` ([sol]3) native-exec sandbox limitation — my ci-local ran `exec-solutions` natively ALL GREEN
  (same precedent as prior plans).

_(Round-2 re-review after the fold.)_

## Post-Execution Report

**Status: implemented, ci-local ALL GREEN (2026-09-23). Content-review gate next.**

- **Phase B:** coverage-map entries (U09/U10) + 2 manifests + 2 syllabus rows; coverage-check/prereq-check
  GREEN; 39→52 introduced-once, no dupes, no forward requires.
- **Phase C (Codex ×2):** U09 `lesson.ipynb` (index/slice; the four methods + membership; palindrome
  index-walk; core transform-each + linear-search; Caesar stretch helper-first) + `exercises.ipynb` (9,
  function form, 2 stretch). U10 `lesson.ipynb` (build/read both loop forms; sort/sorted + find-extreme
  best=nums[0]/argmax + sort()→None trap; filter + prefix sums) + `exercises.ipynb` (9).
- **Phase D (SEPARATE fresh Codex ×2):** U09/U10 `solutions.ipynb` (function form, 41/37 non-vacuous
  asserts; no forbidden methods/builtins/forms).
- **Phase E:** teacher-notes for both units (full heading sets + concrete `## Value plan (sample inputs)`
  inventories). `TMPDIR=/dev/shm bash scripts/ci-local.sh` → **ALL GREEN** (concept-scan, exec-solutions,
  notebook exec+hygiene, manifest/prereq/coverage/stretch, PDF, pre-merge-guard). Static AST audit clean:
  string methods ⊆ {upper,lower,strip,replace}; list methods ⊆ {append,sort}; builtins ⊆
  {len,min,max,sum,sorted,abs,round,print,int,float,str,range}; no `ord`/`chr`; no comprehensions; no
  tuple/multiple assignment; no step slices; no list slices in U10.

No deviations from the approved plan.

# Plan 076 — Book 1b Unit 11 (Dictionaries) + Checkpoint 04

**Origin:** Book 1b buildout ("full book 1b implementation").
**Design:** `docs/designs/005-book1b-concept-first.md` §3 (U11 row + checkpoint-after-U11), §5 (fastforward),
§6 (coverage), §7 (mini-CP exercises, function form).
**Templates:** Book 1b U07–U10 (function-form units); cp03 (checkpoint shape + strict-scan closure discipline).

## Scope

One unit + one checkpoint (checkpoints fall after U03/U05/U08/U11 — cp04 is here). Function form throughout.
No turtle. Book 1b stays `buildout: true`.
- **U11 Dictionaries** — introduces `dict-literal`, `dict-access`, `dict-loop`. Domains: frequency maps,
  tallies, lookup tables, group-by-first-letter (backgrounds avoid untaught methods).
- **Checkpoint 04** — after U11 (design §3/§6), un-themed, strict, assesses U01–U11.

## Coverage-map entries (contracts)

**unit-11-dictionaries** — `kind: unit`, `title: "Dictionaries — key/value maps, lookups, and tallies"`, `lessons: 3`
- introduces: `[dict-literal, dict-access, dict-loop]`
- requires: `[def-function, parameters, return-value, for-loop, list-loop, in-operator, if-statement,
  elif-else, comparison, boolean, arithmetic, variable, print]`
- practices: `[list-literal, list-append, list-sort, filter-into-list, string-index, string-methods,
  count-by-condition, accumulator, builtin-functions, find-extreme, int-type, f-string, comment, naming]`

**checkpoint-04-dictionaries** — `kind: checkpoint`, `title: "Checkpoint 4 — Dictionaries & Collections"`, `lessons: 0.5`
- introduces: `[]`
- requires: `[print, variable, def-function, parameters, return-value, dict-literal, dict-access, dict-loop,
  in-operator, for-loop, list-loop, list-literal, if-statement, elif-else, comparison, boolean, arithmetic,
  builtin-functions, f-string, string-literal, type-conversion]`
- practices: `[print, variable, def-function, parameters, return-value, dict-literal, dict-access, dict-loop,
  in-operator, for-loop, list-loop, list-literal, list-index, if-statement, elif-else, comparison, boolean,
  arithmetic, count-by-condition, accumulator, builtin-functions, find-extreme, int-type, f-string,
  string-literal, type-conversion]`

Closure: U11 requires ⊆ U01–U10 (def/params/return U07, for-loop U05, list-loop U10, in-operator U09, if U03,
comparison/boolean/arithmetic U02, variable/print U01). cp04 requires/practices ⊆ U01–U11 (checkpoints get NO
fastforward — every concept a question uses is listed). No self-practice. After this plan: 52 → 55
introduced-once (adds the 3 dict concepts; cp04 introduces none). 7 remain (files 3 / objects 4).

### Design §6 practice-coverage record (ledger — the full-practice anchor activates when 078 leaves buildout)
U11 practice sites (named): `string-index` (`word[0]` in group-by-first-letter), `list-literal`/`list-append`
(group-by builds a list per key), `filter-into-list` (keys whose value passes a test → a list),
`list-sort`/`builtin-functions` (a sorted leaderboard of scores; `len`/`max` over keys/values),
`string-methods` (`lower()` before keying), `count-by-condition`/`accumulator` (tallies/frequency maps),
`find-extreme` (most-common key via a loop over `items()`), `int-type` (counts), `f-string`/`comment`/`naming`.
cp04 anchors the U01–U11 foundational practices (incl. `find-extreme` in its most-common-key question).
No unit lists its own introductions in `practices`.

**Deferred practice-coverage debt (the coverage anchor counts NON-capstone practices only, curriculum.py:462-473 —
so these MUST be practiced in a unit/checkpoint before 078 leaves buildout):**
| introduced concept | intro | landing practice site |
|---|---|---|
| `string-index` | U09 | **U11 (this plan)** — `word[0]` group-by |
| `list-sort` | U10 | **U11 (this plan)** — sorted leaderboard |
| `filter-into-list` | U10 | **U11 (this plan)** — keys→list filter |
| `transform-each` | U09 | **U12 (plan 077)** — transform each line read from a file |
| `linear-search` | U09 | **U12 (plan 077)** — find the first line matching in a file |
| `string-slice` | U09 | **U13 (plan 077)** — slice a field/attribute string |
Plan 077 MUST list these three in U12/U13 practices; plan 078 then verifies full coverage out of buildout.

## Tooling pins (enforcement tiers — same model as plan 075)

- **CI-enforced (concept-scan):** dict methods = ONLY `items`/`keys`/`values`/`get` (DICT_METHODS,
  concept_scan.py:64); any other `.name(...)` flagged untaught. Built-ins ⊆ {len,min,max,sum,sorted,abs,round};
  **no `key=` argument** on `max`/`min`/`sorted` — NOT scanner-flagged in Book 1b (the `sorted-key` feature is
  unregistered, so `add_feature` no-ops), so this is a tier-C ban caught ONLY by the Phase-E audit;
  `max(d, key=d.get)` is untaught and would defeat the `find-extreme` practice site. List methods ⊆
  {append,sort}; string methods ⊆ {upper,lower,strip,replace}.
- **Detected vs MANUAL_ONLY (corrected per [sol]/[glm]):** `dict-literal` IS detected (`{}`, visit_Dict,
  :296-298); `dict-loop` IS detected from the bare `.items`/`.keys`/`.values` ATTRIBUTE access
  (concept_scan.py:397-405), NOT from the loop itself — a plain `for k in d:` emits no dict-loop; **`dict-access`
  is MANUAL_ONLY** (concept_scan.py:41 — a dict subscript emits no concept, and `.get` adds none), credited by
  the manifest tag and reviewer-verified (like string-index/list-index in plan 075).
- **NOT scanner-flagged in Book 1b (enforced by reviewers + my Phase-E static AST/grep audit):** `ord`/`chr`,
  comprehensions (incl. DICT comprehensions `{k: v for …}`), tuple/multiple ASSIGNMENT statements (`a, b = …`),
  step slices, and `collections`/`defaultdict` (the untaught-method net misses a bare-Name call + a
  `from collections import …`). **Build dicts by assignment in a loop (`d[k] = …`), never a dict comprehension.**
  **EXEMPT:** `for key, value in d.items()` — the two-name for-target is NOT a banned assignment (the scanner
  exempts it, :304-319; it is the taught `dict-loop` form). The Phase-E audit flags only `ast.Assign` with a
  Tuple target, never `ast.For` targets.
- **`+=`** is the `accumulator` idiom (U04, allowed); prefer explicit `d[k] = d[k] + 1`. The **missing-key
  idiom** is taught PRIMARY as `if k in d: d[k] = d[k] + 1` / `else: d[k] = 1` (reuses `in-operator`+`else`),
  with `d.get(k, 0) + 1` shown as the shortcut — never `collections`/`defaultdict`. Group-by uses ONLY the
  explicit `if letter in groups: groups[letter].append(w)` / `else: groups[letter] = [w]` — never
  `groups.get(letter, []).append(w)` (that returns `None`/drops the word).
- **cp04 strict discipline** (no fastforward — checkpoint allowed set = requires∪practices): join text with
  f-strings only (list `string-literal`, already listed), NO `+` string-concat; iterate collections directly
  (`for x in items`/`for k in d`/`for k, v in d.items()`) — NO `range`, `sorted`, `.append`, string methods,
  slices, or `while` (each would be a detected-but-unlisted concept: range-function/list-sort/list-append/
  string-methods/string-slice/while-loop). Include `type-conversion` (listed) only for `int()`/`str()`. No
  `and`/`or` (avoids `logical-ops`), no `ord`/`chr`/comprehensions/tuple-assignment. `find-extreme` (listed
  in practices) backs the most-common-key question.
- Function form: solutions define the function + assert several distinct cases; ≥3 non-vacuous assert cells;
  no `input()`; unique cell ids; student notebooks solution-free with NO executed outputs.

## Teaching outline

**Problem-first opener** (design §6 engagement; like U10's "score board"): open L1 with a concrete payoff,
e.g. "given this list of votes, which option won and by how many?" / "which word appears most often?" — the
motivation for a labelled tally — BEFORE the first `{}` is explained.

### U11 Dictionaries (3 lessons, problem-first, function form)
- **L1 — Key/Value Maps (`dict-literal`, `dict-access`).** A dict as a labelled lookup: `{"gold": 3, …}`;
  read with `d[key]`; `key in d` tests **keys, not values** (state this — top misconception); the
  **`KeyError` trap** shown as a FENCED MARKDOWN traceback block (NOT an executed cell — no `try/except` is
  taught, and lesson cells run in CI), immediately followed by the safe `d.get(key, default)` cell; add/update
  with `d[key] = value`. A lookup table (e.g. Roman-numeral values, price list).
- **L2 — Loop over a Dictionary (`dict-loop`).** `for key in d`; then **`for key, value in d.items()`
  presented explicitly as "two loop names, one per pair"** (accept `for key in d: value = d[key]` as an
  equivalent student form); `d.keys()`/`d.values()`; sum the values; find the key with the largest value (a
  `find-extreme` over `d.items()`) — **spec a unique maximum or "if tied, the first key wins"** (a strict `>`
  loop over items yields insertion-order first).
- **L3 — Build Maps from Data.** A **frequency map** / tally: teach the missing-key idiom PRIMARY as
  `if k in d: d[k] = d[k] + 1` / `else: d[k] = 1`, with `d.get(k, 0) + 1` as the shortcut. A
  **group-by-first-letter** (`word[0]` → `string-index`; each value is a LIST built with the EXPLICIT
  `if letter in groups: groups[letter].append(w)` / `else: groups[letter] = [w]` — never
  `groups.get(letter, []).append(w)`, which returns `None`); lists keep words in input order. A sorted
  leaderboard (`list-sort`) and a keys-passing-a-test filter (`filter-into-list`). Put it together.
60-min cut per lesson in teacher-notes.

### Checkpoint 04 (after U11, strict, no turtle, no fastforward)
6–7 VISIBLE `## Question N`. Mix: build/read a lookup dict; a `d.get`-with-default question; a frequency-map
tally; a loop-over-`items` sum or count; the most-common-key (`find-extreme` over items); an `elif`/lookup
question; and one that combines a list with a dict (tally a list of words with `for w in words`, and also read
a word by POSITION — `words[0]`/`words[-1]`, or `words[n]` for a given `n` — a genuine `list-index` site with
NO `range` loop; cp04 is the only pre-078 practice site for `list-index`). Strict — only concepts ≤ U11;
NO `ord`/`chr`/comprehensions/tuple-assignment; dict methods ⊆ {items,keys,values,get}. teacher-notes has
`## Grading` (two named pass-bar items: build-and-read-a-dict; tally-with-the-missing-key-idiom) + the full
heading set + `## Discussion prompts`.

## Value plan
Distinct input cases per exercise/question, distinct from lesson examples and each other; list the
(function, sample inputs) inventory in the unit's + the checkpoint's teacher-notes so the gate can check.

## Phases

### Phase A — plan-review gate (4-way). No implementation until consensus.
### Phase B — contracts: coverage-map entries (U11 + cp04) + unit manifest + checkpoint manifest + 2 syllabus rows; `--book book1b coverage-check` + `prereq-check` GREEN.
### Phase C — statements + assets (Codex): U11 lesson.ipynb + exercises.ipynb + cp04 checkpoint.ipynb. U11 ≥8 exercises, core ≤7, ≥2 `stretch`; cp04 6–7 visible `## Question N`. Pin: function form; dict methods ⊆ {items,keys,values,get}; build dicts by loop-assignment (NO dict comprehensions); missing-key idiom (no defaultdict); no ord/chr/tuple-assignment; cp04 f-strings only.
### Phase D — solutions (SEPARATE fresh Codex): U11 + cp04 solutions.ipynb (function form; ≥3 assert cells; no forbidden methods/forms). Verify `exec-solutions`.
### Phase E — teacher-notes (inline, both) + verification: full `TMPDIR=/dev/shm bash scripts/ci-local.sh`
ALL GREEN (registry/lint, unit tests, notebook exec+hygiene, manifest/prereq/coverage/stretch, concept-scan,
checkpoint questions, PDF, pre-merge-guard). Static AST/grep audit: dict/list/string methods within the
taught subsets; builtins within the set and NO `key=` arg; no `ord`/`chr`; no `collections`/`defaultdict`
(bare-Name call OR `from collections import …` — the scanner misses these); no comprehensions (incl. dict
comprehensions); no tuple/multiple ASSIGNMENT statements (`ast.Assign` with a Tuple target) — but the
`for key, value in d.items()` for-target is EXEMPT (not flagged); no step slices; cp04 has no
`range`/`sorted`/`.append`/string-methods/slices/`while`/`+`-concat. Scope allowlist = this plan + the
U11/cp04 trees + coverage-map + syllabus.

## Out of scope
- U12/U13, cp05, Algorithm Challenge — plans 077+. No tooling/stub changes; no governance/Book-1/2 changes.
- No files/classes; no `collections`/`defaultdict`; dict methods limited to {items,keys,values,get}; no comprehensions.
- **Verification phase:** Phase E is the named verification phase (unit + checkpoint → required).

## Plan Review

### Round 1 (2026-09-23)
**[self] APPROVE.** Closure: U11 requires ⊆ U01–U10 (list-loop U10, in-operator U09); practices ⊆ U01–U11, no
self-practice; cp04 requires/practices ⊆ U01–U11 (no fastforward), introduces []. 52→55 introduced-once, no
dupes. Named verification phase (E) covers unit + checkpoint. Risks pinned: dict methods ⊆ {items,keys,values,
get}; build dicts by loop-assignment (no dict comprehensions); missing-key idiom (no defaultdict); cp04
strict-scan closure (string-literal with f-string; type-conversion if int/str; logical-ops only if used);
tier-C forms (ord/chr/comprehensions/tuple-assignment) enforced by reviewers + Phase-E audit.

**[fable] APPROVE WITH NITS; [sol] REJECT; [glm] REJECT.** All agree closure holds; the rejects are on
metadata/tooling accuracy + the practice-coverage ledger. Folded:
- `[FIXED]` ([sol]1/[glm]B1) cp04 declares `find-extreme` (its most-common-key question) — added to cp04 practices.
- `[FIXED]` ([glm]B2 — the big catch) added the **Design §6 deferred-practice-debt table**: U11 now practices
  `string-index`/`list-sort`/`filter-into-list` at named sites; `transform-each`/`linear-search`/`string-slice`
  are assigned landing sites in U12/U13 (plan 077) — because the coverage anchor counts non-capstone practices
  only (curriculum.py:462-473), these must be practiced before 078 leaves buildout.
- `[FIXED]` ([glm]B3) `string-index` added to U11 practices (group-by `word[0]`).
- `[FIXED]` ([sol]2/[glm]4) re-tiered dict detection: `dict-literal` detected (`{}`), `dict-loop` via
  `.items`/`.keys`/`.values` only, **`dict-access` MANUAL_ONLY** (subscript/`.get` emit no concept).
- `[FIXED]` ([sol]3/[glm]6) `for key, value in d.items()` explicitly EXEMPTED from the tuple-assignment ban
  (scanner-exempt; the taught dict-loop form); Phase-E audit flags only `ast.Assign` tuple targets.
- `[FIXED]` ([glm]7) `elif-else` added to U11 requires (missing-key idiom's `else`).
- `[FIXED]` ([fable]N1) group-by uses the explicit `if letter in groups … else` form (no `get([]).append`
  trap); missing-key idiom taught PRIMARY as `if k in d … else`, `get` as shortcut.
- `[FIXED]` ([fable]N2) concrete problem-first opener pinned; ([fable]N3) `KeyError` as a fenced markdown
  traceback (not executed) + "`key in d` tests keys, not values"; ([fable]N5) tie-breaking + group-by order specs.
- `[FIXED]` ([glm]5/[fable]N4) cp04 discipline expanded (avoid range/sorted/append/string-methods/slices/
  while/+concat; no `key=` on max/min/sorted); ([glm]6) Phase-E audit += `collections`/`defaultdict`.

### Round 2 (2026-09-23) — [self] APPROVE; [fable] APPROVE; [glm] APPROVE WITH NITS; [sol] REJECT (accuracy).
All three r1 blockers verified resolved by [sol]/[glm]. Remaining folds:
- `[FIXED]` ([sol]2) §Tooling pins accuracy: `dict-loop` detected from the bare `.items`/`.keys`/`.values`
  ATTRIBUTE (concept_scan.py:397-405), not the loop; `sorted(key=)`/`max`/`min` `key=` is NOT scanner-flagged
  in Book 1b (unregistered `sorted-key` feature) → tier-C, Phase-E-audit-only.
- `[FIXED]` ([glm] new nit) cp04's list+dict combine question reads `words[i]` by index — a genuine
  `list-index` site (cp04 is its only pre-078 practice site).

### Round 3 (2026-09-23) — re-dispatched [sol]/[glm]/[fable].
**CONSENSUS — [self] APPROVE; [sol] APPROVE; [glm] APPROVE; [fable] APPROVE.** All blockers/nits resolved
across 3 rounds ([fable]'s r3 range-in-list-index nit fixed by making the cp04 site positional). Contract +
practice-coverage-debt ledger + tier claims all match the tooling. No open findings. **Plan-review gate PASSED.**

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report

**Status: implemented, ci-local ALL GREEN (2026-09-23). Content-review gate next.**

- **Phase B:** coverage-map entries (U11 + cp04) + 2 manifests + 2 syllabus rows; coverage-check/prereq-check
  GREEN; 52→55 introduced-once, no dupes.
- **Phase C (Codex):** U11 `lesson.ipynb` (problem-first opener; dict-literal/access, `key in d` tests keys,
  `KeyError` fenced markdown + `get`; dict-loop `items()`; most-common `find-extreme`; missing-key tally;
  explicit group-by; leaderboard sort; keys filter) + `exercises.ipynb` (9, 2 stretch); cp04 `checkpoint.ipynb`
  (7 Questions; the list+dict question reads `words[0]` positionally).
- **Phase D (SEPARATE fresh Codex):** U11 + cp04 `solutions.ipynb` (function form; 27/21 non-vacuous asserts;
  no forbidden methods/forms; winner asserts use unique maxima).
- **Phase E:** teacher-notes for U11 + cp04 (full heading sets; cp04 `## Grading` with two named pass-bar
  items + concrete value inventories). `TMPDIR=/dev/shm bash scripts/ci-local.sh` → **ALL GREEN**
  (concept-scan, exec-solutions, checkpoint questions, notebook exec+hygiene, manifest/prereq/coverage/stretch,
  PDF, pre-merge-guard). Static AST audit clean: dict methods ⊆ {items,keys,values,get}, list ⊆ {append,sort},
  string ⊆ {upper,lower,strip,replace}, builtins in-set + no `key=`; no `ord`/`chr`/`collections`/
  comprehensions/tuple-assignment/step-slices; cp04 no range/sorted/while/bool-ops/+concat.

No deviations from the approved plan. (Design §6 deferred-practice-debt: `transform-each`/`linear-search`/
`string-slice` land in U12/U13 — plan 077 must list them.)

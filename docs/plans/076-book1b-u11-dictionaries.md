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
  comparison, boolean, arithmetic, variable, print]`
- practices: `[list-literal, list-append, string-methods, count-by-condition, accumulator, builtin-functions,
  find-extreme, int-type, f-string, comment, naming]`

**checkpoint-04-dictionaries** — `kind: checkpoint`, `title: "Checkpoint 4 — Dictionaries & Collections"`, `lessons: 0.5`
- introduces: `[]`
- requires: `[print, variable, def-function, parameters, return-value, dict-literal, dict-access, dict-loop,
  in-operator, for-loop, list-loop, list-literal, if-statement, elif-else, comparison, boolean, arithmetic,
  builtin-functions, f-string, string-literal, type-conversion]`
- practices: `[print, variable, def-function, parameters, return-value, dict-literal, dict-access, dict-loop,
  in-operator, for-loop, list-loop, list-literal, list-index, if-statement, elif-else, comparison, boolean,
  arithmetic, count-by-condition, accumulator, builtin-functions, int-type, f-string, string-literal,
  type-conversion]`

Closure: U11 requires ⊆ U01–U10 (def/params/return U07, for-loop U05, list-loop U10, in-operator U09, if U03,
comparison/boolean/arithmetic U02, variable/print U01). cp04 requires/practices ⊆ U01–U11 (checkpoints get NO
fastforward — every concept a question uses is listed). No self-practice. After this plan: 52 → 55
introduced-once (adds the 3 dict concepts; cp04 introduces none). 7 remain (files 3 / objects 4).

### Design §6 practice-coverage record
U11 practices earlier concepts at genuine sites: `list-literal`/`list-append` (group-by builds a list as each
value), `string-methods` (`lower()` before keying), `count-by-condition`/`accumulator` (tallies/frequency
maps), `builtin-functions` (`len`/`max`/`sorted` over keys/values), `find-extreme` (the most-common key via a
loop over items), `int-type` (counts), `f-string`/`comment`/`naming`. cp04 anchors the U01–U11 foundational
practices (Book-1 checkpoint style). No unit lists its own introductions in `practices`.

## Tooling pins (enforcement tiers — same model as plan 075)

- **CI-enforced (concept-scan):** dict methods = ONLY `items`/`keys`/`values`/`get` (DICT_METHODS,
  concept_scan.py:64); any other `.name(...)` flagged untaught. `dict-literal`/`dict-access`/`dict-loop`
  detected from `{}`/subscript-on-dict/`.items()` looping (reviewers confirm the concept is genuinely present;
  some dict facets are declaration + reviewer-verified). Built-ins ⊆ {len,min,max,sum,sorted,abs,round};
  list methods ⊆ {append,sort}; string methods ⊆ {upper,lower,strip,replace}.
- **NOT scanner-flagged in Book 1b (enforced by reviewers + my Phase-E static AST/grep audit):** `ord`/`chr`,
  comprehensions (incl. DICT comprehensions `{k: v for …}`), tuple/multiple assignment, step slices.
  **Build dicts by assignment in a loop (`d[k] = …`), never a dict comprehension.**
- **`d[key] += 1` is multiple-assignment-free but uses `+=`** — `+=` is the `accumulator` idiom taught from
  U04 (allowed). Prefer the explicit `d[k] = d[k] + 1` if a reviewer flags `+=`; both are fine post-U04.
  The **missing-key idiom** is `if k in d: d[k] = d[k] + 1` / `else: d[k] = 1` (or `d.get(k, 0)`), taught
  explicitly — never `collections`/`defaultdict` (untaught modules).
- **cp04 strict discipline** (no fastforward): join text with f-strings (list `string-literal` since
  literal-bearing f-strings detect both); list `type-conversion` if `int()`/`str()` used; list `logical-ops`
  only if a question uses `and`/`or` (else avoid them). No `ord`/`chr`/comprehensions/tuple-assignment.
- Function form: solutions define the function + assert several distinct cases; ≥3 non-vacuous assert cells;
  no `input()`; unique cell ids; student notebooks solution-free with NO executed outputs.

## Teaching outline

### U11 Dictionaries (3 lessons, problem-first, function form)
- **L1 — Key/Value Maps (`dict-literal`, `dict-access`).** A dict as a labelled lookup: `{"gold": 3, …}`;
  read with `d[key]`; the **`KeyError` trap** for a missing key and the safe `d.get(key, default)`; add/update
  with `d[key] = value`; `key in d` membership. A lookup table (e.g. Roman-numeral values, price list).
- **L2 — Loop over a Dictionary (`dict-loop`).** `for key in d`, `for key, value in d.items()`; `d.keys()`/
  `d.values()`; sum the values; find the key with the largest value (a `find-extreme` over `d.items()`).
- **L3 — Build Maps from Data.** A **frequency map** / tally (count items with the missing-key idiom or
  `d.get(k, 0) + 1`); a **group-by-first-letter** (each value is a LIST built with `append`). Put it together
  (e.g. a word-length tally, a vote counter).
60-min cut per lesson in teacher-notes.

### Checkpoint 04 (after U11, strict, no turtle, no fastforward)
6–7 VISIBLE `## Question N`. Mix: build/read a lookup dict; a `d.get`-with-default question; a frequency-map
tally; a loop-over-`items` sum or count; the most-common-key (`find-extreme` over items); an `elif`/lookup
question; and one that combines a list with a dict (e.g. tally a list of words). Strict — only concepts ≤ U11;
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
taught subsets; builtins within the set; no `ord`/`chr`; no comprehensions (incl. dict comprehensions); no
tuple/multiple assignment; no step slices. Scope allowlist = this plan + the U11/cp04 trees + coverage-map + syllabus.

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
_(Awaiting [sol]/[glm]/[fable].)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(Filled before shipping.)_

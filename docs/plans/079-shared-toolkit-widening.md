# Plan 079 — Widen the Book 1 / Book 1b scanner toolkit

**Goal:** Let Book 1 and Book 1b use the everyday CP facets `split`/`join`, `isdigit`/`isalpha`,
`find`/`startswith`/`endswith`, list `pop`/`insert`/`remove`/`index`, and `continue`, each mapped
to an EXISTING, scanner-enforced concept so code-cell closure still catches premature use.
Book 2 is left exactly as it is.
First plan of the Book 1b enrichment initiative.

**Spec:** `docs/designs/006-book1b-enrichment.md` §2 D1–D2 (user decision 2026-09-24:
"widen for both books" — i.e. Book 1 and Book 1b, the two books sharing the 62-concept catalog).

## Scope

### 1. `tools/concept_scan.py`

- **Scoping (own-catalog key).** Add `features: frozenset[str] = frozenset()` to `ScanProfile`
  (~L73) and populate it in `scanner_profile(concepts)` (~L79-103) with the profile's registered
  concept ids. Add a module constant
  `WIDENED_METHODS = {"split", "join", "isdigit", "isalpha", "find", "startswith", "endswith",
  "pop", "insert", "remove", "index"}` and, in `scanner_profile`, add it to `taught_methods`
  **only when `"string-methods"` is registered** (true for Book 1 and Book 1b's own catalogs; false
  for Book 2's own catalog). The global `TAUGHT_METHODS` / `STRING_METHODS` constants are NOT changed,
  so Book 2 profiles, Book 2's GIVEN-region borrowed-method mechanism (~L1300), and Book 2's source
  policy are untouched.
- **Detection (in `visit_Attribute` ~L396-425, gated on `active_profile.taught_methods` containing
  the method so Book 2 behavior is identical):**
  - `join, isdigit, isalpha, find, startswith, endswith` → `string-methods`.
  - `split` → `if "str-split" in active_profile.features: add_feature("str-split")` (Book 2, and any
    Book 1 cell that explicitly declares `book2:str-split` — its per-cell profile
    `scanner_profile(concepts + _declared_owner_concepts(...))` ~L1182-1184 carries `str-split`, so
    design-004 semantics and the checked-in real-form fixtures are preserved);
    `elif "split" in active_profile.taught_methods: used.add("string-methods")` (gated, so a profile
    without `string-methods` — e.g. a test fixture catalog — never emits an unregistered concept). The key is the **profile**, never `registered_concepts`
    (the Book 1 v2 path's `entry_registered` includes Book 2 dependent-feature owners, ~L1148-1152 /
    ~L816-855, which is exactly why a Book 1 fence resolves to `book2:str-split` today).
    Do not key on `"split" in taught_methods` (always true for Book 1/1b after this plan).
  - `pop`, `insert`, `remove` → `list-append`. The existing set-ops branch becomes an **elif guard**:
    `remove` on a known `set_names` receiver emits `set-ops` ONLY (never also `list-append`).
    Code comment documents that `remove` on a set that is not a tracked set name (e.g. a parameter)
    attributes to `list-append` (closure-safe: sets only exist in Book 2, whose baseline holds all
    Book 1 concepts).
  - `index` → `list-index`, and **remove `list-index` from `MANUAL_ONLY`** (~L40). Safe: no other
    detector emits `list-index` (`visit_Subscript` ~L337-340 does not), so this makes `.index()`
    closure-enforced and changes nothing else (prototype-verified by [fable]: all three books'
    concept-scan PASS).
- **`continue`**: new `visit_Continue` → `break-statement`, mirroring `visit_Break`.
- **`detect()` no-profile fallback**: build it as `scanner_profile([{"id": r} for r in registered])`
  so direct `detect(tree, registered_concepts={...})` callers (e.g.
  `test_book2_tooling.py::test_new_feature_detector_is_registry_gated`) keep their semantics.
- **Dropped from the user's candidate list: `count`.** `str.count` vs `list.count` cannot be told
  apart by the scanner, so any mapping either over- or under-attributes. Counting stays taught as the
  `count-by-condition` technique (a loop), which is the better pedagogy anyway; `count` stays an
  untaught method.

### 2. Catalog names (ids unchanged), edited identically in `book1/` and `book1b/curriculum/concepts.yaml`

- `string-methods` → `"String methods (case, strip/replace, split/join, find, is-tests)"`
- `list-append` → `"Growing and changing lists (append/insert/pop/remove)"`
- `list-index` → `"List indexing (and .index)"`
- `break-statement` → `"Loop control (break/continue)"`

The `variant_of` check (`tools/curriculum.py:108-119`) compares the full parsed catalogs, so
identical edits keep it green; no tool, test or PDF consumes these display names.

### 3. Tests

**Tests expected to CHANGE** — [fable]'s round-2 prototype: exactly **5 tests / 7 cases** fail as-is.
The `_scanner_root` fixture catalog (`tests/test_borrowed_tools_scan.py:83-92`) does NOT register
`string-methods`, and this plan keeps it that way, so the widening is inert there; only the targeted
tests below change:

| test | new expectation |
|---|---|
| `test_borrowed_tools_scan.py::test_markdown_general_closure_ignores_input_but_rejects_undeclared_split` (~L425) | fixture registers `string-methods` with a LATER home (pattern: `_add_future_list_home` ~L453); fence `words = input().split()` in the earlier entry → `undeclared borrowed tool book1:string-methods`; add a positive twin at/after the home → no finding |
| `::test_unauthorized_split_keeps_untaught_method_finding` (~L1487) | keep its `untaught method split` assertion (fixture has no `string-methods`); drop only the `book2:str-split` assertion |
| `::test_split_rejects_wrong_book_owner_declaration` (~L1499) | metadata finding still fires; drop the `book2:str-split` undeclared assertion |
| `::test_attributed_python_fence_scans_undeclared_split` (~L531, 2 params) | fence `split` resolves via `string-methods` (future-home fixture) |
| `::test_python3_markdown_fence_is_scanned_for_borrowed_tools` (~L680, 2 params) | same |

**Tests that MUST keep passing unchanged** (regression guard, prototype-verified with the
profile-keyed mechanism): `test_v1_book1_split_preserves_exact_legacy_finding`,
`test_method_profile_authorization_is_cell_local`,
`test_exercise_method_authorization_is_limited_to_given_region` (all three stay as-is because the
fixture catalog lacks `string-methods`), `test_checked_in_borrowed_tool_shape_passes_cleanly`,
`test_authorized_book2_split_in_markdown_passes_without_duplicate_registry_id`,
`test_solution_real_form_without_given_region_needs_no_pairing_id`,
`test_markdown_unused_check_aggregates_all_fences_in_cell`, the checked-in
`tests/fixtures/borrowed_tools/{lesson-real-form,markdown-real-form}` fixtures (which declare
`book2:str-split` and therefore keep `str-split` semantics via their per-cell profile),
`test_book2_tooling.py` (incl. the registry-gated detector test via the no-profile fallback and the
L365-389 no-mutation test), `test_judge_policy.py`, `test_book1b_tooling.py`.

**New tests** (`tests/test_concept_scan.py`):
- Book 1-style profile (catalog registers `string-methods`): positive detection for EVERY widened
  method — `split, join, isdigit, isalpha, find, startswith, endswith` → `string-methods`;
  `pop, insert, remove` → `list-append`; `index` → `list-index`; `continue` → `break-statement`;
  none reported as untaught.
- Book 1 profile with Book 2 registered in `registered_concepts` (dependent-feature owner) →
  `split` still `string-methods`; Book 1 cell profile that declares `book2:str-split` → `str-split`.
- Book 2-style profile (no `string-methods`, registers `str-split`): `split` → `str-split` and NOT
  `string-methods`; `insert`, `isalpha`, `startswith`, `pop`, `index`, `join` still reported untaught
  (pins inherited Book 2 semantics).
- Set-ops profile: `s.remove(x)` on a known set → `set-ops` only (no `list-append`).
- `count` still untaught in every profile; `title`/`extend` still untaught.
- End-to-end negative closure (via `concept_scan_findings` on a tmp repo): a STRICT checkpoint entry
  whose allowed set lacks `list-index` calling `xs.index(3)` → `used-but-unlisted concept list-index`;
  lacking `break-statement` using `continue` → finding; lacking `string-methods` using `s.split()` →
  finding.

## Enforcement boundary (stated honestly)

- **Code cells**: all widened facets are closure-enforced for Book 1 (map v2) and Book 1b (map v1
  legacy scan), strict for checkpoints/projects and fastforward for Book 1b units.
- **Markdown fences**: Book 1 (v2) fences get only the design-004 future/declared borrowed-tool
  check (~L1255-1270), not ordinary closure. **Book 1b (v1) fences are not scanned at all**
  (`_legacy_scan_findings` reads code cells only). So Book 1b's CP "real program" fences (plans
  080-084) are reviewer-enforced, and every content plan's static AST/grep audit MUST parse every
  fenced python block (esp. in checkpoints/project) against the entry's allowed set.
  A fastforward-aware fence scan for v1 books is a possible follow-up, out of scope here.

## Phases

- **Phase A (Codex, tooling, TDD):** write the new/changed tests first (see them fail), then
  implement Scope 1.
- **Phase B (inline):** Scope 2 catalog names in both books.
- **Phase C — VERIFICATION:** `pytest tests/` GREEN; `TMPDIR=/dev/shm bash scripts/ci-local.sh`
  ALL GREEN for Book 1, Book 1b, Book 2; post-execution report.

## Out of scope

- **Tooling/catalog-only plan**: ships no unit/project/checkpoint content, so the content
  verification phase is replaced by Phase C (tests + full ci-local), per AGENTS.md.
- No Book 2 behavior change (widening is gated on the own catalog registering `string-methods`).
- No content changes; no `count`, `enumerate`, `zip`, tuple unpacking; no new catalog ids;
  no v1 fence scanning.

## Plan Review

### Round 1 — verdicts (HEAD cffe3df)

- `[self]` APPROVE WITH NITS — design D3 `split` ramp should say where multi-number parsing starts.
- `[sol]` **REJECT** — `index`→`list-index` not closure-safe (`list-index` is MANUAL_ONLY); `count`
  ambiguous; global widening leaks into Book 2; split-keying input must be pinned; the markdown-fence
  closure claim contradicts control flow; affected-test inventory incomplete.
- `[glm]` **REJECT** — same `index`/MANUAL_ONLY hole; Book 2 "no change" claim false under a global
  widening; ~15 affected tests unnamed incl. the checked-in real-form fixture cluster; set-receiver
  `remove` needs an elif guard; D3/`continue` nits.
- `[fable]` **REJECT** — prototyped the change: 11 tests fail, only 1 named; supplied the working
  mechanism (`ScanProfile.features` from the own catalog; per-cell declared-owner profile keeps
  design-004 semantics); drop `list-index` from MANUAL_ONLY is safe; Book 1b (map v1) fences are not
  scanned at all; D3 `split`+`int()` belongs in U10.

### Round 1 — fold (this rewrite)

- `[FIXED]` widening scoped to profiles whose own catalog registers `string-methods` (Book 1/1b);
  global pins and Book 2 untouched; Book 2 inherited semantics pinned by a test.
- `[FIXED]` `split` keyed on `ScanProfile.features` (never `registered_concepts`); declared
  `book2:str-split` cells keep design-004 semantics, so the real-form fixtures stay unchanged.
- `[FIXED]` `index` → `list-index` + `list-index` removed from `MANUAL_ONLY` (enforced).
- `[FIXED]` `count` dropped (ambiguous); stays untaught.
- `[FIXED]` set-receiver `remove` → `set-ops` only (elif guard); `visit_Continue` mirrors `visit_Break`;
  `detect()` no-profile fallback builds a profile from `registered_concepts`.
- `[FIXED]` full affected-test table (8 tests/11 cases re-expressed) + must-keep-passing list + new
  positive/negative/end-to-end tests.
- `[FIXED]` enforcement boundary stated honestly (v2 fences: borrowed-tool check only; v1 fences
  unscanned → reviewer + per-plan AST audit); design 006 D2/D3/rollout updated (U09 split = word
  iteration; multi-number parsing in U10; `continue` home explicit).

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_

### Round 2 — verdicts (HEAD 7510ae2)

- `[self]` APPROVE.
- `[sol]` APPROVE — all six r1 items resolved; no new findings (no shipped `.index()` anywhere).
- `[fable]` APPROVE WITH NITS — re-prototyped: 5 tests / 7 cases fail (a strict subset of the table),
  641 pass; static checks PASS for all three books; no Book 2 leak; end-to-end enforcement verified on a
  real strict checkpoint. Nits: correct the test table (3 rows unchanged because the fixture catalog
  lacks `string-methods`); gate the `split` else-branch; say which assertion each split test keeps.
  **All three nits folded** (table corrected, `elif` gate, per-test assertion choice).

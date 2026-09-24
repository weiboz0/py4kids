# Plan 079 — Widen the shared scanner toolkit (both books)

**Goal:** Let Book 1 and Book 1b use the everyday CP facets `split`/`join`, `isdigit`/`isalpha`,
`count`/`find`/`startswith`/`endswith`, list `pop`/`insert`/`remove`/`index`, and `continue`,
each mapped to an EXISTING concept so prereq closure still catches premature use.
First plan of the Book 1b enrichment initiative.

**Spec:** `docs/designs/006-book1b-enrichment.md` §2 D1–D2 (user decision 2026-09-24:
"widen for both books").

## Scope

1. `tools/concept_scan.py`:
   - `TAUGHT_METHODS` gains `split, join, isdigit, isalpha, count, find, startswith, endswith,
     pop, insert, remove, index` (so none is reported as an "untaught method").
   - `STRING_METHODS` gains `join, isdigit, isalpha, count, find, startswith, endswith`
     → detected as `string-methods`.
   - `split`: when the **scanned book's own** concept catalog registers `str-split` (Book 2) keep
     `add_feature("str-split")` exactly as today; otherwise (Book 1, Book 1b) detect `string-methods`.
     **This must key on the scanned book's own catalog, not the cross-book qualified registry** —
     the design-004 borrowed-tools scan of markdown fences (`test_borrowed_tools_scan.py:425`)
     currently resolves a Book 1 fence's `input().split()` to `book2:str-split`; after this plan a
     Book 1/1b fence's `split` is ordinary `string-methods` (subject to normal closure), which is
     what lets Book 1b's CP "real program" blocks use `input().split()`.
   - `pop`, `insert`, `remove` → `list-append` (list mutation facet). The existing Book 2 set-ops
     branch (`remove` on a known set name → `set-ops`) keeps precedence and is unchanged.
   - `index` → `list-index`.
   - New `visit_Continue` → `break-statement` (loop-control facet). No other statement changes.
   - `count` is ambiguous between `str.count` and `list.count`; both map to `string-methods`
     (documented in a code comment; closure-safe because `string-methods` precedes lists in both books).
2. Catalog names (ids unchanged), edited **identically** in `book1/curriculum/concepts.yaml` and
   `book1b/curriculum/concepts.yaml` so the `variant_of` content-identity check stays green:
   - `string-methods` → `"String methods (case, strip/replace, split/join, find/count, is-tests)"`
   - `list-append` → `"Growing and changing lists (append/insert/pop/remove)"`
   - `break-statement` → `"Loop control (break/continue)"`
3. Tests (`tests/test_concept_scan.py`, plus any existing test that pinned the old behavior):
   - Book 1-style profile: `line.split()` → `string-methods`, no unknown methods;
     `"-".join(parts)`, `s.isdigit()`, `s.find("x")`, `s.startswith("a")` → `string-methods`.
   - Book 2-style profile (`str-split` registered): `split` → `str-split`, not `string-methods`.
   - `xs.pop()`, `xs.insert(0, 1)`, `xs.remove(3)` → `list-append`; `xs.index(3)` → `list-index`.
   - Book 2 set-ops profile: `remove` on a set name still → `set-ops`.
   - `for ... : continue` → `break-statement`.
   - A still-untaught method (e.g. `s.title()`, `xs.extend(...)`) is still reported untaught.
   - Update any existing assertion that `.split`/`.index` are untaught for Book 1.
   - `test_borrowed_tools_scan.py::test_markdown_general_closure_ignores_input_but_rejects_undeclared_split`:
     re-express for the new semantics — a Book 1 fence `words = input().split()` in an entry whose
     allowed set lacks `string-methods` fails as an ordinary closure finding for `string-methods`
     (not `book2:str-split`); add the positive case (entry that allows `string-methods` → no
     finding); keep/confirm a Book 2-context test where `split` still resolves to `str-split`.

## Phases

- **Phase A (Codex, tooling):** implement Scope 1 + 3 with tests (TDD: write the failing tests
  first, then the change).
- **Phase B (inline):** Scope 2 catalog names in both books.
- **Phase C — VERIFICATION:** `pytest tests/` GREEN; `TMPDIR=/dev/shm bash scripts/ci-local.sh`
  ALL GREEN for Book 1, Book 1b and Book 2 (proves no content regressed under the widened pins and
  Book 2's `str-split` semantics are intact); post-execution report.

## Out of scope

- **Tooling-only plan:** it ships no unit/project/checkpoint content, so the content verification
  phase is replaced by Phase C (tests + full ci-local) — stated per AGENTS.md.
- No content changes in any book (Book 1b content enrichment is plans 080–084).
- No `enumerate`/`zip`/tuple unpacking; no new catalog ids; no Book 2 behavior change.

## Plan Review
_(4-way plan-review gate — filled before implementation.)_

## Content Review
_(4-way content-review gate — filled before PR.)_

## Post-Execution Report
_(filled before merge.)_

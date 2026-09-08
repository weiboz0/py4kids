# Plan 017 — Book 2 Infrastructure (cross-book registry + curriculum foundation)

**Goal:** Stand up Book 2's foundation with NO lesson content: teach the verification tooling
cross-book prerequisite resolution, add the two-tier (feature vs technique) concept model, and author
Book 2's `concepts.yaml`, the full-arc `coverage-map.yaml`, and `syllabus.md` — so closure discipline
works from Book-2 unit 1.

**Architecture:** Two coupled workstreams. (A) tooling: read `books.yaml depends_on`, seed the
"already-taught" baseline for a dependent book with its dependency's introduced concepts, and make
`concept-scan` two-tier + per-book-aware. (B) curriculum: Book-2 `concepts.yaml` (new ids, each
tagged `kind: feature|technique`), the full ~18-entry `coverage-map.yaml` arc, and a real
`syllabus.md`. No `book2/units|checkpoints|projects` content is created — those are per-unit plans.

**Spec:** `docs/designs/001-book2-algorithms.md` (Book-2 design, esp. §5 two-tier registry, §6
cross-book infra, §7 arc, §8 pacing); `books.yaml` (`book2 depends_on book1`); the shipped `tools/`
package (`curriculum.py` prereq/coverage, `concept_scan.py`, `checks.py`, `cli.py`); Book-1 plan 002
(curriculum) + plan 003 (tooling) as precedent; plan 016 (concept-scan) for the check contract.

## Global Constraints

- **Flat shared concept namespace (design decision, refines design-000's "namespaced ids"):**
  Book-1 concept ids stay BARE (already shipped that way); Book-2 `concepts.yaml` adds only NEW,
  globally-unique ids (e.g. `set-literal`, `binary-search`) — no `book1:` prefix, no redefinition or
  shadowing of a Book-1 id. Cross-book ordering is total: **all of Book 1 precedes all of Book 2**
  (per `depends_on`), so a Book-2 entry may reference any Book-1 concept as an available prerequisite.
  A CI check MUST reject any Book-2 id that collides with a Book-1 id (enforce global uniqueness).
- **Cross-book taught-baseline (tooling):** for a book whose `books.yaml` entry has
  `depends_on: [X]`, the taught baseline before its first entry = the union of every concept X
  `introduces` (transitively across X's dependencies, though only one level exists now). `prereq-check`
  and `coverage-check` seed their cumulative "seen/taught" set with this baseline; `concept-scan`
  adds it to each entry's allowed union. Book-1 runs UNCHANGED (empty `depends_on` → empty baseline).
- **Two-tier concept model (design §5):** every `concepts.yaml` entry carries `kind: feature` or
  `kind: technique`. `feature` = AST-detectable language construct (sets, tuples, `.split`,
  `sorted(key=…)`, comprehensions, recursion-as-self-call, `deque`, bitwise ops). `technique` =
  algorithmic pattern no scanner can see (`complete-search`, `greedy`, `prefix-sum`, `binary-search`,
  `two-pointers`, `backtracking`, `bfs`, `dfs`, `flood-fill`, `graph-repr`, `tree-traversal`,
  `base-conversion`, `sieve`, `gcd`, `modular-arithmetic`, `boolean-algebra`, `postfix-eval`,
  `bitmask`, `code-tracing`). `concept-scan` enforces `feature` concepts only; `technique` concepts
  are treated like `MANUAL_ONLY` (tracked for prereq/coverage closure, never scanner-flagged). Book-1
  concepts are all implicitly `feature`-or-fuzzy as today; the `kind` field is additive and optional
  where absent (Book-1 `concepts.yaml` is NOT rewritten).
- **`concept-scan` per-book constants (plan-016 nit):** `TAUGHT_METHODS`/`BUILTINS`/`MANUAL_ONLY` are
  book1-coupled. Make the scanner's taught-method/builtin/never-flag sets **per-book**, derived where
  possible from the registry (a `technique`-kind or fuzzy concept joins the never-flag set; Book-2
  language features like `.split`, deque/set methods extend the taught-method set). Book-1 behaviour
  is byte-for-byte unchanged (regression-tested).
- **No content, no per-entry dirs:** plan 017 creates the MAP + registry + syllabus only. Book-2 unit
  dirs (`lesson.ipynb` etc.) do NOT exist yet, so per-entry checks (`structure-check`,
  `manifest-check`, exec/hygiene) MUST NOT run against Book-2 in ci-local yet — only the MAP-LEVEL
  checks (`prereq-check`, `coverage-check`, `concept-scan`) are wired for Book 2 now; per-entry checks
  come online as units land (their plans add them). `concept-scan` over content-less entries yields
  zero used concepts → PASS.
- **Closure holds on the skeleton:** the authored map's `introduces`/`requires` must satisfy
  `prereq-check` + `coverage-check` against the Book-1 baseline (every Book-2 `requires` is either a
  Book-1 concept or introduced by an earlier Book-2 entry; `practices ∩ introduces` empty per entry).
  Practices lists start minimal/empty and are AMENDED per-unit when content is authored (Book-1
  precedent). `introduces` places each Book-2 concept at its design §7 home unit.
- **The `solve(data)` contract + mock-contest format are DOCUMENTED in `syllabus.md`** (binding
  convention, enforced by future content gates) — not code in this plan.
- Process (standing): no commits while a `[sol]` review is in flight; branch before drafting; codex
  prompts name the in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

This is a **tooling + curriculum-registry plan; it ships NO units/projects/checkpoints**, so the
reviewer-REJECT-without-verification rule is satisfied by Phase C (the named verification phase).
Out of scope: any `book2/units|checkpoints|projects` content or notebooks; per-unit practices
tuning (amended per-unit later); wiring Book-2 per-entry checks into ci-local (added as content
lands); retrofitting Book-1 concept ids to a namespaced form; Book-1 `concepts.yaml` edits;
extracting a shared "sample judge" helper (deferred to first content plan if needed).

## Phases

Dispatch per AGENTS.md: tooling (`tools/`) via codex; curriculum (`concepts.yaml`/`coverage-map.yaml`/
`syllabus.md`) authored inline (curriculum architecture) with codex assist for bulk YAML if useful.

### Phase A — cross-book tooling + two-tier scanner (codex)

1. `books.yaml` loader helper: resolve a book's `depends_on` and compute the dependency baseline
   (union of the dependency book's `introduces`). Add to `tools/curriculum.py` (or a small
   `tools/books.py`).
2. Seed `prereq_findings` and `coverage_findings` cumulative sets with the baseline for a dependent
   book; Book-1 (empty deps) unchanged.
3. Global-uniqueness check: a Book-2 concept id colliding with any Book-1 id is a finding (new check
   or folded into an existing registry-schema check).
4. `concept_scan.py`: read the per-entry allowed union PLUS the cross-book baseline; make
   never-flag/taught-method/builtin sets per-book (registry-driven for `technique`/fuzzy kinds);
   Book-1 unchanged.
5. Tests: (a) cross-book baseline resolves — a Book-2 entry requiring a Book-1 concept passes
   prereq-check; (b) a Book-2 entry requiring a concept taught NOWHERE ≤ it still FAILS; (c) a Book-2
   lesson using a Book-1 feature is NOT flagged used-but-unlisted; (d) a `technique`-kind concept is
   never scanner-flagged; (e) a Book-1↔Book-2 id collision is caught; (f) Book-1 regression — every
   existing check identical.
- Acceptance (A): `ruff` clean; `uv run pytest -q` green (incl. new tests); Book-1 `ci-local` still
  ALL GREEN.

### Phase B — Book-2 curriculum registry + syllabus (inline)

1. `book2/curriculum/concepts.yaml` — all new Book-2 concept ids, each `{id, name, category, kind}`
   with `kind: feature|technique` per design §5. (Language features: set-literal, set-ops, tuple,
   str-split, input-parse, grid-2d, sorted-key, comprehension, recursion, deque, bitwise-ops, …;
   techniques: the §5 tag list.)
2. `book2/curriculum/coverage-map.yaml` — the full ~18-entry arc (U01–U14 + CP1–CP3 + capstone) from
   design §7: each entry `{id, kind, title, lessons, term, introduces, requires, practices}`.
   `introduces` places each Book-2 concept at its design §7 home unit; `requires` lists the Book-1
   baseline concepts + earlier Book-2 concepts each unit leans on; `practices` starts minimal (amended
   per-unit later). Entry order = the design's term order (closure-safe: U05 has no bitmask/recursion;
   trees/graphs after recursion+deque; etc.).
3. `book2/syllabus.md` — replace the placeholder: the four-term arc, per-unit lesson budget + the §8
   pacing contract (Term 4 compressible buffer), the binding `solve(data:str)->str` judge contract,
   the timed mock-contest checkpoint format, rich-problem-set goal, and the cross-book prerequisite
   note.
- Acceptance (B): `prereq-check`, `coverage-check`, `concept-scan` all PASS for `--book book2`
  against the Book-1 baseline; global-uniqueness PASS; `practices ∩ introduces` empty per entry.

### Phase C — Verification (NAMED, mandatory)

Mechanical: `ruff` clean; `uv run pytest -q` green (incl. all new cross-book + two-tier tests);
wire ONLY Book-2 MAP-LEVEL checks (`prereq-check`/`coverage-check`/`concept-scan --book book2`) into
`scripts/ci-local.sh`; full `ci-local.sh` ALL GREEN (Book-1 per-entry + Book-2 map-level); Book-1
behaviour unchanged (regression); the Book-2 map closes against the Book-1 baseline; no Book-2
content dirs exist (per-entry checks correctly NOT run for Book 2).
Reviewer duties (both gates): the cross-book baseline is correct (Book-1 concepts available to Book 2,
nothing leaks the other way); the two-tier split is right (every `technique` id is genuinely
non-AST-detectable; every `feature` id is detectable); Book-1 regression is exact; the Book-2 arc
order is closure-safe (spot-check U05 no-bitmask/recursion, trees after recursion, BFS after deque);
the syllabus states the `solve` contract + pacing contract; global uniqueness enforced.

**Acceptance criteria:** cross-book tooling + tests shipped; Book-2 `concepts.yaml` + full-arc
`coverage-map.yaml` + `syllabus.md` authored and closing green against the Book-1 baseline; ci-local
ALL GREEN with Book-2 map-level checks wired; Book-1 unchanged; plan-review + content-review 4-way
consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. This is the design's mandated "plan 1" — infrastructure before content, so closure works
from Book-2 unit 1. Scope is deliberately tooling + registry + syllabus, NO lesson content (Phase C
is the named verification phase; the tooling-only exemption is stated). The cross-book baseline is a
focused, testable addition (`depends_on` → seed the taught set), Book-1 runs unchanged (empty deps),
and the two-tier `kind` field cleanly formalizes the "necessary-not-sufficient" line already drawn by
`MANUAL_ONLY` — techniques tracked for closure, never scanner-flagged. The flat-namespace decision
(Book-1 ids stay bare, Book-2 adds unique ids, global-uniqueness enforced) is simpler than
retrofitting `book1:` prefixes onto a shipped book and loses nothing given total Book-1-precedes-Book-2
ordering; it is called out as a refinement of design-000. The "no per-entry dirs yet → only map-level
checks wired for Book 2" handling mirrors the Book-1 Phase-A/manifest-before-dir lesson (plans
014/015). Risk to watch at the gate: the exact `introduces`/`requires` assignments in the 18-entry
map (closure correctness) and that every `technique` id is truly non-detectable — both are explicit
reviewer duties.

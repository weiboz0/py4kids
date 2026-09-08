# Plan 017 — Book 2 Infrastructure (cross-book registry + curriculum foundation)

**Goal:** Stand up Book 2's foundation with NO lesson content: make the verification tooling
per-book and cross-book aware, add the two-tier (feature vs technique) concept model **with real
feature detectors**, and author Book 2's `concepts.yaml`, the full-arc `coverage-map.yaml`, and
`syllabus.md` — so closure discipline (and feature-level `concept-scan`) works from Book-2 unit 1.

**Architecture:** Two coupled workstreams. (A) tooling: read `books.yaml depends_on`; seed the
"already-taught" baseline for a dependent book; **de-couple every Book-1 hardcoding in
`tools/curriculum.py`'s coverage/prereq suite and make it per-book**; add real per-book-gated AST
feature detectors to `concept_scan.py`; enforce global concept-id uniqueness across all books.
(B) curriculum: Book-2 `concepts.yaml` (new ids, each `kind: feature|technique`), the full ~18-entry
`coverage-map.yaml` arc, and a real machine-checked `syllabus.md`. No `book2/units|checkpoints|
projects` content is created — those are per-unit plans. **Book 1 behaviour is byte-for-byte
unchanged (regression-locked).**

**Spec:** `docs/designs/001-book2-algorithms.md` (§5 two-tier, §6 cross-book infra, §7 arc, §8
pacing); `books.yaml` (`book2 depends_on book1`); the shipped `tools/` package — **verified call
sites**: `curriculum.py` `prereq_findings`(cumulative `seen`), `coverage_findings`(a COMPOSITION of
`concepts_schema_findings`+`referenced_concepts_findings`+`practice_findings`+`checkpoint_findings`+
`syllabus_findings`), `concept_scan.py` `detect()`/`concept_scan_findings`, `checks.py`, `cli.py`;
Book-1 plan 002 (curriculum) + plan 003 (tooling) precedent; plan 016 (concept-scan + practice
completeness).

## Global Constraints

- **Coverage is a COMPOSITION, not a cumulative-seen check (gate correction).** `coverage_findings`
  runs five sub-checks; seeding a baseline only fixes the cumulative ones (`prereq_findings`,
  `checkpoint_findings`). Every Book-1 hardcoding in the composition is a NAMED Phase-A work item
  (below). Nothing is left to mid-execution scope expansion (AGENTS.md forbids that without a plan
  amendment).
- **The Book-1-coupling inventory Phase A MUST de-couple (each per-book, Book-1 byte-identical):**
  1. `referenced_concepts_findings` — `known` set for `requires`/`practices` = **dependency baseline
     ∪ own-book registry**; `introduces` stays own-book-only (a book may not introduce a dependency's
     id).
  2. `practice_findings` (practice-completeness, plan 016) — the "every concept practiced before the
     capstone" rule and its **hardcoded capstone id `project-02-grand-adventure`** are Book-1-shaped.
     Derive the capstone from the book's own map (its `kind: project` finale), and **DEFER the
     pre-capstone-coverage requirement for a book whose content is not yet authored** (it re-enables
     once units land and amend practices). It must NEVER be satisfied by inventing practice data on a
     content-less skeleton.
  3. `concepts_schema_findings` — accept an OPTIONAL `kind: feature|technique` key; make the
     hardcoded `len(concepts) >= 40` floor **per-book** (Book 2's registry is ~31 ids); extend the
     `CATEGORIES` whitelist with algorithms categories (search, sorting, data-structures, graphs,
     number-theory, techniques, io). Book-1 registry unchanged and still passes.
  4. `map_schema_findings` — keep the existing exact key-set; therefore the map does **NOT** add a
     `term` field (term grouping lives in the syllabus, not the map schema).
  5. Capstone kind — the schema recognizes `unit|project|checkpoint`; the capstone is a
     `kind: project` Book-2 entry (a legal id, e.g. `project-book2-mock-contest`), so no kind-schema
     change is needed.
  6. `lesson_budget_findings` — the `28–32` workload bound is Book-1-shaped; make the bound per-book
     (Book 2 from its syllabus).
  7. `checkpoint_findings` — its cumulative seen-set also takes the baseline seed.
  8. `syllabus_findings` — Book-2 `syllabus.md` MUST carry the machine-checked `|id|kind|lessons|`
     table the check requires.
- **Cross-book taught-baseline:** for a book whose `books.yaml` entry has `depends_on: [X]`, the
  baseline before its first entry = the union of every concept X `introduces` (directional; ready to
  compose transitively though only one level exists now). Book-1 (empty `depends_on`) → empty
  baseline → unchanged.
- **Two-tier concept model WITH real detectors (design §5).** Every `concepts.yaml` entry carries
  `kind: feature|technique`.
  - `feature` = an AST-detectable construct. Phase A ADDS per-book-gated detectors to
    `concept_scan.py` `detect()` for the Book-2 feature set: `set-literal`/`set-ops` (Set/`&`|`|`|`-`
    on sets, set methods), `tuple`, `comprehension` (ListComp/SetComp/DictComp/GeneratorExp),
    `str-split` (`.split`), `sorted-key` (`sorted(..., key=…)`), `deque` + its methods, `recursion`
    (a function calling its own name), `bitwise-ops` (BinOp `&`/`|`/`^`/`<<`/`>>`, UnaryOp `~`).
    Each detector adds its concept to `used` **ONLY IF that concept id is in the CURRENT book's
    registry** (per-book gating) — so a Book-1 notebook that happens to use a tuple/`&`/`.split` is
    NOT newly flagged (Book-1 byte-identical).
  - `technique` = a pattern no scanner can see: `complete-search`, `greedy`, **`simulation`**,
    `prefix-sum`, `binary-search`, `two-pointers`, `backtracking`, `bfs`, `dfs`, `flood-fill`,
    `graph-repr`, `tree-traversal`, `base-conversion`, `sieve`, `gcd`, `modular-arithmetic`,
    `boolean-algebra`, `postfix-eval`, `bitmask`, `code-tracing`, **`complexity`** (Big-O),
    **`input-parse`**, **`grid-2d`** (the last two are usage patterns, not single AST nodes, so they
    are techniques, NOT features — gate finding). Techniques join the per-book never-flag set
    (alongside Book-1's `MANUAL_ONLY`) — tracked for prereq/coverage closure, never scanner-flagged.
  - Book-1 `concepts.yaml` is NOT rewritten; `kind` is additive/optional where absent.
- **Per-book scanner profile.** `TAUGHT_METHODS`/`BUILTINS`/never-flag are made **per-book** (an
  immutable profile chosen by `--book`): Book-1's stays the current literals; Book-2's extends
  taught-methods (`split`, `add`/`discard` on sets, `append`/`popleft` on deque, …) and its never-flag
  set = `MANUAL_ONLY` ∪ Book-2 technique ids. Book-1 profile byte-identical.
- **Flat shared namespace (recorded architecture decision — supersedes design-000 §"cross-book" and
  design-001 §6).** Book-1 ids stay BARE (already shipped); Book-2 adds only NEW globally-unique ids;
  no `book1:` prefix, no redefinition/shadowing. A CI check enforces **global uniqueness across ALL
  registered books** (not a Book-1↔Book-2 special case). Justified by total Book-1-precedes-Book-2
  ordering; recorded in this plan's `## Architecture decision` and errata-noted in design-001 §6.
- **No content, no per-entry dirs:** plan 017 creates MAP + registry + syllabus only. Book-2 unit
  dirs do NOT exist, so per-entry checks (`structure-check`/`manifest-check`/exec/hygiene) MUST NOT
  run against Book 2 yet — only MAP-LEVEL checks (`prereq-check`/`coverage-check`/`concept-scan
  --book book2`) are wired now (`concept-scan` skips absent dirs → PASS; verified by all three plan
  reviewers). Per-entry checks come online per-unit. `pre-merge-guard` already enumerates
  `book2/units|projects|checkpoints` safely while they hold only `.gitkeep`.
- **Closure holds on the skeleton:** the authored map's `introduces`/`requires` satisfy
  `prereq-check` + `coverage-check` against the baseline (every Book-2 `requires` is a baseline
  concept or introduced by an earlier Book-2 entry; `practices ∩ introduces` empty). `introduces`
  places each Book-2 concept at its design §7 home unit — including **`grid-2d`@U01** (U08's 2D
  prefix needs it ≤ U08) and **`complexity`@U03** (so U03 introduces something deliberate, not by
  accident). Practices start minimal and are amended per-unit (Book-1 precedent).
- **The `solve(data)` contract + mock-contest format are DOCUMENTED in `syllabus.md`** (binding, for
  future content gates) — not code here.
- Process (standing): no commits while a `[sol]` review is in flight; branch before drafting; codex
  prompts name the in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

Tooling + curriculum-registry plan; ships NO units/projects/checkpoints (verification satisfied by
Phase C, the named verification phase). Out of scope: any `book2/units|checkpoints|projects` content
or notebooks; per-unit practices tuning (amended per-unit); wiring Book-2 per-entry checks into
ci-local (added as content lands); retrofitting Book-1 ids to namespaced form; Book-1
`concepts.yaml` edits; extracting a shared "sample judge" helper; a formal
`docs/architecture/decisions.md` entry for the namespace decision (governance-listed file — deferred
to the user; recorded here + design-001 errata instead).

## Phases

Dispatch per AGENTS.md: tooling (`tools/`) via codex; curriculum (`concepts.yaml`/`coverage-map.yaml`/
`syllabus.md`) authored inline (curriculum architecture), codex assist for bulk YAML if useful.

### Phase A — per-book + cross-book tooling, two-tier scanner with detectors (codex)

1. **Baseline resolver:** read `books.yaml`, resolve a book's `depends_on`, compute the baseline
   (union of the dependency's `introduces`; directional; transitive-ready). Add to `tools/curriculum.py`
   or a small `tools/books.py`.
2. **De-couple the coverage/prereq suite per constraint items (1)–(8) above** — each parameterized
   per-book, Book-1 byte-identical: baseline-seed `prereq_findings`/`checkpoint_findings`;
   `referenced_concepts_findings` `known` = baseline ∪ own; `practice_findings` per-book capstone +
   deferred-until-content; `concepts_schema_findings` optional `kind` + per-book count floor + extended
   `CATEGORIES`; per-book `lesson_budget_findings` bound; `syllabus_findings` unchanged contract (the
   Book-2 syllabus supplies the table). `map_schema_findings` unchanged (no `term` field added).
3. **Global-uniqueness check** across ALL books in `books.yaml` (a Book-2 id colliding with any other
   book's id is a finding). New check or folded into a registry-schema check.
4. **`concept_scan.py` — per-book profile + real feature detectors** (per §5): per-book
   `TAUGHT_METHODS`/`BUILTINS`/never-flag; add gated detectors for the Book-2 feature set
   (`set-literal`/`set-ops`, `tuple`, `comprehension`, `str-split`, `sorted-key`, `deque`,
   `recursion`, `bitwise-ops`), each firing only if its id is in the scanned book's registry. Baseline
   added to each entry's allowed union. Book-1 scan byte-identical.
5. **Tests** (per-book, regression-locked):
   - cross-book: a Book-2 entry `requires:` a Book-1 concept → prereq/coverage PASS; a Book-2 entry
     requiring a concept taught NOWHERE ≤ it → FAIL.
   - two-tier: a `technique` id is never scanner-flagged; a Book-1 feature used in a Book-2 lesson is
     not flagged used-but-unlisted.
   - **feature-detector POSITIVE tests** — each new detector fires on a minimal Book-2 snippet
     (set/tuple/comprehension/`.split`/`sorted(key=)`/deque/self-recursion/bitwise), AND is gated OFF
     for Book 1 (the same snippet under a Book-1 registry does not add the concept).
   - schema: `kind` accepted; Book-2 count floor passes ~31 ids; a Book-1↔Book-2 id collision caught;
     `practice_findings` does not fire on a content-less Book-2 skeleton with minimal practices but
     DOES once a (fixture) unit practices/omits a concept.
   - **Book-1 regression, in-process ordering (sol):** the per-book scanner profile must NOT mutate
     module-global sets in place (they are module-level today). A test runs `--book book2` THEN
     `--book book1` IN THE SAME PROCESS and asserts Book-1 output is byte-identical (no cross-book
     state leakage), not merely testing Book 1 in isolation.
   - **Book-1 regression** — every existing check and `concept-scan` output byte-identical.
- **Acceptance (A):** `ruff` clean; `uv run pytest -q` green (incl. all new tests); Book-1 `ci-local`
  still ALL GREEN.

### Phase B — Book-2 curriculum registry + syllabus (inline)

1. `book2/curriculum/concepts.yaml` — ~31 ids, each `{id, name, category, kind}`. Features:
   `set-literal`, `set-ops`, `tuple`, `str-split`, `sorted-key`, `comprehension`, `recursion`,
   `deque`, `bitwise-ops`. Techniques: the §5 list INCLUDING `simulation`, `complexity`,
   `input-parse`, `grid-2d`, `code-tracing`, `boolean-algebra`, `postfix-eval`, `bitmask`, plus the
   algorithm tags (`complete-search`/`greedy`/`prefix-sum`/`binary-search`/`two-pointers`/
   `backtracking`/`bfs`/`dfs`/`flood-fill`/`graph-repr`/`tree-traversal`/`base-conversion`/`sieve`/
   `gcd`/`modular-arithmetic`).
2. `book2/curriculum/coverage-map.yaml` — 18 entries (U01–U14 + CP1–CP3 + capstone as
   `kind: project`), NO `term` field. `introduces` places each concept at its §7 home unit:
   `input-parse`+`str-split`+`grid-2d`@U01; `boolean-algebra`+`code-tracing`@U02; `complexity`@U03;
   `set-literal`+`set-ops`+`tuple`+`sorted-key`@U04; `binary-search`+`complete-search`@U05;
   `greedy`@U06; `simulation`@U07; `prefix-sum`@U08; `recursion`+`backtracking`+`comprehension`@U09;
   `deque`+`postfix-eval`@U10; `base-conversion`+`bitwise-ops`+`bitmask`+`gcd`+`sieve`+
   `modular-arithmetic`@U11; `tree-traversal`@U12; `graph-repr`+`bfs`+`dfs`+`flood-fill`@U13;
   `two-pointers`@U14. `requires` references the Book-1 baseline + earlier Book-2 concepts; entry
   order = design term order (closure-safe). Practices minimal (amended per-unit).
3. `book2/syllabus.md` — replace the placeholder: four-term arc, the machine-checked `|id|kind|
   lessons|` table, the §8 pacing contract (Term-4 compressible buffer), the binding
   `solve(data:str)->str` judge contract, timed mock-contest checkpoint format, rich-problem-set
   goal, cross-book prerequisite note.
- **Acceptance (B):** `prereq-check`, `coverage-check`, `concept-scan --book book2` all PASS against
  the baseline; global-uniqueness PASS; `practices ∩ introduces` empty per entry.

### Phase C — Verification (NAMED, mandatory)

Mechanical: `ruff` clean; `uv run pytest -q` green (incl. all cross-book + two-tier + feature-detector
+ regression tests); wire ONLY Book-2 MAP-LEVEL checks (`prereq-check`/`coverage-check`/`concept-scan
--book book2`) into `scripts/ci-local.sh`; full `ci-local.sh` ALL GREEN (Book-1 per-entry + Book-2
map-level); Book-1 behaviour byte-identical (regression); the Book-2 map closes against the baseline;
no Book-2 content dirs (per-entry checks correctly NOT run for Book 2).
Reviewer duties (both gates): the cross-book baseline is correct (Book-1 available to Book 2, no
backward leak); the coverage-suite de-coupling is complete (no Book-1 hardcoding blocks Book 2, none
loosened for Book 1); **the feature detectors actually fire (positive tests) and are per-book-gated**;
every `technique` id is genuinely non-detectable and every `feature` id has a working detector; the
capstone is `kind: project`; `grid-2d`@U01 and `complexity`@U03 close; global uniqueness enforced
across all books; the syllabus carries the machine-checked table + `solve` contract; Book-1 regression
exact.

**Acceptance criteria:** per-book + cross-book tooling + real feature detectors + tests shipped;
Book-2 `concepts.yaml` + full-arc `coverage-map.yaml` + `syllabus.md` authored and closing green
against the Book-1 baseline; ci-local ALL GREEN with Book-2 map-level checks wired; Book-1 unchanged;
plan-review + content-review 4-way consensus.

---

## Architecture decision (AD-001, recorded here per gate findings)

**Flat shared concept namespace.** Book-1 concept ids remain bare; Book-2 (and later books) add only
globally-unique new ids; no `book1:`-qualified ids. Uniqueness is enforced across ALL registered
books. This SUPERSEDES design-000's "namespaced by book" note and design-001 §6's `book1:for-loop`
examples. Rationale: Book 1 already shipped with bare ids; total Book-1-precedes-Book-2 ordering makes
provenance-prefixing unnecessary; retrofitting prefixes would churn a shipped book and every check for
no closure benefit. Cost accepted: a later book cannot independently *redefine* a same-named concept
(it must pick a new id) — acceptable for this curriculum. Design-001 §6 gets an errata pointer to this
AD; a formal `docs/architecture/decisions.md` entry is a governance-listed edit deferred to the user.

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE (superseded by the reconciled revision below). Original self-review approved the direction;
the 4-way gate then found the coverage-suite couplings and the missing feature detectors, now folded
in. See `## Reconciliation`.

### Review 2 — [fable] (2026-09-07) → APPROVE WITH NITS, reconciled
Verified the cross-book hook against the real `curriculum.py`/`concept_scan.py`; confirmed no-content
PASS empirically; confirmed arc closure and the two-tier boundary; confirmed flat-namespace is sound
and single-plan scope is right (phases sequentially coupled). Main finding (folded in): `coverage_findings`
has Book-1 couplings beyond the cumulative sets — practice-completeness (hardcoded capstone id),
concepts-schema (`kind` key / ≥40 floor / categories), `map_schema` `term` field, `referenced_concepts`
own-book-only, `lesson_budget` bounds, `checkpoint` seed, `syllabus` table — audit + parameterize
per-book. Nits (folded): reclassify `input-parse`/`grid-2d` as techniques; add `simulation`;
all-books uniqueness; `complexity`@U03; design-001 §6 errata.

### Review 3 — [glm] (2026-09-07) → REJECT, reconciled
Built a scratch 18-entry/31-concept skeleton and RAN the tooling. Blocker 1: `coverage_findings` is a
COMPOSITION, not cumulative-seen — seeding fixes nothing there; named the exact failing sub-checks
(referenced-unknown ×14, practice-completeness, schema key/floor/category, hardcoded capstone id).
Blocker 2: the "two-tier scanner" ships NO feature detectors (`detect()` lacks visit_Set/Tuple/ListComp,
`.split`/deque/set methods, recursion self-call, bitwise) → content-less PASS is vacuous and the Term-1
plan inherits an unenforced scanner; ship per-book-gated detectors (recommended) with positive tests.
Nits: pin `grid-2d`@U01; add `simulation`; record namespace override vs design-001 §6; Phase-C
"feature detectable" duty must match the detection decision. Confirmed sound: hook, boundary,
no-content wiring, flat namespace, arc closure, single-plan.

### Review 4 — [sol] (2026-09-07) → REJECT, reconciled
Corroborated glm with call-site citations. Blocker 1: coverage consumers need per-book local-vs-imported
handling (`referenced_concepts` known-set, `checkpoint` seed, `practice_findings` hardcoded capstone +
its full-union comparison misbehaving once Book-1 ids appear in Book-2 practices). Blocker 2: `detect()`
ships no Book-2 detectors; schema rejects `kind`; `simulation` missing from the plan's technique list;
reclassify `input-parse`/`grid-2d`; needs an immutable per-book scanner profile + positive detection
tests per feature. Blocker 4: practices-minimal vs pre-capstone coverage; `term` rejected by map schema;
capstone needs a legal `kind: project` id. Blocker 6: expand Phase A (the real tooling work is larger)
or split. Sharp extra point (folded): scanner constants are module-global sets — the regression suite
must run Book-2 THEN Book-1 in the SAME process and prohibit in-place mutation. Confirmed OK: arc
closure; formal verification-phase/exemption satisfied.

## Reconciliation (2026-09-07)
All three externals converge; two REJECT. The revision above folds in EVERY finding:
- **Coverage-suite de-coupling** is now a named Phase-A inventory (constraint items 1–8 + Phase A.2):
  `referenced_concepts` known = baseline ∪ own; `practice_findings` per-book capstone + deferred on
  content-less skeletons (never satisfied by inventing data); `concepts_schema` optional `kind` +
  per-book count floor + algorithms `CATEGORIES`; **no `term` field** (map schema unchanged); capstone
  = `kind: project`; per-book `lesson_budget`; `checkpoint` baseline seed; Book-2 syllabus supplies the
  machine-checked table.
- **Real per-book-gated feature detectors** in `concept_scan.py` (Phase A.4) with POSITIVE per-feature
  tests + Book-1 gated-off tests (Phase A.5); `input-parse`/`grid-2d` reclassified as techniques;
  `simulation` restored to the technique list; `complexity`@U03; `grid-2d`@U01.
- **Per-book scanner profile** (no in-place mutation of module-global sets) + **in-process Book2→Book1
  regression** test.
- **Flat namespace** recorded as **AD-001** with global uniqueness across ALL books; design-001 §6
  errata pointer.
- **Scope** kept as one plan (fable+glm) but Phase A expanded to the full per-book schema/coverage/
  scanner contract + regression matrix (addresses sol's expand-or-split).
Round-2 plan-review dispatched on the reconciled plan.

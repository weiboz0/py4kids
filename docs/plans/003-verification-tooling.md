# Plan 003 — Verification Tooling Implementation Plan

**Goal:** Replace every `SKIP (plan 003)` in `scripts/ci-local.sh` with a real check: a `tools/` package + `py4kids-tools` CLI providing notebook execution (solutions AND lessons), student hygiene, notebook-cell lint, headless turtle verification, manifest/curriculum checks, and a PDF handout build.

**Architecture:** `tools/` grows focused modules (`notebooks.py`, `curriculum.py`, `fake_turtle.py`, `checks.py` — the check-name → function registry the CLI dispatches through, `cli.py`) exposing pure functions; `tests/test_book1_units.py` and `tests/test_book1_curriculum.py` are refactored into thin wrappers importing the same functions (single source of truth; pytest keeps covering them); `cli.py` exposes each check as `py4kids-tools --book <id> <check>` for ci-local. PDF build uses the system toolchain verified present (nbconvert→xelatex for notebooks, pandoc for markdown) — no new Python dependencies.

**Spec:** `docs/designs/000-project-design.md` §4; plan 004 post-execution follow-ups; plan 002 follow-up (checks promoted from pytest).

## Global Constraints

- This plan takes the RESERVED number 003 (see plan 004 Global Constraints — the ci-local SKIP markers and TODO have always pointed here).
- Behavior parity is law: the promoted checks must enforce EXACTLY the rules the interim tests enforce today (patterns per-line `re.MULTILINE`; seed-ordering; cumulative closure; scaffolding exemption; the five teacher-notes headings; `## Exercise N` floors) — any tightening or loosening is a gate finding.
  Parity is PROVEN by one-fault fixtures: a moved assertion tested only by its own wrapper is
  circular (gate finding sol #2), so `tests/test_tools.py` maintains an enumerated
  rule checklist with ONE generated single-fault fixture per promoted rule — each mutation
  must fail exactly its rule's check, from an otherwise all-green baseline.
- Existing rules stay recorded where they are (plan 004 Global Constraints); tools docstrings reference them rather than restating divergent copies.
- Notebook-cell lint is critical-only: ruff `--select E9,F63,F7,F82` (syntax errors, undefined names) on extracted code cells — kid-facing style is NOT policed.
  Explicit lint contract (gate finding sol round-1 #1): `no-exec`-tagged cells are neither
  executed nor linted — they are teacher-performed material and may be deliberately broken
  (units 01/02 ship intentional error cells); a genuine defect in a `no-exec` cell is caught
  by the content gate's reviewer audit, not by CI. All other code cells are linted.
- Turtle conventions (binding on all current and future `assets/*.py`, recorded here per
  gate finding glm #7): scripts must run headless under the fake-turtle stub to completion
  (≤20s), make ≥1 pen-DOWN move (pen-up moves count only toward the <10000 total-move
  bound), and CLOSE — final position within 1e-6 of start AND |total heading change|
  ≡ 0 (mod 360) within 1e-6. A future deliberately-open drawing opts out with a literal
  `# turtle-check: open-path` comment, which waives only the closure conditions.
  The stub records position via coordinate tracking, not just turn totals (sufficiency fix,
  gate finding sol #4).
- Runtime budget: full `ci-local.sh` stays under 3 minutes on this machine with the three existing units.
- Every commit appends the two mandated trailer lines (exact text in plan 002 §Global Constraints).

## Out of scope

This is a tooling-only plan: it ships no units, projects, or checkpoints, so the named-verification-phase rule for content plans does not apply (exemption per design §5).
Verification here is: the tools' own pytest suite (including negative fixtures), behavior-parity green runs on the shipped units, and a fully SKIP-free `ci-local.sh` ALL GREEN.
Also out of scope: checkpoint/project check variants (no such content exists yet — the unit checks are written so plan 005+ extends kinds, not rewrites), overlap scan, Book 2 anything, solution-notebook PDF rendering (teacher handouts are the exercises).

## Phases

Dispatch: tools/scripts implementation via `codex:codex-rescue` (GPT-5.6-sol, write-capable) per AGENTS.md; plan/orchestration/review handling inline; trivial fixes inline.

### Phase A — package layout, CLI skeleton, fixture factory (TDD)

**Files:** `tools/{__init__.py,cli.py,notebooks.py,curriculum.py,fake_turtle.py,checks.py}`, `tests/test_tools.py`. NOTHING broken is committed: all negative fixtures are GENERATED at test time in `tmp_path` by a fixture factory (this removes the ruff/step-1 collision entirely — gate findings fable #2 / glm #2 / sol #8; `tests/fixtures/` is not created).
- Fixture factory: builds a VALID book root in `tmp_path` — its own `concepts.yaml`, `coverage-map.yaml`, `syllabus.md`, and ONE physically complete unit. Note (fable round-2 #1): the curriculum layer cannot be literally minimal — the promoted rules apply verbatim (parity), so the synthetic map needs ≥40 concepts, budget 28–32, introduce-exactly-once over the whole registry, an entry literally named `project-02-grand-adventure` (the pre-capstone coverage rule keys on it), and a first entry with empty `practices`; only the first unit exists on disk (the prefix rule permits that). Baseline is verified all-green before any mutation; each negative test clones it, applies exactly ONE mutation, and asserts exactly the targeted check fails with its expected `FAIL:` line and exit 1. Mutations cover EVERY promoted rule (the enumerated parity checklist in Global Constraints), including map-level rules (broken registry/map/syllabus — a broken BOOK root, resolving fable #4's map-level gap), a `cell-lint` undefined-name cell, an `exec-lessons` untagged cell depending on `no-exec` state (deterministic NameError), an `exec-solutions` failing assert, a non-compiling asset, and both non-closing and open-path turtle scripts.
- `pyproject.toml` gains `[project.scripts] py4kids-tools = "tools.cli:main"`.
- CLI contract: `py4kids-tools [--root <dir>] --book <id> <check>` where `--root` (default:
  repo root) points at a book-registry root — this is how tests route the CLI at generated
  fixture roots (sol #7); `<check>` ∈
  `manifest-check | hygiene-check | structure-check | noexec-check | exec-solutions |
  exec-lessons | cell-lint | turtle-check | prereq-check | coverage-check | stretch-check`;
  exit 0 = pass, 1 = findings, 2 = usage. Finding format: `FAIL: <unit>: <detail>` for
  unit-scoped checks, `FAIL: <book>: <detail>` for book/map-level checks (glm #9).
  `--unit <id>` optionally narrows unit-scoped checks.
- TDD: `tests/test_tools.py` asserts each check passes on the real `book1`, fails correctly
  on each one-fault fixture, and honors the exit-code contract (explicit assertions for
  0 / 1 / 2 — sol #10).

### Phase B — notebook checks promoted into tools

`tools/notebooks.py` re-homes the logic of `tests/test_book1_units.py` as pure functions
returning finding lists (empty = pass): layout+assets(py_compile), manifest/map agreement,
student hygiene, exercise structure, solutions structure + pattern bans + seed ordering,
lesson no-exec tagging, teacher-notes headings. `tests/test_book1_units.py` becomes thin
wrappers asserting `findings == []` per unit (same pytest ids, same skip guard, same
all-three-units check).
The all-three-units test keeps its test id but is GENERALIZED off the coverage map
(plan 004 follow-up, gate findings fable #3 / glm #4 / sol #3): the hardcoded tuple is
replaced by a map-driven rule — the set of existing `book1/units/unit-*` directories must
equal the FIRST N unit entries of the coverage map in order (no gaps, no orphans, any
N ≥ 0). Known blind spot, accepted: deleting the TRAILING unit dir shrinks N silently —
inherent to any prefix rule; the pre-merge guard's origin/main union catches accidental
deletions at PR time.
Check-name → rule-group binding (glm round-2 #1): `hygiene-check` = student outputs/
execution_count + solution-leak headings; `structure-check` = layout + assets py_compile +
exercise/stretch floors + solutions mirroring/asserts + pattern bans + seed ordering +
teacher-notes headings; `noexec-check` = lesson first-cell markdown + no-exec tagging;
`manifest-check` = manifest schema keys + map agreement; concepts/map schema validation is
part of `coverage-check`. ("Registry" in this plan means `concepts.yaml`; `books.yaml` is
step 1/6's concern and fixture roots need none — fable round-2 #5.)
New capabilities beyond parity:
1. **exec-lessons**: execute `lesson.ipynb` headless via nbclient AFTER dropping cells
   tagged `no-exec` (mechanizes plan 004's follow-up and reviewer duty 7 — attribution per
   sol #11: this is plan 004's promise, not design §4's). Execution contract mirrors
   solutions (sol #5): timeout 120s, kernel cwd = the unit directory. Convention
   clarification (binding, consistent with plan 004's intent): untagged lesson cells must
   not depend on state created by `no-exec` cells — drop-and-run breakage is a content
   defect, not a tooling false positive. (Fable verified all three shipped lessons already
   pass drop-and-run.)
2. **cell-lint**: extract code cells (skipping `no-exec` cells per the lint contract, and
   `%`/`!` magic lines) into ONE temp file per notebook — per-notebook concatenation is
   deliberate: per-cell files would false-positive F821 on cross-cell names (glm #10
   resolved per fable's verification); run ruff `--select E9,F63,F7,F82 --no-cache`;
   findings map back to notebook + cell index via line offsets.
3. **exec-solutions**: the nbclient execution moves here from the test file (tests call it).
Check-ordering rule (glm #5): within CLI composition and ci-local, structure/pattern-ban
checks run BEFORE any nbclient execution, so an `input()`-bearing notebook fails fast
rather than hanging to the 120s timeout.
Double-execution control (fable #7 / glm #11 / sol #9): ci-local exports `PY4KIDS_CI=1`,
under which the pytest exec WRAPPERS for the real book skip their nbclient runs (the CLI
steps are authoritative there); a plain `uv run pytest` still executes everything.
Scope note (glm round-2 #3): `tests/test_tools.py`'s negative exec fixtures do NOT skip
under `PY4KIDS_CI` — they test the tools themselves and always run.

### Phase C — headless turtle verification

`tools/fake_turtle.py`: a recording stub implementing the turtle API surface the assets
use (`forward`, `backward`, `left`, `right`, `penup`, `pendown`, `pensize`, `pencolor`,
`color`, `speed`, `bgcolor`, `Screen`/`done`/`exitonclick` as no-ops, `Turtle` class —
fable verified this is a strict superset of the six shipped scripts' calls) — tracking
(x, y) POSITION and heading via coordinate math, plus pen state and move counts.
`turtle-check`: for each `assets/*.py`, inject the stub as `sys.modules["turtle"]` in a
fresh subprocess and execute; enforce the binding turtle conventions in Global Constraints
(completion ≤20s, ≥1 pen-down move, <10000 total moves, position+heading closure with the
`# turtle-check: open-path` opt-out). Shipped-script expectations: square/pentagon/7-gon
close at 360° total turn; both rosettes total 9000° = 25×360 (hence mod-360, fable #6);
all return to start.
One-fault fixtures cover all four clauses (glm round-2 #2): a non-closing script FAILS
closure; an open-path-commented non-closing script PASSES (the comment waives only the
closure conditions — ≥1 pen-down and the move/completion bounds still apply, per Global
Constraints); an all-pen-up script FAILS the pen-down floor; an over-10000-move loop FAILS
the bound. A completion-timeout fixture is deliberately omitted (a 20s sleep per test run
is not worth it); the timeout path is exercised only if it ever fires in real use.

### Phase D — curriculum checks promoted into tools

`tools/curriculum.py` re-homes `tests/test_book1_curriculum.py` logic (registry schema,
map schema/ids/budget, referenced-concepts-exist, introduced-exactly-once, cumulative
prereq closure over requires ∪ practices, pre-capstone practice coverage, checkpoint
rules, syllabus table match) as functions; the test file becomes thin wrappers.
CLI: `prereq-check`, `coverage-check` (map-level), `stretch-check` (unit-level ≥2
stretch tags), `manifest-check` (unit manifests vs map).

### Phase E — PDF build + ci-local rewrite

1. `scripts/build-pdf.sh --book book1`: exports `JUPYTER_CONFIG_DIR=$(mktemp -d)` FIRST —
   this machine's stale `~/.jupyter/jupyter_nbconvert_config.json` otherwise breaks
   nbconvert with a python3.7-era ModuleNotFoundError (verified by fable AND glm;
   findings #1). For each unit: nbconvert `exercises.ipynb --to pdf --output <unit-id>`
   (the `--output` flag prevents the three same-basename handouts overwriting each other —
   glm #6) into `book1/build/handouts/`; `pandoc book1/syllabus.md --pdf-engine=xelatex
   -o book1/build/syllabus.pdf` (engine bound explicitly — sol #6). Fails on any
   missing/empty output. `book1/build/` gitignore coverage verified (root `build/` rule).
2. `scripts/ci-local.sh` rewrite — six steps, ZERO SKIP lines, `export PY4KIDS_CI=1`:
   1/6 registry + lint (command unchanged; safe because no broken fixture is ever
   committed) · 2/6 pytest (wrappers skip duplicate nbclient runs under PY4KIDS_CI) ·
   3/6 notebook structure THEN execution: `hygiene-check`, `structure-check`,
   `noexec-check`, `cell-lint`, then `exec-solutions`, `exec-lessons` ·
   4/6 curriculum + assets: `manifest-check`, `prereq-check`, `coverage-check`,
   `stretch-check`, `turtle-check` (label fixed per fable #8) ·
   5/6 `build-pdf.sh --book book1` · 6/6 pre-merge guard (unchanged).

### Phase F — Verification (tooling-only; exemption above)

1. `uv run pytest -q` — full suite green (tools tests + refactored wrappers + books).
2. Negative coverage: EVERY promoted rule has a one-fault generated fixture whose mutation
   fails exactly its check with the expected `FAIL:` line and exit 1 (the enumerated parity
   checklist in `tests/test_tools.py`); exit codes 0/1/2 explicitly asserted.
3. Behavior parity: refactored unit/curriculum wrappers pass on the shipped three units
   with NO check regressions (same pass set as pre-refactor), and the one-fault checklist
   covers EVERY promoted rule (the Global Constraints parenthetical is illustrative, not
   the boundary — fable round-2 #2); a rule without a fixture is a finding.
4. `bash scripts/ci-local.sh` — ALL GREEN, zero `SKIP` occurrences
   (`! grep -q "SKIP (plan" scripts/ci-local.sh` and the run output), under 3 minutes
   (fable/glm measured components projecting 40–60s total, so ample margin).
5. PDFs exist, non-empty, open-able (`pdfinfo` or file-size + `%PDF` magic check),
   three distinct handout names + syllabus.

**Acceptance criteria:** all six ci-local steps real and green; parity proven per item 3;
runtime < 3 min; NO broken files committed anywhere (all negative fixtures are
test-generated in tmp_path, so lint/discovery isolation is structural, not configured).

---

## Plan Review

### Review 1 — [self] (2026-09-06)
- **Verdict**: APPROVE
- Parity law + negative fixtures as refactor risk controls; CLI contract, critical-only lint, turtle closure invariant, PDF toolchain pinned; exec-lessons state-dependency resolved as binding convention.

### Review 2 — [fable] (2026-09-06)
- **Verdict**: REJECT (plan-text fixes only; architecture sound). Experiments run: PDF build FAILS on this machine via stale ~/.jupyter config (works with isolated JUPYTER_CONFIG_DIR, 7.3s/notebook); all three lessons execute clean after dropping no-exec cells; cell-lint recipe clean on all 9 notebooks; turtle math verified numerically (rosettes total 9000° — mod-360 needed); runtime projects 40–60s.
1. `[OPEN]` (Major) build-pdf.sh must isolate Jupyter config (`JUPYTER_CONFIG_DIR=$(mktemp -d)`) or step 5/6 is red on first run.
2. `[OPEN]` (Major) Broken fixture's non-compiling file trips ci-local step 1 ruff (invalid-syntax unsuppressable); needs `[tool.ruff] exclude = ["tests/fixtures"]` and the "step 1 unchanged" claim dropped.
3. `[OPEN]` (Major) Plan-004 follow-up "generalize the all-three-units check" is contradicted (plan keeps the hardcoded tuple) while claiming to absorb all follow-ups.
4. `[OPEN]` (Major) "Every check fails on the broken unit" unachievable: prereq/coverage need a broken BOOK root; cell-lint and exec-lessons lack deterministic violations; none of the parity laws (seed-order, bans, headings, floors) are pinned by fixtures.
5. `[OPEN]` (Minor) CLI home for layout/solutions-structure/teacher-notes checks unnamed (aggregation unstated).
6. `[OPEN]` (Minor) Turtle spec: state whether pen-up moves count; closure must be mod-360 (rosettes = 9000°).
7. `[OPEN]` (Nit) Solutions execute twice per run (pytest + CLI) — acknowledge.
8. `[OPEN]` (Nit) Step 4/6 label hosts notebook-structural checks — cosmetic.

### Review 3 — [glm] (2026-09-06)
- **Verdict**: REJECT (same architecture-sound assessment; converges on fable's four blockers with independent reproduction of the PDF config failure and its own /tmp prototypes: turtle closure verified on all six scripts, drop-and-run clean, cell-lint green, budget ample)
1. `[OPEN]` (Must Fix) = fable #1 (JUPYTER_CONFIG_DIR isolation).
2. `[OPEN]` (Must Fix) = fable #2 (ruff extend-exclude for fixtures).
3. `[OPEN]` (Must Fix) = fable #4 (negative coverage impossible as inventoried).
4. `[OPEN]` (Must Fix) = fable #3 (all-three-units generalization contradicted).
5. `[OPEN]` (Should Fix) exec-solutions hang risk: run structure/pattern bans BEFORE nbclient so input()-bearing notebooks fail fast, not at the 120s timeout.
6. `[OPEN]` (Should Fix) PDF basename collision: three `exercises.ipynb` → need `--output <unit-id>`.
7. `[OPEN]` (Should Fix) Turtle closure law + stub API surface become binding conventions on future assets — record them (plan 004 conventions or decisions), and clarify pen-up-move counting.
8. `[OPEN]` (Nit) `tools/checks/` package unused/undescribed.
9. `[OPEN]` (Nit) `FAIL: <unit>: <detail>` format undefined for map-level checks.
10. `[OPEN]` (Nit) Per-notebook temp-file mapping fragility vs per-cell (counterpoint: fable verified per-notebook is right for cross-cell names; resolve explicitly).
11. `[OPEN]` (Nit) Double solution execution (= fable #7).
12. `[OPEN]` (Nit) Design-§4 item 3 (manifest schema) enforced only via pytest, not a named CLI check.

### Review 4 — [sol] (2026-09-06)
- **Verdict**: REJECT
1. `[OPEN]` (Major) `no-exec` cells escape lint with no explicit contract, though shipped lessons deliberately contain broken teaching cells.
2. `[OPEN]` (Blocker) Parity proof circular: wrappers test the very functions the assertions moved into; one multiply-broken fixture can't isolate omitted branches.
3. `[OPEN]` (Major) All-three-units generalization contradicted (= fable #3 / glm #4).
4. `[OPEN]` (Major) Turn-divisibility is neither sufficient (`forward(100); right(360)`) nor necessary (legit open drawings) for turtle validity.
5. `[OPEN]` (Major) exec-lessons lacks timeout/cwd contract.
6. `[OPEN]` (Minor) pandoc engine unbound.
7. `[OPEN]` (Blocker) Fixture can't negatively cover map-level checks; CLI has no fixture-routing argument.
8. `[OPEN]` (Blocker) Committed non-compiling fixture pollutes step-1 ruff (= fable #2 / glm #2).
9. `[OPEN]` (Minor) Runtime unsubstantiated statically; duplication-heavy.
10. `[OPEN]` (Minor) Exit codes specified but never tested.
11. `[OPEN]` (Nit) Lesson execution misattributed to design §4.

### Revision 2 resolutions (2026-09-06) — applied across all three reviews
- fable 1 / glm 1 `[FIXED]`: build-pdf.sh exports `JUPYTER_CONFIG_DIR=$(mktemp -d)` first (both reviewers reproduced the stale-config failure).
- fable 2 / glm 2 / sol 8 `[FIXED]` structurally: NO broken files are committed — all negative fixtures are generated in tmp_path by a fixture factory; `tests/fixtures/` is never created; step-1 lint stays truly unchanged.
- fable 3 / glm 4 / sol 3 `[FIXED]`: hardcoded tuple replaced by the map-driven prefix rule (existing unit dirs = first N map units, in order).
- fable 4 / glm 3 / sol 2+7 `[FIXED]`: fixture strategy is now per-rule ONE-FAULT mutations from an all-green minimal book baseline, covering every promoted rule including map-level ones; CLI gains `--root` for fixture routing; parity checklist enumerated in tests.
- fable 5 `[FIXED]`: `tools/checks.py` is the named check registry the CLI dispatches through; every promoted rule has a CLI home (glm 8, glm 12, sol coverage note included — `manifest-check` is the named home for manifest schema).
- fable 6 / glm 7 / sol 4 `[FIXED]`: turtle invariant upgraded to position+heading closure (coordinate tracking), mod-360 wording, pen-up counting rules, `# turtle-check: open-path` opt-out; recorded as binding conventions in Global Constraints.
- fable 7 / glm 11 / sol 9 `[FIXED]`: `PY4KIDS_CI=1` dedupes nbclient runs in ci-local; plain pytest unchanged; measured runtime evidence cited in Phase F.
- fable 8 `[FIXED]`: step 4/6 relabeled "curriculum + assets".
- glm 5 `[FIXED]`: structure/pattern checks ordered before execution (fail fast on input()-bearing notebooks).
- glm 6 `[FIXED]`: nbconvert `--output <unit-id>` prevents basename collisions.
- glm 9 `[FIXED]`: FAIL format defined for both unit- and book-level checks.
- glm 10 `[FIXED]`: per-notebook concatenation documented as deliberate (cross-cell names), per fable's verification.
- sol 1 `[FIXED]`: explicit lint contract — no-exec cells neither executed nor linted; reviewer audit covers them.
- sol 5 `[FIXED]`: exec-lessons contract = 120s timeout, kernel cwd = unit dir.
- sol 6 `[FIXED]`: `--pdf-engine=xelatex` bound.
- sol 10 `[FIXED]`: exit-code assertions required in tests.
- sol 11 `[FIXED]`: lesson execution attributed to plan 004's follow-up.

### Review 5 — [sol] round 2 (2026-09-06)
- **Verdict**: APPROVE — all 12 tracked items verified resolved at HEAD (static verification); the fixture-factory design "substantively breaks the round-1 circularity rather than merely renaming the wrapper test".

### Review 6 — [glm] round 2 (2026-09-06)
- **Verdict**: APPROVE WITH NITS (no blockers) — all 12 round-1 items confirmed real at HEAD; prefix rule cross-checked against the live repo; no new contradictions.
1. `[OPEN]` Check-name → rule-group binding lives only in the ledger; add a one-line binding in Phase B (which rules live under structure-check / hygiene-check / noexec-check / manifest-check). Priority: Nit.
2. `[OPEN]` Turtle one-fault fixtures enumerate only 2 of the binding's 4 clauses; add all-penup and over-bound fixtures, note the timeout fixture explicitly. Priority: Nit.
3. `[OPEN]` State whether test_tools negative exec fixtures also skip under PY4KIDS_CI. Priority: Nit.

### Review 7 — [fable] round 2 (2026-09-06)
- **Verdict**: APPROVE WITH NITS — all four round-1 blockers verified FIXED (every fixture mention traced to tmp_path generation; prefix rule stress-tested against unit-04 landing, renames, middle deletions; one inherent trailing-deletion blind spot accepted); all cross-reviewer fixes coherent.
1. `[OPEN]` (Minor) Baseline factory understated: curriculum layer can't be minimal (≥40 concepts, budget, literal capstone id, empty first-entry practices). Priority: Minor.
2. `[OPEN]` (Nit) Phase F item 3 "rules named in Global Constraints" narrower than "every promoted rule".
3. `[OPEN]` (Nit) "Same all-three-units check" vs generalization wording; acknowledge trailing-deletion blind spot.
4. `[OPEN]` (Nit) Open-path opt-out scope phrasing inconsistent between Global Constraints and Phase C.
5. `[OPEN]` (Nit) "Registry" overloaded; concepts-schema CLI home implicit.

### Rev3 nit resolutions (2026-09-06)
- fable r2 #1 `[FIXED]`: factory note added (synthetic multi-entry map, literal thresholds and capstone id, first unit only on disk).
- fable r2 #2 `[FIXED]`: Phase F item 3 says "EVERY promoted rule"; parenthetical marked illustrative.
- fable r2 #3 `[FIXED]`: "keeps its test id but is generalized"; trailing-deletion blind spot acknowledged with the pre-merge-guard mitigation.
- fable r2 #4 `[FIXED]`: Phase C now uses the Global Constraints phrasing (opt-out waives only closure).
- fable r2 #5 / glm r2 #1 `[FIXED]`: check-name → rule-group binding added to Phase B; "registry" disambiguated; concepts/map schema homed under coverage-check.
- glm r2 #2 `[FIXED]`: turtle fixtures enumerated for all four clauses; timeout fixture deliberately omitted with rationale.
- glm r2 #3 `[FIXED]`: PY4KIDS_CI scope note — tool tests never skip.

### Gate result (2026-09-06)
- `[self]` APPROVE · `[sol]` APPROVE (round 2) · `[glm]` APPROVE WITH NITS · `[fable]` APPROVE WITH NITS.
- Full consensus, no `[OPEN]` items — **gate PASSED; approval to implement.**

## Content Review

(pre-PR gate findings land here.)

## Post-Execution Report

(written before shipping.)

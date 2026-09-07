# Plan 016 — Hygiene: practice-completeness + scanner promotion Implementation Plan

**Goal:** Close the tracked practice-completeness gaps in five already-shipped Book-1 entries
(concepts their content genuinely USES but their manifest/map don't LIST), and promote the
prototype concept-usage scanner into `tools/` as a first-class, book-clean CI check so this class of
gap is caught automatically going forward.

**Architecture:** Two independent workstreams in one hygiene PR. (A) metadata-only amendments to five
`manifest.yaml` files + their `coverage-map.yaml` entries (add missing PRACTICES; no requires, no
introduces, no content changes). (B) port `scratchpad/concept_scan.py` into the `tools/` package as
a `concept-scan` check wired into `scripts/ci-local.sh`, with the class-body `def-function`
false-positive fixed so the whole book scans clean.

**Spec:** `book1/curriculum/coverage-map.yaml`; the scanner prototype at
`/tmp/.../scratchpad/concept_scan.py` (behaviour reference, NOT a committed path); design-000 §4
(verification); the shipped `tools/` package + `tools/checks.py` CHECKS registry.

## Global Constraints

- **Metadata-only (workstream A):** amend ONLY the `practices` lists (map entry + matching manifest).
  Do NOT touch `introduces`/`requires`, notebook content, or teacher notes. Every added concept must
  be (1) genuinely used by that entry's content and (2) introduced ≤ that entry (closure), and (3)
  NOT already in that entry's `introduces` (`practices ∩ introduces` stays empty). Manifest == map
  after each amendment. Apply surgically (no YAML round-trip — it reflows the file).
- **The exact amendments (scanner-DERIVED + closure-verified):**
  - `unit-03-turtle-art-studio` practices += `f-string, string-literal` (both introduced unit-01).
  - `unit-04-quiz-show` practices += `string-literal` (unit-01).
  - `unit-05-function-factory` practices += `accumulator, import-statement, string-literal`
    (introduced unit-04 / unit-02 / unit-01 respectively; unit-05 introduces functions, so no
    intersection).
  - `checkpoint-02-loops-and-functions` practices += `string-literal` (unit-01).
  - `project-01-arcade-night` practices += `string-literal` (unit-01).
  - **NOT amended:** `checkpoint-04-year-one-finale`'s scanner `def-function` flag is a FALSE POSITIVE
    (class-body method defs home to `methods`/`init-method`; deliberately omitted — plan 014). The
    scanner fix in workstream B removes this false flag; the manifest is NOT changed.
- **Scanner promotion (workstream B, tooling — dispatch to codex):**
  - Port the prototype into the `tools/` package (e.g. `tools/concept_scan.py`) and register a
    `concept-scan` check in `tools/checks.py`'s CHECKS registry; wire it into `scripts/ci-local.sh`
    in the registry+lint / manifest phase.
  - Preserve the prototype's behaviour: AST-parse every notebook + `.py` code cell; per entry compute
    used-but-unlisted vs `introduces ∪ requires ∪ practices`; SKIP `ast.Assert` subtrees; treat
    `Add`/`Mult` with any str operand as string-concat not arithmetic; the `MANUAL_ONLY` set of fuzzy
    concepts the scanner does not flag; the OOP exemption (subtract user `FunctionDef`/method names
    from untaught-method flagging); accumulator detection (read-modify-write self-reference incl.
    `AugAssign` and attribute targets).
  - **FIX (required) — class-body `def` is NOT `def-function`:** a `FunctionDef` whose IMMEDIATE
    PARENT is a `ClassDef` is a METHOD (`methods`/`init-method`), never `def-function`. The test is
    PARENT-BASED, NOT depth-based — a `def` nested inside a METHOD body IS still `def-function` (a
    `class_depth > 0` suppression would wrongly mask it). Only a module-level `def`, or a `def`
    nested in a function/method body, counts as `def-function`. After this fix + workstream A, the
    scanner reports ZERO gaps across ALL 16 book-1 entries (only checkpoint-04's scan OUTCOME
    changes — unit-10 and project-02 already carry `def-function` in their unions via requires, so
    they never flagged; fable-7/glm-F4/sol wording).
  - **`string-literal` from f-string fragments (glm-F2/fable-4):** the scanner counts a `Constant`
    str inside a `JoinedStr` (an f-string's literal text) as `string-literal` — this is WHY
    project-01 (which wraps every string in `f"…"`, even placeholder-free) legitimately practices
    `string-literal`. DOCUMENT this rule in the check's help, and add a test that an f-string-only
    code cell still flags `string-literal`.
  - The check is BLOCKING (fails ci-local on any high-confidence used-but-unlisted concept), and is
    BOOK-LEVEL only (scans all entries like `coverage-check`; no `--unit` selector needed). It is
    necessary-not-sufficient (MANUAL_ONLY fuzzy concepts stay reviewer-enforced) — document that in
    the check's help. Wire it into `scripts/ci-local.sh` in the manifest/registry phase (alongside
    `manifest-check`/`coverage-check`); `ci-local.sh`'s `set -euo pipefail` fails the run closed.
  - **Constants are book1-coupled (fable-10):** `TAUGHT_METHODS`/`BUILTINS`/`MANUAL_ONLY` encode
    book-1 assumptions; note in the module that Book 2 will need per-book treatment (out of scope now).
  - Add pytest coverage: (a) the check PASSES on the real book (all 16 entries clean after
    workstream A); (b) a one-fault fixture (an entry using a concept absent from its union) FAILS;
    (c) def-function classification — a class-body-only `def` does NOT flag `def-function` (NEGATIVE),
    a MODULE-LEVEL `def` DOES (POSITIVE), and a `def` NESTED IN A METHOD body DOES (POSITIVE,
    guards against the depth-based mistake — sol-9/glm-F4); (d) an f-string-only cell flags
    `string-literal` (glm-F2).
- Process (standing): no commits while a `[sol]` review is in flight; codex prompts name the
  in-process execution fallback and avoid bare CLI-flag-like tokens.

## Out of scope

This is a metadata + tooling plan; it ships NO new units/projects/checkpoints, so the "named
verification phase" requirement is satisfied by Phase C (below), which is the mandatory verification
phase. Out of scope: any notebook CONTENT change; new curriculum; changing `introduces`/`requires`;
Book-2 anything; making the MANUAL_ONLY fuzzy concepts machine-detected (they stay reviewer-enforced);
retconning the def-function decision on checkpoint-04 (the manifest stays as shipped).

## Phases

Dispatch per AGENTS.md: metadata amendments inline; the scanner port + check + tests via codex
(tooling). 

### Phase A — practice-completeness amendments (inline)

1. For each of the five entries, surgically add the listed concept(s) to the `coverage-map.yaml`
   entry's `practices` AND the matching `manifest.yaml` `practices` (identical order).
2. Acceptance: `manifest-check` PASS (map == manifest for all five), `coverage-check` PASS (added
   concepts introduced ≤ entry), `prereq-check` PASS, `uv run pytest -q` green.

### Phase B — promote the scanner into tools/ (codex)

1. Port `scratchpad/concept_scan.py` → `tools/concept_scan.py`; register `concept-scan` in
   `tools/checks.py`; wire into `scripts/ci-local.sh`.
2. Apply the class-body `def-function` fix.
3. Add pytest coverage (real book passes; one-fault fixture fails; class-body def not flagged).
- Acceptance (Phase B): `tools/` importable; `py4kids-tools --book book1 concept-scan` PASS (zero
  gaps across all 16 entries after Phase A); new tests green.

### Phase C — Verification (NAMED, mandatory)

Mechanical: `uv run pytest -q` green (incl. the new scanner tests); `scripts/ci-local.sh` ALL GREEN
with the new `concept-scan` check active and passing; `manifest-check`/`coverage-check`/`prereq-check`
PASS; the five amended manifests equal their map entries; the scanner reports ZERO used-but-unlisted
across all 16 book-1 entries (checkpoint-04 def-function false-positive resolved by the fix, not by a
manifest edit).
Reviewer duties (both gates): confirm each added practice is genuinely used AND introduced ≤ entry
AND not in that entry's introduces; confirm no content/requires/introduces changed; confirm the
scanner fix is correct (class-body def ≠ def-function; module-level def still IS) and does not mask a
real gap; confirm the check is wired into ci-local and blocking; confirm the one-fault fixture fails.

**Acceptance criteria:** five entries amended (map == manifest); `concept-scan` in `tools/` + wired
into ci-local + book-clean; new tests green; `ci-local.sh` ALL GREEN; plan-review + content-review
4-way consensus.

---

## Plan Review

### Review 1 — [self] (2026-09-07)
APPROVE. Workstream A is pure metadata: five entries gain PRACTICES for concepts the scanner
high-confidence-detected in their content (string-literal everywhere, f-string in the turtle unit,
accumulator + import-statement in the functions unit), each verified introduced ≤ its entry and not
in its introduces, so closure and `practices ∩ introduces` both hold; no content, requires, or
introduces change. Workstream B promotes the prototype scanner into `tools/` as a blocking
`concept-scan` check, with the one known false-positive (class-body `def` counted as `def-function`)
fixed so the whole book — including checkpoint-04 and project-02 — scans clean WITHOUT a manifest
retcon. The check is necessary-not-sufficient (MANUAL_ONLY fuzzy concepts stay reviewer-enforced),
which the plan states. Phase C is the named verification phase (this is a metadata+tooling plan, no
new content). The def-function decision on checkpoint-04 is preserved (the fix removes the false
flag; the manifest is untouched).

### Reviews 2–4 — [fable] / [glm] / [sol] (2026-09-07) → APPROVE WITH NITS (no blockers), reconciled
All three independently: re-derived the amendment set with the prototype (exactly the five entries ×
listed concepts, nothing missing/extra), AST-audited genuine usage of each added concept, applied
all five amendments to a /dev/shm scratch and got `manifest-check`/`coverage-check`/`prereq-check`
PASS, confirmed checkpoint-04's def-function non-amendment correct (class-body-only defs; plan-014
precedent), and validated the parent-based scanner fix (sol ran a probe: class-body→`def-function`
False, module-level→True, nested-in-method→True; all 16 entries clean). NITS, ALL folded into the
plan's Global Constraints / Phase-B tests:
- **[FIXED] f-string-fragment rule (glm-F2/fable-4):** project-01's `string-literal` comes from
  `Constant` str inside `JoinedStr` (it wraps every string in `f"…"`). Documented + a test added
  (an f-string-only cell flags `string-literal`).
- **[FIXED] parent-based, not depth-based (fable-8/sol-9/glm-F4):** the fix keys on the IMMEDIATE
  parent being a `ClassDef`; a `def` nested in a METHOD body is still `def-function`. Tests now
  require class-body NEGATIVE + module-level POSITIVE + nested-in-method POSITIVE.
- **[FIXED] commit the prototype (glm-F4/fable-9):** the port starts from a committed
  `tools/concept_scan.py` (I seed it from the current prototype) rather than an ephemeral `/tmp`
  path; codex refines in-repo.
- **[FIXED] wording (fable-7/glm-F4/sol):** only checkpoint-04's scan OUTCOME changes; unit-10 and
  project-02 already carry `def-function` in their unions, so they never flagged — corrected.
- **[FIXED] ci-local wiring + scope (glm-F5):** book-level only (no `--unit`), wired in the
  manifest/registry phase, blocking via `set -euo pipefail`.
- **[FIXED] book1-coupling note (fable-10):** `TAUGHT_METHODS`/`BUILTINS`/`MANUAL_ONLY` flagged as
  book-1-scoped for a future Book-2 pass.

### Consensus (2026-09-07)
[self] APPROVE; [fable]/[glm]/[sol] APPROVE WITH NITS — no `[OPEN]` blockers, all nits folded in
(above). Plan-review gate CLOSED. Proceeding to implementation.

---

## Post-Execution Report (2026-09-07)

**Status: implemented, Phases A–C GREEN. Content gate next.**

- **Phase A (metadata):** committed `aa2dc2a`. Five entries' map + manifest practices amended
  (unit-03 +f-string,+string-literal; unit-04 +string-literal; unit-05 +accumulator,
  +import-statement,+string-literal; checkpoint-02 +string-literal; project-01 +string-literal).
  manifest/coverage/prereq PASS; pytest 364.
- **Phase B (scanner promotion, codex):** `tools/concept_scan.py` (ported from the prototype; now
  exposes `concept_scan_findings(root, book, unit=None)`), registered `concept-scan` in
  `tools/checks.py`, added to `BOOK_LEVEL_CHECKS` in `tools/cli.py` (rejects `--unit`), wired into
  `scripts/ci-local.sh` after `coverage-check`. The class-body `def-function` fix is PARENT-BASED
  (`isinstance(parents.get(node), ast.ClassDef)` → method, not def-function; a def nested in a
  method body still counts). New `tests/test_concept_scan.py` (6 tests): class-body-def NEGATIVE,
  module-level POSITIVE, nested-in-method POSITIVE, f-string-fragment → string-literal, real-book
  clean, one-fault fixture fails.
- **Phase C (verification):** ruff clean; `uv run pytest -q` → **373 passed** (+9 vs Phase A; the 6
  new scanner tests all pass — codex's sandbox showed 23 socket-denied notebook-exec "failures",
  confirmed environment-only, all green in the kernel-capable env); `py4kids-tools --book book1
  concept-scan` → PASS (ZERO used-but-unlisted across all 16 entries, checkpoint-04 def-function
  false-positive resolved by the fix, no manifest retcon); `--unit` correctly rejected; full
  `ci-local.sh` **ALL GREEN** with `concept-scan` active; pre-merge-guard OK.

---

## Content Review

Roster + tags per the plan-review gate; findings `[OPEN]`/`[FIXED]`/`[WONTFIX]`; all `[OPEN]` resolve
before merge.

### Review 1 — [self] (2026-09-07) → APPROVE
Verified the delivered code against the plan: (A) the five metadata amendments are exactly the
scanner-derived, closure-checked set (map == manifest, all PASS). (B) `tools/concept_scan.py` exposes
the `_findings(root, book, unit=None)` contract, is registered + book-level + ci-local-wired; the
def-function fix is PARENT-based not depth-based (confirmed in code: `parents.get(node)` immediate
parent test) with the three classification tests (class-body NEG, module-level POS, nested-in-method
POS) proving it; the f-string-fragment → string-literal rule is tested; the one-fault fixture fails;
the real book is clean. ruff clean, pytest 373 green, concept-scan PASS, ci-local ALL GREEN. No
content/requires/introduces changed. Necessary-not-sufficient documented (MANUAL_ONLY stays
reviewer-enforced). NIT (non-blocking): the constants are book1-coupled — noted for a future Book-2
pass, out of scope here.

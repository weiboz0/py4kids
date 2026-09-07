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
  - **FIX (required) — class-body `def` is NOT `def-function`:** a `FunctionDef` whose parent is a
    `ClassDef` is a METHOD (`methods`/`init-method`), never `def-function`. Only MODULE-LEVEL (or
    nested-in-function) `def` counts as `def-function`. After this fix + workstream A, the scanner
    must report ZERO gaps across ALL 16 book-1 entries (checkpoint-04 + project-02 + unit-10 no longer
    false-flag def-function).
  - The check is BLOCKING (fails ci-local on any high-confidence used-but-unlisted concept). It is
    necessary-not-sufficient (MANUAL_ONLY concepts stay reviewer-enforced) — document that in the
    check's help/among the SKIP semantics.
  - Add pytest coverage: the check passes on the real book; a one-fault fixture (an entry using a
    concept absent from its union) makes it FAIL; a class-body-only `def` does NOT trigger
    `def-function`.
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

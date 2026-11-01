# Plan 107 — Keep the group-free test suite free of `racekit`

**Goal:** `uv run pytest -q` (ci-local step 2, the group-free suite) passes in a fresh environment, without any book's dependency group.
User request, 2026-11-01: "fix the roar sync gap on main too".

## Problem

A fresh clone of `main` (927d5f51) fails ci-local step 2 at `tests/test_labs.py::test_racekit_carla_like_is_not_the_simulator` (found in plan aio-001 F.2, `clean-checkout-attempt1.log`).
The test writes a lab whose executed cell is `from racekit.cars import carla_like`, and `lab_findings` executes the lab.
`racekit` is installed only by `uv run --group roar` (`pyproject.toml`), which ci-local first runs *after* the group-free suite.
A long-lived checkout passes only because its venv still holds `racekit` from an earlier roar run (`uv run` syncs inexactly).

That breaks the step-2 law in `scripts/ci-local.sh:76-78`: the global suite must not require any book's dependency group (design 011 §7).

## Decision: a stand-in `racekit` module beside the test lab

The test checks the **lab checker** (`tools/labs.py`): that `carla_like` does not match `SIMULATOR_MENTION`, so the cell may run unmarked, and that such a lab then executes cleanly.
It does not test `racekit`.
The lab kernel runs in the lab's directory (`_execute_lab`, `resources.metadata.path`), so the test writes a minimal `racekit/__init__.py` + `racekit/cars.py` (defining `carla_like(noise=False)`) next to the lab notebook, and the import resolves to it without the roar group.
Rejected: `pytest.importorskip("racekit")` (would silently skip in a fresh clone and lose the assertion); moving the test to `roar/tests/` (the checker lives in `tools/`, and its tests belong with the group-free suite); reordering ci-local (would hide future violations of the law).

## Phases

### Phase A — the fix (inline; trivially scoped)
- `tests/test_labs.py`: the test writes the stand-in package beside the lab before calling `lab_findings`, with a comment that the stand-in resolves through the kernel's working directory (`_execute_lab`'s `resources.metadata.path`) and shadows an installed `racekit`, so neither `importorskip` nor the real package belongs here.
  No other test, no tool code and no content changes.

### Phase B — verification (named)
1. In a fresh venv **without** `racekit` (`UV_PROJECT_ENVIRONMENT` pointed at a new `/dev/shm` directory, `uv sync --frozen` with no groups; that venv's own interpreter, `uv run --no-sync python -c "import racekit"`, must fail first): `uv run --no-sync pytest -q` passes, including this test.
   The test also passes in a venv **with** `--group roar` synced (the shadowing case).
2. Mutation check: with the stand-in's `carla_like` renamed, the test fails (the lab really executes the import).
3. `scripts/ci-local.sh` green; `scripts/pre-merge-guard.sh --pr` OK.

## Out of scope (verification-phase exemption)
Test-only fix: no units, projects or checkpoints ship. Also out of scope: the aio-001 branch's clean-checkout provisioning workaround (`uv sync --group roar`), which aio-001 can drop after rebasing onto this fix.

## Plan Review

### Round 1 — [self] (2026-11-01)
- **Verdict**: APPROVE
- Empirical scope check: in a fresh no-group venv (`import racekit` fails in that venv's interpreter), the group-free suite with this one test deselected gave 2247 passed; the test alone fails with `ModuleNotFoundError: racekit`. It is the only group leak.

### Round 1 — [sol] (2026-11-01)
- **Verdict**: APPROVE WITH NITS (GPT-6, `--model gpt-6-sol`)
1. `[FIXED]` Phase B.1: a bare `python -c` probe may check another interpreter. Priority: Nice to Have.
   → Response: B.1 now probes with the fresh venv's own interpreter (`uv run --no-sync`).

### Round 1 — [fable] (2026-11-01)
- **Verdict**: APPROVE WITH NITS
- Verified the diagnosis, the stand-in and the mutation proof in a scratch racekit-free venv; full group-free suite 2247 passed with only this test deselected.
1. `[FIXED]` Phase A: comment that the stand-in resolves via the kernel cwd and shadows an installed racekit. Priority: Nice to Have.
   → Response: added to Phase A.
2. `[FIXED]` Phase B.1: also record a pass in a venv with `--group roar`. Priority: Nice to Have.
   → Response: added to B.1.

Consensus: all three APPROVE / APPROVE WITH NITS; plan gate CLOSED (v1.1).

## Content Review

Test-code review (no content ships).

### Review 1 — [self] (2026-11-01)
- **Verdict**: APPROVE
- The diff is `tests/test_labs.py` only; the stand-in lives in the test's `tmp_path` lab directory, and the comment names why `importorskip` does not belong. No findings.

### Review 1 — [sol] (2026-11-01)
- **Verdict**: APPROVE (GPT-6, `--model gpt-6-sol`)
- No findings.

### Review 1 — [fable] (2026-11-01)
- **Verdict**: APPROVE
- Re-ran the test and the mutation in its own racekit-free venv. No findings.

Consensus: all three APPROVE; no `[OPEN]` items.

## Post-Execution Report

- **Phase A** (`af906b62`): `test_racekit_carla_like_is_not_the_simulator` writes a stand-in `racekit/__init__.py` + `racekit/cars.py` beside the lab; no tool, content or other test changes.
- **B.1:** in a fresh no-group venv (`uv run --no-sync python -c "import racekit"` → `ModuleNotFoundError`), `tests/test_labs.py` 47 passed; before the fix the full group-free suite there gave 2247 passed with only this test failing.
  In a venv with `--group roar` synced (racekit from `roar/projects/racekit`), the test passes too (the stand-in shadows it).
- **B.2:** with the stand-in defining `carla_unlike`, the test fails: `ImportError: cannot import name 'carla_like' from 'racekit.cars' (…/labs/racekit/cars.py)`, so the lab really executes the import.
- **B.3:** `TMPDIR=/dev/shm bash scripts/ci-local.sh` in the worktree, whose `.venv` was created fresh with no groups: **ALL GREEN** (step 2 group-free suite passed before any routed suite installed racekit; site SKIP, no site input changed); `pre-merge-guard: OK`.
- Deviations: none.

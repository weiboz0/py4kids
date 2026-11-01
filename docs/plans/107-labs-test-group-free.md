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
- `tests/test_labs.py`: the test writes the stand-in package beside the lab before calling `lab_findings`.
  No other test, no tool code and no content changes.

### Phase B — verification (named)
1. In a fresh venv **without** `racekit` (`UV_PROJECT_ENVIRONMENT` pointed at a new `/dev/shm` directory, `uv sync --frozen` with no groups; `python -c "import racekit"` must fail first): `uv run pytest -q` passes, including this test.
2. Mutation check: with the stand-in's `carla_like` renamed, the test fails (the lab really executes the import).
3. `scripts/ci-local.sh` green; `scripts/pre-merge-guard.sh --pr` OK.

## Out of scope (verification-phase exemption)
Test-only fix: no units, projects or checkpoints ship. Also out of scope: the aio-001 branch's clean-checkout provisioning workaround (`uv sync --group roar`), which aio-001 can drop after rebasing onto this fix.

## Plan Review

## Content Review

## Post-Execution Report

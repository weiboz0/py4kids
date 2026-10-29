"""Checkpoint B's gates (plan roar-011 CPB.2-CPB.8): a full agent on a track and a car it has never met.

The pooled races (``_checkpoint_b_premise.py``, ``_premise.race_all``) are 70: the six Unit 8 grip
probes on the race-day track ``test-circuit-seed2027`` (CPB.2), the small protocol on the training
family (CPB.3: 7 + 7 + 15 + 15 races of ``agents/unit-11.py``, race seed 0), and three rows of five on
the sealed race-day cars ``carla_like(noise=True, perturb=k)``, k = 1000-1004, race seed k mod 5
(CPB.4 the frozen file with timing off, CPB.4b the frozen file with every ``mpc()`` call over budget,
CPB.5 Unit 11 and Unit 10 at 0.54 with the race-day line and grip), all capped at 700 s. CPB.4c races
the frozen file as shipped, serially in the test process after the pool, and CPB.6 runs
``check_submission`` outside any pool (the routed suite runs tests serially). CPB.1 is
``roar/data/tests/test_gen_tracks.py``.

A race is *clean* when it finishes with 0 collisions and its max error from **its own line** on
driving rows is at most 2 m. Race times are pinned to a tick (0.05 s). The pins come from the probes
(``p1``-``p7``); a miss means stop, amend and re-gate, never a silent re-pin.

The tracks are loaded by their literal generated names: the carla-like car's hidden grip is keyed to
the track name, so a rename changes the car and invalidates every pin.
"""

from __future__ import annotations

import ast
import json

import numpy as np
import pytest
from _checkpoint_b_premise import (
    CHECKPOINT_B,
    PROTOCOL_CARS,
    PROTOCOL_EDGE,
    PROTOCOL_FULL,
    PROTOCOL_PREFIX,
    RACE_DAY,
    RACE_DAY_MU_G,
    SEALED_CARS,
    U10,
    U11,
    checkpoint_b_jobs,
    contrast_key,
    lowest_grip_cars,
    probe_key,
    protocol_key,
    protocol_order,
    race_day_as_shipped,
    race_day_key,
    worst_budget_key,
)
from _line_premise import TRAINING
from conftest import RACEKIT, REPO
from racekit.check_submission import check_submission

TICK = 0.05 + 1e-9
MU_TOL = 0.005 + 1e-9  # the probe estimates are pinned after rounding to 0.01
CLEAN_ERROR = 2.0  # m: the clean rule's limit on the line error
TARGET = 300.0  # s: Checkpoint B's target median on the race-day track
CAP = 700.0
AGENTS = RACEKIT / "agents"
CHECKPOINT_DIR = REPO / "roar" / "checkpoints" / "checkpoint-02-part-2"

# CPB.2: each probe's outcome (probe p2): (finished, collisions) for section 0; sections 1-5 do not
# finish and collide at least once (probe: 12, 7, 5, 3, 3)
PROBE_SECTION_0_TIME = 109.40
# CPB.4: the frozen file (timing off) on the sealed cars, in SEALED_CARS order (probe p4)
RACE_DAY_TIMES = (283.95, 283.90, 283.60, 283.75, 283.95)
RACE_DAY_MEDIAN = 283.90
RACE_DAY_MAX_ERROR = 1.5  # m (probe 1.33)
# CPB.4b: every mpc() call over budget (probe p6)
WORST_BUDGET_TIMES = (284.35, 284.35, 284.00, 284.20, 284.55)
WORST_BUDGET_MEDIAN = 284.35
WORST_BUDGET_MAX_ERROR = 1.7  # m (probe 1.52)


def _clean(outcome) -> bool:
    return outcome.finished and outcome.collisions == 0 and outcome.line_error <= CLEAN_ERROR


def _one(premise, key):
    (outcome,) = premise[key]
    return outcome


def _row(premise, key_of):
    return [_one(premise, key_of(k)) for k in SEALED_CARS]


def _median(outcomes) -> float:
    return float(np.median([o.total_time for o in outcomes]))


def _times(outcomes):
    return [round(o.total_time, 2) for o in outcomes]


def _assigned(name, constant):
    tree = ast.parse((AGENTS / name).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == constant for t in node.targets):
            return node.value
    raise AssertionError(f"{constant} not in {name}")


def _module_constant(name, constant):
    return ast.literal_eval(_assigned(name, constant))


def test_the_job_list_is_the_plans_70_pooled_races(line_controls, race_day_line):
    jobs = checkpoint_b_jobs(line_controls, race_day_line)
    assert sum(len(job.seeds) for job in jobs.values()) == len(jobs) == 70
    assert RACE_DAY == "test-circuit-seed2027" and SEALED_CARS == (1000, 1001, 1002, 1003, 1004)
    for key, job in jobs.items():
        if key.startswith("cpb-probe-"):
            assert job.track == RACE_DAY and job.seeds == (0,) and job.laps == 1 and job.car == "carla", key
            continue
        assert job.max_seconds == CAP, key
        budget = dict(job.constants)["MPC_BUDGET_MS"]
        assert budget == (0.0 if key.startswith("cpb-worst-budget-") else None), key
        if job.track == RACE_DAY:
            assert job.perturb in SEALED_CARS and job.seeds == (job.perturb % 5,), key
        else:
            assert job.track in TRAINING and job.perturb in PROTOCOL_CARS and job.seeds == (0,), key


def test_the_race_day_line_has_131_values_and_the_frozen_file_ships_it(race_day_line):
    assert len(race_day_line) == 131
    assert _module_constant(CHECKPOINT_B, "LINE_CONTROL") == tuple(race_day_line)
    assert _module_constant(CHECKPOINT_B, "MU_G") == RACE_DAY_MU_G
    assert _module_constant(CHECKPOINT_B, "MU_FRACTION") == 0.48
    assert _module_constant(CHECKPOINT_B, "MPC_BUDGET_MS") == 5.0  # the frozen file keeps the timing


# --- CPB.2: the measurement -------------------------------------------------------------------------------


def test_cpb2_the_six_probes_measure_the_race_day_grip(checkpoint_b_premise):
    measured = []
    for section in range(6):
        outcome = _one(checkpoint_b_premise, probe_key(section))
        count, estimate = outcome.sections[section]
        assert estimate is not None, (section, count)
        measured.append(estimate)
        if section == 0:
            # it never slid: a lower bound
            assert outcome.finished and outcome.collisions == 0, outcome
            assert outcome.total_time == pytest.approx(PROBE_SECTION_0_TIME, abs=TICK), outcome
        else:
            # the car slid: the estimate is a measurement
            assert not outcome.finished and outcome.collisions >= 1, (section, outcome)
    assert [round(value, 2) for value in measured] == pytest.approx(RACE_DAY_MU_G, abs=MU_TOL), measured


# --- CPB.3: the family edge -------------------------------------------------------------------------------


def test_cpb3_the_protocol_cars_are_the_three_lowest_grip_training_cars():
    assert lowest_grip_cars() == PROTOCOL_CARS == (16, 18, 8)
    order = protocol_order()
    assert len(order) == 15 and order[PROTOCOL_PREFIX - 1] == ("test-circuit-seed2", 16)


@pytest.mark.parametrize("fraction", PROTOCOL_EDGE)
def test_cpb3_the_7th_protocol_race_is_the_first_not_clean(checkpoint_b_premise, fraction):
    races = [_one(checkpoint_b_premise, protocol_key(fraction, track, k))
             for track, k in protocol_order()[:PROTOCOL_PREFIX]]
    assert [_clean(o) for o in races] == [True] * (PROTOCOL_PREFIX - 1) + [False], races


@pytest.mark.parametrize("fraction", PROTOCOL_FULL)
def test_cpb3_the_edge_and_the_margin_value_are_clean_on_all_15(checkpoint_b_premise, fraction):
    races = [_one(checkpoint_b_premise, protocol_key(fraction, track, k)) for track, k in protocol_order()]
    assert len(races) == 15 and all(_clean(o) for o in races), races
    # so the edge is 0.50 and the margin rule ships 0.48, the frozen file's fraction
    assert _module_constant(CHECKPOINT_B, "MU_FRACTION") == min(PROTOCOL_FULL)


# --- CPB.4: race day --------------------------------------------------------------------------------------


def test_cpb4_race_day_is_clean_and_within_the_target(checkpoint_b_premise):
    row = _row(checkpoint_b_premise, race_day_key)
    assert all(_clean(o) for o in row), row
    assert _median(row) <= TARGET
    assert _times(row) == pytest.approx(RACE_DAY_TIMES, abs=TICK), row
    assert _median(row) == pytest.approx(RACE_DAY_MEDIAN, abs=TICK), row
    assert max(o.line_error for o in row) <= RACE_DAY_MAX_ERROR, row


def test_cpb4b_every_mpc_call_over_budget_is_clean_too(checkpoint_b_premise):
    row = _row(checkpoint_b_premise, worst_budget_key)
    assert all(_clean(o) for o in row), row
    assert _median(row) <= TARGET
    assert _times(row) == pytest.approx(WORST_BUDGET_TIMES, abs=TICK), row
    assert _median(row) == pytest.approx(WORST_BUDGET_MEDIAN, abs=TICK), row
    assert max(o.line_error for o in row) <= WORST_BUDGET_MAX_ERROR, row


def test_cpb4c_the_frozen_file_as_shipped(checkpoint_b_premise, capsys):
    """Raced serially in this process after the pool (the fixture is the pool, already finished)."""
    assert checkpoint_b_premise  # the pool has run
    results = race_day_as_shipped()
    row = [outcome for outcome, _ in results]
    cuts = [count for _, count in results]
    assert all(_clean(o) for o in row), row
    assert _median(row) <= TARGET
    with capsys.disabled():
        print(f"\nCPB.4c: times {_times(row)} median {_median(row):.2f} "
              f"max line error {max(o.line_error for o in row):.2f} horizon cuts {cuts}")
    timing_off = _times(_row(checkpoint_b_premise, race_day_key))
    for k, outcome, count, fresh in zip(SEALED_CARS, row, cuts, timing_off):
        if count == 0:
            # no cut: the race is the timing-off race, to the tick
            assert outcome.total_time == pytest.approx(fresh, abs=TICK), (k, outcome, fresh)


# --- CPB.5: the contrast ----------------------------------------------------------------------------------


def test_cpb5_unit_11_at_0_54_finishes_every_race_but_is_not_clean(checkpoint_b_premise):
    row = _row(checkpoint_b_premise, lambda k: contrast_key(U11, k))
    assert all(o.finished for o in row), row
    assert sum(not _clean(o) for o in row) >= 3, row


def test_cpb5_unit_10_at_0_54_does_not_finish_one(checkpoint_b_premise):
    row = _row(checkpoint_b_premise, lambda k: contrast_key(U10, k))
    assert sum(not o.finished for o in row) >= 1, row


# --- CPB.6 -------------------------------------------------------------------------------------------------


def test_cpb6_check_submission_passes_on_the_race_day_track():
    # the routed suite runs tests serially, so this timing is outside any pool
    report = check_submission(AGENTS / CHECKPOINT_B, track=RACE_DAY)
    assert report.ok, str(report)


# --- CPB.7: the reference is Unit 11 plus three constants ---------------------------------------------------


def _module_parts(name):
    tree = ast.parse((AGENTS / name).read_text(encoding="utf-8"))
    assigns, bodies, others = {}, {}, []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                key = target.id if isinstance(target, ast.Name) else ast.dump(target)
                assigns[key] = ast.dump(node.value)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bodies[node.name] = ast.dump(node)
        else:
            others.append(ast.dump(node))
    return assigns, bodies, others


def test_cpb7_checkpoint_b_is_unit_11_with_three_constants():
    ours, theirs = _module_parts(CHECKPOINT_B), _module_parts(U11)
    changed = {key for key in set(ours[0]) | set(theirs[0]) if ours[0].get(key) != theirs[0].get(key)}
    assert changed == {"MU_FRACTION", "MU_G", "LINE_CONTROL"}, changed
    assert len(_module_constant(CHECKPOINT_B, "LINE_CONTROL")) == 131
    assert len(_module_constant(U11, "LINE_CONTROL")) == 133
    assert ours[1] == theirs[1]  # every function and class, byte-identical as AST
    assert ours[2] == theirs[2]  # the docstring and the imports


# --- CPB.8: the seal ----------------------------------------------------------------------------------------


SEAL_SCAFFOLD = "SEALED_CARS = range(1000, 1005)"
SEALED_LITERALS = range(1000, 1006)


def _sealed_names(tree) -> set:
    """Names bound by iterating over ``SEALED_CARS`` (its members) in a ``for`` or a comprehension."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.comprehension)):
            iterated = node.iter
            if any(isinstance(n, ast.Name) and n.id == "SEALED_CARS" for n in ast.walk(iterated)):
                names |= {n.id for n in ast.walk(node.target) if isinstance(n, ast.Name)}
    return names


def _sealed_tokens(node, members) -> list:
    """The sealed references in ``node``: int literals 1000-1005, ``SEALED_CARS`` and its members."""
    found = []
    for n in ast.walk(node):
        if isinstance(n, ast.Constant) and type(n.value) is int and n.value in SEALED_LITERALS:
            found.append(n.value)
        elif isinstance(n, ast.Name) and (n.id == "SEALED_CARS" or n.id in members):
            found.append(n.id)
    return found


def _calls_factors_on_a_sealed_car(tree, members) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
            if name == "perturbation_factors":
                arguments = list(node.args) + [keyword.value for keyword in node.keywords]
                if any(_sealed_tokens(argument, members) for argument in arguments):
                    return True
    return False


def test_cpb8_the_sealed_cars_are_built_only_in_the_race_day_cell():
    """In ``checkpoint.ipynb`` and ``solutions.ipynb`` the race-day cell is cell-tagged ``race-day``,
    exactly once, and carries the scaffold line ``SEALED_CARS = range(1000, 1005)``; no other code cell
    holds an int literal 1000-1005 or the name ``SEALED_CARS`` (every code cell parsed with ``ast``,
    walking ``ast.Constant`` ints and ``ast.Name`` ids; a cell that does not parse fails); and no cell
    calls ``perturbation_factors`` on ``SEALED_CARS``, one of its members or such a literal.

    Known gap (plan roar-011 CPB.8): a float, a string or a computed 1000 (``999 + 1``) is not caught;
    the seal is an honour rule, and this test checks the scaffold, not every possible route."""
    notebooks = [CHECKPOINT_DIR / "checkpoint.ipynb", CHECKPOINT_DIR / "solutions.ipynb"]
    if not any(path.exists() for path in notebooks):
        pytest.skip("Checkpoint B's notebooks are written in plan roar-011 Phase B (none exist yet)")
    for path in notebooks:
        assert path.exists(), f"{path.name} is missing (the other notebook exists)"
        cells = json.loads(path.read_text(encoding="utf-8"))["cells"]
        tagged = [cell for cell in cells if "race-day" in cell.get("metadata", {}).get("tags", [])]
        assert len(tagged) == 1 and tagged[0]["cell_type"] == "code", (path.name, len(tagged))
        race_day_source = "".join(tagged[0]["source"])
        assert SEAL_SCAFFOLD in race_day_source.splitlines(), path.name
        for index, cell in enumerate(cells):
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            try:
                tree = ast.parse(source)
            except SyntaxError as error:  # a cell that does not parse cannot be scanned
                raise AssertionError(f"{path.name} cell {index} does not parse: {error}") from error
            members = _sealed_names(tree)
            assert not _calls_factors_on_a_sealed_car(tree, members), (path.name, index)
            if cell is not tagged[0]:
                assert not _sealed_tokens(tree, members), (path.name, index, _sealed_tokens(tree, members))

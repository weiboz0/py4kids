"""The Unit 10 premise races (plan roar-009 U10.2-U10.8), raced once per test session in parallel
with ``_premise.race_all``.

Each job is an ``_agent_premise.AgentJob`` on ``carla_like(noise=True)``: ``agents/unit-10.py`` (the
MPC) or ``agents/unit-09.py`` (pure pursuit) with some module constants changed through
``write_variant``. The per-track constants are written in as ``_line_premise.py`` writes them:
``MU_G`` from ``MEASURED_MU_G`` and ``LINE_CONTROL`` from the test-side solver (the session fixture
``line_controls``); on ``test-circuit`` the shipped values are raced as shipped.

Every MPC race runs the variant ``MPC_BUDGET_MS = None`` (no timing: the race never depends on the
machine's load), except U10.7's ``MPC_BUDGET_MS = 0.0`` races (every tick over budget, so the horizon
is 40, 20, then 10, deterministically). The pursuit sides of U10.2 and U10.5 are not raced here:
the gates read them from ``line_premise`` (``U9_REFERENCE``, ``line_key(CHECKPOINT, 0.54)``).

``race_mpc_job`` races one job and keeps what the gates need: the clean rule's numbers (the max
cross-track error from the job's own line, as ``_line_premise.race_line_job`` measures it), a digest
of the telemetry (the equivalence is asserted to the tick), the number of agent steps and driving
rows, and the MPC's own counters: ``over_budget``, ``fallbacks``, the final ``horizon`` and the
horizon each ``mpc()`` call planned with (run-length encoded).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from typing import Dict, List, NamedTuple, Optional, Tuple

from _agent_premise import AGENTS, AgentJob, make_car
from _line_premise import BASE, CHECKPOINT, MEASURED_MU_G, MONZA, TRAINING, _line_of, cap_for
from _premise import SEEDS, race_all

MPC = "unit-10.py"
PURSUIT = "unit-09.py"
SHIPPED_FRACTION = {MPC: 0.58, PURSUIT: 0.54}
NO_TIMING = (("MPC_BUDGET_MS", None),)  # every gate MPC race but U10.7's budget-0 races
ALL_OVER = (("MPC_BUDGET_MS", 0.0),)  # U10.7: every mpc() call over budget
SEED4 = "test-circuit-seed4"
SEED1 = "test-circuit-seed1"


class MpcOutcome(NamedTuple):
    total_time: float
    collisions: int
    finished: bool
    line_error: float  # max |offset - n[(progress + 1) mod n]| over the driving rows
    digest: str  # sha256 of the telemetry and the respawn causes (the equivalence)
    steps: int  # agent step() calls
    driving_rows: int  # telemetry rows with held == 0
    over_budget: Optional[int]  # the agent's counters (None for a pursuit-only agent)
    fallbacks: Optional[int]
    horizon: Optional[int]  # the final horizon
    horizons: Tuple[Tuple[int, int], ...]  # (horizon, mpc() calls in a row) per run


def mpc_key(track: str, fraction: float) -> str:
    return f"mpc-{track}-{fraction}"


def pursuit_key(track: str, fraction: float) -> str:
    return f"pursuit-{track}-{fraction}"


def budget0_key(track: str) -> str:
    return f"mpc-budget0-{track}"


LAG0 = "mpc-lag0-test-circuit-0.6"  # U10.6
U10_AS_PURSUIT = "u10-pursuit-test-circuit-seed4-0.58"  # U10.7: unit-10 with STEERING = "pursuit", seed 0


def _job(agent, constants, track, seeds=SEEDS) -> AgentJob:
    return AgentJob(agent, tuple(constants), track, seeds=seeds, max_seconds=cap_for(track), car="carla")


def _track_constants(track: str, controls) -> Tuple[Tuple[str, object], ...]:
    if track == BASE:
        return ()  # the agents ship test-circuit's MU_G and LINE_CONTROL
    return (("MU_G", MEASURED_MU_G[track]), ("LINE_CONTROL", controls[(track, "global")]))


def _fraction(agent: str, fraction: float) -> Tuple[Tuple[str, object], ...]:
    return () if fraction == SHIPPED_FRACTION[agent] else (("MU_FRACTION", fraction),)


def mpc_job(track: str, fraction: float, controls, *extra, timing=NO_TIMING, seeds=SEEDS) -> AgentJob:
    """``agents/unit-10.py`` on the track's line with its measured grip (no timing by default)."""
    return _job(MPC, _track_constants(track, controls) + _fraction(MPC, fraction) + timing + tuple(extra),
                track, seeds)


def pursuit_job(track: str, fraction: float, controls) -> AgentJob:
    """``agents/unit-09.py`` on the track's line with its measured grip (as ``_line_premise.line_job``)."""
    return _job(PURSUIT, _track_constants(track, controls) + _fraction(PURSUIT, fraction), track)


def mpc_premise_jobs(controls) -> Dict[str, AgentJob]:
    """Every Unit 10 gate race, keyed by name: 76 races, 65 of them MPC (the plan's job table)."""
    jobs: Dict[str, AgentJob] = {}
    # U10.2: the same f (MPC; pursuit is line_premise's U9_REFERENCE)
    jobs[mpc_key(BASE, 0.54)] = mpc_job(BASE, 0.54, controls)
    # U10.3: the hook
    jobs[mpc_key(SEED4, 0.58)] = mpc_job(SEED4, 0.58, controls)
    jobs[pursuit_key(SEED4, 0.58)] = pursuit_job(SEED4, 0.58, controls)
    # U10.4: the edge
    for track in TRAINING:
        jobs[mpc_key(track, 0.6)] = mpc_job(track, 0.60, controls)
    jobs[mpc_key(SEED1, 0.62)] = mpc_job(SEED1, 0.62, controls)
    # U10.5: the transfer (pursuit is line_premise's line_key(CHECKPOINT, 0.54))
    jobs[mpc_key(CHECKPOINT, 0.58)] = mpc_job(CHECKPOINT, 0.58, controls)
    # U10.6: the lag
    jobs[LAG0] = mpc_job(BASE, 0.60, controls, ("MPC_LAG", 0))
    # U10.7: the over-budget policy, and the pursuit equivalence
    for track in (SEED4, CHECKPOINT):
        jobs[budget0_key(track)] = mpc_job(track, 0.58, controls, timing=ALL_OVER)
    jobs[U10_AS_PURSUIT] = _job(MPC, _track_constants(SEED4, controls) + (("STEERING", "pursuit"),), SEED4,
                                seeds=(0,))
    # U10.8: monza-like
    jobs[mpc_key(MONZA, 0.64)] = mpc_job(MONZA, 0.64, controls)
    jobs[pursuit_key(MONZA, 0.64)] = pursuit_job(MONZA, 0.64, controls)
    return jobs


def is_mpc_job(job: AgentJob) -> bool:
    return job.agent == MPC and dict(job.constants).get("STEERING", "mpc") == "mpc"


def _run_lengths(values: List[int]) -> Tuple[Tuple[int, int], ...]:
    runs: List[List[int]] = []
    for value in values:
        if runs and runs[-1][0] == value:
            runs[-1][1] += 1
        else:
            runs.append([value, 1])
    return tuple((value, count) for value, count in runs)


def _recorded(agent_class: type, agents: list, horizons: List[int]) -> type:
    """The submission's class, keeping its instance in ``agents`` and the horizon of every ``mpc()``
    call in ``horizons`` (nothing else changes: the race is the submission's)."""

    class Recorded(agent_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            agents.append(self)

        def mpc(self, yaw, speed):
            horizons.append(self.horizon)
            return super().mpc(yaw, speed)

    return Recorded


def race_mpc_job(job: AgentJob) -> List[MpcOutcome]:
    """Race one job (every seed in ``job.seeds``) in this process, keeping the agent's counters."""
    import numpy as np
    from _line_solver import line_offsets
    from racekit.runner import load_submission, run_race, shim_installed
    from racekit.tracks import load_track
    from racekit.variants import write_variant

    track = load_track(job.track)
    n = len(track)
    with tempfile.TemporaryDirectory() as folder:
        submission = AGENTS / job.agent
        if job.constants:
            key = hashlib.sha256(json.dumps([job.agent, job.constants]).encode()).hexdigest()[:12]
            submission = write_variant(submission, os.path.join(folder, f"variant_{key}.py"),
                                       {name: repr(value) for name, value in job.constants})
        control, step = _line_of(submission)
        assert step == 10 and len(control) == n // step, (job.agent, len(control), n)
        target = line_offsets(control, n)
        outcomes = []
        for seed in job.seeds:
            with shim_installed():
                agent_class, module_name = load_submission(submission)
            try:
                agents: list = []
                horizons: List[int] = []
                result = run_race(_recorded(agent_class, agents, horizons), job.track, car=make_car(job), seed=seed,
                                  max_seconds=job.max_seconds)
            finally:
                sys.modules.pop(module_name, None)
            (agent,) = agents
            telemetry = result.telemetry
            driving = telemetry["held"] == 0
            offset = telemetry["offset"][driving]
            error = np.abs(offset - target[(telemetry["progress"][driving] + 1) % n])
            digest = hashlib.sha256(telemetry.tobytes() + repr(result.respawn_causes).encode()).hexdigest()
            outcomes.append(MpcOutcome(
                result.total_time, result.collisions, result.finished, float(np.max(error)), digest,
                int(result.step_ms.size), int(driving.sum()), getattr(agent, "over_budget", None),
                getattr(agent, "fallbacks", None), getattr(agent, "horizon", None), _run_lengths(horizons)))
    return outcomes


def race_mpc_premise(controls) -> Dict[str, List[MpcOutcome]]:
    return race_all(mpc_premise_jobs(controls), worker=race_mpc_job)

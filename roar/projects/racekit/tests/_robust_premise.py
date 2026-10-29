"""The Unit 11 premise races (plan roar-010 U11.2-U11.9), raced once per test session in parallel
with ``_premise.race_all``.

Each job is a ``RobustJob``: ``agents/unit-10.py`` (Unit 10's MPC) or ``agents/unit-11.py`` (the same
MPC with the respawn handler and the fallback) with some module constants changed through
``write_variant``, on ``carla_like(noise=True, perturb=k, lag_ticks=...)``: car ``k`` of the perturbed
family (design 013 §4.4 v4.9), or the unperturbed car (``perturb=None``). The training perturbations
are k = 0-23, the held-out ones k = 24-47; a perturbed race uses the race seed ``k mod 5``, every
other race seed 0. Every race is capped at 700 s (a crash loop runs to the cap; a race not finished
counts at the cap in a mean) and runs the variant ``MPC_BUDGET_MS = None`` (no wall clock in a gate
race). On ``test-circuit`` the agents' shipped ``MU_G`` and ``LINE_CONTROL`` are raced as shipped; on
``test-circuit-seed2026`` (U11.8) they are written in as ``_line_premise.py`` writes them.

``race_robust_job`` races one job and keeps what the gates need: the clean rule's numbers (the max
error from the job's own line, as ``_mpc_premise.race_mpc_job`` measures it), a digest of the
telemetry (the equivalence is asserted to the tick), the respawn times, and Unit 11's own counters
(``respawns`` handled, ``warnings``, the final ``mode``; None for ``agents/unit-10.py``).

**Why a crashed race's remainder is shorter than a fresh race (q10; U11.3).** After a respawn the
time left (race time - crash time - 1.0 s) is 0.4-0.7 s *shorter* than a fresh race of the same car
and race seed in the fallback configuration. The cause is the agent's state, which the restart does
not reset: on a major collision ``racekit.runner`` (like the official runner) resets the car to the
start pose at rest, holds it for 20 ticks and resets the progress index to 0, but it never
re-constructs or re-initializes the agent. ``fall_back()`` resets the MPC's queue and plan, not
the speed loop, so the PI integral the speed loop had at the crash carries into the restarted race;
it is positive, so the restarted car takes more throttle than a fresh one and finishes earlier.
Measured with ``noise=False`` on car 8 (race seed 3): the remainder is 0.40 s shorter than the
fresh fallback race, and **0.00 s** (to the tick) shorter when ``fall_back()`` also resets the speed
PI; with noise the jitter stream (not re-seeded at a respawn) adds the usual spread of about 0.15 s.
The clock accounting itself is exact: the hold is 20 ticks, 1.0 s. Sign: remainder minus fresh
race < 0. The lesson states the crash cost as "t + 1 s, to within a second".
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from typing import Dict, List, NamedTuple, Optional, Tuple

from _agent_premise import AGENTS
from _line_premise import BASE, CHECKPOINT, MEASURED_MU_G, _line_of
from _premise import race_all

U10 = "unit-10.py"
U11 = "unit-11.py"
SHIPPED_FRACTION = {U10: 0.58, U11: 0.54}
NO_TIMING = (("MPC_BUDGET_MS", None),)
CAP = 700.0  # s: every gate race
TRAINING_CARS = tuple(range(24))
HELD_OUT_CARS = tuple(range(24, 48))
FRACTIONS = (0.58, 0.56, 0.54, 0.52)  # U11.4 (unit-10's 0.58 is U11.2's race)
FALLBACK_SCALE = 0.86
# U11.3: the cars whose U11.5 race (unit-11 at 0.58) crashes exactly once and finishes (probe q10);
# each gets a fresh twin in the fallback configuration. The gate asserts the U11.5 set is this set.
TWIN_CARS = (8, 16, 20, 24, 32, 35, 41)
EQUIVALENCE_CARS = (0, 8, 16)  # U11.7: training cars raced by unit-11 at 0.54 (unit-10's are U11.4's)
TRANSFER_CARS = tuple(range(12))  # U11.8, race seed 0
LAG2 = 2  # U11.5: the lag Unit 8 identified, plus one tick


class RobustJob(NamedTuple):
    agent: str  # a file in agents/
    constants: Tuple[Tuple[str, object], ...]
    track: str
    seeds: Tuple[int, ...]
    perturb: Optional[int] = None  # carla_like(perturb=...)
    lag_ticks: Optional[int] = None  # carla_like(lag_ticks=...)
    max_seconds: float = CAP
    laps: Optional[int] = None  # None: run_race's default (3); Unit 12's knob map races one lap (roar-012)


class RobustOutcome(NamedTuple):
    total_time: float
    collisions: int
    finished: bool
    line_error: float  # max |offset - n[(progress + 1) mod n]| over the driving rows
    digest: str  # sha256 of the telemetry and the respawn causes (the equivalence)
    respawn_times: Tuple[float, ...]  # sim time of each major collision (the start of its hold)
    respawns: Optional[int]  # unit-11's counters (None for unit-10)
    warnings: Optional[int]
    mode: Optional[str]


def race_seed(k: int) -> int:
    return k % 5


def fraction(agent: str, value: float) -> Tuple[Tuple[str, object], ...]:
    return () if value == SHIPPED_FRACTION[agent] else (("MU_FRACTION", value),)


def perturbed_job(agent: str, value: float, k: int, *extra) -> RobustJob:
    """``agent`` at fraction ``value`` on perturbed car ``k`` of ``test-circuit``, race seed k mod 5."""
    return RobustJob(agent, fraction(agent, value) + NO_TIMING + tuple(extra), BASE, (race_seed(k),), perturb=k)


def u10_key(value: float, k: int) -> str:
    return f"u10-{value}-p{k}"


def u11_key(value: float, k: int) -> str:
    return f"u11-{value}-p{k}"


def twin_key(k: int) -> str:
    return f"twin-p{k}"


def warn_key(k: int) -> str:
    return f"u11-warn-0.58-p{k}"


def transfer_key(k: int) -> str:
    return f"u11-0.54-{CHECKPOINT}-p{k}"


LAG2_U10 = "lag2-u10-0.54"
LAG2_U11 = "lag2-u11-0.54"
NOMINAL_U10 = "nominal-u10-0.54"
NOMINAL_U11 = "nominal-u11-0.54"
TWIN_CONSTANTS = (("STEERING", "pursuit"), ("MU_FRACTION", 0.58 * FALLBACK_SCALE))
WARN_CONSTANTS = (("WARN_FALLBACK", True), ("WARN_ERROR_M", None))  # U11.9: the beta trigger (8 deg)


def robust_premise_jobs(controls) -> Dict[str, RobustJob]:
    """Every Unit 11 gate race, keyed by name: 218 races (the plan's job table). The likely crash
    loops (to the 700 s cap) come first, so the pool starts them first."""
    jobs: Dict[str, RobustJob] = {}
    # U11.2 (the hook) and U11.4 (the fraction): unit-10 on the training family
    for value in FRACTIONS:
        for k in TRAINING_CARS:
            jobs[u10_key(value, k)] = perturbed_job(U10, value, k)
    # U11.5: the lag-2 car, both agents at 0.54
    jobs[LAG2_U10] = RobustJob(U10, fraction(U10, 0.54) + NO_TIMING, BASE, (0,), lag_ticks=LAG2)
    jobs[LAG2_U11] = RobustJob(U11, NO_TIMING, BASE, (0,), lag_ticks=LAG2)
    # U11.5 (and U11.3's crashed races): unit-11 at 0.58 on the training and held-out families
    for k in TRAINING_CARS + HELD_OUT_CARS:
        jobs[u11_key(0.58, k)] = perturbed_job(U11, 0.58, k)
    # U11.9: the warnings as a trigger
    for k in TRAINING_CARS:
        jobs[warn_key(k)] = perturbed_job(U11, 0.58, k, *WARN_CONSTANTS)
    # U11.3: the fresh twins in the fallback configuration (constants override the fraction)
    for k in TWIN_CARS:
        jobs[twin_key(k)] = RobustJob(U11, NO_TIMING + TWIN_CONSTANTS, BASE, (race_seed(k),), perturb=k)
    # U11.6: the gate, and U11.7's training cars
    for k in HELD_OUT_CARS + EQUIVALENCE_CARS:
        jobs[u11_key(0.54, k)] = perturbed_job(U11, 0.54, k)
    # U11.7: the nominal car
    jobs[NOMINAL_U10] = RobustJob(U10, fraction(U10, 0.54) + NO_TIMING, BASE, (0,))
    jobs[NOMINAL_U11] = RobustJob(U11, NO_TIMING, BASE, (0,))
    # U11.8: the transfer to test-circuit-seed2026 (its line and measured grip), race seed 0
    track_constants = (("MU_G", MEASURED_MU_G[CHECKPOINT]), ("LINE_CONTROL", controls[(CHECKPOINT, "global")]))
    for k in TRANSFER_CARS:
        jobs[transfer_key(k)] = RobustJob(U11, track_constants + NO_TIMING, CHECKPOINT, (0,), perturb=k)
    return jobs


def _recorded(agent_class: type, agents: list) -> type:
    """The submission's class, keeping its instance in ``agents`` (the race is the submission's)."""

    class Recorded(agent_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            agents.append(self)

    return Recorded


def race_robust_job(job: RobustJob) -> List[RobustOutcome]:
    """Race one job (every seed in ``job.seeds``) in this process, keeping the agent's counters."""
    import numpy as np
    from _line_solver import line_offsets
    from racekit.cars import carla_like
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
                car = carla_like(noise=True, perturb=job.perturb, lag_ticks=job.lag_ticks)
                laps = {} if job.laps is None else {"laps": job.laps}
                result = run_race(_recorded(agent_class, agents), job.track, car=car, seed=seed,
                                  max_seconds=job.max_seconds, **laps)
            finally:
                sys.modules.pop(module_name, None)
            (agent,) = agents
            telemetry = result.telemetry
            driving = telemetry["held"] == 0
            offset = telemetry["offset"][driving]
            error = np.abs(offset - target[(telemetry["progress"][driving] + 1) % n])
            digest = hashlib.sha256(telemetry.tobytes() + repr(result.respawn_causes).encode()).hexdigest()
            outcomes.append(RobustOutcome(
                result.total_time, result.collisions, result.finished, float(np.max(error)), digest,
                tuple(result.respawn_times), getattr(agent, "respawns", None), getattr(agent, "warnings", None),
                getattr(agent, "mode", None)))
    return outcomes


def race_robust_premise(controls) -> Dict[str, List[RobustOutcome]]:
    return race_all(robust_premise_jobs(controls), worker=race_robust_job)

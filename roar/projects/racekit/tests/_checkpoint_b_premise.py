"""Checkpoint B's races (plan roar-011 CPB.2-CPB.5), raced once per test session in parallel with
``_premise.race_all``; CPB.4c's serial races are ``race_day_as_shipped`` (called by the test, in the
test process, after the pool has finished).

Two kinds of job share the pool (``race_checkpoint_b_job`` dispatches on the job's type):

* the six **grip probes** on the race-day track (CPB.2) are ``_agent_premise.AgentJob`` s raced by
  ``_line_premise.race_line_job``, exactly as Unit 8's probes are (``agents/unit-07.py``, A_LAT 3.5,
  one section's knob at 3.5, one lap, race seed 0, a 300 s cap, the nominal ``carla_like(noise=True)``);
* every other race is a ``_robust_premise.RobustJob`` raced by ``race_robust_job``, on
  ``carla_like(noise=True, perturb=k)``, race seed ``k mod 5`` for a sealed race-day car
  (k = 1000-1004) and race seed **0** for the small protocol's training cars (CPB.3), capped at 700 s.

The per-track constants are written in as ``_line_premise`` and ``_robust_premise`` write them:
``MU_G`` from the grip probes (``MEASURED_MU_G``; the race-day track's ``RACE_DAY_MU_G``) and
``LINE_CONTROL`` from the test-side solver; on ``test-circuit`` the agents' shipped values are raced as
shipped. The race-day line is solved once per session (``solve_race_day_line``); the training lines
come from the session's ``line_controls``.

Timing: every CPB.3-CPB.5 race runs the variant ``MPC_BUDGET_MS = None`` (no wall clock in a pinned
race), CPB.4b runs ``MPC_BUDGET_MS = 0.0`` (every ``mpc()`` call over budget), and CPB.4c races the
frozen file as shipped (``MPC_BUDGET_MS = 5.0``), serially, outside any pool.

**The seal.** The sealed cars (k = 1000-1004) are only ever *built* here, by ``carla_like(perturb=k)``
inside a race; nothing in the suite calls ``perturbation_factors`` on them (the protocol's car order
reads the factors of the training cars k = 0-23 only).

The tracks are loaded by their LITERAL generated names: the carla-like car's hidden grip is keyed to
the track name, so a rename changes the car and invalidates every pin.
"""

from __future__ import annotations

import contextlib
import io
from typing import Dict, List, Tuple

from _agent_premise import AgentJob
from _line_premise import (
    BASE,
    MEASURED_MU_G,
    PROBE_A_LAT,
    PROBE_CAP,
    TRAINING,
    probe_grip,
    race_line_job,
)
from _premise import race_all
from _robust_premise import CAP, NO_TIMING, RobustJob, race_robust_job, race_seed

RACE_DAY = "test-circuit-seed2027"  # Checkpoint B's race-day track (the stem is pinned literally)
# CPB.2: the race-day track's measured mu * g per section (probe p2, rounded to 0.01 as _line_premise
# rounds); section 0's probe never slid, so its value is a lower bound, used as measured
RACE_DAY_MU_G = (9.10, 9.55, 7.79, 9.35, 9.00, 7.76)
SEALED_CARS = tuple(range(1000, 1005))  # the race-day cars (race seed k mod 5); never inspected
TRAINING_CARS = tuple(range(24))
PROTOCOL_CARS = (16, 18, 8)  # CPB.3: the three lowest-grip training cars, ascending (asserted)
PROTOCOL_SEED = 0
PROTOCOL_FULL = (0.50, 0.48)  # all 15 protocol races
PROTOCOL_EDGE = (0.54, 0.52)  # the first 7 protocol races (the 7th is the first that is not clean)
PROTOCOL_PREFIX = 7
CONTRAST_FRACTION = 0.54  # CPB.5: Unit 11's shipped fraction
WORST_BUDGET = (("MPC_BUDGET_MS", 0.0),)  # CPB.4b: every mpc() call over budget

U10 = "unit-10.py"
U11 = "unit-11.py"
CHECKPOINT_B = "checkpoint-b.py"


def solve_race_day_line() -> Tuple[float, ...]:
    """The race-day track's smoothest line (Unit 9's method), solved once per session (about 0.1 s)."""
    from _line_solver import solve_track

    return solve_track((RACE_DAY, "global"))


def protocol_order() -> Tuple[Tuple[str, int], ...]:
    """The small protocol's 15 races in order: the five training tracks, each with the three cars."""
    return tuple((track, k) for track in TRAINING for k in PROTOCOL_CARS)


def lowest_grip_cars(count: int = 3) -> Tuple[int, ...]:
    """The ``count`` training cars with the lowest grip factor, ascending (training cars only)."""
    from racekit.cars import perturbation_factors

    return tuple(sorted(TRAINING_CARS, key=lambda k: perturbation_factors(k)["grip"])[:count])


def probe_key(section: int) -> str:
    return f"cpb-probe-{section}"


def protocol_key(fraction: float, track: str, k: int) -> str:
    return f"cpb-protocol-{fraction}-{track}-p{k}"


def race_day_key(k: int) -> str:
    return f"cpb-race-day-p{k}"


def worst_budget_key(k: int) -> str:
    return f"cpb-worst-budget-p{k}"


def contrast_key(agent: str, k: int) -> str:
    return f"cpb-contrast-{agent}-p{k}"


def _track_constants(track: str, controls) -> Tuple[Tuple[str, object], ...]:
    """A training track's measured grip and line (``test-circuit``: the agents' shipped ones)."""
    if track == BASE:
        return ()
    return (("MU_G", MEASURED_MU_G[track]), ("LINE_CONTROL", controls[(track, "global")]))


def _race_day_constants(race_day_line) -> Tuple[Tuple[str, object], ...]:
    return (("MU_G", RACE_DAY_MU_G), ("LINE_CONTROL", tuple(race_day_line)))


def checkpoint_b_jobs(controls, race_day_line) -> Dict[str, object]:
    """Every pooled Checkpoint B gate race, keyed by name: 70 races (the plan's job count). The
    likely crash loops (Unit 10 at 0.54 on race day, to the 700 s cap) come first."""
    jobs: Dict[str, object] = {}
    race_day = _race_day_constants(race_day_line)
    # CPB.5: the contrast on the sealed cars, Unit 10 (no fallback) first, then Unit 11, at 0.54
    for agent in (U10, U11):
        for k in SEALED_CARS:
            jobs[contrast_key(agent, k)] = RobustJob(
                agent, (("MU_FRACTION", CONTRAST_FRACTION),) + race_day + NO_TIMING, RACE_DAY, (race_seed(k),),
                perturb=k)
    # CPB.4: the frozen file, timing off; CPB.4b: the frozen file, every mpc() call over budget
    for k in SEALED_CARS:
        jobs[race_day_key(k)] = RobustJob(CHECKPOINT_B, NO_TIMING, RACE_DAY, (race_seed(k),), perturb=k)
    for k in SEALED_CARS:
        jobs[worst_budget_key(k)] = RobustJob(CHECKPOINT_B, WORST_BUDGET, RACE_DAY, (race_seed(k),), perturb=k)
    # CPB.3: the small protocol, race seed 0 (the first 7 races at 0.54 and 0.52, all 15 at 0.50, 0.48)
    order = protocol_order()
    for fraction in PROTOCOL_EDGE + PROTOCOL_FULL:
        races = order[:PROTOCOL_PREFIX] if fraction in PROTOCOL_EDGE else order
        for track, k in races:
            jobs[protocol_key(fraction, track, k)] = RobustJob(
                U11, (("MU_FRACTION", fraction),) + _track_constants(track, controls) + NO_TIMING, track,
                (PROTOCOL_SEED,), perturb=k)
    # CPB.2: Unit 8's six grip probes on the race-day track (the nominal carla-like car)
    for section in range(6):
        jobs[probe_key(section)] = AgentJob(
            "unit-07.py", (("A_LAT", PROBE_A_LAT), ("GRIP", probe_grip(section))), RACE_DAY, seeds=(0,),
            max_seconds=PROBE_CAP, car="carla", laps=1)
    return jobs


def race_checkpoint_b_job(job) -> List[object]:
    """Race one job in this process: a grip probe (``AgentJob``) or a perturbed race (``RobustJob``)."""
    if isinstance(job, RobustJob):
        return race_robust_job(job)
    return race_line_job(job)


def race_checkpoint_b(controls, race_day_line) -> Dict[str, List[object]]:
    return race_all(checkpoint_b_jobs(controls, race_day_line), worker=race_checkpoint_b_job)


def race_day_as_shipped() -> List[Tuple[object, int]]:
    """CPB.4c: ``agents/checkpoint-b.py`` as shipped (``MPC_BUDGET_MS = 5.0``) on the five sealed cars,
    raced serially in THIS process (call it after the pool has finished, as ``check_submission`` is).
    Returns ``(RobustOutcome, horizon cuts)`` per car; a cut is one line the agent printed when an
    ``mpc()`` call went over budget and the horizon was halved."""
    results = []
    for k in SEALED_CARS:
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            (outcome,) = race_robust_job(RobustJob(CHECKPOINT_B, (), RACE_DAY, (race_seed(k),), perturb=k,
                                                   max_seconds=CAP))
        cuts = sum("mpc() took" in line for line in printed.getvalue().splitlines())
        results.append((outcome, cuts))
    return results

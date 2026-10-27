"""The Unit 6 and Unit 7 premise races (plan roar-006 U6.1-U6.4, U7.1-U7.8), raced once per test
session in parallel with ``_premise.race_all``.

Each job races ``agents/unit-06.py`` or ``agents/unit-07.py`` (some module constants changed through
``write_variant``) on the dynamic car or the carla-like car, through ``_agent_premise``'s
``AgentJob`` / ``race_agent_job``. The results are ``{job key: [AgentOutcome per seed]}``, read
through the session fixture ``speed_premise`` (``conftest.py``). A job that serves two gates is raced
once (for example the reference's ten seeds on ``test-circuit`` serve U7.4, U7.5 and U7.8).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from _agent_premise import AgentJob, AgentOutcome, race_agent_job
from _premise import SEEDS, race_all

TRACKS = ("oval", "test-circuit", "monza-like")
SEEDS_10 = tuple(range(10))
UNIT6_CAP = 1500.0  # s: every Unit 6 race, and Unit 7's oval / monza-like / deterministic races
UNIT7_CAP = 600.0  # s: Unit 7's test-circuit races

# U6.2 / U6.3: the A_LAT sweeps of the cap (one deterministic race each)
U6_DYNAMIC_A_LAT = (5.0, 6.0, 7.0, 8.0, 9.0, 9.25, 9.5, 9.75, 10.0)
U6_CARLA0_A_LAT = {"test-circuit": (5.0, 6.0, 7.0, 8.0), "monza-like": (5.0, 6.0, 7.0, 8.0, 9.0)}

# U7.1: the pure-pursuit lookahead at 45 m/s (0.5 is the reference)
U7_PP_K = (0.3, 0.4, 0.6, 0.7)
# U7.2: the lead's edge rows (A_DEC, A_LAT), at the short lead 0.15 s and the reference's 0.3 s
U7_LEAD_ROWS = ((4.0, 5.0), (6.0, 4.0))
# U7.3: per A_DEC row, the last clean A_LAT and the first unclean A_LAT (on the given seeds)
U7_GRID_EDGE = {  # a_dec: (last clean a_lat, first unclean a_lat, its seeds)
    3.0: (5.2, 5.4, (0, 1)),
    4.0: (5.0, 5.2, (0, 1)),
    4.5: (4.8, 5.0, (1,)),
    5.0: (4.8, 5.0, (0, 1)),
    6.0: (4.4, 4.6, (0, 1)),
}
# U7.6 / U7.7: the per-section knobs (on top of the reference's A_LAT 4.6, A_DEC 5.0)
SINGLES = (1.2, 1.5, 1.1, 1.1, 1.05, 1.1)  # each section's knob, swept alone (q20)
EDGE_VECTOR = (1.2, 1.4, 1.0, 1.0, 1.0, 1.0)  # the sequential pass on seeds 0-4
ACCEPTED = (1.15, 1.3, 1.0, 1.0, 1.0, 1.0)  # one step back on the raised knobs


def knobs(**sections: float) -> Tuple[float, ...]:
    """A GRIP vector: 1.0 everywhere except ``s<section>=knob``."""
    grip = [1.0] * 6
    for name, knob in sections.items():
        grip[int(name[1:])] = knob
    return tuple(grip)


def grid_key(a_dec: float, a_lat: float) -> str:
    return f"u7-grid-{a_dec}-{a_lat}"


def grip_key(grip: Tuple[float, ...]) -> str:
    return "u7-grip-" + "-".join(str(knob) for knob in grip)


def _u6(constants, track, car, seeds=(0,)) -> AgentJob:
    return AgentJob("unit-06.py", tuple(constants), track, seeds=seeds, max_seconds=UNIT6_CAP, car=car)


def _u7(constants=(), track="test-circuit", car="carla", seeds=SEEDS, max_seconds=UNIT7_CAP) -> AgentJob:
    return AgentJob("unit-07.py", tuple(constants), track, seeds=seeds, max_seconds=max_seconds, car=car)


def speed_premise_jobs() -> Dict[str, AgentJob]:
    """Every Unit 6 / Unit 7 premise race, keyed by name."""
    flat = (("SPEED_MODE", "flat"),)
    jobs: Dict[str, AgentJob] = {
        # U6.1: the hook, the Unit 5 agent (unit-06.py with SPEED_MODE "flat") on the sliding cars
        "u6-flat-dynamic-test-circuit": _u6(flat, "test-circuit", "dynamic"),
        "u6-flat-carla0-test-circuit": _u6(flat, "test-circuit", "carla0"),
        "u6-flat-dynamic-monza-like": _u6(flat, "monza-like", "dynamic"),
        "u6-flat-dynamic-oval": _u6(flat, "oval", "dynamic"),
    }
    # U6.2: the cap against mu * g on DynamicCar()
    for track in ("test-circuit", "monza-like"):
        for a_lat in U6_DYNAMIC_A_LAT:
            jobs[f"u6-dynamic-{track}-{a_lat}"] = _u6((("A_LAT", a_lat),), track, "dynamic")
    # U6.3: the cap on carla_like(noise=False)
    for track, values in U6_CARLA0_A_LAT.items():
        for a_lat in values:
            jobs[f"u6-carla0-{track}-{a_lat}"] = _u6((("A_LAT", a_lat),), track, "carla0")
    # U6.4: the reference, carla_like(noise=True), seeds 0-4
    for track in TRACKS:
        jobs[f"u6-ref-{track}"] = _u6((), track, "carla", seeds=SEEDS)

    # U7.1: the lookahead at speed
    for k in U7_PP_K:
        jobs[f"u7-ppk-{k}"] = _u7((("PP_K", k),))
    # U7.2: the short lead on the two edge rows
    for a_dec, a_lat in U7_LEAD_ROWS:
        jobs[f"u7-lead-0.15-{a_dec}-{a_lat}"] = _u7((("A_LAT", a_lat), ("A_DEC", a_dec), ("PROFILE_LEAD_S", 0.15)))
    # U7.3: each grid row's last clean cell (seeds 0-4) and first unclean cell; (5.0, 4.8) is raced on
    # seeds 0-9 for U7.8, and U7.3 reads its first five
    for a_dec, (clean, unclean, seeds) in U7_GRID_EDGE.items():
        jobs[grid_key(a_dec, clean)] = _u7((("A_LAT", clean), ("A_DEC", a_dec)),
                                           seeds=SEEDS_10 if (a_dec, clean) == (5.0, 4.8) else SEEDS)
        jobs[grid_key(a_dec, unclean)] = _u7((("A_LAT", unclean), ("A_DEC", a_dec)), seeds=seeds)
    # U7.2: the edge rows at the reference lead 0.3 s ((4.0, 5.0) is a U7.3 cell already)
    for a_dec, a_lat in U7_LEAD_ROWS:
        jobs.setdefault(grid_key(a_dec, a_lat), _u7((("A_LAT", a_lat), ("A_DEC", a_dec))))
    # U7.4: the reference (test-circuit on seeds 0-9; oval and monza-like on seeds 0-4) ...
    jobs["u7-ref-test-circuit"] = _u7(seeds=SEEDS_10)
    for track in ("oval", "monza-like"):
        jobs[f"u7-ref-{track}"] = _u7(track=track, max_seconds=UNIT6_CAP)
    # ... and deterministic on seed 0
    for car in ("carla0", "dynamic"):
        for track in TRACKS:
            jobs[f"u7-ref-{car}-{track}"] = _u7(track=track, car=car, seeds=(0,), max_seconds=UNIT6_CAP)
    # U7.6: each section's knob alone (section 0's 1.2 is U7.7's kept step), and the stack on seeds 0-9
    vectors = {knobs(**{f"s{section}": knob}): SEEDS for section, knob in enumerate(SINGLES)}
    vectors[SINGLES] = SEEDS_10
    # U7.7: the sequential pass's kept and first unclean steps (section 1's kept step is the first five
    # seeds of the edge vector), the edge vector and the accepted vector on seeds 0-9
    vectors[knobs(s0=1.3)] = SEEDS
    vectors[knobs(s0=1.2, s1=1.5)] = SEEDS
    for section in range(2, 6):
        grip = list(EDGE_VECTOR)
        grip[section] = 1.05
        vectors[tuple(grip)] = SEEDS
    vectors[EDGE_VECTOR] = SEEDS_10
    vectors[ACCEPTED] = SEEDS_10
    for grip, seeds in vectors.items():
        jobs[grip_key(grip)] = _u7((("GRIP", grip),), seeds=seeds)
    return jobs


def race_speed_premise() -> Dict[str, List[AgentOutcome]]:
    return race_all(speed_premise_jobs(), worker=race_agent_job)

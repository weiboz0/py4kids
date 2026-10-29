"""The Unit 12 premise races (plan roar-012 U12.0-U12.7), raced once per test session in parallel with
``_premise.race_all``.

Two pools, in two session fixtures (``tests/conftest.py``):

* ``tuning_test_track``: Unit 12's **test track** ``test-circuit-seed2028`` (raced only by the final
  gate): its smoothest line (Unit 9's method, ``_line_solver.solve_track``, solved serially, about
  0.1 s) and Unit 8's six grip probes on it (U12.0; ``_agent_premise.AgentJob`` s raced by
  ``_line_premise.race_line_job``, exactly as Unit 8's and Checkpoint B's probes are:
  ``agents/unit-07.py``, A_LAT 3.5, one section's knob at 3.5, one lap, race seed 0, a 300 s cap,
  the nominal ``carla_like(noise=True)``);
* ``tuning_premise``: every other gate race, a ``_robust_premise.RobustJob`` raced by
  ``race_robust_job`` (the clean rule's numbers from the job's own line, a telemetry digest), on the
  nominal ``carla_like(noise=True)`` or a perturbed car ``carla_like(noise=True, perturb=k)``, 3 laps
  unless said (U12.2's knob map races one lap), capped at 700 s.

**Every race runs ``MPC_BUDGET_MS = None``** (no wall clock in a pinned race). The per-track
constants are written in as ``_line_premise`` and ``_robust_premise`` write them: ``MU_G`` from the
grip probes (``MEASURED_MU_G``; the test track's ``TEST_MU_G``, pinned from probe p9 and checked by
U12.0) and ``LINE_CONTROL`` from the test-side solver; on ``test-circuit`` the agents' shipped values
are raced as shipped.

**Each distinct race is raced once.** A gate names its races by ``race_key`` (the setting's label,
the track, the race seed, the car, the laps), and ``tuning_jobs`` keeps one job per key: U12.3's and
U12.4's ``agents/unit-11.py`` training races are U12.6's, and U12.1's spread uses U12.5a's races. The
one exception is U12.1's determinism re-race: its key carries the tag ``RERACE_TAG``, so the pool races
its twin (a U12.5 race) a second time, in the same pool.

The settings (plan roar-012's probes):

* ``unit-11.py`` and ``unit-12.py`` as shipped (``unit-12.py`` is ``unit-11.py`` with ``A_DEC = 5.5``);
* ``SPEED_SETTING``: the speed search's result on the training family (probe p3), written on the grid
  (``MU_FRACTION = 0.60``; the search's own value was ``0.6000000000000001``, the same race times in p8);
* ``OVERFIT_SETTING``: the one-track search's result on ``test-circuit`` (probe p5), raced with the
  values the search produced (``0.6400000000000001`` and ``1.2000000000000002``: grid steps added one at
  a time);
* ``DEAD_KNOBS``: three knobs the shipped mode never reads (U12.2), and ``MU_FRACTION = 0.60``;
* ``A_DEC = 6.0``: the step the crash-aware search rejected (U12.6).

The tracks are loaded by their LITERAL generated names: the carla-like car's hidden grip is keyed to
the track name, so a rename changes the car and invalidates every pin. Unit 12 never races
``test-circuit-seed2027`` (Checkpoint B's race-day track).
"""

from __future__ import annotations

from typing import Dict, List, NamedTuple, Optional, Tuple

from _agent_premise import AgentJob
from _line_premise import (
    BASE,
    CHECKPOINT,
    MEASURED_MU_G,
    PROBE_A_LAT,
    PROBE_CAP,
    TRAINING,
    probe_grip,
    race_line_job,
)
from _premise import race_all
from _robust_premise import NO_TIMING, RobustJob, race_robust_job

TEST = "test-circuit-seed2028"  # Unit 12's test track (the stem is pinned literally)
VALIDATION = CHECKPOINT  # test-circuit-seed2026: Unit 12's validation track
# U12.0: the test track's measured mu * g per section (probe p9, rounded to 0.01 as _line_premise
# rounds); section 0's probe never slid, so its value is a lower bound, used as measured
TEST_MU_G = (9.01, 9.13, 8.63, 9.38, 8.20, 10.09)
SEEDS5 = (0, 1, 2, 3, 4)
OBJECTIVE_SEEDS = (0, 1)  # the search's race seeds on the training tracks (one replicate each)
LOW_GRIP_CARS = (16, 18, 8)  # Unit 11's grip_order[:3] (Checkpoint B's PROTOCOL_CARS)
HELD_OUT_CARS = tuple(range(24, 48))
KNOB_LAPS = 1  # U12.2: the knob map races one lap
RERACE_TAG = "rerace"  # U12.1: the determinism twin's tag (raced a second time, past the dedupe)

U11 = "unit-11.py"
U12 = "unit-12.py"


class Setting(NamedTuple):
    label: str  # the race key's prefix
    agent: str  # a file in agents/
    constants: Tuple[Tuple[str, object], ...]  # module constants changed (before the track's)


SHIPPED_11 = Setting("u11", U11, ())
SHIPPED_12 = Setting("u12", U12, ())
# U12.4: the speed search's result (probe p3), on the grid
SPEED_SETTING = Setting("speed", U11, (("MU_FRACTION", 0.60), ("A_DEC", 5.5), ("A_ACC", 4.5)))
# U12.3: the one-track search's result (probe p5), the values the search produced
OVERFIT_SETTING = Setting("overfit", U11, (
    ("MU_FRACTION", 0.6400000000000001), ("A_DEC", 5.5),
    ("GRIP", (1.2000000000000002, 1.0, 1.05, 1.0, 1.0, 1.0)),
))
# U12.6: the step the crash-aware search rejected
A_DEC_6 = Setting("adec6", U11, (("A_DEC", 6.0),))
# U12.2: three dead knobs (the shipped mode never reads them) and one live one
DEAD_KNOBS = (
    Setting("dead-fallback-scale", U11, (("FALLBACK_SCALE", 0.5),)),
    Setting("dead-curvature-horizon", U11, (("CURVATURE_HORIZON", 5),)),
    Setting("dead-predict-ticks", U11, (("PREDICT_TICKS", 1),)),
)
MU_060 = Setting("mu-0.60", U11, (("MU_FRACTION", 0.60),))


class TestTrack(NamedTuple):
    line: Tuple[float, ...]  # the test track's LINE_CONTROL (131 values)
    probes: Dict[str, List[object]]  # probe_key(section) -> [LineOutcome]


def probe_key(section: int) -> str:
    return f"u12-probe-{section}"


def probe_jobs() -> Dict[str, AgentJob]:
    """U12.0: Unit 8's six grip probes on the test track (the nominal carla-like car)."""
    return {probe_key(section): AgentJob(
        "unit-07.py", (("A_LAT", PROBE_A_LAT), ("GRIP", probe_grip(section))), TEST, seeds=(0,),
        max_seconds=PROBE_CAP, car="carla", laps=1) for section in range(6)}


def measure_test_track() -> TestTrack:
    """U12.0: the test track's line (solved in this process) and its six grip probes (one small pool)."""
    from _line_solver import solve_track

    line = solve_track((TEST, "global"))
    return TestTrack(line, race_all(probe_jobs(), worker=race_line_job))


def race_key(setting: Setting, track: str, seed: int, perturb: Optional[int] = None,
             laps: Optional[int] = None, tag: str = "") -> str:
    key = f"{setting.label}|{track}|s{seed}"
    if perturb is not None:
        key += f"|p{perturb}"
    if laps is not None:
        key += f"|L{laps}"
    return key + (f"|{tag}" if tag else "")


def _track_constants(track: str, controls, test_line) -> Tuple[Tuple[str, object], ...]:
    """A track's measured grip and line (``test-circuit``: the agents' shipped ones)."""
    if track == BASE:
        return ()
    if track == TEST:
        return (("MU_G", TEST_MU_G), ("LINE_CONTROL", tuple(test_line)))
    return (("MU_G", MEASURED_MU_G[track]), ("LINE_CONTROL", controls[(track, "global")]))


class _Table:
    """The pooled job table: one job per race key (a key raced twice must be the same job)."""

    def __init__(self, controls, test_line) -> None:
        self.controls, self.test_line = controls, test_line
        self.jobs: Dict[str, RobustJob] = {}

    def add(self, setting: Setting, track: str, seed: int, perturb: Optional[int] = None,
            laps: Optional[int] = None, tag: str = "") -> str:
        assert track != "test-circuit-seed2027"  # Checkpoint B's race-day track: never raced here
        assert perturb is None or perturb < 1000  # never a sealed car
        constants = setting.constants + _track_constants(track, self.controls, self.test_line) + NO_TIMING
        job = RobustJob(setting.agent, constants, track, (seed,), perturb=perturb, laps=laps)
        key = race_key(setting, track, seed, perturb, laps, tag)
        assert self.jobs.setdefault(key, job) == job, key
        return key


def tuning_jobs(controls, test_line) -> Dict[str, RobustJob]:
    """Every pooled Unit 12 gate race, keyed by ``race_key``, each distinct race once (U12.1's twin
    twice). The likely crashes (to hundreds of seconds) come first, so the pool starts them first."""
    table = _Table(controls, test_line)
    # U12.6: A_DEC = 6.0 on car 16 at replicates 0 and 1 (p8: both crash)
    for replicate in OBJECTIVE_SEEDS:
        table.add(A_DEC_6, BASE, (16 + replicate) % 5, perturb=16)
    # U12.3: the overfit setting on the validation track (p5: crashes)
    for seed in SEEDS5[:3]:
        table.add(OVERFIT_SETTING, VALIDATION, seed)
    # U12.4 and U12.5: the speed setting on the validation and test tracks
    for seed in SEEDS5:
        table.add(SPEED_SETTING, VALIDATION, seed)
        table.add(SPEED_SETTING, TEST, seed)
    # U12.4: the speed setting on the training family
    for track in TRAINING:
        for seed in OBJECTIVE_SEEDS:
            table.add(SPEED_SETTING, track, seed)
    # U12.3: the overfit setting on test-circuit
    for seed in OBJECTIVE_SEEDS:
        table.add(OVERFIT_SETTING, BASE, seed)
    # U12.6 (and U12.3's and U12.4's unit-11 races): the crash-aware objective's 16 races per agent
    for setting in (SHIPPED_11, SHIPPED_12):
        for replicate in range(len(OBJECTIVE_SEEDS)):
            for track, seed, perturb in objective_races(replicate):
                table.add(setting, track, seed, perturb)
    # U12.5a (and U12.1's spread): the validation track; U12.5: the test track
    for setting in (SHIPPED_11, SHIPPED_12):
        for seed in SEEDS5:
            table.add(setting, VALIDATION, seed)
            table.add(setting, TEST, seed)
    # U12.1: the determinism twin of a U12.5 race, raced again in the same pool
    table.add(SHIPPED_12, TEST, 0, tag=RERACE_TAG)
    # U12.7: unit-12 on the held-out perturbed cars
    for k in HELD_OUT_CARS:
        table.add(SHIPPED_12, BASE, k % 5, perturb=k)
    # U12.2: the knob map, one lap of test-circuit, race seed 0
    for setting in (SHIPPED_11,) + DEAD_KNOBS + (MU_060,):
        table.add(setting, BASE, 0, laps=KNOB_LAPS)
    return table.jobs


def objective_races(replicate: int) -> Tuple[Tuple[str, int, Optional[int]], ...]:
    """The crash-aware objective's 16 races for one replicate ``r``: (track, race seed, car): the five
    training tracks at race seed ``OBJECTIVE_SEEDS[r]`` (the nominal car), then ``test-circuit`` on cars
    16, 18 and 8 at race seed (k + r) mod 5."""
    seed = OBJECTIVE_SEEDS[replicate]
    return (tuple((track, seed, None) for track in TRAINING)
            + tuple((BASE, (k + replicate) % 5, k) for k in LOW_GRIP_CARS))


def objective_keys(setting: Setting, replicate: int) -> Tuple[str, ...]:
    return tuple(race_key(setting, track, seed, perturb) for track, seed, perturb in objective_races(replicate))


def race_tuning_premise(controls, test_track: TestTrack) -> Dict[str, List[object]]:
    return race_all(tuning_jobs(controls, test_track.line), worker=race_robust_job)

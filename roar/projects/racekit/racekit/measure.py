"""Repeated races and noise-aware comparison (design 013 §4.5, Unit 1's measurement rule).

Single-run comparisons partly rank noise: places in the real race are tenths of a second apart and
run-to-run noise is about 0.3 s. ``repeat_races`` runs a submission several times; the **spread is
the range (max − min)**, the conservative choice for about five runs. ``noise_aware_better(a, b)``
says "a beats b" only when b's median is slower than a's by more than either spread.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, List, Optional, Sequence, Union

import numpy as np

from .cars import Car
from .runner import DEFAULT_LAPS, DEFAULT_MAX_SECONDS, RaceResult, run_race
from .tracks import Track


class RepeatResult:
    """``n`` races of one submission: per-run results, their times, the median and the spread."""

    def __init__(self, results: List[RaceResult]) -> None:
        self.results = results
        self.times = np.array([result.total_time for result in results], dtype=np.float64)
        self.median = float(np.median(self.times))
        self.spread = spread(self.times)
        self.collisions = int(sum(result.collisions for result in results))
        self.all_finished = all(result.finished for result in results)

    def __repr__(self) -> str:
        return (
            f"RepeatResult(n={len(self.results)}, median={self.median:.2f} s, "
            f"spread={self.spread:.2f} s, collisions={self.collisions})"
        )


def spread(times: Iterable[float]) -> float:
    """The spread of repeated race times: the range, max − min."""
    values = np.asarray(list(times), dtype=np.float64)
    return float(values.max() - values.min()) if values.size else 0.0


def repeat_races(
    submission: Union[str, Path, type],
    track: Union[str, Path, Track],
    n: int = 5,
    seeds: Optional[Sequence[int]] = None,
    car_factory: Optional[Any] = None,
    laps: int = DEFAULT_LAPS,
    max_seconds: float = DEFAULT_MAX_SECONDS,
) -> RepeatResult:
    """Race ``submission`` ``n`` times, one seed per run (default seeds ``0 .. n-1``).

    ``car_factory()`` builds a fresh car per run (default: racekit's default car).
    """
    seeds = list(range(n)) if seeds is None else list(seeds)
    if len(seeds) != n:
        raise ValueError(f"need {n} seeds, got {len(seeds)}")
    results = []
    for seed in seeds:
        car: Optional[Car] = car_factory() if car_factory is not None else None
        results.append(run_race(submission, track, car=car, laps=laps, max_seconds=max_seconds, seed=seed))
    return RepeatResult(results)


def noise_aware_better(a_times: Iterable[float], b_times: Iterable[float]) -> bool:
    """True when ``a`` beats ``b`` by more than the noise: median(b) − median(a) > max(spreads)."""
    a = np.asarray(list(a_times), dtype=np.float64)
    b = np.asarray(list(b_times), dtype=np.float64)
    if a.size == 0 or b.size == 0:
        raise ValueError("both samples need at least one time")
    return bool(np.median(b) - np.median(a) > max(spread(a), spread(b)))

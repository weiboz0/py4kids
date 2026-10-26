"""Repeated races and noise-aware comparison (plan roar-001 Phase D)."""

from __future__ import annotations

import numpy as np
import pytest
from conftest import STARTER
from racekit.measure import RepeatResult, noise_aware_better, repeat_races, spread


def test_repeat_races_is_deterministic_with_seeds():
    first = repeat_races(STARTER, "oval", n=3, seeds=[4, 5, 6], laps=1)
    second = repeat_races(STARTER, "oval", n=3, seeds=[4, 5, 6], laps=1)
    assert isinstance(first, RepeatResult)
    assert np.array_equal(first.times, second.times)
    assert [result.seed for result in first.results] == [4, 5, 6]
    assert first.median == pytest.approx(float(np.median(first.times)))
    assert first.spread == pytest.approx(0.0)  # the kinematic car is noise-free
    assert first.all_finished and first.collisions == 0
    with pytest.raises(ValueError, match="seeds"):
        repeat_races(STARTER, "oval", n=2, seeds=[1])


def test_spread_is_the_range():
    assert spread([320.1, 319.7, 320.4, 319.9, 320.0]) == pytest.approx(0.7)
    assert spread([5.0]) == 0.0


def test_noise_aware_rule_on_synthetic_times():
    rng = np.random.default_rng(0)
    base = 320.0 + rng.uniform(-0.15, 0.15, size=5)  # about 0.3 s of run-to-run noise
    much_slower = base + 1.0
    barely_slower = base + 0.1
    assert noise_aware_better(base, much_slower)  # a beats b by more than either spread
    assert not noise_aware_better(much_slower, base)
    assert not noise_aware_better(base, barely_slower)  # inside the noise: not a real win
    assert not noise_aware_better(base, base)
    # the margin must exceed the larger spread, not just a's
    a = [300.0, 300.0, 300.0]
    b = [300.4, 301.0, 302.0]  # median 301.0, spread 1.6 > 1.0
    assert not noise_aware_better(a, b)
    assert noise_aware_better(a, [302.0, 302.5, 302.6])
    with pytest.raises(ValueError):
        noise_aware_better([], [1.0])

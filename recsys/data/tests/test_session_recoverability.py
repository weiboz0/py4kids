"""Session recoverability harness (plan recsys-014 Goal 3) — the U12 order-signal CI gate.

Unit 12 teaches sequence-aware retrieval on the separate session log (``sessions.csv.gz`` +
``series.csv.gz``). This guard asserts, at the committed seed, that the log's order signal is real
and recoverable by small numpy references (``_reference_recommenders.py``; fixed protocol:
positives only, ``(timestamp, file row order)`` ordering, train-only references, the scoreboard's
``val − train`` cohort, k = 10):

- **G3a** last-3 CF beats bag CF (order-aware context beats the bag);
- **G3b** the last-5 transition reference beats its shuffled-history control (order, not the item
  multiset, carries the lift);
- **G3c** next-in-series: when volume v is in the last-5 window and v+1 is an unseen val positive,
  the transition reference ranks v+1 far more often than bag CF;
- **G3d** sanity: bag CF ≥ 2× popularity, popularity ≥ 0.05 (strong-but-beatable baseline).

The committed-seed tests read the CI-regenerated files (zero regeneration cost; skipped when the
generated directory is absent). The **teeth** tests regenerate a small session log with all three
order mechanisms disabled and assert the G3b / G3c ratio and difference clauses FAIL, plus a
positive control (same small config, mechanisms ON) that passes G3b — so the guard is shown to
detect the signal's absence, not just to pass.

Pinned thresholds (plan: "pinned from the one-shot committed-seed measurement with headroom, never
below the floors"). Committed-seed one-shot values: eligible 1419; popularity .113; bag CF .480;
last-3 CF .550; last-5 transition ordered .510 / shuffled .343; G3c n 654, transition .500 vs bag
.301; G3d bag/pop 4.23. Each pin sits roughly midway between the plan floor and the measured value,
so CI keeps real margin (a NEP-19 numpy-stream change will not trip it by noise; G3a's paired SE is
≈ 0.014) while still failing well above the floor if the signal erodes:

==========  =========================  =============  ===========
gate        clause                     plan floor     pinned
==========  =========================  =============  ===========
eligible    readers                    ≥ 800          ≥ 1100
G3a         lastk_cf − bag_cf          ≥ +0.02        ≥ +0.04
G3b         ordered / shuffled         ≥ 1.3×         ≥ 1.38×
G3b         ordered − shuffled         ≥ +0.06        ≥ +0.11
G3c         n                          ≥ 100          ≥ 350
G3c         transk / bag_cf            ≥ 1.3×         ≥ 1.45×
G3c         transk − bag_cf            ≥ +0.10        ≥ +0.14
G3d         bag_cf / popularity        ≥ 2×           ≥ 3×
G3d         popularity                 ≥ 0.05         ≥ 0.08
==========  =========================  =============  ===========

Runs in the routed ``uv run --group recsys pytest recsys/`` step (numpy + the generators).
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest
from _common import GENERATED_DIR, DatasetConfig
from _reference_recommenders import (
    evaluate_session_recoverability,
    next_volume_from_series,
    ordered_positive_sequences,
    ordered_split_sequences,
)
from gen_catalog import generate_catalog
from gen_sessions import generate_series, generate_sessions

# Plan floors (Goal 3) — the teeth / positive-control tests judge against these.
FLOOR_G3B_RATIO, FLOOR_G3B_DIFF = 1.3, 0.06
FLOOR_G3C_RATIO, FLOOR_G3C_DIFF = 1.3, 0.10

# Committed-seed CI pins (see the module docstring table for floors + measured values).
PIN_ELIGIBLE = 1100
PIN_G3A_DIFF = 0.04
PIN_G3B_RATIO, PIN_G3B_DIFF = 1.38, 0.11
PIN_G3C_N, PIN_G3C_RATIO, PIN_G3C_DIFF = 350, 1.45, 0.14
PIN_G3D_RATIO, PIN_G3D_POP = 3.0, 0.08

# The teeth config: a small catalog, dense long series and a larger val share, sized so that even
# with every order mechanism OFF the chance next-in-series cohort reaches n >= 30 (asserted), while
# the 500-book catalog keeps hit@10 off the ceiling so the mechanisms-ON positive control can clear
# the G3b floors. Fixture-only knobs (series_len 5..10, val_fraction 0.2) — not the committed data.
TEETH_CONFIG = DatasetConfig(
    seed=12345,
    n_books=500,
    n_authors=40,
    n_readers=120,
    n_cold_items=20,
    n_cold_readers=20,
    series_fraction=0.95,
    series_len_min=5,
    series_len_max=10,
    val_fraction=0.2,
    session_n_readers=1200,
)
MECHANISMS_OFF = {
    "session_series_follow_prob": 0.0,
    "session_author_bump": 0.0,
    "session_mood_boost": 0.0,
}
TEETH_MIN_G3C_N = 30


# --------------------------------------------------------------------------------- committed seed
@pytest.fixture(scope="module")
def committed() -> dict:
    """Goal-3 metrics on the CI-generated committed-seed session log."""
    if not GENERATED_DIR.is_dir():
        pytest.skip("CI-generated artifacts are absent; run gen_catalog.py and gen_interactions.py")
    missing = [n for n in ("sessions.csv.gz", "series.csv.gz") if not (GENERATED_DIR / n).is_file()]
    assert not missing, f"generated directory is incomplete (missing: {', '.join(missing)})"
    config = DatasetConfig()
    train, val = ordered_split_sequences(GENERATED_DIR / "sessions.csv.gz")
    next_volume = next_volume_from_series(GENERATED_DIR / "series.csv.gz", config.n_books)
    return evaluate_session_recoverability(
        train, val, next_volume, config.n_books, seed=config.effective_session_seed
    )


def test_enough_eligible_readers(committed: dict) -> None:
    assert committed["eligible"] >= PIN_ELIGIBLE, committed["eligible"]


def test_g3a_last_k_cf_beats_bag_cf(committed: dict) -> None:
    assert committed["g3a_diff"] >= PIN_G3A_DIFF, (committed["lastk_cf"], committed["bag_cf"])


def test_g3b_transition_beats_shuffled_control(committed: dict) -> None:
    detail = (committed["transk"], committed["transk_shuf"])
    assert committed["g3b_ratio"] >= PIN_G3B_RATIO, detail
    assert committed["g3b_diff"] >= PIN_G3B_DIFF, detail


def test_g3c_next_in_series_transition_beats_bag_cf(committed: dict) -> None:
    detail = (committed["g3c_n"], committed["g3c_transk"], committed["g3c_bag"])
    assert committed["g3c_n"] >= PIN_G3C_N, detail
    assert committed["g3c_ratio"] >= PIN_G3C_RATIO, detail
    assert committed["g3c_diff"] >= PIN_G3C_DIFF, detail


def test_g3d_bag_cf_beats_a_strong_popularity_baseline(committed: dict) -> None:
    detail = (committed["bag_cf"], committed["popularity"])
    assert committed["popularity"] >= PIN_G3D_POP, detail
    assert committed["g3d_ratio"] >= PIN_G3D_RATIO, detail


# ------------------------------------------------------------------------------------------ teeth
_TEETH_CACHE: dict[bool, dict] = {}


def _teeth_metrics(mechanisms_on: bool) -> dict:
    """Goal-3 metrics on the small teeth config, order mechanisms ON or all three OFF."""
    if mechanisms_on not in _TEETH_CACHE:
        config = TEETH_CONFIG if mechanisms_on else replace(TEETH_CONFIG, **MECHANISMS_OFF)
        catalog = generate_catalog(config, np.random.default_rng(config.seed))
        series = generate_series(catalog, config)
        log = generate_sessions(catalog, series, np.zeros(0, dtype=np.int64), config)
        train, val = ordered_positive_sequences(
            log.reader_ids, log.item_ids, log.timestamps, log.splits, log.labels
        )
        _TEETH_CACHE[mechanisms_on] = evaluate_session_recoverability(
            train, val, series.next_volume(), catalog.n_books, seed=config.effective_session_seed
        )
    return _TEETH_CACHE[mechanisms_on]


def test_teeth_g3b_clauses_fail_without_order_mechanisms() -> None:
    off = _teeth_metrics(mechanisms_on=False)
    detail = (off["transk"], off["transk_shuf"])
    assert off["g3b_ratio"] < FLOOR_G3B_RATIO, detail
    assert off["g3b_diff"] < FLOOR_G3B_DIFF, detail


def test_teeth_g3c_clauses_fail_without_order_mechanisms() -> None:
    off = _teeth_metrics(mechanisms_on=False)
    detail = (off["g3c_n"], off["g3c_transk"], off["g3c_bag"])
    # The small config is sized so the chance next-in-series cohort is non-trivial even with no
    # forced next-volume slot — otherwise "the G3c clauses fail" would be vacuous.
    assert off["g3c_n"] >= TEETH_MIN_G3C_N, detail
    assert off["g3c_ratio"] < FLOOR_G3C_RATIO, detail
    assert off["g3c_diff"] < FLOOR_G3C_DIFF, detail


def test_positive_control_g3b_passes_with_order_mechanisms_on() -> None:
    on = _teeth_metrics(mechanisms_on=True)
    detail = (on["transk"], on["transk_shuf"])
    assert on["g3b_ratio"] >= FLOOR_G3B_RATIO, detail
    assert on["g3b_diff"] >= FLOOR_G3B_DIFF, detail

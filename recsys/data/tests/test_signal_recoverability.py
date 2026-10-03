"""Recoverability harness (plan recsys-004 Phase C) — the committed acceptance gate.

This is the durable CI guard that the synthetic data keeps the signal hierarchy the personalization
arc teaches: popularity is a strong but beatable baseline; content (genre + keyword BM25) and
collaborative (item-item CF, learned MF) signals each beat popularity and are ordered
``content < CF ≈ MF``; the true-affinity oracle beats popularity while the exposure-propensity
oracle is the ceiling; and the U2 positive-rate "quality" lens stays weak. Denominators use the
**analytic** expected random floor (U1), and every gate carries a ratio threshold, an absolute
margin, and a minimum eligible-reader count (NEP-19 robustness; [fable]#2 / [sol]#3).

Runs in the routed ``uv run --group recsys pytest recsys/`` step (numpy + the generators).
"""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest
from _common import DatasetConfig
from _reference_recommenders import evaluate_recoverability
from gen_catalog import generate_catalog, generate_keywords
from gen_interactions import generate_interactions

K = 10
MIN_READERS = 300
COMMITTED_SEED = DatasetConfig().seed

_CACHE: dict[tuple, dict] = {}


def _measure(**overrides) -> dict:
    """Build the dataset for a config (committed defaults + overrides) and evaluate recoverability."""
    key = tuple(sorted(overrides.items()))
    if key not in _CACHE:
        config = replace(DatasetConfig(), **overrides)
        rng = np.random.default_rng(config.seed)
        catalog = generate_catalog(config, rng)
        inter = generate_interactions(catalog, config, rng)
        keywords = generate_keywords(catalog, config)
        _CACHE[key] = evaluate_recoverability(inter, keywords.tf_matrix(), k=K, seed=0)
    return _CACHE[key]


@pytest.fixture(scope="module")
def m() -> dict:
    """Metrics on the committed seed / default config (the shipped dataset)."""
    return _measure()


# ----------------------------------------------------------------------- committed-seed gates
def test_enough_eligible_readers(m: dict) -> None:
    assert m["readers"] >= MIN_READERS, m["readers"]


def test_popularity_is_strong_but_beatable_baseline(m: dict) -> None:
    floor = m["analytic_floor"]
    assert m["popularity"] >= 5.0 * floor, (m["popularity"], floor)
    assert m["popularity"] >= floor + 0.03, (m["popularity"], floor)


def test_quality_positive_rate_stays_weak(m: dict) -> None:
    # U2 lesson preserved: ranking by positive-RATE ignores popularity AND the reader → weak.
    assert m["quality"] < 0.5 * m["popularity"], (m["quality"], m["popularity"])


def test_genre_content_beats_floor(m: dict) -> None:
    floor = m["analytic_floor"]
    assert m["genre_cosine"] >= 2.0 * floor, (m["genre_cosine"], floor)
    assert m["genre_cosine"] >= floor + 0.03, (m["genre_cosine"], floor)


def test_keyword_bm25_beats_floor(m: dict) -> None:
    floor = m["analytic_floor"]
    assert m["keyword_bm25"] >= 2.0 * floor, (m["keyword_bm25"], floor)
    assert m["keyword_bm25"] >= floor + 0.03, (m["keyword_bm25"], floor)


def test_content_is_below_collaborative(m: dict) -> None:
    content = max(m["genre_cosine"], m["keyword_bm25"])
    assert content < m["item_item_cf"] - 0.02, (content, m["item_item_cf"])


def test_item_item_cf_beats_popularity(m: dict) -> None:
    assert m["item_item_cf"] >= 1.3 * m["popularity"], (m["item_item_cf"], m["popularity"])
    assert m["item_item_cf"] >= m["popularity"] + 0.03, (m["item_item_cf"], m["popularity"])


def test_learned_mf_beats_popularity_and_content(m: dict) -> None:
    content = max(m["genre_cosine"], m["keyword_bm25"])
    assert m["learned_mf"] >= 1.2 * m["popularity"], (m["learned_mf"], m["popularity"])
    assert m["learned_mf"] >= content, (m["learned_mf"], content)


def test_true_affinity_oracle_beats_popularity(m: dict) -> None:
    # Holds at α=0.75; we do NOT assert "oracle ≥ CF" — CF legitimately learns the exposure
    # pattern the pure-affinity oracle ignores ([fable]#1).
    assert m["affinity_oracle"] >= 2.0 * m["popularity"], (m["affinity_oracle"], m["popularity"])
    assert m["affinity_oracle"] >= m["popularity"] + 0.05, (m["affinity_oracle"], m["popularity"])


def test_propensity_oracle_is_the_ceiling(m: dict) -> None:
    others = (m["affinity_oracle"], m["item_item_cf"], m["learned_mf"], m["popularity"])
    assert m["propensity_oracle"] > max(others), (m["propensity_oracle"], others)


def test_popularity_coverage_guard(m: dict) -> None:
    assert m["popularity_coverage"] < 0.05, m["popularity_coverage"]
    assert m["popularity_coverage"] < 0.1 * m["random_coverage"], (
        m["popularity_coverage"],
        m["random_coverage"],
    )


def test_popularity_recommendations_are_all_head(m: dict) -> None:
    assert m["pop_rec_head_share"] == 1.0, m["pop_rec_head_share"]


def test_keywords_encode_latent_structure_beyond_genre(m: dict) -> None:
    # Controlling for genre, latent-near books share MORE keywords than latent-far ones.
    assert m["kw_latent_near_overlap"] > 1.1 * m["kw_genre_control_overlap"], (
        m["kw_latent_near_overlap"],
        m["kw_genre_control_overlap"],
    )


# ----------------------------------------------------------------------- robustness across seeds
@pytest.mark.parametrize("seed", [COMMITTED_SEED + 1, COMMITTED_SEED + 2])
def test_hierarchy_is_robust_across_seeds(seed: int) -> None:
    r = _measure(seed=seed)
    floor = r["analytic_floor"]
    content = max(r["genre_cosine"], r["keyword_bm25"])
    assert r["readers"] >= MIN_READERS, r["readers"]
    assert r["popularity"] >= 5.0 * floor
    assert r["genre_cosine"] >= 2.0 * floor
    assert r["keyword_bm25"] >= 2.0 * floor
    assert content < r["item_item_cf"]
    assert r["item_item_cf"] >= 1.3 * r["popularity"]
    assert r["learned_mf"] >= 1.2 * r["popularity"]
    assert r["learned_mf"] >= content
    assert r["affinity_oracle"] >= 2.0 * r["popularity"]
    assert r["quality"] < 0.5 * r["popularity"]
    assert r["kw_latent_near_overlap"] > 1.1 * r["kw_genre_control_overlap"]


# ------------------------------------------------------------------------- the guard has teeth
def test_guard_fails_when_affinity_signal_removed() -> None:
    # β→0: no taste in exposure ⇒ collaborative signal collapses (CF no longer beats popularity,
    # true-affinity oracle no longer beats popularity). The harness must go red here.
    r = _measure(exposure_affinity_weight=0.0)
    assert not (
        r["item_item_cf"] >= 1.3 * r["popularity"]
        and r["affinity_oracle"] >= 2.0 * r["popularity"]
    ), (r["item_item_cf"], r["affinity_oracle"], r["popularity"])


def test_guard_fails_when_popularity_swamps_affinity() -> None:
    # α raised high: popularity swamps taste ⇒ the true-affinity oracle can no longer beat
    # popularity. The harness must go red here.
    r = _measure(popularity_exposure_weight=3.0)
    assert r["affinity_oracle"] < 2.0 * r["popularity"], (r["affinity_oracle"], r["popularity"])

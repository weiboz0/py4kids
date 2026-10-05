"""Unit 6 (recsys-008): evaluation deepened + the first blended recommender.

Two layers are verified here:

1. **Pure metrics** on hand-checkable fixtures — precision@k and NDCG@k (binary-gain DCG with a
   ``log2(rank + 1)`` discount over IDCG), intra-list diversity (``1 − mean pairwise similarity``)
   and novelty (mean ``−log2 p̂``, monotonic in rarity). All deterministic and 0-safe.
2. **The pinned-config blend** on the shipped recsys-004 data, bound to the MEASURED numbers so the
   lesson/checkpoint prose cannot drift from the shipped code. Measured (seed 0, k=10, pool 30, 60
   cold readers excluded, 500 eligible val readers), with weights
   ``{popularity 0.25, lexical 0.5, item-item 1.0, mf 1.0}``:

   - single paths: popularity 0.108 (cov 0.008), lexical 0.158 (0.278), item-item 0.252 (0.490),
     **MF 0.276 (0.0745)**;
   - **full blend 0.306 (cov 0.333)** — beats the best single path (MF) AND covers ~4.5x more
     catalog;
   - leave-one-path-out ablation: **dropping popularity RAISES hit@10** (0.308 > 0.306) — a
     reader-independent path, once min-max calibrated to [0, 1], ties its head books with every
     reader's true top pick, so "every path helps" is false here.

The config is **pinned** (pool/weights fixed) so the subagent cannot tune it on ``val`` — which is
the anti-lesson the unit teaches. numpy-only.
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import re
from pathlib import Path

import pytest
from bookrec import (
    Candidate,
    ItemItemRetrievalPath,
    LexicalRetrievalPath,
    MatrixFactorizationPath,
    PopularityRetrievalPath,
    blend,
    generated_dir,
    intra_list_diversity,
    load_catalog,
    load_keywords,
    ndcg_at_k,
    novelty,
    precision_at_k,
    rank,
    recall_at_k,
    run_blended_scoreboard,
    run_validation_scoreboard,
)

K = 10
POOL = 30
SEED = 0
WEIGHTS = {"popularity": 0.25, "lexical": 0.5, "item-item": 1.0, "mf": 1.0}


# ======================================================================================
# Pure metrics on hand-checkable fixtures
# ======================================================================================


def test_precision_at_k_counts_relevant_slots_over_k() -> None:
    recs = [1, 2, 3, 4]
    relevant = {2, 4}
    # 2 of the top-4 slots are relevant -> 2/4 = 0.5 (denominator is always k).
    assert precision_at_k(recs, relevant, 4) == pytest.approx(0.5)
    # Over the top-2 only item 2 is relevant -> 1/2 = 0.5.
    assert precision_at_k(recs, relevant, 2) == pytest.approx(0.5)
    # A perfectly relevant top-2 -> 2/2 = 1.0.
    assert precision_at_k([2, 4, 1, 3], relevant, 2) == pytest.approx(1.0)
    # Empty relevant set is defined as 0.0 (no precision to earn), never a divide error.
    assert precision_at_k(recs, set(), 4) == 0.0


def test_precision_at_k_accepts_candidates_and_rejects_bad_k() -> None:
    recs = [Candidate(2, 9.0, "p"), Candidate(5, 8.0, "p"), Candidate(7, 7.0, "p")]
    assert precision_at_k(recs, {5}, 3) == pytest.approx(1.0 / 3.0)
    for bad in (0, -1, 2.0, True):
        with pytest.raises(ValueError):
            precision_at_k(recs, {5}, bad)  # type: ignore[arg-type]


def test_ndcg_at_k_matches_a_hand_computed_value() -> None:
    # Ranking [1,2,3,4,5], relevant {2,5}: a relevant item at 1-based rank r earns 1/log2(r+1).
    #   DCG  = 1/log2(3) + 1/log2(6)          (ranks 2 and 5)
    #   IDCG = 1/log2(2) + 1/log2(3)          (two relevant items front-loaded)
    #   NDCG = DCG / IDCG = 0.62402...
    dcg = 1.0 / math.log2(3) + 1.0 / math.log2(6)
    idcg = 1.0 / math.log2(2) + 1.0 / math.log2(3)
    expected = dcg / idcg
    assert ndcg_at_k([1, 2, 3, 4, 5], {2, 5}, 5) == pytest.approx(expected)
    assert expected == pytest.approx(0.6240, abs=1e-4)  # the hand value, pinned


def test_ndcg_at_k_rewards_higher_placement() -> None:
    relevant = {7}
    # The same single relevant item scores strictly more the higher it sits.
    top = ndcg_at_k([7, 1, 2, 3], relevant, 4)
    mid = ndcg_at_k([1, 7, 2, 3], relevant, 4)
    low = ndcg_at_k([1, 2, 3, 7], relevant, 4)
    assert top == pytest.approx(1.0)  # one relevant item at rank 1 is the ideal ranking
    assert top > mid > low > 0.0


def test_ranking_metrics_are_range_safe_on_duplicate_ids() -> None:
    # A malformed ranking that repeats an item must not earn relevance credit twice: de-dup keeps
    # the first occurrence, so precision@2 of [1, 1] against {1} is |{1}|/2 = 0.5 and NDCG stays in
    # [0, 1] (the single relevant item at rank 1 is the ideal ordering -> 1.0), never 1.63.
    assert precision_at_k([1, 1], {1}, 2) == pytest.approx(0.5)
    assert ndcg_at_k([1, 1], {1}, 2) == pytest.approx(1.0)
    assert 0.0 <= ndcg_at_k([3, 3, 3, 1], {1, 3}, 4) <= 1.0
    # recall counts each relevant item once regardless of repeats.
    assert recall_at_k([5, 5], {5, 9}, 2) == pytest.approx(0.5)


def test_ndcg_at_k_is_zero_safe_on_empty_relevant() -> None:
    assert ndcg_at_k([1, 2, 3], set(), 3) == 0.0
    assert ndcg_at_k([], {1}, 3) == 0.0  # nothing retrieved -> no gain


def test_intra_list_diversity_of_a_two_item_list() -> None:
    # Two items whose similarity is 0.25 -> diversity = 1 - 0.25 = 0.75 (a callable similarity).
    sim = {(10, 20): 0.25, (20, 10): 0.25}
    assert intra_list_diversity([10, 20], lambda a, b: sim[(a, b)]) == pytest.approx(0.75)
    # Identical items (similarity 1.0) -> diversity 0.0; orthogonal (0.0) -> diversity 1.0.
    assert intra_list_diversity([10, 20], lambda a, b: 1.0) == pytest.approx(0.0)
    assert intra_list_diversity([10, 20], lambda a, b: 0.0) == pytest.approx(1.0)
    # Fewer than two items -> no pairs -> 0.0 by convention.
    assert intra_list_diversity([10], lambda a, b: 1.0) == 0.0
    assert intra_list_diversity([], lambda a, b: 1.0) == 0.0


def test_intra_list_diversity_accepts_a_matrix_lookup() -> None:
    # A nested-mapping "matrix" indexed by item id: ids 0,1,2 with sims s[0][1]=0.0, s[0][2]=1.0.
    matrix = {0: {1: 0.0, 2: 1.0}, 1: {0: 0.0, 2: 0.5}, 2: {0: 1.0, 1: 0.5}}
    # pairs (0,1)=0.0, (0,2)=1.0, (1,2)=0.5 -> mean 0.5 -> diversity 0.5.
    assert intra_list_diversity([0, 1, 2], matrix) == pytest.approx(0.5)


def test_novelty_is_monotonic_in_rarity() -> None:
    # Train counts: item 1 seen 2x, item 2 seen 8x (total 10). Self-information -log2 p:
    #   item 1: -log2(0.2) = 2.3219...   item 2: -log2(0.8) = 0.3219...
    popularity = {1: 2, 2: 8}
    rare = novelty([1], popularity)
    common = novelty([2], popularity)
    assert rare == pytest.approx(-math.log2(0.2))
    assert common == pytest.approx(-math.log2(0.8))
    assert rare > common  # the rarer item is more novel
    # A list's novelty is the mean of its items' self-information.
    assert novelty([1, 2], popularity) == pytest.approx((rare + common) / 2.0)


def test_novelty_is_zero_safe() -> None:
    assert novelty([], {1: 5}) == 0.0  # nothing recommended
    assert novelty([1], {}) == 0.0  # no train signal at all
    # An item unseen in train (count 0) is skipped rather than returning infinite novelty.
    assert novelty([99], {1: 5}) == 0.0
    assert novelty([1, 99], {1: 5, 2: 5}) == pytest.approx(-math.log2(0.5))


def test_blend_is_deterministic() -> None:
    # The blend pipeline (calibrate -> weighted union -> rank) is order-stable run to run.
    per_path = {
        "a": [Candidate(1, 3.0, "a"), Candidate(2, 1.0, "a"), Candidate(3, 2.0, "a")],
        "b": [Candidate(2, 5.0, "b"), Candidate(4, 1.0, "b")],
    }
    weights = {"a": 1.0, "b": 0.5}
    first = rank(blend(per_path, weights=weights), n=3, exclude={3})
    second = rank(blend(per_path, weights=weights), n=3, exclude={3})
    assert [(c.item_id, c.score) for c in first] == [(c.item_id, c.score) for c in second]
    assert all(c.item_id != 3 for c in first)  # excluded id never appears


# ======================================================================================
# The pinned-config blend on the shipped data (bound to measured numbers)
# ======================================================================================


def _read_rows(path: Path) -> list[dict[str, object]]:
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        return [
            {
                "reader_id": int(row["reader_id"]),
                "item_id": int(row["item_id"]),
                "split": row["split"],
                "label": int(row["label"]),
            }
            for row in csv.DictReader(handle)
        ]


@pytest.fixture(scope="module")
def generated() -> dict[str, object]:
    gen = generated_dir()
    catalog_ids = sorted(load_catalog(gen / "catalog.csv.gz"))
    cold = json.loads((gen / "cold_partitions.json").read_text())
    return {
        "interactions_path": gen / "interactions.csv.gz",
        "catalog_ids": catalog_ids,
        "cold_readers": cold["cold_readers"],
        "keywords": load_keywords(gen / "keywords.csv.gz"),
        "rows": _read_rows(gen / "interactions.csv.gz"),
    }


@pytest.fixture(scope="module")
def paths(generated: dict[str, object]) -> dict[str, object]:
    # Fit the four Part-1 paths ONCE at their pinned configs and share across the blend tests
    # (one ~15 s MF fit, not one per test).
    rows = generated["rows"]
    catalog_ids = generated["catalog_ids"]
    return {
        "popularity": PopularityRetrievalPath().fit(rows, catalog=catalog_ids),
        "lexical": LexicalRetrievalPath(generated["keywords"]).fit(rows, catalog=catalog_ids),
        "item-item": ItemItemRetrievalPath().fit(rows, catalog=catalog_ids),
        "mf": MatrixFactorizationPath(seed=SEED).fit(rows, catalog=catalog_ids),
    }


def _blended(paths: dict[str, object], weights: dict[str, float], generated: dict[str, object]):
    return run_blended_scoreboard(
        paths,
        generated["interactions_path"],
        catalog_ids=generated["catalog_ids"],
        k=K,
        pool=POOL,
        weights=weights,
        cold_readers=generated["cold_readers"],
    )


@pytest.fixture(scope="module")
def measured(paths: dict[str, object], generated: dict[str, object]) -> dict[str, float]:
    # Three scoreboard passes shared by every binding assertion: the full blend, the
    # leave-popularity-out ablation, and the MF single path (hit + coverage in one blended pass).
    full = _blended(paths, WEIGHTS, generated)
    drop_pop_paths = {n: p for n, p in paths.items() if n != "popularity"}
    drop_pop_weights = {n: WEIGHTS[n] for n in drop_pop_paths}
    drop_pop = _blended(drop_pop_paths, drop_pop_weights, generated)
    mf = _blended({"mf": paths["mf"]}, {"mf": 1.0}, generated)
    return {
        "blend_hit": full.hit_rate_at_k,
        "blend_cov": full.catalog_coverage,
        "blend_readers": full.readers,
        "drop_pop_hit": drop_pop.hit_rate_at_k,
        "mf_hit": mf.hit_rate_at_k,
        "mf_cov": mf.catalog_coverage,
    }


def test_blend_beats_the_best_single_path_on_hit_rate(measured: dict[str, float]) -> None:
    # The headline accuracy claim, bound to the pinned config: the blend is at least on par with
    # the best single path (MF). Measured: blend 0.306 >= MF 0.276, a +0.03 margin; the -0.01
    # tolerance guards the seeded MF negative-sampling draw.
    assert measured["blend_readers"] == 500
    assert measured["blend_hit"] >= measured["mf_hit"] - 0.01
    assert measured["blend_hit"] == pytest.approx(0.306, abs=1e-3)
    assert measured["mf_hit"] == pytest.approx(0.276, abs=1e-3)


def test_blend_covers_far_more_catalog_than_the_best_single_path(measured: dict[str, float]) -> None:
    # The beyond-accuracy payoff: the blend reaches >= 3x MF's catalog coverage. Measured:
    # blend 0.333 vs MF 0.0745 (~4.5x).
    assert measured["blend_cov"] >= 3 * measured["mf_cov"]
    assert measured["blend_cov"] == pytest.approx(0.333, abs=1e-3)
    assert measured["mf_cov"] == pytest.approx(0.0745, abs=1e-3)


def test_dropping_popularity_raises_hit_rate(measured: dict[str, float]) -> None:
    # The taught headline of the leave-one-path-out ablation: removing the reader-INDEPENDENT
    # popularity path RAISES hit@10 (0.308 > 0.306). Min-max calibration maps every path's top
    # candidate to 1.0, so a flat popularity path ties its head books with every reader's true top
    # pick -- "every path contributes" is false; a path earns its place by reader-dependence.
    assert measured["drop_pop_hit"] > measured["blend_hit"]
    assert measured["drop_pop_hit"] == pytest.approx(0.308, abs=1e-3)


def test_single_path_scoreboard_reports_ranking_metrics(
    paths: dict[str, object], generated: dict[str, object]
) -> None:
    # The additive scoreboard extension: precision@k and NDCG@k ride alongside hit/recall, and the
    # default split stays "val" so every existing caller is unaffected.
    result = run_validation_scoreboard(
        paths["mf"],
        generated["interactions_path"],
        catalog_ids=generated["catalog_ids"],
        k=K,
        cold_readers=generated["cold_readers"],
    )
    assert result.readers == 500
    assert result.hit_rate_at_k == pytest.approx(0.276, abs=1e-3)
    assert 0.0 < result.precision_at_k < result.hit_rate_at_k  # per-slot precision < per-list hit
    assert 0.0 < result.ndcg_at_k < 1.0


def test_test_split_is_scorable_once_for_the_checkpoint(
    paths: dict[str, object], generated: dict[str, object]
) -> None:
    # Checkpoint A unseals the sealed `test` holdout for ONE honest final score: the split= param
    # accepts "test" with the SAME cold-reader exclusion. 593 readers hold a test positive (2339
    # positive rows); after cold exclusion and dropping re-reads, 500 are scored -- the same count
    # as val, so the checkpoint can compare the two on equal footing.
    result = run_validation_scoreboard(
        paths["popularity"],
        generated["interactions_path"],
        catalog_ids=generated["catalog_ids"],
        k=K,
        cold_readers=generated["cold_readers"],
        split="test",
    )
    assert result.readers == 500
    assert result.hit_rate_at_k > 0.0


def test_run_validation_scoreboard_rejects_an_unknown_split(
    paths: dict[str, object], generated: dict[str, object]
) -> None:
    with pytest.raises(ValueError, match="split"):
        run_validation_scoreboard(
            paths["popularity"],
            generated["interactions_path"],
            catalog_ids=generated["catalog_ids"],
            k=K,
            split="train",
        )


# ======================================================================================
# Test-holdout hygiene guard (also enforced in Phase H): only the checkpoint solution may
# reference the sealed `test` split anywhere in Unit-6 / Checkpoint-A notebook source.
# ======================================================================================


_TEST_SPLIT = re.compile(r"""split\s*={1,2}\s*['"]test['"]""")


def test_only_the_checkpoint_solution_touches_the_test_split() -> None:
    repo = Path(__file__).resolve().parents[4]
    roots = [
        repo / "recsys" / "units" / "unit-06-evaluation-and-blending",
        repo / "recsys" / "checkpoints" / "checkpoint-01-part-1",
        repo / "recsys" / "projects" / "bookrec" / "milestones",
    ]
    # Only Checkpoint A (the authorized Part-1 unseal) may touch the sealed test split — BOTH its
    # statement (which instructs the one-shot test evaluation) and its solution.
    allowed = {
        "checkpoint-01-part-1/checkpoint.ipynb",
        "checkpoint-01-part-1/solutions.ipynb",
    }
    offenders: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        for notebook in sorted(root.rglob("*.ipynb")):
            # Only the Unit-6 milestone, not every project milestone, is in scope.
            if root.name == "milestones" and "unit-06" not in notebook.name:
                continue
            payload = json.loads(notebook.read_text(encoding="utf-8"))
            code = "\n".join(
                "".join(cell.get("source", []))
                for cell in payload.get("cells", [])
                if cell.get("cell_type") == "code"
            )
            if not _TEST_SPLIT.search(code):
                continue
            rel = notebook.relative_to(repo).as_posix()
            tail = "/".join(rel.split("/")[-2:])
            if tail not in allowed:
                offenders.append(rel)
    assert not offenders, f"these Unit-6 notebooks must not filter the sealed test split: {offenders}"

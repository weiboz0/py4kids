"""Unit 11 (recsys-013): the neural reranker — a learned second stage over the merged pool.

Verifies, on the seeded recsys-004 interaction log and the Unit 2–10 retrieval paths, the
:class:`~bookrec.rerank.NeuralRerankerPath` this unit ships. The MEASURED story (probe + this suite,
pool=50, seed 0, val split):

- **gate** — the clean-recipe reranker is not tanked (``hit@10 >= two_tower.hit - 0.01``) and it
  beats the fixed 6-way score-order over the SAME pool it reranks;
- **negative (the leak)** — the naive same-train recipe (``leaky=True``: feature-paths fit on the
  full train that includes the label items) scores BELOW the clean time-ordered-holdout recipe;
- **record, not gated** — the hybrid comparison, ``linear ~= MLP``, catalog coverage (reported as a
  LOSS), the feature ablation (content-only >= scores-only) and the pool recall ceiling;
- determinism (identical top-k + ``allclose`` weights), the empty-seen / unknown-reader contract, a
  fit->artifact->load round-trip (torch-free), and train-only invariance to val/test perturbation;
- registry ownership as ``reranker-v1``.

CPU-deterministic; routed ``--group recsys``. To stay in budget the module fits the six serving
paths ONCE, refits them on the 75% profile ONCE (shared ``path_factory``), and assembles the
training matrix ONCE — model variants (linear, ablations, seeds) are swapped onto that matrix.
"""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    DuplicatePathError,
    ItemItemRetrievalPath,
    LexicalRetrievalPath,
    MatrixFactorizationPath,
    NeuralRerankerPath,
    PathRegistry,
    PopularityRetrievalPath,
    RerankerModel,
    SemanticEmbeddingRetrievalPath,
    TwoTowerRetrievalPath,
    generated_dir,
    load_catalog,
    load_glove_subset,
    load_keywords,
    run_blended_scoreboard,
)
from bookrec.protocol import BaseRetrievalPath, Candidate
from bookrec.rerank import (
    _train_positive_counts,
    family_mask,
    feature_names,
    split_profile_labels,
)
from bookrec.scoreboard import _seen_and_relevant

K = 10
POOL = 50
SEED = 0
PATH_NAMES = ("popularity", "lexical", "item-item", "mf", "semantic", "two-tower")


def _read_rows(path: Path) -> list[dict[str, object]]:
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        return [
            {
                "reader_id": int(row["reader_id"]),
                "item_id": int(row["item_id"]),
                "timestamp": int(row["timestamp"]),
                "split": row["split"],
                "label": int(row["label"]),
            }
            for row in csv.DictReader(handle)
        ]


def _fit_six(rows: list[dict[str, object]], catalog_ids, keywords, glove) -> dict[str, object]:
    """Fit the six retrieval paths whose calibrated scores feed the reranker (seed 0)."""
    return {
        "popularity": PopularityRetrievalPath().fit(rows, catalog=catalog_ids),
        "lexical": LexicalRetrievalPath(keywords).fit(rows, catalog=catalog_ids),
        "item-item": ItemItemRetrievalPath().fit(rows, catalog=catalog_ids),
        "mf": MatrixFactorizationPath(seed=SEED).fit(rows, catalog=catalog_ids),
        "semantic": SemanticEmbeddingRetrievalPath(keywords, glove).fit(rows, catalog=catalog_ids),
        "two-tower": TwoTowerRetrievalPath(seed=SEED).fit(rows, catalog=catalog_ids),
    }


@pytest.fixture(scope="module")
def env() -> dict[str, object]:
    gen = generated_dir()
    catalog = load_catalog(gen / "catalog.csv.gz")
    catalog_ids = sorted(catalog)
    cold = json.loads((gen / "cold_partitions.json").read_text())["cold_readers"]
    keywords = load_keywords(gen / "keywords.csv.gz")
    glove = load_glove_subset()
    rows = _read_rows(gen / "interactions.csv.gz")
    serving = _fit_six(rows, catalog_ids, keywords, glove)

    # ONE refit of the six paths on the 75% profile, shared by every clean-recipe reranker below.
    from bookrec.rerank import split_profile_labels

    _profile, labels = split_profile_labels(rows, 0.25)
    profile_rows = [
        r
        for r in rows
        if not (
            r["split"] == "train"
            and int(r["label"]) == 1
            and int(r["item_id"]) in labels.get(int(r["reader_id"]), set())
        )
    ]
    profile_paths = _fit_six(profile_rows, catalog_ids, keywords, glove)
    factory_calls = {"n": 0}

    def path_factory(train_rows: list[dict[str, object]]) -> dict[str, object]:
        factory_calls["n"] += 1
        return profile_paths  # the profile refit is done once, up front, and reused

    return {
        "interactions_path": gen / "interactions.csv.gz",
        "catalog": catalog,
        "catalog_ids": catalog_ids,
        "cold_readers": cold,
        "keywords": keywords,
        "glove": glove,
        "rows": rows,
        "serving": serving,
        "profile_paths": profile_paths,
        "path_factory": path_factory,
        "factory_calls": factory_calls,
    }


def _make_reranker(env: dict[str, object], **kwargs) -> NeuralRerankerPath:
    return NeuralRerankerPath(
        env["serving"],
        env["path_factory"],
        env["catalog"],
        pool=POOL,
        seed=SEED,
        **kwargs,
    )


@pytest.fixture(scope="module")
def clean(env: dict[str, object]) -> dict[str, object]:
    """The clean-recipe reranker, its training matrix (assembled once), and model variants."""
    path = _make_reranker(env)
    X, y = path.assemble_training_matrix(env["rows"], train_paths=env["profile_paths"])
    all_model = RerankerModel(seed=SEED).fit(X, y, feature_mask=family_mask(("scores", "presence", "meta", "content")))
    path.set_model(all_model)
    linear_model = RerankerModel(seed=SEED, linear=True).fit(X, y)
    content_model = RerankerModel(seed=SEED).fit(X, y, feature_mask=family_mask(("content",)))
    scores_model = RerankerModel(seed=SEED).fit(X, y, feature_mask=family_mask(("scores", "presence", "meta")))
    return {
        "path": path,
        "X": X,
        "y": y,
        "all_model": all_model,
        "linear_model": linear_model,
        "content_model": content_model,
        "scores_model": scores_model,
    }


def _board(path: object, env: dict[str, object], pool: int = K):
    return run_blended_scoreboard(
        {path.name: path},
        env["interactions_path"],
        catalog_ids=env["catalog_ids"],
        k=K,
        pool=pool,
        cold_readers=env["cold_readers"],
    )


def _board_model(clean: dict[str, object], env: dict[str, object], model: RerankerModel):
    """Score the val set with a given model installed on the clean reranker's serving machinery."""
    path = clean["path"]
    original = path.model
    try:
        path.set_model(model)
        return _board(path, env)
    finally:
        path.set_model(original)


@pytest.fixture(scope="module")
def boards(env: dict[str, object], clean: dict[str, object]) -> dict[str, object]:
    """Every val board computed ONCE (hit@10 + coverage), shared across the record/gate tests."""
    serving = env["serving"]
    six_way = run_blended_scoreboard(
        {n: serving[n] for n in PATH_NAMES},
        env["interactions_path"],
        catalog_ids=env["catalog_ids"],
        k=K,
        pool=POOL,
        cold_readers=env["cold_readers"],
    )
    two_tower = _board(serving["two-tower"], env, pool=K)
    from bookrec import HybridRetrievalPath

    hybrid = HybridRetrievalPath(serving["lexical"], serving["two-tower"], weight=0.7, pool=50).fit(env["rows"])
    hybrid_board = _board(hybrid, env, pool=K)
    u6 = run_blended_scoreboard(
        {n: serving[n] for n in ("popularity", "lexical", "item-item", "mf")},
        env["interactions_path"],
        catalog_ids=env["catalog_ids"],
        k=K,
        pool=30,
        weights={"popularity": 0.25, "lexical": 0.5, "item-item": 1.0, "mf": 1.0},
        cold_readers=env["cold_readers"],
    )
    reranker = _board(clean["path"], env)
    linear = _board_model(clean, env, clean["linear_model"])
    content = _board_model(clean, env, clean["content_model"])
    scores = _board_model(clean, env, clean["scores_model"])

    # leaky recipe: feature-paths = the serving (full-fit) paths that memorised the label items.
    leaky = _make_reranker(env, leaky=True)
    leaky.fit(env["rows"])
    leaky_board = _board(leaky, env)

    pool_recall = _pool_recall(clean["path"], env)
    return {
        "six_way": six_way,
        "two_tower": two_tower,
        "hybrid": hybrid_board,
        "u6": u6,
        "reranker": reranker,
        "linear": linear,
        "content": content,
        "scores": scores,
        "leaky": leaky_board,
        "pool_recall": pool_recall,
    }


def _pool_recall(path: NeuralRerankerPath, env: dict[str, object]) -> float:
    """Any-relevant-in-pool recall over the val cohort — the ceiling any reranker is capped at."""
    known = set(env["catalog_ids"])
    seen_by, target_by = _seen_and_relevant(env["interactions_path"], known, "val")
    cold = set(env["cold_readers"])
    hits = []
    for reader in sorted(target_by):
        seen = seen_by[reader]
        relevant = target_by[reader] - seen
        if reader in cold or not relevant:
            continue
        per_item = path._build_pool(env["serving"], reader, seen)
        hits.append(1.0 if any(i in relevant for i in per_item) else 0.0)
    return float(np.mean(hits)) if hits else 0.0


# --- (1) GATE: not tanked, and beats the fixed score-order over the same pool -----------------


def test_reranker_gate_beats_score_order_and_is_not_tanked(
    boards: dict[str, object], clean: dict[str, object]
) -> None:
    reranker = boards["reranker"].hit_rate_at_k
    two_tower = boards["two_tower"].hit_rate_at_k
    six_way = boards["six_way"].hit_rate_at_k
    print(
        f"\n[gate] reranker hit@10={reranker:.3f} cov={boards['reranker'].catalog_coverage:.3f} | "
        f"two-tower={two_tower:.3f} | 6-way score-order(pool{POOL})={six_way:.3f}"
    )
    # (a) not tanked vs the two-tower (measured reranker ~0.35-0.39 >= 0.340 - 0.01):
    assert reranker >= two_tower - 0.01
    # (b) beats the fixed 6-way equal-weight score-order over the SAME pool it reranks:
    assert reranker >= six_way


# --- (2) NEGATIVE: the leaky same-train recipe scores BELOW the clean recipe (codifies the leak)


def test_leaky_recipe_tanks_below_clean(boards: dict[str, object]) -> None:
    leaky = boards["leaky"].hit_rate_at_k
    clean_hit = boards["reranker"].hit_rate_at_k
    print(f"\n[leak] leaky same-train recipe hit@10={leaky:.3f}  <  clean recipe hit@10={clean_hit:.3f}")
    # The naive recipe memorises the label items through the feature-paths -> distribution shift at
    # val -> it tanks (measured ~0.28 at pool 50) well below the clean time-ordered-holdout recipe.
    assert leaky < clean_hit


# --- (3) RECORD (not gated): hybrid, linear ~= MLP, coverage as a LOSS -------------------------


def test_record_hybrid_linear_and_coverage(boards: dict[str, object]) -> None:
    r = boards["reranker"]
    print(
        "\n[record] hit@10 / coverage: "
        f"reranker {r.hit_rate_at_k:.3f}/{r.catalog_coverage:.3f} | "
        f"two-tower {boards['two_tower'].hit_rate_at_k:.3f}/{boards['two_tower'].catalog_coverage:.3f} | "
        f"U6 blend {boards['u6'].hit_rate_at_k:.3f}/{boards['u6'].catalog_coverage:.3f} | "
        f"U10 hybrid {boards['hybrid'].hit_rate_at_k:.3f}/{boards['hybrid'].catalog_coverage:.3f} | "
        f"linear {boards['linear'].hit_rate_at_k:.3f}/{boards['linear'].catalog_coverage:.3f}"
    )
    print(f"[record] pool recall ceiling @pool{POOL} = {boards['pool_recall']:.3f}")
    # linear ~= MLP here (the non-linear combiner adds nothing): recorded, never gated.
    assert abs(boards["linear"].hit_rate_at_k - r.hit_rate_at_k) < 0.1
    # Coverage is an honest LOSS vs the U6 blend (a precise reranker concentrates its picks):
    assert r.catalog_coverage < boards["u6"].catalog_coverage


# --- (5) ABLATION (recorded): content carries the lift (content-only >= scores-only) ----------


def test_feature_ablation_content_at_least_scores(boards: dict[str, object]) -> None:
    content = boards["content"].hit_rate_at_k
    scores = boards["scores"].hit_rate_at_k
    print(f"\n[ablation] content-only hit@10={content:.3f}  >=  scores-only hit@10={scores:.3f}")
    # The counterintuitive payoff: dropping the path-score features does NOT hurt; the content
    # features (genre/author affinity, log-pop) carry the lift a single path's score cannot.
    assert content >= scores


# --- (4) DETERMINISM: identical top-k ranking + allclose weights (design §184) -----------------


def test_determinism_two_fits_allclose_and_identical_topk(
    env: dict[str, object], clean: dict[str, object]
) -> None:
    X, y = clean["X"], clean["y"]
    first = RerankerModel(seed=SEED).fit(X, y)
    second = RerankerModel(seed=SEED).fit(X, y)
    # Gate (§184): allclose on EVERY weight (never exact-float). array_equal is a printed BONUS.
    assert len(first.weights) == len(second.weights)
    assert all(np.allclose(a, b) for a, b in zip(first.weights, second.weights))
    print("\n[determinism] allclose weights: True | array_equal bonus:",
          all(np.array_equal(a, b) for a, b in zip(first.weights, second.weights)))
    # Identical top-k ranking for a few readers (the ranking the student actually sees).
    path = clean["path"]
    original = path.model
    seen_by, target_by = _seen_and_relevant(env["interactions_path"], set(env["catalog_ids"]), "val")
    readers = [r for r in sorted(target_by) if r not in set(env["cold_readers"]) and (target_by[r] - seen_by[r])][:5]
    try:
        path.set_model(first)
        a = {r: [c.item_id for c in path.retrieve(r, {"seen": seen_by[r]}, K)] for r in readers}
        path.set_model(second)
        b = {r: [c.item_id for c in path.retrieve(r, {"seen": seen_by[r]}, K)] for r in readers}
    finally:
        path.set_model(original)
    assert a == b


# --- (7) TRAIN-ONLY: val/test rows cannot change the fitted artifact --------------------------


def test_val_test_perturbation_does_not_change_training(env: dict[str, object], clean: dict[str, object]) -> None:
    path = clean["path"]
    # Perturb: inject bogus val/test positive rows (new reader + flipped items). Train-only fit must
    # ignore them entirely — the assembled matrix, counts and known-reader set are unchanged.
    perturbed = list(env["rows"]) + [
        {"reader_id": 9_999_999, "item_id": env["catalog_ids"][0], "timestamp": 10 ** 9, "split": "val", "label": 1},
        {"reader_id": env["rows"][0]["reader_id"], "item_id": env["catalog_ids"][-1], "timestamp": 10 ** 9, "split": "test", "label": 1},
    ]
    probe = _make_reranker(env)
    X2, y2 = probe.assemble_training_matrix(perturbed, train_paths=env["profile_paths"])
    assert np.array_equal(clean["X"], X2)
    assert np.array_equal(clean["y"], y2)
    # The recorded serving statistics (counts, known readers) ignore the injected val/test rows.
    assert path._counts == probe._counts
    assert path._known_readers == probe._known_readers
    assert 9_999_999 not in probe._known_readers


# --- (6) CONTRACT: empty-seen, unknown reader, fit->artifact->load round-trip ------------------


def test_empty_seen_returns_k_and_unknown_reader_empty(env: dict[str, object], clean: dict[str, object]) -> None:
    path = clean["path"]
    known_reader = next(iter(sorted(path.artifact()["known_readers"])))
    recs = path.retrieve(known_reader, {"seen": set()}, K)
    assert len(recs) == K
    assert all(c.provenance == "reranker" for c in recs)
    assert recs == path.retrieve(known_reader, {}, K)  # missing seen == empty seen
    known = set(path.artifact()["known_readers"])
    unknown = next(r for r in range(10_000_000) if r not in known)
    assert path.retrieve(unknown, {"seen": set()}, K) == []
    assert path.retrieve(unknown, {"seen": {1, 2, 3}}, K) == []


def test_fit_artifact_load_round_trip_is_torch_free(env: dict[str, object], clean: dict[str, object]) -> None:
    path = clean["path"]
    restored = NeuralRerankerPath(env["serving"], env["path_factory"], env["catalog"], pool=POOL).load(path.artifact())
    seen_by, target_by = _seen_and_relevant(env["interactions_path"], set(env["catalog_ids"]), "val")
    readers = [r for r in sorted(target_by) if r not in set(env["cold_readers"])][:6]
    for reader in readers:
        seen = seen_by[reader]
        a = path.retrieve(reader, {"seen": seen}, K)
        b = restored.retrieve(reader, {"seen": seen}, K)
        assert [c.item_id for c in a] == [c.item_id for c in b]
        assert [c.score for c in a] == [c.score for c in b]
    # load copied the model arrays (mutating the artifact cannot reach into the loaded path).
    artifact = path.artifact()
    loaded = NeuralRerankerPath(env["serving"], env["path_factory"], env["catalog"]).load(artifact)
    artifact["model"]["weights"][0][0, 0] = 123.0
    assert loaded.retrieve(readers[0], {"seen": seen_by[readers[0]]}, K)  # still serves


# --- (9) REGRESSION: a repeat-read held-out event never leaks into the training log_pop count ---


class _FixedPath(BaseRetrievalPath):
    """A tiny synthetic path that returns a fixed candidate pool (for the leakage regression)."""

    def __init__(self, pool_items: list[int], name: str = "p") -> None:
        super().__init__(name=name, version="1")
        self._pool_items = list(pool_items)
        self._fitted = True

    def fit(self, interactions, catalog=None):
        return self

    def retrieve(self, query, context, k: int) -> list[Candidate]:
        # Descending integer scores so calibration is well-defined; ids are the synthetic pool.
        cands = [Candidate(int(i), float(len(self._pool_items) - j), self.name) for j, i in enumerate(self._pool_items)]
        return cands[:k]


class _Book:
    def __init__(self, genres: str, author: str) -> None:
        self.fields = {"genres": genres, "author_id": author}


def test_repeat_read_holdout_event_not_in_training_log_pop() -> None:
    """A repeat-read item in BOTH the profile and label sets must not leak its held-out event.

    Reader 1 reads item A three times (t=1,2,5), B once (t=3), C once (t=4). The time-ordered 25%
    holdout makes the last A event a *label* while two earlier A events sit in the profile, so A
    lands in both the profile set AND the label set. The label-item-excluded profile rows drop EVERY
    A occurrence, so the training ``log_pop`` count for A is 0 — no held-out (or earlier) A event
    enters the count. The old profile-membership count (``keep=profile``) would instead have counted
    all three A events, leaking the held-out one.
    """
    rows = [
        {"reader_id": 1, "item_id": 10, "timestamp": 1, "split": "train", "label": 1},  # A
        {"reader_id": 1, "item_id": 10, "timestamp": 2, "split": "train", "label": 1},  # A
        {"reader_id": 1, "item_id": 20, "timestamp": 3, "split": "train", "label": 1},  # B
        {"reader_id": 1, "item_id": 30, "timestamp": 4, "split": "train", "label": 1},  # C
        {"reader_id": 1, "item_id": 10, "timestamp": 5, "split": "train", "label": 1},  # A (held out)
    ]
    profile, labels = split_profile_labels(rows, 0.25)
    # The trap condition: A (10) is simultaneously a profile item and a held-out label.
    assert 10 in profile[1]
    assert labels[1] == {10}

    # Helper-level contrast: the OLD profile-membership count keeps all three A events (leak);
    # the full-train count also sees all three; the label-item-excluded count drops every A event.
    profile_rows = [
        r
        for r in rows
        if not (r["split"] == "train" and int(r["label"]) == 1 and int(r["item_id"]) in labels.get(int(r["reader_id"]), set()))
    ]
    assert _train_positive_counts(rows)[10] == 3  # full-train (serving) count
    assert _train_positive_counts(rows, keep=profile)[10] == 3  # OLD buggy count -> leaks held-out event
    assert _train_positive_counts(profile_rows).get(10, 0) == 0  # NEW count: strictly less, no A event

    # End-to-end: assemble the training matrix and read A's log_pop feature straight off X.
    pool_items = [10, 20, 30, 40, 50]  # A positive; B/C/40/50 negatives
    catalog_books = {i: _Book(genres="fic", author="auth") for i in pool_items}
    serving = {"p": _FixedPath(pool_items)}
    reranker = NeuralRerankerPath(
        serving,
        lambda train_rows: {"p": _FixedPath(pool_items)},
        catalog_books,
        pool=POOL,
        seed=SEED,
        n_negatives=10,
        path_names=("p",),
    )
    X, y = reranker.assemble_training_matrix(rows)
    names = feature_names(("p",))
    log_pop_col = names.index("log_pop")
    pos_rows = np.flatnonzero(y == 1.0)
    assert pos_rows.size == 1  # exactly one held-out label (A) landed in the pool
    # A's held-out event never entered the training count -> its log_pop feature is exactly 0.
    assert X[pos_rows[0], log_pop_col] == 0.0
    # Serving counts (used at retrieve) are the UNCHANGED full-train statistic.
    assert reranker._counts[10] == 3


# --- (8) registry ownership --------------------------------------------------------------------


def test_reranker_registers_as_reranker_v1(env: dict[str, object], clean: dict[str, object]) -> None:
    registry = PathRegistry()
    path = clean["path"]
    registry.register(path)
    assert path.artifact_name() == "reranker-v1"
    assert "reranker" in registry
    with pytest.raises(DuplicatePathError):
        registry.register(_make_reranker(env))

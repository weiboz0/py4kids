"""Unit 12 (recsys-015): sequence-aware retrieval on the session log.

Verifies the three :mod:`bookrec.sequence` paths this unit ships, the ordered-history contract and
the evaluation helpers:

- **gates (a)/(b)** on the CI-generated ``sessions.csv.gz`` (committed seed, val, k = 10, the
  unchanged ``run_validation_scoreboard`` cohort). Measured on the shipped code: item-item 0.4799,
  distinct last-3 CF 0.5511 (+0.071, paired SE 0.014), last-5 transition 0.5159 vs its
  order-shuffled control 0.3326 (1.55x, +0.183). Pinned with headroom: (a) last-3 >= item-item +
  0.03; (b) transition >= 1.3x shuffled AND >= +0.10. Gate (c) — SASRec ordered beats its shuffled
  copy by >= 0.02 and >= 2 paired SE at the frozen recipe D — needs two ~45 s fits, so it is
  asserted in the CI-executed Unit-12 milestone notebook, not here;
- the **shuffle and leakage mutants**: four small subclassed mutants on an order-decisive hand-made
  fixture (learning-only shuffle, query-only shuffle, a query built from the unordered
  ``context["seen"]``, a fit that reads val/test rows) — each must be DETECTED by the contract
  checks the shipped paths pass;
- SASRec contracts on a reduced config: numpy-forward vs torch-forward fidelity, determinism
  (identical top-k + ``allclose`` weights), a torch-free ``fit -> artifact -> load`` round-trip, and
  the save/restore of torch's process-global determinism knobs;
- ``fit(rows)`` histories == ``load_train_sequences``; ``reader_hits`` mean == scoreboard hit;
  ``LastKItemItemPath(k_last=None)`` == ``ItemItemRetrievalPath``; empty/unknown-reader contracts;
  train-only invariance; registration names.

CPU-deterministic; routed ``--group recsys`` (torch is only needed by the SASRec fits).
"""

from __future__ import annotations

import csv
import gzip
from pathlib import Path

import numpy as np
import pytest
from bookrec import (
    ItemItemRetrievalPath,
    LastKItemItemPath,
    PathRegistry,
    SasrecRetrievalPath,
    TransitionRetrievalPath,
    first_unseen_val,
    generated_dir,
    load_catalog,
    load_train_sequences,
    ordered_train_histories,
    reader_hits,
    run_validation_scoreboard,
)
from bookrec.sequence import build_sasrec_module, shuffle_histories

K = 10
SHUFFLE_SEED = 20260930 + 1000  # the recsys-014 control seed (committed seed + 1000)
SESSIONS = generated_dir() / "sessions.csv.gz"
TINY_SASREC = {"dim": 8, "max_len": 12, "n_epochs": 3, "batch_size": 16, "learning_rate": 1e-2}

needs_sessions = pytest.mark.skipif(
    not SESSIONS.is_file(), reason="sessions.csv.gz not generated (CI regenerates it)"
)


# --------------------------------------------------------------------------------- fixtures
def _rows_from_histories(
    histories: dict[int, list[int]], *, rng_seed: int = 0, scramble: bool = True
) -> list[dict[str, object]]:
    """Train-positive rows whose (timestamp, row order) reproduces ``histories``.

    Rows are written in a scrambled file order (so ordering must come from the timestamps), and a
    few train negatives are mixed in (they must never enter a history).
    """
    rows: list[dict[str, object]] = []
    for reader, items in histories.items():
        for position, item in enumerate(items):
            rows.append(
                {
                    "reader_id": reader,
                    "item_id": item,
                    "timestamp": 100 * position,
                    "split": "train",
                    "label": 1,
                }
            )
        rows.append(
            {"reader_id": reader, "item_id": 99, "timestamp": 5, "split": "train", "label": 0}
        )
    if scramble:
        order = np.random.default_rng(rng_seed).permutation(len(rows))
        rows = [rows[i] for i in order]
    return rows


def _order_fixture() -> dict[int, list[int]]:
    """An order-decisive fixture: readers walk short "series" chains, interleaved with noise.

    Chains 0->1->2->3->4, 10->11->...->14, 20->...->24; each reader reads several chain segments in
    order with random distractors between, so the LAST reads predict the next volume while the
    bag of reads does not.
    """
    rng = np.random.default_rng(7)
    chains = [list(range(5)), list(range(10, 15)), list(range(20, 25))]
    histories: dict[int, list[int]] = {}
    for reader in range(40):
        seq: list[int] = []
        for _ in range(3):
            chain = chains[int(rng.integers(0, 3))]
            start = int(rng.integers(0, 3))
            seq.extend(chain[start : start + int(rng.integers(2, 4))])
            seq.extend(int(x) for x in rng.choice(np.arange(30, 45), size=2, replace=False))
        histories[reader] = seq
    return histories


@pytest.fixture(scope="module")
def order_rows() -> list[dict[str, object]]:
    return _rows_from_histories(_order_fixture())


def _make(cls, **kwargs):
    if cls is LastKItemItemPath:
        return LastKItemItemPath(3, **kwargs)
    if cls is TransitionRetrievalPath:
        return TransitionRetrievalPath(5, **kwargs)
    return SasrecRetrievalPath(**TINY_SASREC, **kwargs)


# ------------------------------------------------------------------- contract checks (+ mutants)
def _learned(path) -> np.ndarray:
    if isinstance(path, LastKItemItemPath):
        return path.similarity
    if isinstance(path, TransitionRetrievalPath):
        return path.transitions
    return path.artifact()["weights"]["item.weight"]


def _top(path, reader: int, seen: set[int], k: int = K) -> list[int]:
    return [c.item_id for c in path.retrieve(reader, {"seen": seen}, k)]


def check_shuffle_semantics(cls, rows, seed: int = SHUFFLE_SEED) -> None:
    """The shuffled control == the ordered path fitted on rows re-timed into the shuffled order.

    It must permute BOTH the learning sequences (same learned statistics) AND the stored query
    histories (same retrieval).
    """
    shuffled = cls(shuffle_seed=seed).fit(rows)
    expected = shuffle_histories(ordered_train_histories(rows), seed)
    assert shuffled.histories == expected, "query histories are not the shuffled control"
    reference = cls(shuffle_seed=None).fit(_rows_from_histories(expected, scramble=False))
    np.testing.assert_array_equal(_learned(shuffled), _learned(reference))
    for reader, items in expected.items():
        assert _top(shuffled, reader, set(items)) == _top(reference, reader, set(items)), reader


def _reference_scores(path, history: list[int]) -> np.ndarray:
    """An independent from-scratch score of a stored ordered history (the hand computation)."""
    ids = path.artifact()["item_ids"]
    col = {item: i for i, item in enumerate(ids)}
    if isinstance(path, LastKItemItemPath):
        recent: list[int] = []
        for item in reversed(history):
            if item not in recent:
                recent.append(item)
        recent = recent[: path.k_last]
        return path.similarity[:, [col[i] for i in recent]].sum(axis=1)
    return path.transitions[[col[i] for i in history[-path.k_last :]]].sum(axis=0)


def check_query_uses_stored_history(path, rows) -> None:
    """``retrieve`` scores the STORED ordered history; ``context["seen"]`` only excludes."""
    ordered = ordered_train_histories(rows)
    ids = path.artifact()["item_ids"]
    for reader, items in ordered.items():
        seen = set(items)
        scores = _reference_scores(path, items)
        expected = sorted(
            (i for i, item in enumerate(ids) if scores[i] > 0 and item not in seen),
            key=lambda i: (-scores[i], ids[i]),
        )[:K]
        assert _top(path, reader, seen) == [ids[i] for i in expected], reader
        # Exclusion only: an EMPTY seen set must still retrieve (filtered down to the same top-k).
        unfiltered = _top(path, reader, set(), k=len(ids))
        assert [item for item in unfiltered if item not in seen][:K] == _top(path, reader, seen)


def _leaky_rows(rows) -> list[dict[str, object]]:
    """Inject val/test positives (new items, interleaved timestamps) into the rows."""
    extra = []
    for reader in sorted({int(r["reader_id"]) for r in rows})[:15]:
        extra.append(
            {
                "reader_id": reader,
                "item_id": 45 + reader % 3,
                "timestamp": 150,
                "split": "val",
                "label": 1,
            }
        )
        extra.append(
            {"reader_id": reader, "item_id": 2, "timestamp": 10_000, "split": "test", "label": 1}
        )
    extra.append({"reader_id": 999, "item_id": 3, "timestamp": 1, "split": "val", "label": 1})
    return rows[:7] + extra + rows[7:]


def _assert_same_artifact(a: dict, b: dict) -> None:
    assert a.keys() == b.keys()
    for key, value in a.items():
        if isinstance(value, np.ndarray):
            np.testing.assert_array_equal(value, b[key])
        elif key == "weights":
            assert value.keys() == b[key].keys()
            for name, weight in value.items():
                np.testing.assert_allclose(weight, b[key][name], rtol=0, atol=1e-6)
        else:
            assert value == b[key], key


def check_train_only(make, rows) -> None:
    """Val/test rows change neither the learned statistics nor the stored query histories."""
    _assert_same_artifact(make().fit(rows).artifact(), make().fit(_leaky_rows(rows)).artifact())


class _LearnShuffledQueryOrdered(TransitionRetrievalPath):  # mutant 1
    def _prepare_histories(self, ordered):
        learn, _ = super()._prepare_histories(ordered)
        return learn, ordered


class _LearnOrderedQueryShuffled(TransitionRetrievalPath):  # mutant 2
    def _prepare_histories(self, ordered):
        _, query = super()._prepare_histories(ordered)
        return ordered, query


def _seen_query(cls):  # mutant 3: query from the unordered context["seen"]
    class _SeenQuery(cls):
        def _query_history(self, reader_id, context):
            return sorted(context.get("seen", ()))

    return _SeenQuery


def _all_splits(cls):  # mutant 4: histories read every split, not train only
    class _AllSplits(cls):
        def _ordered_histories(self, rows):
            return ordered_train_histories([{**r, "split": "train"} for r in rows])

    return _AllSplits


@pytest.mark.parametrize("cls", [LastKItemItemPath, TransitionRetrievalPath])
def test_shipped_paths_pass_every_contract_check(cls, order_rows) -> None:
    make = lambda **kw: _make(cls, **kw)
    check_shuffle_semantics(make, order_rows)
    check_query_uses_stored_history(make().fit(order_rows), order_rows)
    check_train_only(make, order_rows)


def test_mutant_1_learning_only_shuffle_is_detected(order_rows) -> None:
    with pytest.raises(AssertionError):
        check_shuffle_semantics(lambda **kw: _LearnShuffledQueryOrdered(5, **kw), order_rows)


def test_mutant_2_query_only_shuffle_is_detected(order_rows) -> None:
    with pytest.raises(AssertionError):
        check_shuffle_semantics(lambda **kw: _LearnOrderedQueryShuffled(5, **kw), order_rows)


@pytest.mark.parametrize("cls", [LastKItemItemPath, TransitionRetrievalPath])
def test_mutant_3_query_from_seen_is_detected(cls, order_rows) -> None:
    mutant = _seen_query(cls)(3 if cls is LastKItemItemPath else 5).fit(order_rows)
    with pytest.raises(AssertionError):
        check_query_uses_stored_history(mutant, order_rows)


@pytest.mark.parametrize("cls", [LastKItemItemPath, TransitionRetrievalPath])
def test_mutant_4_val_test_leak_is_detected(cls, order_rows) -> None:
    k_last = 3 if cls is LastKItemItemPath else 5
    with pytest.raises(AssertionError):
        check_train_only(lambda: _all_splits(cls)(k_last), order_rows)


# ------------------------------------------------------------------------- path contracts
def test_order_decides_on_the_fixture(order_rows) -> None:
    """Sanity: the fixture is order-decisive (the shuffled control retrieves differently)."""
    ordered = TransitionRetrievalPath(5).fit(order_rows)
    shuffled = TransitionRetrievalPath(5, shuffle_seed=SHUFFLE_SEED).fit(order_rows)
    hist = ordered_train_histories(order_rows)
    differ = sum(_top(ordered, r, set(h)) != _top(shuffled, r, set(h)) for r, h in hist.items())
    assert differ >= len(hist) // 2


def test_shuffle_control_permutes_and_is_seed_deterministic(order_rows) -> None:
    ordered = ordered_train_histories(order_rows)
    first = TransitionRetrievalPath(shuffle_seed=3).fit(order_rows).histories
    again = TransitionRetrievalPath(shuffle_seed=3).fit(order_rows).histories
    other = TransitionRetrievalPath(shuffle_seed=4).fit(order_rows).histories
    assert first == again
    assert first != ordered and first != other
    assert all(sorted(first[r]) == sorted(ordered[r]) for r in ordered)  # same multiset


def test_distinct_last_k_uses_most_recent_occurrence() -> None:
    rows = _rows_from_histories({0: [1, 2, 3, 1, 4], 1: [1, 5], 2: [2, 6], 3: [3, 7], 4: [4, 8]})
    path = LastKItemItemPath(3).fit(rows)
    assert path.histories[0] == [1, 2, 3, 1, 4]
    # last-3 distinct of [1,2,3,1,4] = {4, 1, 3}: 2 is excluded, so 2's neighbour 6 never scores.
    recs = _top(path, 0, {1, 2, 3, 4})
    assert 6 not in recs and {5, 7, 8} <= set(recs)


def test_transition_counts_consecutive_train_pairs() -> None:
    rows = _rows_from_histories({0: [1, 2, 3], 1: [1, 2, 4], 2: [2, 3], 3: [5, 2]})
    path = TransitionRetrievalPath(1).fit(rows, catalog=[1, 2, 3, 4, 5])
    t = path.transitions
    col = {item: i for i, item in enumerate([1, 2, 3, 4, 5])}
    assert t[col[1], col[2]] == 2 and t[col[2], col[3]] == 2 and t[col[2], col[4]] == 1
    assert t[col[5], col[2]] == 1 and t.sum() == 6
    assert _top(path, 3, {5, 2}) == [3, 4]  # last read 2 -> 3 (x2) before 4 (x1)
    assert _top(path, 1, {1, 2, 4}) == []  # 4 is a dead end -> no positive score -> []


def test_unknown_reader_empty_fit_and_missing_timestamp(order_rows) -> None:
    for path in (LastKItemItemPath(3), TransitionRetrievalPath(5)):
        with pytest.raises(RuntimeError):
            path.retrieve(0, {"seen": set()}, K)
        path.fit(order_rows)
        assert path.retrieve(12345, {"seen": set()}, K) == []
        assert path.retrieve("not-a-reader", {"seen": set()}, K) == []
        assert len(path.retrieve(0, {"seen": set()}, 2)) <= 2
        with pytest.raises(ValueError):
            path.retrieve(0, {"seen": set()}, 0)
    negatives_only = [{**r, "label": 0} for r in order_rows]
    with pytest.raises(ValueError, match="no positive train"):
        TransitionRetrievalPath().fit(negatives_only)
    no_ts = [{k: v for k, v in r.items() if k != "timestamp"} for r in order_rows]
    with pytest.raises(ValueError, match="timestamp"):
        LastKItemItemPath().fit(no_ts)
    with pytest.raises(ValueError):
        TransitionRetrievalPath(k_last=None)  # type: ignore[arg-type]


@pytest.mark.parametrize("cls", [LastKItemItemPath, TransitionRetrievalPath])
def test_fit_artifact_load_round_trip(cls, order_rows) -> None:
    fitted = _make(cls, shuffle_seed=SHUFFLE_SEED).fit(order_rows)
    restored = cls().load(fitted.artifact())
    assert restored.histories == fitted.histories  # the shuffled query history survives
    assert restored.k_last == fitted.k_last and restored.shuffle_seed == SHUFFLE_SEED
    for reader, items in ordered_train_histories(order_rows).items():
        assert _top(restored, reader, set(items)) == _top(fitted, reader, set(items))


def test_registration_names() -> None:
    registry = PathRegistry()
    for path in (LastKItemItemPath(), TransitionRetrievalPath(), SasrecRetrievalPath()):
        registry.register(path)
    assert registry.names() == ["last-k-item-item", "transition", "sasrec"]
    assert [p.artifact_name() for p in registry] == [
        "last-k-item-item-v1",
        "transition-v1",
        "sasrec-v1",
    ]


def test_first_unseen_val(tmp_path: Path) -> None:
    path = tmp_path / "sessions.csv"
    path.write_text(
        "reader_id,item_id,session_id,timestamp,split,label\n"
        "1,10,0,1,train,1\n"
        "1,11,0,9,val,1\n"
        "1,10,0,5,val,1\n"  # a re-read of a train positive: never the target
        "1,12,0,7,val,0\n"  # a negative: never the target
        "1,13,0,8,val,1\n"
        "2,20,0,1,train,1\n"
        "2,20,0,4,val,1\n",  # only a re-read -> no key
        encoding="utf-8",
    )
    assert first_unseen_val(path) == {1: 13}


# --------------------------------------------------------------------------- SASRec (reduced)
@pytest.fixture(scope="module")
def tiny_sasrec(order_rows):
    pytest.importorskip("torch")
    return SasrecRetrievalPath(**TINY_SASREC).fit(order_rows)


def test_sasrec_numpy_forward_matches_torch(tiny_sasrec, order_rows) -> None:
    """Right after fit, the numpy forward's top-k equals the torch module's top-k (rank-based)."""
    import torch

    art = tiny_sasrec.artifact()
    params = art["params"]
    module = build_sasrec_module(
        torch,
        n_vocab=len(art["item_ids"]) + 1,
        dim=params["dim"],
        max_len=params["max_len"],
        dropout=params["dropout"],
        init_std=params["init_std"],
    )
    module.load_state_dict({k: torch.from_numpy(v) for k, v in art["weights"].items()})
    module.eval()
    ids = art["item_ids"]
    for reader in sorted(art["histories"])[::4]:
        x = torch.from_numpy(tiny_sasrec.encode(art["histories"][reader]))[None]
        with torch.no_grad():
            torch_scores = (module.item.weight[1:] @ module(x)[0, -1]).numpy().astype(np.float64)
        numpy_scores = tiny_sasrec._scores(art["histories"][reader])
        np.testing.assert_allclose(numpy_scores, torch_scores, rtol=0, atol=1e-4)
        torch_top = [ids[i] for i in np.argsort(-torch_scores, kind="stable")[:K]]
        numpy_top = [ids[i] for i in np.argsort(-numpy_scores, kind="stable")[:K]]
        assert numpy_top == torch_top, reader


def test_sasrec_fit_is_deterministic_and_restores_torch_state(tiny_sasrec, order_rows) -> None:
    import torch

    before = (torch.are_deterministic_algorithms_enabled(), torch.get_num_threads())
    again = SasrecRetrievalPath(**TINY_SASREC).fit(order_rows)
    assert (torch.are_deterministic_algorithms_enabled(), torch.get_num_threads()) == before
    for name, weight in tiny_sasrec.artifact()["weights"].items():
        np.testing.assert_allclose(again.artifact()["weights"][name], weight, rtol=0, atol=1e-6)
    for reader, items in ordered_train_histories(order_rows).items():
        assert _top(again, reader, set(items)) == _top(tiny_sasrec, reader, set(items))
    assert len(tiny_sasrec.loss_history) == TINY_SASREC["n_epochs"]


def test_sasrec_round_trip_shuffle_and_train_only(tiny_sasrec, order_rows) -> None:
    restored = SasrecRetrievalPath().load(tiny_sasrec.artifact())
    assert restored.dim == TINY_SASREC["dim"] and restored.max_len == TINY_SASREC["max_len"]
    for reader, items in ordered_train_histories(order_rows).items():
        assert _top(restored, reader, set(items)) == _top(tiny_sasrec, reader, set(items))
    assert restored.retrieve(12345, {"seen": set()}, K) == []
    shuffled = SasrecRetrievalPath(**TINY_SASREC, shuffle_seed=SHUFFLE_SEED).fit(order_rows)
    expected = shuffle_histories(ordered_train_histories(order_rows), SHUFFLE_SEED)
    assert shuffled.histories == expected
    assert SasrecRetrievalPath().load(shuffled.artifact()).histories == expected
    check_train_only(lambda: SasrecRetrievalPath(**TINY_SASREC), order_rows)


def test_sasrec_rejects_configs_beyond_the_design_ceiling() -> None:
    with pytest.raises(ValueError, match="caps SASRec"):
        SasrecRetrievalPath(dim=64)
    with pytest.raises(ValueError, match="caps SASRec"):
        SasrecRetrievalPath(max_len=51)


# ---------------------------------------------------------------- the session log (CI data)
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


@pytest.fixture(scope="module")
def session_env() -> dict[str, object]:
    if not SESSIONS.is_file():
        pytest.skip("sessions.csv.gz not generated (CI regenerates it)")
    rows = _read_rows(SESSIONS)
    catalog_ids = sorted(load_catalog(generated_dir() / "catalog.csv.gz"))
    paths = {
        "item-item": ItemItemRetrievalPath().fit(rows, catalog=catalog_ids),
        "last-3": LastKItemItemPath(3).fit(rows, catalog=catalog_ids),
        "transition": TransitionRetrievalPath(5).fit(rows, catalog=catalog_ids),
        "transition-shuffled": TransitionRetrievalPath(5, shuffle_seed=SHUFFLE_SEED).fit(
            rows, catalog=catalog_ids
        ),
    }
    hits = {
        name: reader_hits(path, SESSIONS, catalog_ids=catalog_ids, k=K)
        for name, path in paths.items()
    }
    return {"rows": rows, "catalog_ids": catalog_ids, "paths": paths, "hits": hits}


def _mean(values: dict[int, float]) -> float:
    return sum(values.values()) / len(values)


@needs_sessions
def test_gate_a_recency_lift(session_env) -> None:
    hits = session_env["hits"]
    assert hits["last-3"].keys() == hits["item-item"].keys()
    assert _mean(hits["last-3"]) >= _mean(hits["item-item"]) + 0.03


@needs_sessions
def test_gate_b_order_evidence(session_env) -> None:
    ordered = _mean(session_env["hits"]["transition"])
    shuffled = _mean(session_env["hits"]["transition-shuffled"])
    assert ordered >= 1.3 * shuffled
    assert ordered >= shuffled + 0.10


@needs_sessions
def test_reader_hits_mean_equals_scoreboard(session_env) -> None:
    result = run_validation_scoreboard(
        session_env["paths"]["last-3"], SESSIONS, catalog_ids=session_env["catalog_ids"], k=K
    )
    hits = session_env["hits"]["last-3"]
    assert result.readers == len(hits)
    assert abs(_mean(hits) - result.hit_rate_at_k) < 1e-12


@needs_sessions
def test_fit_histories_equal_the_loader(session_env) -> None:
    assert session_env["paths"]["transition"].histories == load_train_sequences(SESSIONS)


@needs_sessions
def test_last_k_none_equals_item_item(session_env) -> None:
    bag = LastKItemItemPath(None).fit(session_env["rows"], catalog=session_env["catalog_ids"])
    item_item = session_env["paths"]["item-item"]
    np.testing.assert_array_equal(bag.similarity, item_item.similarity)
    sequences = load_train_sequences(SESSIONS)
    for reader in sorted(session_env["hits"]["item-item"])[:400]:
        seen = set(sequences.get(reader, ()))
        assert _top(bag, reader, seen) == _top(item_item, reader, seen), reader

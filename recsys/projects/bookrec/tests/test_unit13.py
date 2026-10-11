"""Unit 13 (recsys-016): whole-system evaluation — exposure fairness, filter bubbles, feedback loops.

Verifies :mod:`bookrec.fairness` in three layers:

1. **Pure helpers** on hand-checkable fixtures — the Gini edge cases (uniform → 0; one item takes
   everything → ``(n − 1)/n``), full-catalog exposure Gini, author Gini + catalog share, long-tail
   share, genre entropy / spread vs history, and the pinned ``pop-penalized`` re-rank formula.
2. **The feedback-loop contract** on a small synthetic log — determinism (``allclose`` on every
   round column), val/test rows never modified, the **leakage guard** (the augmented log never
   contains a reader's own val/test positive) proven by a **recording, leaky ``path_factory``
   mutant** that pushes held-out answers to the top and records every row ``fit`` receives, and the
   mitigations really changing exposure.
3. **The plan gates** (a)/(b)/(c) and the (d) pieces on the CI-generated main log (skipped if absent),
   at the pinned thresholds of plan recsys-016 v2.2.

Plus the **test-unseal guard (v2.3, AST-based)**: every ``"test"`` string constant in the code cells of
every recsys notebook must sit on an exact allowlist, and Checkpoint B's solution unseals ``test``
exactly once, unconditionally, after its ``# FREEZE`` cell.
"""

from __future__ import annotations

import ast
import copy
import csv
import gzip
import json
import math
import re
from collections import Counter
from itertools import pairwise
from pathlib import Path
from typing import ClassVar

import numpy as np
import pytest
from bookrec import (
    Book,
    Candidate,
    ItemItemRetrievalPath,
    MatrixFactorizationPath,
    PopularityRetrievalPath,
    generated_dir,
    head_ids_from_counts,
    load_catalog,
    rank,
)
from bookrec.fairness import (
    PopularityPenalizedPath,
    RoundMetrics,
    author_catalog_share,
    author_exposure_gini,
    exposure_gini,
    genre_entropy,
    genre_spread_vs_history,
    gini,
    long_tail_share,
    popularity_penalized,
    simulate_feedback_loop,
    val_cohort,
)
from bookrec.protocol import BaseRetrievalPath

K = 10
SEED = 0
REPO = Path(__file__).resolve().parents[4]
INTERACTIONS = generated_dir() / "interactions.csv.gz"
LAMBDAS = (0.0, 0.1, 0.3, 0.5, 1.0)
ROUND_COLUMNS = ("coverage", "head_share", "gini", "genre_entropy", "clean_hit", "accepted")

needs_main_log = pytest.mark.skipif(
    not INTERACTIONS.is_file(), reason="interactions.csv.gz not generated (CI regenerates it)"
)


# ======================================================================================
# 1. Pure helpers
# ======================================================================================


def test_gini_edge_cases() -> None:
    assert gini([5, 5, 5, 5]) == pytest.approx(0.0)
    for n in (2, 5, 100):
        assert gini([0] * (n - 1) + [7]) == pytest.approx((n - 1) / n)
    assert gini([]) == 0.0
    assert gini([0, 0, 0]) == 0.0
    # Order-free and scale-free.
    assert gini([1, 2, 3, 10]) == pytest.approx(gini([30, 10, 20, 100]))
    with pytest.raises(ValueError):
        gini([1, -1])


def test_exposure_gini_counts_the_full_catalog() -> None:
    catalog = [1, 2, 3, 4]
    # Every item shown equally -> 0; zeros are included, so showing only one item -> 3/4.
    assert exposure_gini({0: [1, 2], 1: [3, 4]}, catalog) == pytest.approx(0.0)
    assert exposure_gini({0: [1], 1: [1]}, catalog) == pytest.approx(0.75)
    # Same lists, bigger catalog -> more never-shown items -> a higher Gini.
    assert exposure_gini([[1, 2]], range(1, 11)) > exposure_gini([[1, 2]], [1, 2, 3])
    # Candidates and out-of-catalog ids.
    assert exposure_gini([[Candidate(1, 1.0, "p"), 99]], [1, 2]) == pytest.approx(0.5)


def _books() -> dict[int, Book]:
    # author "a" owns 3 books, "b" owns 1.
    spec = {1: ("a", "x;y"), 2: ("a", "x"), 3: ("a", "y"), 4: ("b", "z")}
    return {
        i: Book(item_id=i, title=f"b{i}", fields={"author_id": a, "genres": g})
        for i, (a, g) in spec.items()
    }


def test_author_gini_and_catalog_share() -> None:
    books = _books()
    assert author_catalog_share(books) == {"a": pytest.approx(0.75), "b": pytest.approx(0.25)}
    # Both authors shown once -> equal author exposure.
    assert author_exposure_gini([[1, 4]], books) == pytest.approx(0.0)
    # Only author a shown -> (2 - 1)/2.
    assert author_exposure_gini([[1, 2, 3]], books) == pytest.approx(0.5)


def test_long_tail_share() -> None:
    assert long_tail_share([[1, 2], [3, 4]], head_ids=[1]) == pytest.approx(0.75)
    assert long_tail_share({0: [1]}, head_ids=[1]) == pytest.approx(0.0)
    assert long_tail_share([], head_ids=[1]) == 0.0


def test_genre_entropy_and_spread() -> None:
    books = _books()
    assert genre_entropy([2], books) == pytest.approx(0.0)
    assert genre_entropy([1], books) == pytest.approx(1.0)  # x, y equally -> 1 bit
    assert genre_entropy([1, 4], books) == pytest.approx(math.log2(3))
    assert genre_entropy([], books) == 0.0
    spread = genre_spread_vs_history({7: [2]}, {7: [1, 4]}, books)
    assert spread == {7: (pytest.approx(0.0), pytest.approx(math.log2(3)))}


class _FixedPath(BaseRetrievalPath):
    def __init__(self, scores: dict[int, float]) -> None:
        super().__init__(name="fixed", version="1", _fitted=True)
        self.scores = scores

    def fit(self, interactions, catalog=None):
        return self

    def retrieve(self, query, context, k):
        seen = set(context.get("seen", ()))
        cands = [Candidate(i, s, self.name) for i, s in self.scores.items() if i not in seen]
        return self._finish(cands, k)


def test_popularity_penalized_formula() -> None:
    inner = _FixedPath({1: 10.0, 2: 6.0, 3: 2.0})
    counts = {1: 99, 2: 9, 3: 0}
    path = popularity_penalized(inner, 0.5, counts, pool=50)
    assert isinstance(path, PopularityPenalizedPath)
    assert (path.name, path.version, path.artifact_name()) == (
        "pop-penalized",
        "1",
        "pop-penalized-v1",
    )
    out = path.retrieve(0, {"seen": set()}, 3)
    expected = {
        1: 1.0 - 0.5 * math.log1p(99) / math.log1p(99),
        2: 0.5 - 0.5 * math.log1p(9) / math.log1p(99),
        3: 0.0,
    }
    assert {c.item_id: c.score for c in out} == {i: pytest.approx(s) for i, s in expected.items()}
    assert [c.item_id for c in out] == sorted(expected, key=lambda i: (-expected[i], i))
    # penalty 0 keeps the inner order; k bounds; seen honoured.
    assert [c.item_id for c in popularity_penalized(inner, 0.0, counts).retrieve(0, {}, 2)] == [
        1,
        2,
    ]
    assert [c.item_id for c in path.retrieve(0, {"seen": {1}}, 5)] == [2, 3]
    with pytest.raises(ValueError):
        popularity_penalized(inner, -0.1, counts)


# ======================================================================================
# 2. The feedback-loop contract on a small synthetic log
# ======================================================================================


def _synthetic() -> tuple[list[dict[str, object]], dict[int, Book], list[int]]:
    rng = np.random.default_rng(7)
    genres = ["x", "y", "z", "w"]
    books = {
        i: Book(
            item_id=i,
            title=f"b{i}",
            fields={"author_id": str(i % 6), "genres": f"{genres[i % 4]};{genres[(i // 4) % 4]}"},
        )
        for i in range(40)
    }
    rows: list[dict[str, object]] = []
    for reader in range(30):
        items = rng.choice(40, size=8, replace=False).tolist()
        for t, item in enumerate(items[:6]):
            rows.append(
                {"reader_id": reader, "item_id": item, "timestamp": t, "split": "train", "label": 1}
            )
        rows.append(
            {"reader_id": reader, "item_id": items[6], "timestamp": 6, "split": "val", "label": 1}
        )
        rows.append(
            {"reader_id": reader, "item_id": items[7], "timestamp": 7, "split": "test", "label": 1}
        )
        rows.append(
            {"reader_id": reader, "item_id": items[0], "timestamp": 0, "split": "train", "label": 0}
        )
    return rows, books, val_cohort(rows, books)


def _columns(result: list[RoundMetrics]) -> np.ndarray:
    return np.array([[getattr(m, c) for c in ROUND_COLUMNS] for m in result], dtype=float)


def test_loop_is_deterministic_and_leaves_rows_untouched() -> None:
    rows, books, cohort = _synthetic()
    before = copy.deepcopy(rows)
    kwargs = {"cohort": cohort, "catalog": books, "rounds": 3, "k": 5, "accept_prob": 0.5}
    first = simulate_feedback_loop(ItemItemRetrievalPath, rows, seed=3, **kwargs)
    second = simulate_feedback_loop(ItemItemRetrievalPath, rows, seed=3, **kwargs)
    assert len(first) == 4 and [m.round for m in first] == [0, 1, 2, 3]
    np.testing.assert_allclose(_columns(first), _columns(second))
    assert [m.new_rows for m in first] == [m.new_rows for m in second]
    assert rows == before  # val/test (and train) rows never modified
    assert sum(m.accepted for m in first) > 0
    for m in first:
        # Per-item Bernoulli (plan v2.5): a reader may read several served items in one round.
        assert m.accepted == len(m.new_rows) <= 5 * len(cohort)
        assert all(r["split"] == "train" and r["label"] == 1 for r in m.new_rows)
        assert all(r["session_id"] == -1 for r in m.new_rows)
    # Several reads by one reader in one round do happen (it is not a one-read rule).
    per_round_reader = [Counter(r["reader_id"] for r in m.new_rows) for m in first]
    assert max(max(c.values(), default=0) for c in per_round_reader) >= 2
    reads = [(r["reader_id"], r["item_id"]) for m in first for r in m.new_rows]
    assert len(reads) == len(set(reads))  # never a duplicate (reader, item) read
    train_pos = {
        (r["reader_id"], r["item_id"]) for r in rows if r["split"] == "train" and r["label"] == 1
    }
    assert not set(reads) & train_pos  # never an already-seen item
    held = {(r["reader_id"], r["item_id"]) for r in rows if r["split"] in ("val", "test")}
    assert not set(reads) & held  # the leakage guard holds


class _RecordingLeakyPath(BaseRetrievalPath):
    """A mutant that records every row ``fit`` sees and ranks held-out answers FIRST."""

    fit_rows: ClassVar[list[list[dict[str, object]]]] = []
    served: ClassVar[list[list[int]]] = []

    def __init__(self, held_out: dict[int, set[int]], items: list[int]) -> None:
        super().__init__(name="leaky", version="1", _fitted=True)
        self.held_out = held_out
        self.items = items

    def fit(self, interactions, catalog=None):
        type(self).fit_rows.append(list(interactions))
        return self

    def retrieve(self, query, context, k):
        seen = set(context.get("seen", ()))
        cheat = self.held_out.get(query, set())
        cands = [
            Candidate(i, 2.0 if i in cheat else 1.0 / (1 + i), self.name)
            for i in self.items
            if i not in seen
        ]
        out = self._finish(cands, k)
        type(self).served.append([c.item_id for c in out])
        return out


def test_leakage_guard_with_a_recording_mutant() -> None:
    rows, books, cohort = _synthetic()
    held_rows = [r for r in rows if r["split"] in ("val", "test")]
    held_out: dict[int, set[int]] = {}
    for r in held_rows:
        if r["label"] == 1:
            held_out.setdefault(int(r["reader_id"]), set()).add(int(r["item_id"]))
    _RecordingLeakyPath.fit_rows = []
    _RecordingLeakyPath.served = []
    result = simulate_feedback_loop(
        lambda: _RecordingLeakyPath(held_out, sorted(books)),
        rows,
        cohort=cohort,
        catalog=books,
        seed=1,
        rounds=3,
        k=3,
        accept_prob=1.0,
    )
    # The mutant really pushed held-out answers into the served lists (the guard is exercised).
    assert any(
        set(top) & held_out.get(r, set()) for r in cohort for top in _RecordingLeakyPath.served
    )
    # No original val/test row ever reached fit (by identity AND by split).
    held_ids = {id(r) for r in held_rows}
    for seen_rows in _RecordingLeakyPath.fit_rows:
        assert all(r["split"] == "train" for r in seen_rows)
        assert not any(id(r) in held_ids for r in seen_rows)
    # The acceptance step never appended a reader's own val/test positive.
    augmented = [r for m in result for r in m.new_rows]
    assert augmented, "accept_prob=1.0 must produce reads"
    assert not any(int(r["item_id"]) in held_out.get(int(r["reader_id"]), set()) for r in augmented)
    # Timestamps follow each reader's last train timestamp; no duplicate (reader, item) reads.
    assert all(int(r["timestamp"]) >= 6 for r in augmented)
    pairs = [(r["reader_id"], r["item_id"]) for r in augmented]
    assert len(pairs) == len(set(pairs))


def test_mitigations_change_exposure() -> None:
    rows, books, cohort = _synthetic()
    kw = {"cohort": cohort, "catalog": books, "seed": 2, "rounds": 2, "k": 5}
    base = simulate_feedback_loop(PopularityRetrievalPath, rows, **kw)
    explore = simulate_feedback_loop(PopularityRetrievalPath, rows, mitigation="explore", **kw)
    assert explore[0].coverage > base[0].coverage and explore[0].gini < base[0].gini
    # (A popularity penalty cannot reorder the popularity path itself, so test it on item-item.)
    ii = simulate_feedback_loop(ItemItemRetrievalPath, rows, **kw)
    penalty = simulate_feedback_loop(
        ItemItemRetrievalPath, rows, mitigation="penalty", penalty=1.0, **kw
    )
    assert penalty[0].head_share < ii[0].head_share
    # The clean-hit readout scores the refit (unmitigated) path, so round 0 is identical.
    assert explore[0].clean_hit == pytest.approx(base[0].clean_hit)
    with pytest.raises(ValueError):
        simulate_feedback_loop(PopularityRetrievalPath, rows, mitigation="bogus", **kw)


# ======================================================================================
# 3. Plan gates on the CI-generated main log (plan recsys-016 v2.2 thresholds)
# ======================================================================================


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


class _Recording:
    """Wrap a path factory and record whether any non-train row ever reaches ``fit``."""

    def __init__(self, factory) -> None:
        self.factory = factory
        self.non_train_rows = 0
        self.fits = 0

    def __call__(self):
        path = self.factory()
        inner_fit = path.fit

        def fit(interactions, catalog=None):
            interactions = list(interactions)
            self.fits += 1
            self.non_train_rows += sum(1 for r in interactions if r["split"] != "train")
            return inner_fit(interactions, catalog=catalog)

        path.fit = fit
        return path


@pytest.fixture(scope="module")
def main_env() -> dict[str, object]:
    gen = generated_dir()
    books = load_catalog(gen / "catalog.csv.gz")
    rows = _read_rows(gen / "interactions.csv.gz")
    cold = json.loads((gen / "cold_partitions.json").read_text())
    ids = sorted(books)
    cohort = val_cohort(rows, ids, cold["cold_readers"])
    seen: dict[int, set[int]] = {}
    val: dict[int, set[int]] = {}
    held: dict[int, set[int]] = {}
    for r in rows:
        if r["label"] != 1:
            continue
        target = {"train": seen, "val": val}.get(r["split"])
        if target is not None:
            target.setdefault(r["reader_id"], set()).add(r["item_id"])
        if r["split"] in ("val", "test"):
            held.setdefault(r["reader_id"], set()).add(r["item_id"])
    popularity = PopularityRetrievalPath().fit(rows, catalog=ids)
    return {
        "rows": rows,
        "books": books,
        "ids": ids,
        "cohort": cohort,
        "seen": seen,
        "val": val,
        "held": held,
        "counts": popularity.counts,
        "popularity": popularity,
    }


@pytest.fixture(scope="module")
def loops(main_env: dict[str, object]) -> dict[str, object]:
    kw = {"cohort": main_env["cohort"], "catalog": main_env["books"], "seed": SEED}
    recording = _Recording(ItemItemRetrievalPath)
    item_item = simulate_feedback_loop(recording, main_env["rows"], **kw)
    explore = simulate_feedback_loop(
        ItemItemRetrievalPath, main_env["rows"], mitigation="explore", **kw
    )
    popularity = simulate_feedback_loop(PopularityRetrievalPath, main_env["rows"], **kw)
    return {
        "item-item": item_item,
        "explore": explore,
        "popularity": popularity,
        "recording": recording,
    }


@needs_main_log
def test_main_log_cohort_and_loop_leakage(main_env, loops) -> None:
    assert len(main_env["cohort"]) == 500
    recording = loops["recording"]
    assert recording.fits == 7 and recording.non_train_rows == 0
    held = main_env["held"]
    for name in ("item-item", "explore", "popularity"):
        reads = [r for m in loops[name] for r in m.new_rows]
        assert reads and not any(r["item_id"] in held.get(r["reader_id"], set()) for r in reads)


@needs_main_log
def test_gate_a_the_loop_concentrates(loops) -> None:
    ii = loops["item-item"]
    assert len(ii) == 7
    assert ii[-1].coverage <= ii[0].coverage - 0.08, [m.coverage for m in ii]
    assert ii[-1].gini >= ii[0].gini + 0.03, [m.gini for m in ii]
    for m in loops["popularity"]:
        assert m.gini >= 0.98 and m.coverage <= 0.03, m


@needs_main_log
def test_gate_b_exploration_slot_restores_exposure(loops) -> None:
    loop, explore = loops["item-item"], loops["explore"]
    assert explore[-1].coverage >= loop[-1].coverage + 0.04
    assert explore[-1].gini <= loop[-1].gini - 0.01
    # The accuracy cost is reported, not asserted: cost_0 is 0 by construction (clean hit scores
    # the refit, unmitigated path, and round 0 fits the same original log).
    assert explore[0].clean_hit - loop[0].clean_hit == pytest.approx(0.0)


@needs_main_log
def test_gate_d_filter_bubble_narrows(loops) -> None:
    entropy = [m.genre_entropy for m in loops["item-item"]]
    assert min(entropy[1:5]) <= entropy[0] - 0.3, entropy


def _recs(path, env, k=K) -> dict[int, list[int]]:
    seen = env["seen"]
    return {
        r: [
            c.item_id
            for c in rank(
                path.retrieve(r, {"seen": seen.get(r, set())}, k), n=K, exclude=seen.get(r, set())
            )
        ]
        for r in env["cohort"]
    }


def _hit(recs: dict[int, list[int]], env) -> float:
    seen, val = env["seen"], env["val"]
    return float(
        np.mean([1.0 if set(t) & (val[r] - seen.get(r, set())) else 0.0 for r, t in recs.items()])
    )


@pytest.fixture(scope="module")
def part1_paths(main_env) -> dict[str, object]:
    rows, ids = main_env["rows"], main_env["ids"]
    members = {
        "popularity": main_env["popularity"],
        "item-item": ItemItemRetrievalPath().fit(rows, catalog=ids),
        "mf": MatrixFactorizationPath(seed=SEED).fit(rows, catalog=ids),
    }
    return members


# Plan anchors at lambda = 0.3 (+-0.003 hit / +-0.005 Gini).
# The U6-blend half of gate (c) (0.290 / 0.858) is asserted in the Unit-13 milestone (plan v2.5), as
# are the U6-blend / two-tower head-tail ratios and the feature-tower cold readout (pytest budget).
ANCHORS = {"item-item": (0.224, 0.747)}


@needs_main_log
@pytest.mark.parametrize("base", ["item-item"])
def test_gate_c_penalty_tradeoff_curve(base, main_env, part1_paths) -> None:
    hits, ginis = [], []
    for lam in LAMBDAS:
        recs = _recs(
            popularity_penalized(part1_paths[base], lam, main_env["counts"], pool=50), main_env
        )
        hits.append(_hit(recs, main_env))
        ginis.append(exposure_gini(recs, main_env["ids"]))
    assert all(a > b for a, b in pairwise(ginis)), ginis
    assert all(a >= b for a, b in pairwise(hits)), hits
    hit_03, gini_03 = hits[LAMBDAS.index(0.3)], ginis[LAMBDAS.index(0.3)]
    assert hit_03 == pytest.approx(ANCHORS[base][0], abs=0.003)
    assert gini_03 == pytest.approx(ANCHORS[base][1], abs=0.005)


@needs_main_log
def test_gate_d_offline_head_tail_and_cold_readout(main_env, part1_paths) -> None:
    head = set(head_ids_from_counts(main_env["counts"], main_env["ids"]))
    seen, val = main_env["seen"], main_env["val"]
    positives = [i for r in main_env["cohort"] for i in val[r] - seen.get(r, set())]
    assert np.mean([i in head for i in positives]) == pytest.approx(0.441, abs=0.005)
    zero_train = set(main_env["ids"]) - set(main_env["counts"])
    assert zero_train
    for name in ("popularity", "item-item", "mf"):
        recs = _recs(part1_paths[name], main_env)
        # Cold readout: warm-only collaborative paths surface 0 zero-train items.
        assert not {i for t in recs.values() for i in t} & zero_train, name
        if name == "popularity":
            continue
        head_hits, tail_hits = [], []
        for r, top in recs.items():
            rel = val[r] - seen.get(r, set())
            if rel & head:
                head_hits.append(1.0 if set(top) & rel & head else 0.0)
            if rel - head:
                tail_hits.append(1.0 if set(top) & (rel - head) else 0.0)
        assert np.mean(head_hits) >= 5 * np.mean(tail_hits), (name, head_hits, tail_hits)


# ======================================================================================
# 4. Test-unseal guard (plan v2.3, AST-based)
# ======================================================================================

# Exact allowlist: notebook -> number of "test" string constants in its code cells.
TEST_CONSTANT_ALLOWLIST = {
    "recsys/units/unit-01-problem-and-scoreboard/lesson.ipynb": 1,  # ("min", "test") diagnostic
    "recsys/checkpoints/checkpoint-01-part-1/checkpoint.ipynb": 0,
    "recsys/checkpoints/checkpoint-01-part-1/solutions.ipynb": 1,
    "recsys/checkpoints/checkpoint-02-part-2/checkpoint.ipynb": 0,
    "recsys/checkpoints/checkpoint-02-part-2/solutions.ipynb": 1,
}
CPB_SOLUTIONS = REPO / "recsys/checkpoints/checkpoint-02-part-2/solutions.ipynb"
_TEST_WORD = re.compile(r"\btest\b")


def _code_cells(notebook: Path) -> list[str]:
    payload = json.loads(notebook.read_text(encoding="utf-8"))
    cells = []
    for cell in payload.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        lines = source.splitlines()
        # IPython magics / shell escapes are not Python; blank them (keeping line numbers).
        cells.append("\n".join("" if ln.lstrip().startswith(("%", "!")) else ln for ln in lines))
    return cells


def _test_constants(tree: ast.AST) -> list[ast.Constant]:
    return [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and n.value == "test"]


def _fstrings_naming_test(tree: ast.AST) -> list[ast.JoinedStr]:
    return [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.JoinedStr)
        and any(
            isinstance(v, ast.Constant) and isinstance(v.value, str) and _TEST_WORD.search(v.value)
            for v in n.values
        )
    ]


def test_global_test_constant_allowlist() -> None:
    notebooks = sorted(
        nb for nb in (REPO / "recsys").rglob("*.ipynb") if ".ipynb_checkpoints" not in nb.parts
    )
    assert notebooks
    counts: dict[str, int] = {}
    fstring_offenders: list[str] = []
    for notebook in notebooks:
        rel = notebook.relative_to(REPO).as_posix()
        n = 0
        for source in _code_cells(notebook):
            tree = ast.parse(source)  # a code cell that is not Python fails loudly
            n += len(_test_constants(tree))
            if rel not in TEST_CONSTANT_ALLOWLIST and _fstrings_naming_test(tree):
                fstring_offenders.append(rel)
        if n:
            counts[rel] = n
    offenders = {rel: n for rel, n in counts.items() if TEST_CONSTANT_ALLOWLIST.get(rel) is None}
    assert not offenders, f'unlisted notebooks hold "test" constants: {offenders}'
    for rel, n in counts.items():
        assert n <= TEST_CONSTANT_ALLOWLIST[rel], (rel, n)
    # The listed non-CP-B entries must match exactly (a moved diagnostic or a second CP-A unseal
    # is a change to review, not to absorb).
    for rel in (
        "recsys/units/unit-01-problem-and-scoreboard/lesson.ipynb",
        "recsys/checkpoints/checkpoint-01-part-1/solutions.ipynb",
    ):
        assert counts.get(rel, 0) == TEST_CONSTANT_ALLOWLIST[rel], rel
    if CPB_SOLUTIONS.exists():
        assert counts.get(CPB_SOLUTIONS.relative_to(REPO).as_posix(), 0) == 1
    assert not fstring_offenders, (
        f'f-strings naming "test" outside the allowlist: {fstring_offenders}'
    )


_FORBIDDEN_ANCESTORS = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.With,
    ast.AsyncWith,
    ast.Try,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.BoolOp,
    ast.IfExp,
    ast.Match,
)


_SCOREBOARD_CALLEES = frozenset(
    {"run_blended_scoreboard", "run_validation_scoreboard", "reader_hits"}
)


def _callee_name(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _cpb_once_violations(cells: list[str]) -> list[str]:
    """Return why a CP-B solutions notebook does NOT unseal ``test`` exactly once (empty = OK).

    Rules (plan v2.3 + content-gate r1): exactly one ``"test"`` constant in the notebook; every
    ``split=`` keyword anywhere is a string LITERAL (no computed / named / concatenated split);
    no scoreboard call uses ``**kwargs``; the single ``split="test"`` belongs to a call of
    ``run_blended_scoreboard`` that is the direct value of a top-level ``Expr``/``Assign`` of its
    cell (so it runs unconditionally, exactly once), in a cell after the ``# FREEZE`` cell.
    """
    freeze = [i for i, src in enumerate(cells) if "# FREEZE" in src]
    if not freeze:
        return ["no cell carries the '# FREEZE' marker"]
    problems: list[str] = []
    found: list[tuple[int, ast.Module, ast.Constant]] = []
    test_calls: list[tuple[int, ast.Module, ast.Call]] = []
    for index, source in enumerate(cells):
        tree = ast.parse(source)
        found += [(index, tree, const) for const in _test_constants(tree)]
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            callee = _callee_name(call)
            if callee in _SCOREBOARD_CALLEES and any(kw.arg is None for kw in call.keywords):
                problems.append(f"{callee} called with **kwargs (split could be hidden)")
            for kw in call.keywords:
                if kw.arg != "split":
                    continue
                if not (isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str)):
                    problems.append("a split= argument is not a string literal")
                elif kw.value.value == "test":
                    test_calls.append((index, tree, call))
    if len(found) != 1:
        return [*problems, f'expected exactly one "test" constant, found {len(found)}']
    if len(test_calls) != 1:
        return [*problems, f'expected exactly one split="test" call, found {len(test_calls)}']
    index, tree, call = test_calls[0]
    if _callee_name(call) != "run_blended_scoreboard":
        problems.append('split="test" is not passed to run_blended_scoreboard')
    if index <= freeze[0]:
        problems.append("the test call is not after the # FREEZE cell")
    top_level = any(
        isinstance(stmt, ast.Expr | ast.Assign) and stmt.value is call for stmt in tree.body
    )
    if not top_level:
        problems.append('the split="test" call is not a top-level Expr/Assign value')
    return problems


def test_cpb_once_checker_rejects_mutants() -> None:
    ok = (
        'm = run_blended_scoreboard(b, split="val")\n',
        "# FREEZE\nfrozen = b\n",
        'res = run_blended_scoreboard(frozen, split="test")\n',
    )
    assert _cpb_once_violations(list(ok)) == []
    mutants = [
        ('run_blended_scoreboard(b, split="test")\n', "# FREEZE\n"),  # before the freeze
        ("# FREEZE\n", 'for _ in range(2):\n    run_blended_scoreboard(b, split="test")\n'),  # loop
        ("# FREEZE\n", 'if go:\n    run_blended_scoreboard(b, split="test")\n'),  # conditional
        ("# FREEZE\n", 'x = go and run_blended_scoreboard(b, split="test")\n'),  # BoolOp
        ("# FREEZE\n", 'x = run_blended_scoreboard(b, split="test") if go else None\n'),  # IfExp
        ("# FREEZE\n", 'def f():\n    return run_blended_scoreboard(b, split="test")\n'),  # def
        (
            "# FREEZE\n",
            'x = [run_blended_scoreboard(b, split="test") for _ in "ab"]\n',
        ),  # comprehension
        ("# FREEZE\n", 's = "test"\nrun_blended_scoreboard(b, split=s)\n'),  # indirect via a name
        ("# FREEZE\n", 'run_blended_scoreboard(b, **{"split": "test"})\n'),  # **kwargs
        (
            "# FREEZE\n",
            'run_blended_scoreboard(b, split="test")\nrun_blended_scoreboard(b, split="test")\n',
        ),  # twice
        ("frozen = b\n", 'run_blended_scoreboard(b, split="test")\n'),  # no freeze marker
        ("# FREEZE\n", 'x = dict(split="test")\n'),  # wrong callee
        ("# FREEZE\n", 'r = run_blended_scoreboard(b, split="te" + "st")\n'),  # computed split
        ("# FREEZE\n", 'p = "va" + "l"\nr = run_blended_scoreboard(b, split=p)\n'),  # named split
        ("# FREEZE\n", "kw = {}\nr = run_validation_scoreboard(b, **kw)\n"),  # **kwargs
        (  # one literal test call plus a second, computed one
            "# FREEZE\n",
            (
                'r = run_blended_scoreboard(b, split="test")\n'
                'r2 = run_blended_scoreboard(b, split="te" + "st")\n'
            ),
        ),
    ]
    for cells in mutants:
        assert _cpb_once_violations(list(cells)), cells


def test_cpb_solution_unseals_test_exactly_once() -> None:
    if not CPB_SOLUTIONS.exists():
        pytest.skip("checkpoint-02-part-2/solutions.ipynb not written yet (Phase F)")
    assert _cpb_once_violations(_code_cells(CPB_SOLUTIONS)) == []


def test_cp_a_guard_still_passes() -> None:
    from test_unit06 import test_only_the_checkpoint_solution_touches_the_test_split

    test_only_the_checkpoint_solution_touches_the_test_split()

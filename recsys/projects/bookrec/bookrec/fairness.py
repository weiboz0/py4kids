"""Unit 13: whole-system evaluation — exposure fairness, filter bubbles and feedback loops.

Design 011 §8 row 13 (the ethics & beyond-accuracy thread). Every helper here is a *descriptive*
measurement on our data, not a complete fairness judgment. Pure numpy + stdlib, seeded, torch-free.

**Exposure fairness** — who gets recommended?

- :func:`gini` — the Gini coefficient of a non-negative vector (``0`` = perfectly equal exposure,
  ``(n − 1)/n`` = one entry takes everything).
- :func:`exposure_gini` — the Gini of per-item exposure (slot counts) over the **full catalog**,
  zeros included, so every path is compared over the same ``N``.
- :func:`author_exposure_gini` — the same at the author level; read it next to
  :func:`author_catalog_share` (an author with more books *should* get more exposure, so part of the
  inequality is the catalog's own).
- :func:`long_tail_share` — the fraction of recommendation slots that go to non-head items.
- :class:`PopularityPenalizedPath` / :func:`popularity_penalized` — a re-ranking wrapper path
  (``"pop-penalized"``, version ``"1"``) that over-retrieves a pool of ``pool`` candidates from an
  inner path and re-scores ``score' = minmax(score) − λ · log1p(count)/log1p(max count)``.

**Filter bubbles** — :func:`genre_entropy` (Shannon entropy, in bits, of the genre labels of a list
of items) and :func:`genre_spread_vs_history` (per reader: entropy of the recommendations vs the
entropy of the reader's own history).

**Feedback loops** — :func:`simulate_feedback_loop`, a *stylized exposure-to-consumption loop*:
simulated readers take what they are shown with a fixed probability, the accepted reads are
appended to the train log, and the path is refit. It is **not** a realistic preference model. The
semantics are pinned by plan recsys-016 (see the function docstring); the most important one is the
**leakage guard**: a simulated reader never "reads" one of its own held-out (val/test) positives, so
the simulation never hands the model a held-out answer.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from bookrec.catalog import Book
from bookrec.diversity import catalog_coverage, head_ids_from_counts, head_share
from bookrec.protocol import BaseRetrievalPath, Candidate, calibrate_scores
from bookrec.rank import rank

GENRE_SEPARATOR = ";"


def _item_id(item: Candidate | int) -> int:
    return item.item_id if isinstance(item, Candidate) else int(item)


def _lists(
    recommendations: Mapping[Any, Sequence[Candidate | int]] | Iterable[Sequence[Candidate | int]],
) -> list[list[int]]:
    """Normalise ``{reader: top-k}`` or an iterable of top-k lists into lists of int ids."""
    values = recommendations.values() if isinstance(recommendations, Mapping) else recommendations
    return [[_item_id(item) for item in recs] for recs in values]


# ------------------------------------------------------------------------------ exposure fairness


def gini(values: Iterable[float]) -> float:
    """The Gini coefficient of a non-negative vector (``0.0`` for an empty or all-zero vector).

    ``G = Σ_i (2i − n − 1)·x_(i) / (n · Σ x)`` over the ascending-sorted values ``x_(1..n)``. Perfect
    equality gives ``0``; one entry holding everything gives ``(n − 1)/n``. Negative or non-finite
    values raise :class:`ValueError`.
    """
    x = np.sort(np.asarray(list(values), dtype=float))
    if x.size and (not np.isfinite(x).all() or (x < 0).any()):
        raise ValueError("gini needs finite, non-negative values")
    n = x.size
    total = float(x.sum())
    if n == 0 or total == 0.0:
        return 0.0
    ranks = np.arange(1, n + 1, dtype=float)
    return float(((2.0 * ranks - n - 1.0) * x).sum() / (n * total))


def exposure_counts(
    recommendations: Mapping[Any, Sequence[Candidate | int]] | Iterable[Sequence[Candidate | int]],
    catalog_ids: Iterable[int],
) -> dict[int, int]:
    """Slot count per catalog item (every catalog item present, zeros included)."""
    counts = {int(item_id): 0 for item_id in catalog_ids}
    for recs in _lists(recommendations):
        for item_id in recs:
            if item_id in counts:
                counts[item_id] += 1
    return counts


def exposure_gini(
    recommendations: Mapping[Any, Sequence[Candidate | int]] | Iterable[Sequence[Candidate | int]],
    catalog_ids: Iterable[int],
) -> float:
    """Gini of item exposure over the **full catalog** (never-recommended items count as ``0``).

    ``recommendations`` is ``{reader_id: top-k}`` (or an iterable of top-k lists) of
    :class:`~bookrec.protocol.Candidate` objects or int ids. Items outside ``catalog_ids`` are
    ignored. Because the zeros are included, every path is measured over the same ``N``.
    """
    return gini(exposure_counts(recommendations, catalog_ids).values())


def _author_of(book: Book) -> str:
    return str(book.fields.get("author_id", "")).strip()


def author_catalog_share(catalog: Mapping[int, Book]) -> dict[str, float]:
    """Each author's share of the catalog's books (sums to ``1``) — the context for author Gini."""
    books = Counter(_author_of(book) for book in catalog.values())
    total = sum(books.values())
    return {author: count / total for author, count in sorted(books.items())} if total else {}


def author_exposure_gini(
    recommendations: Mapping[Any, Sequence[Candidate | int]] | Iterable[Sequence[Candidate | int]],
    catalog: Mapping[int, Book],
) -> float:
    """Gini of exposure summed per **author**, over every catalog author (zeros included).

    Unequal author exposure partly reflects unequal numbers of books per author; compare with
    ``gini(author_catalog_share(catalog).values())`` before reading it as unfairness.
    """
    exposure = dict.fromkeys(author_catalog_share(catalog), 0)
    for recs in _lists(recommendations):
        for item_id in recs:
            book = catalog.get(item_id)
            if book is not None:
                exposure[_author_of(book)] += 1
    return gini(exposure.values())


def long_tail_share(
    recommendations: Mapping[Any, Sequence[Candidate | int]] | Iterable[Sequence[Candidate | int]],
    head_ids: Iterable[int],
) -> float:
    """Fraction of recommendation slots whose item is **not** in ``head_ids`` (``1 − head-share``)."""
    lists = _lists(recommendations)
    if not any(lists):
        return 0.0
    return 1.0 - head_share(lists, head_ids)


# --------------------------------------------------------------------------------- filter bubbles


def _genres(book: Book | None) -> list[str]:
    if book is None:
        return []
    raw = str(book.fields.get("genres", ""))
    return [genre.strip() for genre in raw.split(GENRE_SEPARATOR) if genre.strip()]


def genre_entropy(items: Iterable[Candidate | int], catalog: Mapping[int, Book]) -> float:
    """Shannon entropy (bits) of the genre labels over ``items`` (each item adds each of its genres).

    ``0.0`` for an empty list (or items with no genres). Higher = the list spans more genres.
    """
    counts = Counter(genre for item in items for genre in _genres(catalog.get(_item_id(item))))
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return float(-sum((c / total) * math.log2(c / total) for c in counts.values()))


def genre_spread_vs_history(
    recommendations: Mapping[int, Sequence[Candidate | int]],
    history: Mapping[int, Iterable[int]],
    catalog: Mapping[int, Book],
) -> dict[int, tuple[float, float]]:
    """Per reader: ``(genre entropy of the recommendations, genre entropy of the history)``.

    A recommendation entropy well below the history's means the recommender shows the reader a
    *narrower* slice of genres than the reader actually reads — a filter-bubble symptom. Readers
    absent from ``history`` get a history entropy of ``0.0``.
    """
    return {
        int(reader): (
            genre_entropy(recs, catalog),
            genre_entropy(history.get(reader, ()), catalog),
        )
        for reader, recs in sorted(recommendations.items())
    }


# ------------------------------------------------------------------- popularity-penalised re-rank


class PopularityPenalizedPath(BaseRetrievalPath):
    """Re-rank an inner path's pool with a popularity penalty (name ``"pop-penalized"``, ``v1``).

    For each query the inner path retrieves ``max(pool, k)`` candidates; their scores are min-max
    calibrated to ``[0, 1]`` and re-scored as
    ``score' = minmax(score) − penalty · log1p(count) / log1p(max count)``, where ``count`` is an
    item's train-positive count (``counts``; missing = 0) and ``max count`` the largest count. The
    top ``k`` by ``score'`` (ties → smaller id) are returned. ``penalty = 0`` keeps the inner order.
    ``fit`` refits the inner path; the counts are fixed at construction. ``max_count`` overrides the
    normaliser's ``max count`` (default: the largest of ``counts``) — the feedback loop pins it to
    the round-0 maximum so the penalty scale stays fixed while the counts grow.
    """

    def __init__(
        self,
        path: Any,
        penalty: float,
        counts: Mapping[int, int],
        *,
        pool: int = 50,
        max_count: int | None = None,
    ) -> None:
        super().__init__(name="pop-penalized", version="1", _fitted=True)
        penalty = float(penalty)
        if not math.isfinite(penalty) or penalty < 0:
            raise ValueError(f"penalty must be finite and >= 0, got {penalty!r}")
        if not isinstance(pool, int) or isinstance(pool, bool) or pool <= 0:
            raise ValueError(f"pool must be a positive int, got {pool!r}")
        self.path = path
        self.penalty = penalty
        self.pool = pool
        self.counts = {int(item): int(count) for item, count in counts.items()}
        if max_count is None:
            max_count = max(self.counts.values(), default=0)
        self._max_log = math.log1p(max_count) if max_count > 0 else 1.0

    def fit(self, interactions: Any, catalog: Any | None = None) -> PopularityPenalizedPath:
        self.path.fit(interactions, catalog=catalog)
        return self

    def load(self, artifact: Any) -> PopularityPenalizedPath:
        raise NotImplementedError("pop-penalized is a stateless wrapper; load the inner path")

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
            raise ValueError(f"k must be a positive int, got {k!r}")
        pool = calibrate_scores(self.path.retrieve(query, context, max(self.pool, k)))
        rescored = [
            Candidate(
                c.item_id,
                c.score - self.penalty * math.log1p(self.counts.get(c.item_id, 0)) / self._max_log,
                self.name,
            )
            for c in pool
        ]
        return self._finish(rescored, k)


def popularity_penalized(
    path: Any,
    penalty: float,
    counts: Mapping[int, int],
    *,
    pool: int = 50,
    max_count: int | None = None,
) -> PopularityPenalizedPath:
    """Wrap ``path`` in a :class:`PopularityPenalizedPath` (the pinned U13 re-rank, pool 50)."""
    return PopularityPenalizedPath(path, penalty, counts, pool=pool, max_count=max_count)


# --------------------------------------------------------------------------------- feedback loops


@dataclass(frozen=True)
class RoundMetrics:
    """One round of :func:`simulate_feedback_loop`.

    ``coverage`` / ``head_share`` / ``gini`` / ``genre_entropy`` describe the round's served top-k
    lists (head frozen at round 0; Gini over the full catalog; genre entropy = mean per-list bits).
    ``clean_hit`` is the refit path's hit@k on the ORIGINAL val positives with the ORIGINAL train
    seen set. ``accepted`` counts the reads appended this round; ``new_rows`` holds them.
    """

    round: int
    coverage: float
    head_share: float
    gini: float
    genre_entropy: float
    clean_hit: float
    accepted: int
    new_rows: tuple[dict[str, Any], ...] = field(default=(), repr=False, compare=False)


def _positives(rows: Iterable[Mapping[str, Any]], known: set[int]) -> dict[str, dict[int, set]]:
    by_split: dict[str, dict[int, set[int]]] = {
        "train": defaultdict(set),
        "val": defaultdict(set),
        "test": defaultdict(set),
    }
    for row in rows:
        split = row["split"]
        if split not in by_split or int(row["label"]) != 1:
            continue
        item_id = int(row["item_id"])
        if item_id in known:
            by_split[split][int(row["reader_id"])].add(item_id)
    return by_split


def val_cohort(
    rows: Iterable[Mapping[str, Any]],
    catalog_ids: Iterable[int],
    cold_readers: Iterable[int] = (),
) -> list[int]:
    """The scoreboard's val cohort: readers with an unseen val positive, cold readers excluded.

    Matches :func:`~bookrec.scoreboard.run_validation_scoreboard`'s eligibility exactly (ascending).
    """
    positives = _positives(rows, {int(i) for i in catalog_ids})
    cold = {int(r) for r in cold_readers}
    train, val = positives["train"], positives["val"]
    return [r for r in sorted(val) if r not in cold and (val[r] - train.get(r, set()))]


def _top_ids(path: Any, reader: int, seen: set[int], k: int) -> list[int]:
    """The reader's ranked top-``k`` ids; a path emitting one item twice is an error, not deduped."""
    top = [c.item_id for c in rank(path.retrieve(reader, {"seen": seen}, k), n=k, exclude=seen)]
    if len(set(top)) != len(top):
        raise ValueError(f"path {getattr(path, 'name', path)!r} returned duplicate items: {top}")
    return top


def simulate_feedback_loop(
    path_factory: Callable[[], Any],
    rows: Iterable[Mapping[str, Any]],
    *,
    cohort: Sequence[int],
    catalog: Mapping[int, Book],
    seed: int,
    rounds: int = 6,
    k: int = 10,
    accept_prob: float = 0.3,
    mitigation: str | None = None,
    penalty: float = 0.3,
    pool: int = 50,
) -> list[RoundMetrics]:
    """Retrain a path on its own recommendations and measure exposure each round (plan recsys-016).

    Pinned semantics (rounds ``0..rounds``; round 0 is the path fit on the original log):

    1. ``path_factory()`` is fit on the **augmented train log** — the original ``split == "train"``
       rows plus every simulated row so far. No original val/test row ever reaches ``fit``.
    2. Each ``cohort`` reader (fixed for all rounds) gets a top-``k`` excluding its *augmented* seen
       set (original train positives + its simulated reads).
    3. (plan v2.5) **Each** of the reader's top-``k`` items is accepted **independently** with
       probability ``accept_prob`` (a per-item Bernoulli; about ``k·p`` reads per reader per round),
       provided it is unseen **and not among the reader's val/test positives** (the **leakage
       guard**: never hand the model a held-out answer).
    4. Each read is appended as ``{split: "train", label: 1, session_id: -1}`` with a timestamp
       after the reader's latest train timestamp; never a duplicate (the seen set grows).

    Readouts per round (:class:`RoundMetrics`): coverage, head-share (head = top 10% by ORIGINAL
    train count, frozen at round 0), exposure Gini (full catalog) and mean genre entropy of the
    served lists; and **clean hit@k** — the refit (unmitigated) path scored on the ORIGINAL val
    positives with the ORIGINAL train seen set, so a growing seen set cannot move the accuracy
    readout for a bookkeeping reason.

    ``mitigation`` changes what is *served* (and so what can be read): ``"explore"`` replaces the last
    served slot with a seeded random warm (original train count > 0) item the reader has not seen and that
    is not already in the list; ``"penalty"`` serves a :class:`PopularityPenalizedPath` re-rank
    (``penalty``, ``pool``) using the current augmented train counts, normalised by the round-0 max
    count. ``rows`` is never mutated. Deterministic for a given ``seed``: one generator
    ``default_rng(seed)`` first draws the readers' processing order (a seeded permutation of the
    sorted ``cohort``), then, per reader, the exploration item (``rng.choice`` over the round-0 warm
    items in ascending id order, minus the reader's seen set and current list) and one acceptance
    draw per served slot in rank order (drawn before the guards) — the exact draw protocol of the
    plan-gate probe (plan v2.6), so its measured numbers reproduce. The exploration item replaces
    the last slot whenever the list is non-empty, even a short one (it is never appended).
    """
    if mitigation not in (None, "explore", "penalty"):
        raise ValueError(f"mitigation must be None, 'explore' or 'penalty', got {mitigation!r}")
    if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds < 0:
        raise ValueError(f"rounds must be a non-negative int, got {rounds!r}")
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    if not 0.0 <= float(accept_prob) <= 1.0:
        raise ValueError(f"accept_prob must be in [0, 1], got {accept_prob!r}")

    rows = list(rows)
    catalog_ids = sorted(int(i) for i in catalog)
    known = set(catalog_ids)
    positives = _positives(rows, known)
    seen0 = positives["train"]
    held_out: dict[int, set[int]] = defaultdict(set)
    for split in ("val", "test"):
        for reader, items in positives[split].items():
            held_out[reader] |= items

    train_log: list[Mapping[str, Any]] = [row for row in rows if row["split"] == "train"]
    last_time: dict[int, int] = {}
    counts: dict[int, int] = defaultdict(int)
    for row in train_log:
        reader = int(row["reader_id"])
        stamp = row.get("timestamp")
        if stamp not in (None, ""):
            last_time[reader] = max(last_time.get(reader, int(stamp)), int(stamp))
        if int(row["label"]) == 1 and int(row["item_id"]) in known:
            counts[int(row["item_id"])] += 1
    head = set(head_ids_from_counts(counts, catalog_ids))
    warm = sorted(counts)

    rng = np.random.default_rng(seed)
    cohort_ids = sorted(int(r) for r in cohort)
    readers = (
        [int(r) for r in rng.choice(cohort_ids, size=len(cohort_ids), replace=False)]
        if cohort_ids
        else []
    )
    seen = {r: set(seen0.get(r, set())) for r in readers}
    max_count0 = max(counts.values(), default=0)

    results: list[RoundMetrics] = []
    for round_no in range(rounds + 1):
        path = path_factory()
        path.fit(train_log, catalog=catalog_ids)
        served_path = path
        if mitigation == "penalty":
            served_path = PopularityPenalizedPath(
                path, penalty, counts, pool=pool, max_count=max_count0
            )

        served: dict[int, list[int]] = {}
        clean_hits: list[float] = []
        new_rows: list[dict[str, Any]] = []
        for reader in readers:
            reader_seen = seen[reader]
            top = _top_ids(served_path, reader, reader_seen, k)
            if mitigation == "explore":
                shown = set(top)
                options = [i for i in warm if i not in reader_seen and i not in shown]
                if top and options:
                    # Replace the LAST served slot (even on a short list; never append).
                    top[-1] = int(rng.choice(options))
            served[reader] = top

            relevant = positives["val"].get(reader, set()) - seen0.get(reader, set())
            if relevant:
                clean = top if round_no == 0 and mitigation is None else None
                if clean is None:
                    original_seen = seen0.get(reader, set())
                    clean = _top_ids(path, reader, original_seen, k)
                clean_hits.append(1.0 if set(clean) & relevant else 0.0)

            guard = held_out.get(reader, set())
            for item in top:
                # One draw per served slot (drawn first, as in the probe), then the guards.
                if rng.random() < accept_prob and item not in reader_seen and item not in guard:
                    stamp = last_time.get(reader, 0) + 1
                    last_time[reader] = stamp
                    new_rows.append(
                        {
                            "reader_id": reader,
                            "item_id": int(item),
                            "session_id": -1,
                            "timestamp": stamp,
                            "split": "train",
                            "label": 1,
                        }
                    )
                    reader_seen.add(int(item))

        lists = list(served.values())
        results.append(
            RoundMetrics(
                round=round_no,
                coverage=catalog_coverage(lists, catalog_ids),
                head_share=head_share(lists, head),
                gini=exposure_gini(lists, catalog_ids),
                genre_entropy=float(np.mean([genre_entropy(t, catalog) for t in lists]))
                if lists
                else 0.0,
                clean_hit=float(np.mean(clean_hits)) if clean_hits else 0.0,
                accepted=len(new_rows),
                new_rows=tuple(new_rows),
            )
        )
        train_log.extend(new_rows)
        for new in new_rows:
            counts[int(new["item_id"])] += 1
    return results

"""Seeded series + session-log generator for U12 (design 011 §6 "Session log for U12", plan recsys-014).

The main interaction log's sequential signal is order-insensitive, so Unit 12 (sequence-aware
retrieval) gets a **separate** seeded session log over the same catalog. Two artifacts:

``series.csv.gz`` — ``item_id, series_id, volume`` (a catalog-side observable)
    About ``series_fraction`` of catalog books grouped into **same-author** series of
    ``series_len_min..series_len_max`` volumes, numbered ``1..L`` in ``(year, item_id)`` order.
    One series per book; books outside every series have no row. U12 uses it for diagnostics only
    (next-in-series hit rate), not as a model input unless it is taught. Drawn on
    ``SUBSTREAM_SERIES`` at the committed ``seed`` (never the session seed).

``sessions.csv.gz`` — ``reader_id, item_id, session_id, timestamp, split, label``
    The **same 6-column schema** as ``interactions.csv.gz``, over its **own** synthetic reader
    population (``session_n_readers``; ids ``0..n-1`` are NOT the main-log readers). Exposure has
    the main log's taste-aware form ``popularity**α · exp(β · z_u(affinity))`` over **non-cold**
    items only (``cold_items`` are never exposed — U12 needs no cold machinery), plus three
    **order mechanisms**:

    1. *forced next-volume slot* — after a positive on volume ``v``, volume ``v+1`` takes the first
       exposure slot of each of the next ``session_series_window`` sessions with probability
       ``session_series_follow_prob`` until read, with acceptance boost ``session_series_accept``;
    2. *decaying author-follow* — each positive adds ``session_author_bump`` to the exposure logit
       and the acceptance score of that author's books, decaying ×``session_author_decay`` per
       session;
    3. *persistent genre mood* — a per-session mood genre (drawn from the reader's genre prefs),
       kept with probability ``session_mood_persist``, adding ``session_mood_boost`` × genre
       membership to the exposure logit.

    Acceptance mirrors the main log: ``sigmoid(T · (score − threshold))`` where ``score`` is the
    reader's true affinity plus the boosts above (affinity units, like ``author_follow_boost``).
    Each positive draws ``session_negatives_per_positive`` exposure-weighted negatives at the same
    timestamp. Session timestamps strictly increase per reader; the split is per reader **by
    session** (``train < val < test``; test is sealed). Rows are written reader by reader in event
    order, so ``(timestamp, file row order)`` is the canonical ordering key.

Both artifacts draw only from named ``SeedSequence`` sub-streams (``SUBSTREAM_SERIES``,
``SUBSTREAM_SESSIONS``) — no function here takes an ``rng`` — so the threaded catalog/interaction
stream and the four byte-pinned main artifacts cannot move. ``session_seed`` re-draws only the
session log over the fixed catalog. Nothing is committed: output lands in the gitignored
``recsys/data/generated/`` via ``gen_interactions.py``'s single CLI.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:  # script vs. package-relative import
    from _common import (
        GENERATED_DIR,
        SUBSTREAM_SERIES,
        SUBSTREAM_SESSIONS,
        DatasetConfig,
        Manifest,
        substream_rng,
        write_gzip_csv,
    )
    from gen_catalog import Catalog
except ImportError:  # pragma: no cover - exercised only as a module
    from recsys.data._common import (  # type: ignore[no-redef]
        GENERATED_DIR,
        SUBSTREAM_SERIES,
        SUBSTREAM_SESSIONS,
        DatasetConfig,
        Manifest,
        substream_rng,
        write_gzip_csv,
    )
    from recsys.data.gen_catalog import Catalog  # type: ignore[no-redef]

SERIES_COLUMNS = ["item_id", "series_id", "volume"]
SESSION_COLUMNS = ["reader_id", "item_id", "session_id", "timestamp", "split", "label"]
SPLITS = ("train", "val", "test")


@dataclass
class Series:
    """Same-author book series. Arrays are aligned rows of ``series.csv.gz``."""

    item_ids: np.ndarray  # (n_series_books,) int, rows sorted by (series_id, volume)
    series_ids: np.ndarray  # (n_series_books,) int, 0..n_series-1
    volumes: np.ndarray  # (n_series_books,) int, 1..L within each series
    n_books: int  # catalog size (for the dense lookups below)
    seed: int  # the dataset seed the grouping was drawn under

    @property
    def n_series(self) -> int:
        return int(self.series_ids.max()) + 1 if self.series_ids.size else 0

    def next_volume(self) -> np.ndarray:
        """Dense ``(n_books,)`` map: the item id of volume ``v+1`` of the same series, else ``-1``."""
        nxt = -np.ones(self.n_books, dtype=np.int64)
        for k in range(self.item_ids.shape[0] - 1):
            if self.series_ids[k] == self.series_ids[k + 1]:
                nxt[self.item_ids[k]] = self.item_ids[k + 1]
        return nxt

    def rows(self):
        for item, sid, vol in zip(self.item_ids, self.series_ids, self.volumes):
            yield [int(item), int(sid), int(vol)]


def generate_series(catalog: Catalog, config: DatasetConfig) -> Series:
    """Group ~``series_fraction`` of the catalog into same-author series (``SUBSTREAM_SERIES``).

    Authors with at least ``series_len_min`` books are visited in a seeded random order; from each,
    series of a random length in ``[series_len_min, series_len_max]`` (capped by the author's
    remaining books) are cut from a random subset of that author's books until the target count is
    reached. Volumes are numbered ``1..L`` by ``(year, item_id)``.
    """
    rng = substream_rng(config.seed, SUBSTREAM_SERIES)
    lo, hi = config.series_len_min, config.series_len_max
    target = round(config.series_fraction * catalog.n_books)

    by_author: dict[int, list[int]] = {}
    for item in range(catalog.n_books):
        by_author.setdefault(int(catalog.author_ids[item]), []).append(item)
    authors = sorted(a for a, books in by_author.items() if len(books) >= lo)
    order = rng.permutation(len(authors))

    groups: list[list[int]] = []
    covered = 0
    for idx in order:
        if covered >= target:
            break
        remaining = list(by_author[authors[int(idx)]])
        while len(remaining) >= lo and covered < target:
            length = min(int(rng.integers(lo, hi + 1)), len(remaining))
            picked = rng.choice(np.array(remaining), size=length, replace=False).tolist()
            picked.sort(key=lambda b: (int(catalog.years[b]), int(b)))
            groups.append([int(b) for b in picked])
            covered += length
            chosen = set(picked)
            remaining = [b for b in remaining if b not in chosen]

    item_ids, series_ids, volumes = [], [], []
    for sid, members in enumerate(groups):
        for vol, item in enumerate(members, start=1):
            item_ids.append(item)
            series_ids.append(sid)
            volumes.append(vol)
    return Series(
        item_ids=np.array(item_ids, dtype=np.int64),
        series_ids=np.array(series_ids, dtype=np.int64),
        volumes=np.array(volumes, dtype=np.int64),
        n_books=catalog.n_books,
        seed=config.seed,
    )


def write_series(series: Series, out_dir: Path = GENERATED_DIR) -> Manifest:
    """Write ``series.csv.gz`` and return its manifest."""
    path = out_dir / "series.csv.gz"
    digest = write_gzip_csv(path, SERIES_COLUMNS, series.rows())
    return Manifest(
        source="synthetic:gen_sessions.series",
        version="1",
        config={"seed": series.seed},
        rowcounts={"series_books": int(series.item_ids.shape[0]), "series": series.n_series},
        schema={"series.csv.gz": SERIES_COLUMNS},
        checksums={"series.csv.gz": digest},
    )


@dataclass
class SessionLog:
    """The U12 session log (same schema as the main interaction log) plus its reader ground-truth."""

    reader_ids: np.ndarray
    item_ids: np.ndarray
    session_ids: np.ndarray
    timestamps: np.ndarray
    splits: np.ndarray  # dtype '<U5': train/val/test
    labels: np.ndarray  # int 0/1
    reader_latent: np.ndarray  # (session_n_readers, latent_dim)
    reader_prefs: np.ndarray  # (session_n_readers, n_genres)
    cold_items: np.ndarray  # never exposed in this log
    config: DatasetConfig

    @property
    def n_events(self) -> int:
        return int(self.reader_ids.shape[0])

    def rows(self):
        for i in range(self.n_events):
            yield [
                int(self.reader_ids[i]),
                int(self.item_ids[i]),
                int(self.session_ids[i]),
                int(self.timestamps[i]),
                str(self.splits[i]),
                int(self.labels[i]),
            ]


def _split_for_session(session_index: int, n_sessions: int, config: DatasetConfig) -> str:
    n_test = max(1, round(config.test_fraction * n_sessions))
    n_val = max(1, round(config.val_fraction * n_sessions))
    n_train = n_sessions - n_val - n_test
    if session_index < n_train:
        return "train"
    if session_index < n_train + n_val:
        return "val"
    return "test"


def generate_sessions(
    catalog: Catalog, series: Series, cold_items: np.ndarray, config: DatasetConfig
) -> SessionLog:
    """Generate the U12 session log on ``SUBSTREAM_SESSIONS`` (seeded by ``effective_session_seed``)."""
    rng = substream_rng(config.effective_session_seed, SUBSTREAM_SESSIONS)
    n_readers, n_books = config.session_n_readers, catalog.n_books
    n_genres = catalog.genre_matrix.shape[1]
    reader_latent = rng.normal(0, 1.0, size=(n_readers, catalog.latent.shape[1]))
    reader_prefs = rng.dirichlet(np.ones(n_genres), size=n_readers)

    warm = np.ones(n_books, dtype=bool)
    warm[np.asarray(cold_items, dtype=np.int64)] = False
    warm_ids = np.nonzero(warm)[0]
    next_vol = series.next_volume()
    next_vol[next_vol >= 0] = np.where(warm[next_vol[next_vol >= 0]], next_vol[next_vol >= 0], -1)

    affinity = reader_latent @ catalog.latent.T + config.feature_weight * (
        reader_prefs @ catalog.genre_matrix.T
    )  # (n_readers, n_books)
    aw = affinity[:, warm_ids]
    z = (affinity - aw.mean(axis=1, keepdims=True)) / np.maximum(
        aw.std(axis=1, keepdims=True), 1e-9
    )
    log_pop = config.popularity_exposure_weight * np.log(catalog.popularity)
    beta = config.exposure_affinity_weight
    temp, threshold = config.logit_temperature, config.positive_threshold
    author_books = {
        a: np.nonzero(catalog.author_ids == a)[0] for a in np.unique(catalog.author_ids)
    }

    reader_ids: list[int] = []
    item_ids: list[int] = []
    session_ids: list[int] = []
    timestamps: list[int] = []
    splits: list[str] = []
    labels: list[int] = []

    for u in range(n_readers):
        n_sessions = max(
            config.session_min_sessions, int(rng.poisson(config.session_mean_sessions))
        )
        clock = int(rng.integers(0, 100))
        base_logit = (log_pop + beta * z[u])[warm_ids]  # time-invariant exposure logit (warm)
        author_bonus = np.zeros(n_books)
        pending: dict[int, int] = {}  # next-volume item -> last session its forced slot applies
        read: set[int] = set()
        mood = int(rng.choice(n_genres, p=reader_prefs[u]))
        for s in range(n_sessions):
            clock += int(rng.integers(1, 30))
            split = _split_for_session(s, n_sessions, config)
            if rng.random() >= config.session_mood_persist:
                mood = int(rng.choice(n_genres, p=reader_prefs[u]))
            author_bonus *= config.session_author_decay
            pending = {item: last for item, last in pending.items() if last >= s}

            logit = (
                base_logit
                + author_bonus[warm_ids]
                + config.session_mood_boost * catalog.genre_matrix[warm_ids, mood]
            )
            probs = np.exp(logit - logit.max())
            probs /= probs.sum()
            n_slots = int(rng.integers(1, config.session_max_items + 1))
            exposed = [
                int(i)
                for i in warm_ids[
                    rng.choice(warm_ids.shape[0], size=n_slots, replace=False, p=probs)
                ]
            ]
            if pending and rng.random() < config.session_series_follow_prob:
                forced = sorted(pending)[int(rng.integers(0, len(pending)))]
                exposed = [forced] + [i for i in exposed if i != forced][: n_slots - 1]

            for item in exposed:
                clock += 1
                score = affinity[u, item] + author_bonus[item]
                if item in pending:
                    score += config.session_series_accept
                is_positive = rng.random() < 1.0 / (1.0 + np.exp(-temp * (score - threshold)))
                reader_ids.append(u)
                item_ids.append(item)
                session_ids.append(s)
                timestamps.append(clock)
                splits.append(split)
                labels.append(1 if is_positive else 0)
                if not is_positive:
                    continue
                read.add(item)
                pending.pop(item, None)
                author_bonus[author_books[int(catalog.author_ids[item])]] += (
                    config.session_author_bump
                )
                nxt = int(next_vol[item])
                if nxt >= 0 and nxt not in read:
                    pending[nxt] = s + config.session_series_window
                for _ in range(config.session_negatives_per_positive):
                    neg = int(warm_ids[rng.choice(warm_ids.shape[0], p=probs)])
                    if neg == item:
                        continue
                    reader_ids.append(u)
                    item_ids.append(neg)
                    session_ids.append(s)
                    timestamps.append(clock)
                    splits.append(split)
                    labels.append(0)

    return SessionLog(
        reader_ids=np.array(reader_ids, dtype=np.int64),
        item_ids=np.array(item_ids, dtype=np.int64),
        session_ids=np.array(session_ids, dtype=np.int64),
        timestamps=np.array(timestamps, dtype=np.int64),
        splits=np.array(splits, dtype="<U5"),
        labels=np.array(labels, dtype=np.int64),
        reader_latent=reader_latent,
        reader_prefs=reader_prefs,
        cold_items=np.asarray(cold_items, dtype=np.int64),
        config=config,
    )


def write_sessions(log: SessionLog, out_dir: Path = GENERATED_DIR) -> Manifest:
    """Write ``sessions.csv.gz`` (the U12 session log) and return its manifest."""
    path = out_dir / "sessions.csv.gz"
    digest = write_gzip_csv(path, SESSION_COLUMNS, log.rows())
    return Manifest(
        source="synthetic:gen_sessions.sessions",
        version="1",
        config={
            "seed": log.config.effective_session_seed,
            "session_n_readers": log.config.session_n_readers,
        },
        rowcounts={"sessions": log.n_events, "positives": int(log.labels.sum())},
        schema={"sessions.csv.gz": SESSION_COLUMNS},
        checksums={"sessions.csv.gz": digest},
        notes={"splits": list(SPLITS), "cold_items": "excluded from exposure"},
    )

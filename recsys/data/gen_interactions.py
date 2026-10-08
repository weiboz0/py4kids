"""Seeded interaction generator (design 011 §6) — a reader x book log with exposed ground-truth.

Implements the design §6 signal table so the synthetic log can drive every unit:

- **low-rank latent taste** — reader/book latent factors (U5 MF, U8 two-tower);
- **feature-derived taste** — reader genre preferences over the catalog genre matrix (U3/U7/U9);
- **popularity bias** — a heavy-tailed, popularity-weighted exposure process (U2, U13);
- **timestamps + ordered sessions + author-following + taste drift** — a per-reader event timeline
  with a monotone timestamp and an author-follow bonus (U12 sequence model);
- **implicit positives + exposure + sampled negatives** — exposed items become implicit positives
  by a calibrated probability; extra negatives are sampled per positive (U4, U8-U9 training);
- **cold items / cold readers + leakage-safe temporal splits** — held-out cold partitions and a
  per-reader ``train < val < test`` split by event time (U6 eval, U9, U13).

**U12 uses a separate session log.** This log's sequence signal is order-insensitive (plan
recsys-014 probe), so the U12 sequence model is scored on ``sessions.csv.gz`` (+ ``series.csv.gz``)
from ``gen_sessions.py``. :func:`write_generated_dataset` writes those too, from independent
sub-streams, so this module's outputs stay byte-identical.

**Exposed ground-truth.** The returned object exposes the base affinity (reader latent . book
latent + feature affinity) that positives are drawn from, so tests verify observed positives are
enriched against it. Latent factors are not identifiable, so only scores/rankings are checked.

Nothing is committed — output lands in the gitignored ``recsys/data/generated/``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:  # script vs. package-relative import
    from _common import GENERATED_DIR, DatasetConfig, Manifest, checksum, write_gzip_csv
    from gen_catalog import (
        Catalog,
        generate_catalog,
        generate_keywords,
        write_catalog,
        write_keywords,
    )
    from gen_sessions import generate_series, generate_sessions, write_series, write_sessions
except ImportError:  # pragma: no cover - exercised only as a module
    from recsys.data._common import (  # type: ignore[no-redef]
        GENERATED_DIR,
        DatasetConfig,
        Manifest,
        checksum,
        write_gzip_csv,
    )
    from recsys.data.gen_catalog import (  # type: ignore[no-redef]
        Catalog,
        generate_catalog,
        generate_keywords,
        write_catalog,
        write_keywords,
    )
    from recsys.data.gen_sessions import (  # type: ignore[no-redef]
        generate_series,
        generate_sessions,
        write_series,
        write_sessions,
    )

INTERACTION_COLUMNS = ["reader_id", "item_id", "session_id", "timestamp", "split", "label"]
SPLITS = ("train", "val", "test")


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


@dataclass
class Interactions:
    """The generated event log plus the exposed latent ground-truth."""

    reader_ids: np.ndarray
    item_ids: np.ndarray
    session_ids: np.ndarray
    timestamps: np.ndarray
    splits: np.ndarray  # dtype '<U5': train/val/test
    labels: np.ndarray  # int 0/1
    reader_latent: np.ndarray  # (n_readers, dim)
    reader_prefs: np.ndarray  # (n_readers, n_genres)
    cold_items: np.ndarray
    cold_readers: np.ndarray
    catalog: Catalog
    config: DatasetConfig
    affinity_matrix: np.ndarray  # (n_readers, n_books) exposed true affinity (ground truth)

    @property
    def n_events(self) -> int:
        return int(self.reader_ids.shape[0])

    def affinity(self, reader_id: int, item_ids: np.ndarray) -> np.ndarray:
        """Base (time-invariant) true affinity of a reader for items — the ground-truth signal."""
        latent_term = self.catalog.latent[item_ids] @ self.reader_latent[reader_id]
        feature_term = self.catalog.genre_matrix[item_ids] @ self.reader_prefs[reader_id]
        return latent_term + self.config.feature_weight * feature_term

    def observation_propensity(self) -> np.ndarray:
        """The generator's exposure log-propensity ``α·log pop + β·z_u(affinity)`` (n_readers, n_books).

        This is the ground-truth exposure process — the recoverability harness's sanity *ceiling*
        (ranking by it recovers what the generator actually exposed, not just true taste).
        """
        a = self.affinity_matrix
        z = (a - a.mean(axis=1, keepdims=True)) / np.maximum(a.std(axis=1, keepdims=True), 1e-9)
        alpha = self.config.popularity_exposure_weight
        beta = self.config.exposure_affinity_weight
        return alpha * np.log(self.catalog.popularity)[None, :] + beta * z

    def mask(self, split: str | None = None, label: int | None = None) -> np.ndarray:
        keep = np.ones(self.n_events, dtype=bool)
        if split is not None:
            keep &= self.splits == split
        if label is not None:
            keep &= self.labels == label
        return keep

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


def generate_interactions(
    catalog: Catalog, config: DatasetConfig, rng: np.random.Generator
) -> Interactions:
    """Generate the event log from a threaded ``rng`` (continues the catalog's stream)."""
    n_readers, dim = config.n_readers, config.latent_dim
    reader_latent = rng.normal(0, 1.0, size=(n_readers, dim))
    reader_prefs = rng.dirichlet(np.ones(config.n_genres), size=n_readers)
    drift_dir = rng.normal(0, 1.0, size=(n_readers, dim))

    cold_items = np.sort(rng.choice(catalog.n_books, size=config.n_cold_items, replace=False))
    cold_readers = np.sort(rng.choice(n_readers, size=config.n_cold_readers, replace=False))
    cold_reader_set = set(cold_readers.tolist())

    n_books = catalog.n_books
    warm_mask = np.ones(n_books, dtype=bool)
    warm_mask[cold_items] = False

    # --- Taste-aware exposure (plan recsys-004) --------------------------------------------------
    # exposure(u, i) ∝ popularity(i)**α · exp(β · z_u(affinity(u, i))), with z_u the per-reader
    # standardisation of affinity. affinity = reader·item latent + feature_weight·(genre pref). The
    # popularity term keeps popularity a strong baseline; the z-scored affinity term makes content/
    # collaborative/latent taste recoverable above it. α=popularity_exposure_weight, β=exposure_
    # affinity_weight. author_exposure_recur makes a read raise the same author's exposure later.
    alpha = config.popularity_exposure_weight
    beta = config.exposure_affinity_weight
    affinity = reader_latent @ catalog.latent.T + config.feature_weight * (
        reader_prefs @ catalog.genre_matrix.T
    )  # (n_readers, n_books), the exposed ground-truth affinity
    z_affinity = (affinity - affinity.mean(axis=1, keepdims=True)) / np.maximum(
        affinity.std(axis=1, keepdims=True), 1e-9
    )
    log_pop = alpha * np.log(catalog.popularity)  # (n_books,)

    reader_ids: list[int] = []
    item_ids: list[int] = []
    session_ids: list[int] = []
    timestamps: list[int] = []
    splits: list[str] = []
    labels: list[int] = []

    for u in range(n_readers):
        is_cold_reader = u in cold_reader_set
        n_sessions = max(4, int(rng.poisson(config.mean_sessions_per_reader)))
        clock = int(rng.integers(0, 100))
        liked_authors: set[int] = set()
        base_logit = log_pop + beta * z_affinity[u]  # (n_books,) time-invariant exposure logit
        author_bonus = np.zeros(n_books)  # recurs across sessions as the reader reads authors
        for s in range(n_sessions):
            clock += int(rng.integers(1, 30))
            split = "test" if is_cold_reader else _split_for_session(s, n_sessions, config)
            logit = base_logit + author_bonus
            if split != "test":  # warm splits may not expose held-out cold items
                logit = np.where(warm_mask, logit, -np.inf)
            finite = np.isfinite(logit)
            probs_all = np.zeros(n_books)
            probs_all[finite] = np.exp(logit[finite] - logit[finite].max())
            probs_all /= probs_all.sum()
            drifted = reader_latent[u] + config.drift_scale * s * drift_dir[u]
            n_slots = int(rng.integers(1, config.max_items_per_session + 1))
            exposed = rng.choice(n_books, size=n_slots, replace=False, p=probs_all)
            for item in exposed:
                item = int(item)
                clock += 1
                base = (
                    catalog.latent[item] @ drifted
                    + config.feature_weight * (catalog.genre_matrix[item] @ reader_prefs[u])
                )
                if catalog.author_ids[item] in liked_authors:
                    base += config.author_follow_boost
                prob = _sigmoid(config.logit_temperature * (base - config.positive_threshold))
                is_positive = rng.random() < prob
                reader_ids.append(u)
                item_ids.append(item)
                session_ids.append(s)
                timestamps.append(clock)
                splits.append(split)
                labels.append(1 if is_positive else 0)
                if is_positive:
                    liked_authors.add(int(catalog.author_ids[item]))
                    # Author-follow recurs: raise this author's exposure in later sessions.
                    author_bonus[catalog.author_ids == catalog.author_ids[item]] += (
                        config.author_exposure_recur
                    )
                    for _ in range(config.negatives_per_positive):
                        neg = int(rng.choice(n_books, p=probs_all))
                        if neg == item:
                            continue
                        reader_ids.append(u)
                        item_ids.append(neg)
                        session_ids.append(s)
                        timestamps.append(clock)
                        splits.append(split)
                        labels.append(0)

    return Interactions(
        reader_ids=np.array(reader_ids, dtype=np.int64),
        item_ids=np.array(item_ids, dtype=np.int64),
        session_ids=np.array(session_ids, dtype=np.int64),
        timestamps=np.array(timestamps, dtype=np.int64),
        splits=np.array(splits, dtype="<U5"),
        labels=np.array(labels, dtype=np.int64),
        reader_latent=reader_latent,
        reader_prefs=reader_prefs,
        cold_items=cold_items,
        cold_readers=cold_readers,
        catalog=catalog,
        config=config,
        affinity_matrix=affinity,
    )


def write_interactions(inter: Interactions, out_dir: Path = GENERATED_DIR) -> Manifest:
    """Write the interaction CSV and return its manifest (§6 provenance record)."""
    path = out_dir / "interactions.csv.gz"
    digest = write_gzip_csv(path, INTERACTION_COLUMNS, inter.rows())
    return Manifest(
        source="synthetic:gen_interactions",
        version="1",
        config={"seed": inter.config.seed, "n_readers": inter.config.n_readers},
        rowcounts={
            "interactions": inter.n_events,
            "positives": int(inter.labels.sum()),
            "cold_items": int(inter.cold_items.shape[0]),
            "cold_readers": int(inter.cold_readers.shape[0]),
        },
        schema={"interactions.csv.gz": INTERACTION_COLUMNS},
        checksums={"interactions.csv.gz": digest},
        notes={"splits": list(SPLITS), "ground_truth": "regenerate from seed for latent factors"},
    )


def write_generated_dataset(inter: Interactions, out_dir: Path = GENERATED_DIR) -> None:
    """Persist the complete generated dataset plus cold partitions and exact-byte checksums.

    Also writes the U12 ``series.csv.gz`` + ``sessions.csv.gz`` (plan recsys-014). They draw only
    from their own ``SeedSequence`` sub-streams, so the four main artifacts are byte-identical.
    """
    catalog_manifest = write_catalog(inter.catalog, out_dir)
    keyword_manifest = write_keywords(generate_keywords(inter.catalog, inter.config), out_dir)
    interaction_manifest = write_interactions(inter, out_dir)
    series = generate_series(inter.catalog, inter.config)
    series_manifest = write_series(series, out_dir)
    session_manifest = write_sessions(
        generate_sessions(inter.catalog, series, inter.cold_items, inter.config), out_dir
    )

    cold_path = out_dir / "cold_partitions.json"
    cold_path.write_text(
        json.dumps(
            {
                "cold_items": inter.cold_items.tolist(),
                "cold_readers": inter.cold_readers.tolist(),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    checksums = {
        **catalog_manifest.checksums,
        **keyword_manifest.checksums,
        **interaction_manifest.checksums,
        **series_manifest.checksums,
        **session_manifest.checksums,
        cold_path.name: checksum(cold_path),
    }
    (out_dir / "checksums.json").write_text(
        json.dumps(checksums, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def build_dataset(config: DatasetConfig | None = None) -> Interactions:
    """Generate the whole dataset from one threaded rng (catalog then interactions)."""
    config = config or DatasetConfig()
    rng = np.random.default_rng(config.seed)
    catalog = generate_catalog(config, rng)
    return generate_interactions(catalog, config, rng)


def main() -> None:
    config = DatasetConfig()
    rng = np.random.default_rng(config.seed)
    catalog = generate_catalog(config, rng)
    inter = generate_interactions(catalog, config, rng)
    write_generated_dataset(inter)
    print(
        f"interactions: {inter.n_events} events "
        f"({int(inter.labels.sum())} positives) -> {GENERATED_DIR / 'interactions.csv.gz'}"
    )
    print(f"sha256: {checksum(GENERATED_DIR / 'interactions.csv.gz')}")


if __name__ == "__main__":
    main()

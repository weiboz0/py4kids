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

**Exposed ground-truth.** The returned object exposes the base affinity (reader latent . book
latent + feature affinity) that positives are drawn from, so tests verify observed positives are
enriched against it. Latent factors are not identifiable, so only scores/rankings are checked.

Nothing is committed — output lands in the gitignored ``recsys/data/generated/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:  # script vs. package-relative import
    from _common import GENERATED_DIR, DatasetConfig, Manifest, write_gzip_csv
    from gen_catalog import Catalog, generate_catalog, write_catalog
except ImportError:  # pragma: no cover - exercised only as a module
    from recsys.data._common import (  # type: ignore[no-redef]
        GENERATED_DIR,
        DatasetConfig,
        Manifest,
        write_gzip_csv,
    )
    from recsys.data.gen_catalog import (  # type: ignore[no-redef]
        Catalog,
        generate_catalog,
        write_catalog,
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

    @property
    def n_events(self) -> int:
        return int(self.reader_ids.shape[0])

    def affinity(self, reader_id: int, item_ids: np.ndarray) -> np.ndarray:
        """Base (time-invariant) true affinity of a reader for items — the ground-truth signal."""
        latent_term = self.catalog.latent[item_ids] @ self.reader_latent[reader_id]
        feature_term = self.catalog.genre_matrix[item_ids] @ self.reader_prefs[reader_id]
        return latent_term + self.config.feature_weight * feature_term

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
    cold_item_set = set(cold_items.tolist())
    cold_reader_set = set(cold_readers.tolist())

    all_items = catalog.item_ids
    warm_items = np.array([i for i in all_items if i not in cold_item_set], dtype=np.int64)
    # Popularity-biased exposure, tunable by ``popularity_exposure_weight``: exposure ∝
    # popularity ** weight. weight=1 (default) is raw-popularity exposure; weight=0 flattens to
    # uniform exposure; weight>1 sharpens the head. The knob is live, matching the §6 signal table.
    pop = catalog.popularity ** config.popularity_exposure_weight
    warm_prob = pop[warm_items] / pop[warm_items].sum()
    all_prob = pop / pop.sum()

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
        for s in range(n_sessions):
            clock += int(rng.integers(1, 30))
            split = "test" if is_cold_reader else _split_for_session(s, n_sessions, config)
            pool = all_items if split == "test" else warm_items
            probs = all_prob if split == "test" else warm_prob
            drifted = reader_latent[u] + config.drift_scale * s * drift_dir[u]
            n_slots = int(rng.integers(1, config.max_items_per_session + 1))
            exposed = rng.choice(pool, size=n_slots, replace=False, p=probs)
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
                    for _ in range(config.negatives_per_positive):
                        neg = int(rng.choice(pool, p=probs))
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
    write_catalog(catalog)
    manifest = write_interactions(inter)
    print(
        f"interactions: {inter.n_events} events "
        f"({int(inter.labels.sum())} positives) -> {GENERATED_DIR / 'interactions.csv.gz'}"
    )
    print(f"sha256: {manifest.checksums['interactions.csv.gz']}")


if __name__ == "__main__":
    main()

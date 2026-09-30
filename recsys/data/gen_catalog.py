"""Seeded catalog generator (design 011 §6) — a synthetic book catalog with exposed structure.

Produces, for stable integer item ids ``0 .. n_books-1``:

- surface metadata (title, author id, genres, year) written to a gzip'd CSV;
- the latent structure that drives reader taste, **exposed as ground-truth**: a low-rank latent
  factor per book (for MF / two-tower recovery), a genre-membership matrix (content features), and
  a heavy-tailed popularity base (popularity bias / exposure).

Latent factors are not identifiable (rotations give equivalent predictions), so downstream units
verify recovered *scores / rankings*, never literal coordinates (design 011 §6).

Never an opaque blob: run this script to regenerate the catalog deterministically. Nothing is
committed — output lands in the gitignored ``recsys/data/generated/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:  # script vs. package-relative import
    from _common import GENERATED_DIR, DatasetConfig, Manifest, write_gzip_csv
except ImportError:  # pragma: no cover - exercised only as a module
    from recsys.data._common import (  # type: ignore[no-redef]
        GENERATED_DIR,
        DatasetConfig,
        Manifest,
        write_gzip_csv,
    )

CATALOG_COLUMNS = ["item_id", "title", "author_id", "genres", "year"]
GENRE_NAMES = [
    "fantasy", "sci-fi", "mystery", "romance", "history", "biography",
    "science", "poetry", "horror", "adventure", "philosophy", "children",
]


@dataclass
class Catalog:
    """The generated catalog and its exposed latent ground-truth."""

    item_ids: np.ndarray  # (n_books,) int
    author_ids: np.ndarray  # (n_books,) int
    years: np.ndarray  # (n_books,) int
    genre_matrix: np.ndarray  # (n_books, n_genres) float in [0, 1]
    latent: np.ndarray  # (n_books, latent_dim) float
    popularity: np.ndarray  # (n_books,) float > 0, heavy-tailed
    config: DatasetConfig

    @property
    def n_books(self) -> int:
        return int(self.item_ids.shape[0])

    def title(self, item_id: int) -> str:
        return f"Book {int(item_id):05d}"

    def genre_label(self, item_id: int) -> str:
        active = np.nonzero(self.genre_matrix[item_id] > 0)[0]
        return ";".join(GENRE_NAMES[g] for g in active) or GENRE_NAMES[0]

    def rows(self):
        for item_id in self.item_ids:
            yield [
                int(item_id),
                self.title(item_id),
                int(self.author_ids[item_id]),
                self.genre_label(int(item_id)),
                int(self.years[item_id]),
            ]


def generate_catalog(config: DatasetConfig, rng: np.random.Generator) -> Catalog:
    """Generate the catalog from a threaded ``rng`` (advances the shared stream)."""
    n, g, dim = config.n_books, config.n_genres, config.latent_dim
    item_ids = np.arange(n, dtype=np.int64)
    author_ids = rng.integers(0, config.n_authors, size=n)
    years = rng.integers(1950, 2025, size=n)

    # Genre membership: 1-3 genres per book, weighted; content-feature signal for taste.
    genre_matrix = np.zeros((n, g), dtype=np.float64)
    n_genres_each = rng.integers(1, 4, size=n)
    for i in range(n):
        chosen = rng.choice(g, size=int(n_genres_each[i]), replace=False)
        genre_matrix[i, chosen] = rng.uniform(0.5, 1.0, size=chosen.shape[0])
    row_sums = genre_matrix.sum(axis=1, keepdims=True)
    genre_matrix = genre_matrix / np.where(row_sums == 0, 1.0, row_sums)

    # Low-rank latent factors correlated with genre (so content and collaborative signals agree).
    genre_to_latent = rng.normal(0, config.genre_latent_scale, size=(g, dim))
    latent = config.latent_scale * (
        genre_matrix @ genre_to_latent + rng.normal(0, config.latent_noise, size=(n, dim))
    )

    # Heavy-tailed popularity (lognormal): drives popularity bias + the exposure process.
    popularity = np.exp(rng.normal(0.0, 1.2, size=n))

    return Catalog(
        item_ids=item_ids,
        author_ids=author_ids,
        years=years,
        genre_matrix=genre_matrix,
        latent=latent,
        popularity=popularity,
        config=config,
    )


def write_catalog(catalog: Catalog, out_dir: Path = GENERATED_DIR) -> Manifest:
    """Write the catalog CSV and return its manifest (source/version/schema/checksums/rowcounts)."""
    path = out_dir / "catalog.csv.gz"
    digest = write_gzip_csv(path, CATALOG_COLUMNS, catalog.rows())
    return Manifest(
        source="synthetic:gen_catalog",
        version="1",
        config={"seed": catalog.config.seed, "n_books": catalog.n_books},
        rowcounts={"catalog": catalog.n_books},
        schema={"catalog.csv.gz": CATALOG_COLUMNS},
        checksums={"catalog.csv.gz": digest},
    )


def main() -> None:
    config = DatasetConfig()
    rng = np.random.default_rng(config.seed)
    catalog = generate_catalog(config, rng)
    manifest = write_catalog(catalog)
    print(f"catalog: {catalog.n_books} books -> {GENERATED_DIR / 'catalog.csv.gz'}")
    print(f"sha256: {manifest.checksums['catalog.csv.gz']}")


if __name__ == "__main__":
    main()

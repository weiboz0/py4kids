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
    from vocabulary import build_topics
except ImportError:  # pragma: no cover - exercised only as a module
    from recsys.data._common import (  # type: ignore[no-redef]
        GENERATED_DIR,
        DatasetConfig,
        Manifest,
        write_gzip_csv,
    )
    from recsys.data.vocabulary import build_topics  # type: ignore[no-redef]

CATALOG_COLUMNS = ["item_id", "title", "author_id", "genres", "year"]
KEYWORD_COLUMNS = ["item_id", "keywords"]
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


@dataclass
class Keywords:
    """Per-book keyword token bags — the slice text for lexical (U3) / GloVe (U7) content.

    ``token_strings[i]`` is a space-joined bag for ``item_ids[i]`` (tokens may repeat → TF varies;
    lengths vary → BM25 ``b`` matters). ``vocab`` is the committed topic vocabulary this draws from.
    """

    item_ids: np.ndarray  # (n_books,) int
    token_strings: list[str]
    vocab: list[str]
    seed: int  # the dataset seed this bag was sampled under (provenance for the manifest)

    def rows(self):
        for item_id, bag in zip(self.item_ids, self.token_strings):
            yield [int(item_id), bag]

    def tf_matrix(self) -> np.ndarray:
        """Dense term-frequency matrix ``(n_books, |vocab|)`` for the recoverability harness."""
        index = {word: j for j, word in enumerate(self.vocab)}
        tf = np.zeros((self.item_ids.shape[0], len(self.vocab)), dtype=np.float64)
        for i, bag in enumerate(self.token_strings):
            if not bag:
                continue
            cols = [index[w] for w in bag.split(" ")]
            np.add.at(tf[i], cols, 1.0)
        return tf


def generate_keywords(catalog: Catalog, config: DatasetConfig) -> Keywords:
    """Sample a latent+genre-conditioned keyword bag per book (design 011 §6, plan recsys-004).

    Topic weights per book come from the book's latent factors (z-scored per dimension, split into
    positive/negative poles) and its genre membership, so books sharing latent structure or genre
    share tokens — latent neighbours more finely than genre alone. Tokens are drawn **from a
    ``SeedSequence.spawn`` sub-stream**, independent of the threaded catalog/interaction RNG, so the
    5-column ``catalog.csv.gz`` (and U1's pinned search ids) are byte-identical regardless of this
    text. Token count ``T`` varies and tokens repeat, so TF and document length both vary (BM25).
    """
    n, g, dim = catalog.n_books, config.n_genres, config.latent_dim
    topics = build_topics(g, dim)  # order: latent_pos(dim), latent_neg(dim), genre(g)
    vocab: list[str] = [word for topic in topics for word in topic]
    topic_words = [list(topic) for topic in topics]

    latent = catalog.latent
    std = latent.std(axis=0, keepdims=True)
    lz = (latent - latent.mean(axis=0, keepdims=True)) / np.where(std == 0.0, 1.0, std)
    feats = np.concatenate(
        [
            np.maximum(lz, 0.0),
            np.maximum(-lz, 0.0),
            catalog.genre_matrix * config.keyword_genre_scale,
        ],
        axis=1,
    )  # (n, 2*dim + g), columns aligned to ``topics``
    weights = np.exp(config.keyword_topic_sharpness * feats)
    weights /= weights.sum(axis=1, keepdims=True)

    # Independent sub-stream: does not advance the catalog/interaction RNG (byte-stable catalog).
    kw_rng = np.random.default_rng(np.random.SeedSequence(config.seed).spawn(2)[1])
    n_topics = len(topic_words)
    token_strings: list[str] = []
    for i in range(n):
        length = int(kw_rng.integers(config.keyword_len_min, config.keyword_len_max + 1))
        chosen_topics = kw_rng.choice(n_topics, size=length, p=weights[i])
        tokens = [
            topic_words[t][int(kw_rng.integers(0, len(topic_words[t])))] for t in chosen_topics
        ]
        token_strings.append(" ".join(tokens))

    return Keywords(
        item_ids=catalog.item_ids, token_strings=token_strings, vocab=vocab, seed=config.seed
    )


def write_keywords(keywords: Keywords, out_dir: Path = GENERATED_DIR) -> Manifest:
    """Write the SEPARATE ``keywords.csv.gz`` (NOT a catalog column) and return its manifest."""
    path = out_dir / "keywords.csv.gz"
    digest = write_gzip_csv(path, KEYWORD_COLUMNS, keywords.rows())
    return Manifest(
        source="synthetic:gen_catalog.keywords",
        version="1",
        config={"seed": keywords.seed, "vocab": len(keywords.vocab)},
        rowcounts={"keywords": keywords.item_ids.shape[0]},
        schema={"keywords.csv.gz": KEYWORD_COLUMNS},
        checksums={"keywords.csv.gz": digest},
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
    keyword_manifest = write_keywords(generate_keywords(catalog, config))
    print(f"catalog: {catalog.n_books} books -> {GENERATED_DIR / 'catalog.csv.gz'}")
    print(f"sha256: {manifest.checksums['catalog.csv.gz']}")
    print(f"keywords: {catalog.n_books} bags -> {GENERATED_DIR / 'keywords.csv.gz'}")
    print(f"sha256: {keyword_manifest.checksums['keywords.csv.gz']}")


if __name__ == "__main__":
    main()

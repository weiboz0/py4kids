"""Shared configuration and deterministic I/O helpers for the recsys data substrate.

Determinism contract (design 011 §7, plan recsys-001 global constraints):

- **One seed, threaded.** A single ``numpy.random.default_rng(seed)`` is created once and passed
  through catalog then interaction generation, so the whole dataset is one reproducible stream.
- **Fixed float precision.** Floats are written with a fixed number of decimals, so the CSV bytes
  do not depend on platform float repr.
- **Normalised gzip mtime.** gzip headers are written with ``mtime=0``, so identical content
  yields byte-identical ``.gz`` files (and stable checksums) run to run.
- **NEP-19.** Reproducibility is "identical under ``uv.lock``": numpy's bit stream is stable for a
  pinned numpy, not frozen across numpy releases. Invariants are therefore threshold/rank based.

Nothing here is committed: outputs live under ``recsys/data/generated/`` (gitignored). CI
regenerates and re-validates every run.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
GENERATED_DIR = DATA_DIR / "generated"
FLOAT_DECIMALS = 6
SEED = 20260930


@dataclass(frozen=True)
class DatasetConfig:
    """All knobs for one reproducible dataset. Defaults are CI-bounded (below the §7 ceilings)."""

    seed: int = SEED
    # catalog
    n_books: int = 2000
    n_authors: int = 300
    n_genres: int = 12
    latent_dim: int = 16
    latent_scale: float = 2.0
    latent_noise: float = 0.2
    genre_latent_scale: float = 1.8
    # readers / interactions
    n_readers: int = 600
    n_cold_items: int = 150
    n_cold_readers: int = 60
    mean_sessions_per_reader: float = 6.0
    max_items_per_session: int = 4
    negatives_per_positive: int = 2
    # signal strengths
    feature_weight: float = 2.0
    drift_scale: float = 0.05
    author_follow_boost: float = 1.5
    popularity_exposure_weight: float = 1.0
    positive_threshold: float = 2.0
    logit_temperature: float = 3.0
    # temporal split fractions (per warm reader, by event time)
    val_fraction: float = 0.15
    test_fraction: float = 0.15

    def __post_init__(self) -> None:
        if self.n_cold_items + 1 >= self.n_books:
            raise ValueError("n_cold_items must leave warm items")
        if self.n_cold_readers + 1 >= self.n_readers:
            raise ValueError("n_cold_readers must leave warm readers")
        if not 0 < self.val_fraction + self.test_fraction < 1:
            raise ValueError("val_fraction + test_fraction must be in (0, 1)")


def fmt_float(value: float) -> str:
    """Format a float with fixed precision so CSV bytes are platform-independent."""
    return f"{float(value):.{FLOAT_DECIMALS}f}"


def _cell(value: object) -> str:
    if isinstance(value, float):
        return fmt_float(value)
    return str(value)


def write_gzip_csv(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    """Write ``rows`` as a gzip'd CSV with normalised mtime; return the sha256 of the gz bytes.

    Float cells use :func:`fmt_float`. The gzip header carries ``mtime=0`` so identical content is
    byte-identical across runs (stable checksum).
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow([_cell(value) for value in row])
    payload = buffer.getvalue().encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle, gzip.GzipFile(
        filename="", mode="wb", fileobj=handle, mtime=0
    ) as gz:
        gz.write(payload)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checksum(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@dataclass
class Manifest:
    """Records source/version/params/rowcounts/schema/checksums for a written dataset (§6)."""

    source: str
    version: str
    config: dict
    rowcounts: dict[str, int] = field(default_factory=dict)
    schema: dict[str, list[str]] = field(default_factory=dict)
    checksums: dict[str, str] = field(default_factory=dict)
    notes: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "version": self.version,
            "config": self.config,
            "rowcounts": self.rowcounts,
            "schema": self.schema,
            "checksums": self.checksums,
            "notes": self.notes,
        }

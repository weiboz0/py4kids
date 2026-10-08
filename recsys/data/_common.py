"""Shared configuration and deterministic I/O helpers for the recsys data substrate.

Determinism contract (design 011 §7, plan recsys-001 global constraints):

- **One seed, threaded.** A single ``numpy.random.default_rng(seed)`` is created once and passed
  through catalog then interaction generation, so the whole dataset is one reproducible stream.
- **Named independent sub-streams.** Artifacts added after the threaded stream was pinned draw from
  ``SeedSequence(seed).spawn(...)`` children via :func:`substream_rng`, never from the threaded rng:
  ``SUBSTREAM_KEYWORDS`` (``keywords.csv.gz``), ``SUBSTREAM_SERIES`` (``series.csv.gz``) and
  ``SUBSTREAM_SESSIONS`` (``sessions.csv.gz``, the U12 session log). A child's identity is its
  index (``spawn_key=(index,)``), so adding a stream never moves another; ``catalog.csv.gz``,
  ``interactions.csv.gz``, ``keywords.csv.gz`` and ``cold_partitions.json`` stay byte-identical.
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

import numpy as np

DATA_DIR = Path(__file__).resolve().parent
GENERATED_DIR = DATA_DIR / "generated"
FLOAT_DECIMALS = 6
SEED = 20260930

# Named, independent SeedSequence sub-streams (design 011 §6). Never renumber: the index IS the
# stream identity (child ``spawn_key=(index,)``), and the keyword index predates this table.
SUBSTREAM_KEYWORDS = 1
SUBSTREAM_SERIES = 2
SUBSTREAM_SESSIONS = 3
SERIES_FRACTION = 0.5


def substream_rng(seed: int, index: int) -> np.random.Generator:
    """An rng on the ``index``-th ``SeedSequence(seed)`` child — independent of the threaded rng.

    ``SeedSequence(seed).spawn(n)[i]`` has ``spawn_key=(i,)`` for every ``n > i``, so this equals the
    historical ``spawn(2)[1]`` keyword stream for ``index=SUBSTREAM_KEYWORDS``.
    """
    if index < 0:
        raise ValueError("sub-stream index must be >= 0")
    return np.random.default_rng(np.random.SeedSequence(seed).spawn(index + 1)[index])


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
    # Independent latent component beyond the genre image. Raised from 0.2 (recsys-004) so latent
    # taste carries signal *beyond* genre — a learned MF (U5) can then beat genre/keyword content
    # (U3). Changing this re-scales latent VALUES only; it draws the same standard-normals, so the
    # downstream popularity draw and ``catalog.csv.gz`` bytes are unaffected.
    latent_noise: float = 0.4
    genre_latent_scale: float = 1.8
    # keyword text (plan recsys-004). Per-book token bag conditioned on z-scored latent poles +
    # genre; drawn from an independent sub-stream so the catalog CSV stays byte-identical.
    keyword_topic_sharpness: float = 2.0  # softmax temperature over topic weights
    keyword_genre_scale: float = 3.0  # genre feature weight vs. latent poles in the topic mix
    keyword_len_min: int = 12  # min tokens per book (with repetition → TF/doc-length vary)
    keyword_len_max: int = 40
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
    # Taste-aware exposure (plan recsys-004): exposure ∝ popularity**α · exp(β · z_u(affinity)),
    # with z_u the per-reader standardisation of affinity (so β is well-conditioned regardless of
    # latent_scale/feature_weight). α=popularity_exposure_weight keeps popularity a strong baseline
    # (α≥0.75 ⇒ popularity ≥5× the random floor); β=exposure_affinity_weight makes latent/content/
    # collaborative taste recoverable above popularity (the recsys-004 recoverability harness).
    popularity_exposure_weight: float = 0.75  # α
    exposure_affinity_weight: float = 2.5  # β, acting on per-reader z-scored affinity
    author_exposure_recur: float = 0.3  # read → raises exposure of that author's books in later sessions
    positive_threshold: float = 2.0
    logit_temperature: float = 3.0
    # temporal split fractions (per warm reader, by event time)
    val_fraction: float = 0.15
    test_fraction: float = 0.15
    # --- series (plan recsys-014; ``series.csv.gz``, SUBSTREAM_SERIES, always at ``seed``) --------
    series_fraction: float = SERIES_FRACTION  # target share of catalog books placed in a series
    series_len_min: int = 3  # volumes per same-author series
    series_len_max: int = 5
    # --- U12 session log (plan recsys-014; ``sessions.csv.gz``, SUBSTREAM_SESSIONS) --------------
    # ``session_seed`` varies ONLY the session log (the catalog/keywords/series stay at ``seed``);
    # None means the committed ``seed``. The session readers are a separate synthetic population.
    # Defaults are the Phase-B round-1 knobs with 1,500 readers (round-3 variant V1); they are
    # frozen (recsys-014 v5, R3-V1).
    session_seed: int | None = None
    session_n_readers: int = 1500
    session_mean_sessions: float = 16.0  # Poisson mean sessions per reader (floored at min below)
    session_min_sessions: int = 6
    session_max_items: int = 5  # exposure slots per session drawn uniformly from 1..max
    session_negatives_per_positive: int = 2
    # Order mechanism 1 — forced next-volume slot: after reading volume v, v+1 takes the FIRST
    # exposure slot of each of the next ``window`` sessions with ``follow_prob``, until read, with an
    # acceptance-logit boost ``accept`` (the plain exposure-logit bonus alone barely surfaces it).
    session_series_window: int = 3
    session_series_follow_prob: float = 1.0
    session_series_accept: float = 4.0
    # Order mechanism 2 — decaying author-follow: each positive adds ``author_bump`` to the exposure
    # and acceptance logits of that author's books; the bump decays ×``author_decay`` per session.
    session_author_bump: float = 3.0
    session_author_decay: float = 0.5
    # Order mechanism 3 — persistent genre mood: a per-session mood genre (drawn from the reader's
    # genre prefs) kept with ``mood_persist``; exposure-logit boost ``mood_boost`` on that genre.
    session_mood_boost: float = 5.0
    session_mood_persist: float = 0.9

    def __post_init__(self) -> None:
        if self.n_cold_items + 1 >= self.n_books:
            raise ValueError("n_cold_items must leave warm items")
        if self.n_cold_readers + 1 >= self.n_readers:
            raise ValueError("n_cold_readers must leave warm readers")
        if not 0 < self.val_fraction + self.test_fraction < 1:
            raise ValueError("val_fraction + test_fraction must be in (0, 1)")
        if not 0 < self.series_fraction < 1:
            raise ValueError("series_fraction must be in (0, 1)")
        if not 2 <= self.series_len_min <= self.series_len_max:
            raise ValueError("series lengths must satisfy 2 <= series_len_min <= series_len_max")
        if self.session_n_readers < 1:
            raise ValueError("session_n_readers must be >= 1")
        if self.session_mean_sessions <= 0:
            raise ValueError("session_mean_sessions must be > 0")
        if self.session_min_sessions < 3:
            raise ValueError("session_min_sessions must be >= 3 (train, val and test sessions)")
        if self.session_max_items < 1:
            raise ValueError("session_max_items must be >= 1")
        if self.session_negatives_per_positive < 0:
            raise ValueError("session_negatives_per_positive must be >= 0")
        if self.session_series_window < 1:
            raise ValueError("session_series_window must be >= 1")
        for name in ("session_series_follow_prob", "session_author_decay", "session_mood_persist"):
            if not 0.0 <= getattr(self, name) <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        for name in ("session_series_accept", "session_author_bump", "session_mood_boost"):
            if getattr(self, name) < 0.0:
                raise ValueError(f"{name} must be >= 0")

    @property
    def effective_session_seed(self) -> int:
        """The seed the session sub-stream uses: ``session_seed`` if set, else the committed seed."""
        return self.seed if self.session_seed is None else self.session_seed


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

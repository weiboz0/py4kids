"""Unit 14 (recsys-017): the assembled full system and the regenerated-only model cache.

Units 2–13 each built one piece of a recommender. Unit 14 assembles them into **one** system and the
capstone defends a choice on its hit ↔ reach ↔ exposure frontier. This module is the glue:

- **The model cache.** ``recsys/projects/bookrec/scripts/build_models.py`` fits the expensive models
  once (MF, the two-tower, the warm and hard-negative feature towers, the HNSW index, the two learned
  rerankers and SASRec) and pickles their torch-free ``artifact()`` dicts to
  ``recsys/data/generated/models/`` (gitignored, regenerated-only, exactly like the data). Each pickle
  is an *envelope* — ``{"schema", "schema_version", "name", "path_class", "path_version", "meta",
  "artifact"}`` — and a ``manifest.json`` sidecar records the versions plus the sha256 of the
  generated data's ``checksums.json``. :func:`load_cached_models` refuses a cache built from
  different data and names the build command when the cache is missing.
- **The pinned full stack** (plan recsys-017 "The assembled system"): an equal-weight 8-path pool
  (popularity, lexical, item-item, MF, semantic, the two-tower **served through HNSW**, the warm
  feature tower and the U10 hybrid), ``pool = 50``, re-scored by the **8-path learned reranker**
  trained with the unchanged Unit-11 recipe (time-ordered 75/25 profile/label holdout).
  :class:`FullSystem` loads every piece from the cache and serves the full stack, the fixed blend,
  the stage/path ablations and the Part-1 (Unit 6) build.
- **The whole-system readout** (:func:`compute_readouts`): the 10-row ablation table (stage rows vs
  the full stack, path rows as fixed-blend leave-one-out) and the beyond-accuracy table.

Everything here is **val only** and imports neither torch nor faiss at module level (loading the
ANN path rebuilds its HNSW graph, which needs faiss at call time; nothing else does).
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import pickle
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any

import numpy as np

from bookrec.ann import AnnRetrievalPath
from bookrec.blend import blend
from bookrec.catalog import Book, load_catalog
from bookrec.diversity import (
    catalog_coverage,
    head_ids_from_counts,
    head_share,
    intra_list_diversity,
    novelty,
)
from bookrec.embeddings import GloveSubset, SemanticEmbeddingRetrievalPath, load_glove_subset
from bookrec.factorization import MatrixFactorizationPath
from bookrec.fairness import author_exposure_gini, exposure_gini
from bookrec.feature_tower import FeatureTowerRetrievalPath
from bookrec.hybrid import HybridRetrievalPath
from bookrec.keywords import load_keywords
from bookrec.lexical import LexicalRetrievalPath
from bookrec.neighborhood import ItemItemRetrievalPath
from bookrec.popularity import PopularityRetrievalPath
from bookrec.protocol import Candidate
from bookrec.rank import rank
from bookrec.rerank import DEFAULT_PATH_NAMES, NeuralRerankerPath
from bookrec.sequence import SasrecRetrievalPath
from bookrec.two_tower import TwoTowerRetrievalPath

# ------------------------------------------------------------------------------- pinned constants
K = 10
POOL = 50
SEED = 0
HYBRID_WEIGHT = 0.7

#: Every cached model, in build order.
MODEL_NAMES: tuple[str, ...] = (
    "mf",
    "two-tower",
    "feature-tower",
    "feature-tower-hard",
    "ann",
    "reranker-u11",
    "reranker-full8",
    "sasrec",
)
CACHE_SCHEMA = "bookrec-model-cache"
CACHE_SCHEMA_VERSION = 1
PICKLE_PROTOCOL = 5
MANIFEST_FILE = "manifest.json"
READOUTS_FILE = "readouts.json"
READOUTS_SCHEMA = "bookrec-readouts"
READOUTS_SCHEMA_VERSION = 1
BUILD_COMMAND = "uv run --group recsys python recsys/projects/bookrec/scripts/build_models.py"

#: The Unit-11 leakage-safe reranker recipe, frozen for both cached rerankers.
RERANKER_RECIPE = "u11-holdout-75-25"
HOLDOUT_FRAC = 0.25

#: The shipped Unit-11 reranker's six feature paths and the full stack's eight.
U11_PATH_NAMES: tuple[str, ...] = DEFAULT_PATH_NAMES
FULL8_PATH_NAMES: tuple[str, ...] = (
    "popularity",
    "lexical",
    "item-item",
    "mf",
    "semantic",
    "two-tower",
    "feature-tower",
    "hybrid",
)

#: The Part-1 build (the Unit-6 / Checkpoint-A blend).
PART1_WEIGHTS: dict[str, float] = {"popularity": 0.25, "lexical": 0.5, "item-item": 1.0, "mf": 1.0}
PART1_POOL = 30

#: The ablation table: (row id, kind, baseline row id). Stage rows are deltas vs the full stack;
#: path rows are fixed-blend leave-one-out deltas vs the fixed 8-path blend.
ABLATION_ROWS: tuple[tuple[str, str, str], ...] = (
    ("no-reranker", "stage", "full-stack"),
    ("exact-two-tower", "stage", "full-stack"),
    *((f"minus-{name}", "path", "fixed-blend") for name in FULL8_PATH_NAMES),
)
BASELINE_ROWS: tuple[str, ...] = ("full-stack", "fixed-blend")
BEYOND_ACCURACY_ROWS: tuple[str, ...] = ("full-system", "best-single-path", "part1-build")
BEYOND_ACCURACY_COLUMNS: tuple[str, ...] = (
    "coverage",
    "head_share",
    "exposure_gini",
    "novelty",
    "diversity",
)


# ------------------------------------------------------------------------------------- locations
def default_models_dir() -> Path:
    """``recsys/data/generated/models`` — the regenerated-only model cache (may not exist yet)."""
    return Path(__file__).resolve().parents[3] / "data" / "generated" / "models"


def default_data_dir() -> Path:
    """``recsys/data/generated`` — the regenerated-only data directory (may not exist yet)."""
    return Path(__file__).resolve().parents[3] / "data" / "generated"


def data_hash(data_dir: str | Path | None = None) -> str:
    """The sha256 of the generated data's ``checksums.json`` — the cache's data fingerprint."""
    path = Path(data_dir) if data_dir is not None else default_data_dir()
    checksums = path / "checksums.json"
    if not checksums.is_file():
        raise FileNotFoundError(
            f"generated recsys data is missing at {path}; run the recsys data generators first"
        )
    return hashlib.sha256(checksums.read_bytes()).hexdigest()


def file_sha256(path: str | Path) -> str:
    """The sha256 of a file's bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------------------------------- rows
_INT_COLUMNS = ("reader_id", "item_id", "session_id", "timestamp", "label")


def read_rows(path: str | Path) -> list[dict[str, Any]]:
    """Read an interaction/session log (gzip'd CSV) as row dicts, numeric columns as ``int``.

    The same values and order as ``pandas.read_csv(path).to_dict("records")``, without pandas.
    """
    with gzip.open(path, mode="rt", encoding="utf-8", newline="") as handle:
        rows = []
        for raw in csv.DictReader(handle):
            row: dict[str, Any] = dict(raw)
            for column in _INT_COLUMNS:
                if column in row:
                    row[column] = int(row[column])
            rows.append(row)
    return rows


def seen_and_relevant(
    rows: Iterable[Mapping[str, Any]], known_items: set[int], split: str = "val"
) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    """Train-positive ``seen`` sets and ``split``-positive relevant sets (the scoreboard's own rule)."""
    seen: dict[int, set[int]] = {}
    target: dict[int, set[int]] = {}
    for row in rows:
        item = int(row["item_id"])
        if item not in known_items or int(row["label"]) != 1:
            continue
        reader = int(row["reader_id"])
        if row["split"] == "train":
            seen.setdefault(reader, set()).add(item)
        elif row["split"] == split:
            target.setdefault(reader, set()).add(item)
    return seen, target


# -------------------------------------------------------------------------------------- data
@dataclass
class BookData:
    """The generated main log + catalog features, and the val cohort every readout scores."""

    data_dir: Path
    catalog: dict[int, Book]
    catalog_ids: list[int]
    keywords: dict[int, str]
    glove: GloveSubset
    cold_readers: list[int]
    rows: list[dict[str, Any]]
    seen_by: dict[int, set[int]] = field(repr=False)
    relevant: dict[int, set[int]] = field(repr=False)
    cohort: list[int] = field(repr=False)

    @property
    def interactions_path(self) -> Path:
        return self.data_dir / "interactions.csv.gz"

    @property
    def sessions_path(self) -> Path:
        return self.data_dir / "sessions.csv.gz"

    @cached_property
    def session_rows(self) -> list[dict[str, Any]]:
        """The session log (the sequence path is trained and scored on it only; design §6)."""
        return read_rows(self.sessions_path)

    @cached_property
    def session_cohort(self) -> tuple[dict[int, set[int]], dict[int, set[int]], list[int]]:
        """``(seen_by, relevant, cohort)`` on the session log's val split (no cold exclusion)."""
        seen, target = seen_and_relevant(self.session_rows, set(self.catalog_ids), "val")
        relevant = {r: target[r] - seen.get(r, set()) for r in target}
        cohort = [r for r in sorted(relevant) if relevant[r]]
        return seen, relevant, cohort


def load_book_data(data_dir: str | Path | None = None) -> BookData:
    """Load the catalog, keywords, GloVe subset, main log and its val cohort (cold readers excluded)."""
    path = Path(data_dir) if data_dir is not None else default_data_dir()
    if not (path / "checksums.json").is_file():
        raise FileNotFoundError(
            f"generated recsys data is missing at {path}; run the recsys data generators first"
        )
    catalog = load_catalog(path / "catalog.csv.gz")
    catalog_ids = sorted(catalog)
    cold = json.loads((path / "cold_partitions.json").read_text(encoding="utf-8"))["cold_readers"]
    rows = read_rows(path / "interactions.csv.gz")
    seen, target = seen_and_relevant(rows, set(catalog_ids), "val")
    cold_set = set(cold)
    relevant = {r: target[r] - seen.get(r, set()) for r in target if r not in cold_set}
    cohort = [r for r in sorted(relevant) if relevant[r]]
    seen_by = {r: seen.get(r, set()) for r in set(seen) | set(target)}
    return BookData(
        data_dir=path,
        catalog=catalog,
        catalog_ids=catalog_ids,
        keywords=load_keywords(path / "keywords.csv.gz"),
        glove=load_glove_subset(),
        cold_readers=list(cold),
        rows=rows,
        seen_by=seen_by,
        relevant={r: relevant[r] for r in cohort},
        cohort=cohort,
    )


# ------------------------------------------------------------------------- path recipes (seed 0)
def make_mf(config: Mapping[str, Any] | None = None) -> MatrixFactorizationPath:
    return MatrixFactorizationPath(seed=SEED, **dict((config or {}).get("mf", {})))


def make_two_tower(config: Mapping[str, Any] | None = None) -> TwoTowerRetrievalPath:
    return TwoTowerRetrievalPath(seed=SEED, **dict((config or {}).get("two-tower", {})))


def make_feature_tower(
    data: BookData, negative_pool: str = "warm", config: Mapping[str, Any] | None = None
) -> FeatureTowerRetrievalPath:
    return FeatureTowerRetrievalPath(
        data.catalog,
        data.keywords,
        data.glove,
        negative_pool=negative_pool,
        seed=SEED,
        **dict((config or {}).get("feature-tower", {})),
    )


def make_sasrec(config: Mapping[str, Any] | None = None) -> SasrecRetrievalPath:
    return SasrecRetrievalPath(**dict((config or {}).get("sasrec", {})))


def fit_cheap_paths(data: BookData, rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Fit the four cheap paths (popularity, lexical, item-item, semantic) — seconds, never cached."""
    rows = data.rows if rows is None else rows
    ids = data.catalog_ids
    return {
        "popularity": PopularityRetrievalPath().fit(rows, catalog=ids),
        "lexical": LexicalRetrievalPath(data.keywords).fit(rows, catalog=ids),
        "item-item": ItemItemRetrievalPath().fit(rows, catalog=ids),
        "semantic": SemanticEmbeddingRetrievalPath(data.keywords, data.glove).fit(
            rows, catalog=ids
        ),
    }


def six_path_factory(
    data: BookData, config: Mapping[str, Any] | None = None
) -> Callable[[list[dict[str, Any]]], dict[str, Any]]:
    """The Unit-11 ``path_factory``: refit the six feature paths on the given (profile) rows."""

    def fit_six(rows: list[dict[str, Any]]) -> dict[str, Any]:
        cheap = fit_cheap_paths(data, rows)
        return {
            "popularity": cheap["popularity"],
            "lexical": cheap["lexical"],
            "item-item": cheap["item-item"],
            "mf": make_mf(config).fit(rows, catalog=data.catalog_ids),
            "semantic": cheap["semantic"],
            "two-tower": make_two_tower(config).fit(rows, catalog=data.catalog_ids),
        }

    return fit_six


def eight_path_factory(
    data: BookData, config: Mapping[str, Any] | None = None
) -> Callable[[list[dict[str, Any]]], dict[str, Any]]:
    """The full stack's ``path_factory``: the Unit-11 recipe generalised to all eight paths.

    The profile-refit two-tower is used exactly (the HNSW index is a serving-time speed-up only).
    """

    def fit_eight(rows: list[dict[str, Any]]) -> dict[str, Any]:
        six = six_path_factory(data, config)(rows)
        return {
            **six,
            "feature-tower": make_feature_tower(data, "warm", config).fit(
                rows, catalog=data.catalog_ids
            ),
            "hybrid": HybridRetrievalPath(
                six["lexical"], six["two-tower"], weight=HYBRID_WEIGHT, pool=POOL
            ).fit(rows),
        }

    return fit_eight


def _no_refit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    raise RuntimeError(
        "this reranker was loaded from the model cache; its training-time path refit lives in "
        "build_models.py (use the cached training matrix to refit the model)"
    )


# --------------------------------------------------------------------------------- the cache
def make_envelope(
    name: str, path: Any, artifact: Mapping[str, Any], meta: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Wrap a path's ``artifact()`` with its schema, class, version and build metadata."""
    return {
        "schema": CACHE_SCHEMA,
        "schema_version": CACHE_SCHEMA_VERSION,
        "name": name,
        "path_class": type(path).__name__,
        "path_name": path.name,
        "path_version": path.version,
        "meta": dict(meta or {}),
        "artifact": dict(artifact),
    }


def write_envelope(directory: str | Path, envelope: Mapping[str, Any]) -> Path:
    """Pickle an envelope (protocol 5) to ``<directory>/<name>.pkl``."""
    target = Path(directory) / f"{envelope['name']}.pkl"
    with open(target, "wb") as handle:
        pickle.dump(dict(envelope), handle, protocol=PICKLE_PROTOCOL)
    return target


def _missing(directory: Path, what: str) -> FileNotFoundError:
    return FileNotFoundError(
        f"the bookrec model cache is missing {what} at {directory}; build it with:\n"
        f"    {BUILD_COMMAND}"
    )


@dataclass
class ModelCache:
    """The loaded model cache: one envelope per model + the manifest (+ the readouts, if built)."""

    directory: Path
    manifest: dict[str, Any]
    envelopes: dict[str, dict[str, Any]]

    def envelope(self, name: str) -> dict[str, Any]:
        if name not in self.envelopes:
            raise KeyError(f"no cached model {name!r}; cached: {sorted(self.envelopes)}")
        return self.envelopes[name]

    def artifact(self, name: str) -> dict[str, Any]:
        """The path's own ``artifact()`` dict, ready for ``path.load(...)``."""
        return self.envelope(name)["artifact"]

    def meta(self, name: str) -> dict[str, Any]:
        """Build metadata (recipe, profile fraction, training log, …)."""
        return self.envelope(name)["meta"]

    def loss_history(self, name: str) -> list[float]:
        """The stored per-epoch training curve (rerankers: the MLP's training log)."""
        if name.startswith("reranker"):
            return list(self.artifact(name)["model"].get("loss_history", []))
        return list(self.artifact(name).get("loss_history", []))

    def training_matrix(self, name: str) -> tuple[np.ndarray, np.ndarray]:
        """A cached reranker's leakage-safe ``(X, y)`` training matrix (refit a model on it)."""
        matrix = self.meta(name).get("training_matrix")
        if matrix is None:
            raise KeyError(f"cached model {name!r} carries no training matrix")
        return np.array(matrix["X"], dtype=np.float32), np.array(matrix["y"], dtype=np.float32)

    @cached_property
    def readouts(self) -> dict[str, Any]:
        """The build's ``readouts.json`` (ablation + beyond-accuracy tables)."""
        path = self.directory / READOUTS_FILE
        if not path.is_file():
            raise _missing(self.directory, READOUTS_FILE)
        return json.loads(path.read_text(encoding="utf-8"))


def load_cached_models(
    dir: str | Path | None = None,
    *,
    data_dir: str | Path | None = None,
    names: Sequence[str] = MODEL_NAMES,
) -> ModelCache:
    """Load the model cache (torch-free and faiss-free: pickles of numpy arrays + builtins).

    Raises :class:`FileNotFoundError` naming the build command when the cache (or any model) is
    missing, and :class:`ValueError` when the cache was built from different generated data (the
    manifest's sha256 of ``checksums.json`` no longer matches) or an envelope has the wrong schema.
    """
    directory = Path(dir) if dir is not None else default_models_dir()
    manifest_path = directory / MANIFEST_FILE
    if not manifest_path.is_file():
        raise _missing(directory, MANIFEST_FILE)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema") != CACHE_SCHEMA
        or manifest.get("schema_version") != CACHE_SCHEMA_VERSION
    ):
        raise ValueError(
            f"{manifest_path} is not a {CACHE_SCHEMA} v{CACHE_SCHEMA_VERSION} manifest; rebuild with:\n"
            f"    {BUILD_COMMAND}"
        )
    current = data_hash(data_dir)
    if manifest.get("data_hash") != current:
        raise ValueError(
            "the model cache was built from different generated data (checksums.json sha256 "
            f"{manifest.get('data_hash')!r} != current {current!r}); rebuild with:\n"
            f"    {BUILD_COMMAND}"
        )
    envelopes: dict[str, dict[str, Any]] = {}
    for name in names:
        path = directory / f"{name}.pkl"
        if not path.is_file():
            raise _missing(directory, path.name)
        with open(path, "rb") as handle:
            envelope = pickle.load(handle)
        if (
            not isinstance(envelope, dict)
            or envelope.get("schema") != CACHE_SCHEMA
            or envelope.get("schema_version") != CACHE_SCHEMA_VERSION
            or envelope.get("name") != name
        ):
            raise ValueError(f"{path} is not a {CACHE_SCHEMA} v{CACHE_SCHEMA_VERSION} envelope")
        envelopes[name] = envelope
    return ModelCache(directory=directory, manifest=manifest, envelopes=envelopes)


# ----------------------------------------------------------------------------- serving helpers
class MemoPath:
    """A transparent memo over a fitted path's ``retrieve`` (deterministic paths only).

    The full stack, the fixed blend and every ablation re-ask the same paths for the same reader's
    top-50; caching those answers makes a 13-row readout cost about one pass. Results are identical
    to calling the wrapped path directly.
    """

    def __init__(self, path: Any) -> None:
        self.path = path
        self.name = path.name
        self._memo: dict[tuple[Any, frozenset[int], int], list[Candidate]] = {}

    def calibrate(self, candidates: Sequence[Candidate]) -> list[Candidate]:
        return self.path.calibrate(candidates)

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        seen = frozenset(context.get("seen", ())) if isinstance(context, Mapping) else frozenset()
        key = (query, seen, k)
        if key not in self._memo:
            self._memo[key] = list(self.path.retrieve(query, {"seen": set(seen)}, k))
        return list(self._memo[key])


class FixedBlendPath:
    """A calibrated weighted union over per-path pools (Units 6/10), seen books excluded.

    Each path proposes its top ``pool``; :func:`~bookrec.blend.blend` calibrates each to ``[0, 1]``
    and sums (``weights`` default 1.0 each); the reader's seen books are dropped and the top ``k``
    kept. With no weights this is the full stack's **fixed 8-path blend** — the "no reranker" stage.
    """

    def __init__(
        self,
        paths: Mapping[str, Any],
        weights: Mapping[str, float] | None = None,
        pool: int = POOL,
        name: str = "fixed-blend",
    ) -> None:
        self.paths = dict(paths)
        self.weights = dict(weights) if weights is not None else None
        self.pool = int(pool)
        self.name = name

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        context = context if isinstance(context, Mapping) else {}
        per_path = {n: p.retrieve(query, context, self.pool) for n, p in self.paths.items()}
        seen = set(context.get("seen", ()))
        return [c for c in blend(per_path, weights=self.weights) if c.item_id not in seen][:k]


def top_k(path: Any, reader: int, seen: set[int], k: int = K) -> list[int]:
    """The scoreboard's top-``k`` list for one reader: ``rank(retrieve(...), exclude=seen)``."""
    return [c.item_id for c in rank(path.retrieve(reader, {"seen": seen}, k), n=k, exclude=seen)]


class FullSystem:
    """The whole recommender, assembled from the model cache (plan recsys-017's pinned definition).

    Attributes after :meth:`from_cache`: ``data``, ``cache``, the fitted ``paths`` (cheap paths
    refit in seconds, expensive ones loaded), ``full8`` (the 8 serving paths, two-tower via HNSW),
    ``full_stack`` (the 8-path learned reranker over ``full8``), ``reranker_u11`` (the shipped
    6-path Unit-11 model over its own pool) and ``sasrec`` (session log only).
    """

    def __init__(self, data: BookData, cache: ModelCache, paths: Mapping[str, Any]) -> None:
        self.data = data
        self.cache = cache
        self.paths = dict(paths)
        memo = {name: MemoPath(path) for name, path in self.paths.items()}
        self._memo = memo
        self.full8 = {
            "popularity": memo["popularity"],
            "lexical": memo["lexical"],
            "item-item": memo["item-item"],
            "mf": memo["mf"],
            "semantic": memo["semantic"],
            "two-tower": memo["ann"],
            "feature-tower": memo["feature-tower"],
            "hybrid": memo["hybrid-ann"],
        }
        #: The same 8 paths with the EXACT two-tower (and the hybrid over it) — the "no ANN" stage.
        self.full8_exact = {**self.full8, "two-tower": memo["two-tower"], "hybrid": memo["hybrid"]}
        self.full_stack = self._reranker("reranker-full8", self.full8, FULL8_PATH_NAMES)
        self.full_stack_exact = self._reranker("reranker-full8", self.full8_exact, FULL8_PATH_NAMES)
        six = {name: memo[name] for name in U11_PATH_NAMES}
        self.reranker_u11 = self._reranker("reranker-u11", six, U11_PATH_NAMES)
        self.sasrec = self.paths["sasrec"]

    def _reranker(
        self, name: str, paths: Mapping[str, Any], path_names: Sequence[str]
    ) -> NeuralRerankerPath:
        return NeuralRerankerPath(
            paths, _no_refit, self.data.catalog, pool=POOL, seed=SEED, path_names=path_names
        ).load(self.cache.artifact(name))

    @classmethod
    def from_cache(
        cls,
        cache: ModelCache | None = None,
        data: BookData | None = None,
    ) -> FullSystem:
        """Load every expensive model from the cache, refit the cheap paths, and assemble."""
        data = data if data is not None else load_book_data()
        cache = cache if cache is not None else load_cached_models(data_dir=data.data_dir)
        paths = fit_cheap_paths(data)
        paths["mf"] = make_mf().load(cache.artifact("mf"))
        paths["two-tower"] = make_two_tower().load(cache.artifact("two-tower"))
        paths["feature-tower"] = make_feature_tower(data, "warm").load(
            cache.artifact("feature-tower")
        )
        paths["feature-tower-hard"] = make_feature_tower(data, "hard").load(
            cache.artifact("feature-tower-hard")
        )
        paths["ann"] = AnnRetrievalPath(paths["two-tower"]).load(cache.artifact("ann"))
        paths["hybrid"] = HybridRetrievalPath(
            paths["lexical"], paths["two-tower"], weight=HYBRID_WEIGHT, pool=POOL
        ).fit(data.rows)
        paths["hybrid-ann"] = HybridRetrievalPath(
            paths["lexical"], paths["ann"], weight=HYBRID_WEIGHT, pool=POOL
        ).fit(data.rows)
        paths["sasrec"] = make_sasrec().load(cache.artifact("sasrec"))
        return cls(data, cache, paths)

    # ------------------------------------------------------------------------ the named systems
    def fixed_blend(self, drop: str | None = None, *, exact: bool = False) -> FixedBlendPath:
        """The equal-weight 8-path fixed blend (``drop`` one path for a leave-one-out row)."""
        source = self.full8_exact if exact else self.full8
        if drop is not None and drop not in source:
            raise ValueError(f"unknown path {drop!r}; choose from {sorted(source)}")
        kept = {n: p for n, p in source.items() if n != drop}
        return FixedBlendPath(
            kept, pool=POOL, name="fixed-blend" if drop is None else f"minus-{drop}"
        )

    def part1_build(self) -> FixedBlendPath:
        """The Part-1 build: the Unit-6 weighted blend of popularity, lexical, item-item and MF."""
        paths = {n: self._memo[n] for n in PART1_WEIGHTS}
        return FixedBlendPath(paths, PART1_WEIGHTS, pool=PART1_POOL, name="part1-build")

    @property
    def best_single_path(self) -> Any:
        """The best single path: the Unit-10 hybrid over the exact two-tower (0.362)."""
        return self._memo["hybrid"]

    # ------------------------------------------------------------------------------- readouts
    def top_lists(self, path: Any, readers: Iterable[int] | None = None) -> dict[int, list[int]]:
        """``{reader: top-10}`` on the main-log val cohort (or the given readers)."""
        readers = self.data.cohort if readers is None else readers
        return {r: top_k(path, r, self.data.seen_by.get(r, set())) for r in readers}

    def session_top_lists(self, readers: Iterable[int] | None = None) -> dict[int, list[int]]:
        """SASRec's ``{reader: top-10}`` on the SESSION log's val cohort (design §6)."""
        seen, _relevant, cohort = self.data.session_cohort
        readers = cohort if readers is None else readers
        return {r: top_k(self.sasrec, r, seen.get(r, set())) for r in readers}

    @cached_property
    def _diversity_lookup(self) -> tuple[dict[int, int], np.ndarray]:
        state = self.paths["item-item"].artifact()
        return {i: j for j, i in enumerate(state["item_ids"])}, state["similarity"]

    def _similarity(self, a: int, b: int) -> float:
        row_of, sim = self._diversity_lookup
        ia, ib = row_of.get(a), row_of.get(b)
        return 0.0 if ia is None or ib is None else float(sim[ia, ib])

    def readout(self, lists: Mapping[int, Sequence[int]]) -> dict[str, float]:
        """hit@10, catalog coverage, head-share, exposure Gini (items, full catalog; authors),
        novelty and intra-list diversity of a ``{reader: top-10}`` mapping (main-log val)."""
        counts = self.paths["popularity"].counts
        head = set(head_ids_from_counts(counts, self.data.catalog_ids))
        relevant = self.data.relevant
        return {
            "hit": float(
                np.mean([1.0 if set(top) & relevant[r] else 0.0 for r, top in lists.items()])
            ),
            "coverage": float(catalog_coverage(lists.values(), self.data.catalog_ids)),
            "head_share": float(head_share(lists.values(), head)),
            "exposure_gini": float(exposure_gini(lists, self.data.catalog_ids)),
            "author_gini": float(author_exposure_gini(lists, self.data.catalog)),
            "novelty": float(np.mean([novelty(t, counts) for t in lists.values()])),
            "diversity": float(
                np.mean([intra_list_diversity(t, self._similarity) for t in lists.values()])
            ),
        }

    def evaluate(self, path: Any) -> dict[str, float]:
        """The full :meth:`readout` of ``path`` over the val cohort."""
        return self.readout(self.top_lists(path))


def compute_readouts(system: FullSystem) -> dict[str, Any]:
    """The whole-system readout written to ``readouts.json`` (val only).

    ``baselines``: the full stack and the fixed 8-path blend. ``ablation``: exactly the 10
    :data:`ABLATION_ROWS`, each with its own metrics, its declared baseline and signed deltas
    ``d_hit`` / ``d_coverage`` = row − baseline. ``beyond_accuracy``: the full system, the best single
    path and the Part-1 build with all :data:`BEYOND_ACCURACY_COLUMNS` (+ hit).
    """
    full = system.evaluate(system.full_stack)
    fixed = system.evaluate(system.fixed_blend())
    baselines = {"full-stack": full, "fixed-blend": fixed}
    measured = {
        "no-reranker": fixed,
        "exact-two-tower": system.evaluate(system.full_stack_exact),
    }
    for name in FULL8_PATH_NAMES:
        measured[f"minus-{name}"] = system.evaluate(system.fixed_blend(drop=name))
    ablation = []
    for row, kind, baseline in ABLATION_ROWS:
        values = measured[row]
        base = baselines[baseline]
        ablation.append(
            {
                "row": row,
                "kind": kind,
                "baseline": baseline,
                "hit": values["hit"],
                "coverage": values["coverage"],
                "d_hit": values["hit"] - base["hit"],
                "d_coverage": values["coverage"] - base["coverage"],
                "metrics": values,
            }
        )
    beyond_sources = {
        "full-system": full,
        "best-single-path": system.evaluate(system.best_single_path),
        "part1-build": system.evaluate(system.part1_build()),
    }
    beyond = [{"system": name, **beyond_sources[name]} for name in BEYOND_ACCURACY_ROWS]
    return {
        "schema": READOUTS_SCHEMA,
        "schema_version": READOUTS_SCHEMA_VERSION,
        "split": "val",
        "k": K,
        "pool": POOL,
        "cohort_size": len(system.data.cohort),
        "baselines": baselines,
        "ablation": ablation,
        "beyond_accuracy": beyond,
        "beyond_accuracy_columns": list(BEYOND_ACCURACY_COLUMNS),
    }


def check_readouts(readouts: Mapping[str, Any]) -> None:
    """Structural gate (b)/(c) on a readouts dict: exact rows, recomputed deltas, finite, in range.

    Raises :class:`AssertionError` describing the first violation. Used by the build, the required
    check and the Unit-14 milestone.
    """
    assert readouts.get("schema") == READOUTS_SCHEMA, readouts.get("schema")
    assert readouts.get("split") == "val", readouts.get("split")
    baselines = readouts["baselines"]
    assert sorted(baselines) == sorted(BASELINE_ROWS), sorted(baselines)
    rows = readouts["ablation"]
    assert [(r["row"], r["kind"], r["baseline"]) for r in rows] == list(ABLATION_ROWS), [
        r["row"] for r in rows
    ]

    def _finite_unit(value: Any, what: str) -> None:
        assert isinstance(value, (int, float)) and np.isfinite(value), (what, value)
        assert 0.0 <= value <= 1.0, (what, value)

    for name, base in baselines.items():
        _finite_unit(base["hit"], f"{name}.hit")
        _finite_unit(base["coverage"], f"{name}.coverage")
    for row in rows:
        _finite_unit(row["hit"], f"{row['row']}.hit")
        _finite_unit(row["coverage"], f"{row['row']}.coverage")
        base = baselines[row["baseline"]]
        for delta, key in (("d_hit", "hit"), ("d_coverage", "coverage")):
            assert np.isfinite(row[delta]), (row["row"], delta)
            assert abs(row[delta] - (row[key] - base[key])) <= 1e-9, (row["row"], delta)
    beyond = readouts["beyond_accuracy"]
    assert [r["system"] for r in beyond] == list(BEYOND_ACCURACY_ROWS), [
        r["system"] for r in beyond
    ]
    assert list(readouts["beyond_accuracy_columns"]) == list(BEYOND_ACCURACY_COLUMNS)
    for row in beyond:
        for column in ("hit", *BEYOND_ACCURACY_COLUMNS):
            value = row[column]
            assert isinstance(value, (int, float)) and np.isfinite(value), (row["system"], column)
            if column != "novelty":
                assert 0.0 <= value <= 1.0, (row["system"], column, value)
            else:
                assert value >= 0.0, (row["system"], column, value)

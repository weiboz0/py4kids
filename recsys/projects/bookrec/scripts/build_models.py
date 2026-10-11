"""Build the Unit-14 / capstone model cache (plan recsys-017; design 011 §8 row 14, §9).

Fits every expensive model ONCE, seeded and deterministic, and writes its torch-free ``artifact()``
(wrapped in a versioned envelope, pickle protocol 5) to ``recsys/data/generated/models/``:

    mf, two-tower, feature-tower (warm), feature-tower-hard, ann (HNSW over the two-tower; ``load``
    rebuilds the graph), reranker-u11 (the shipped 6-path Unit-11 model), reranker-full8 (the full
    stack's 8-path reranker), sasrec (session log only)

plus ``manifest.json`` (artifact versions, file hashes, the sha256 of the generated data's
``checksums.json``, build timings) and ``readouts.json`` (the 10-row ablation table, both baselines
and the beyond-accuracy table, computed from the freshly built caches; val only).

Both rerankers use the **unchanged Unit-11 leakage-safe recipe** (``u11-holdout-75-25``): train-only
rows; per reader the time-ordered latest 25% of train positives (>= 1) are the labels and the earlier
75% the profile; the feature paths are refit on the profile rows with every occurrence of a held-out
label item removed (via ``path_factory``); ``log_pop`` and the genre/author statistics come from the
profile; serving uses the full-train paths. ``NeuralRerankerPath.assemble_training_matrix`` then
``set_model(RerankerModel(seed=0).fit(X, y))`` — nothing is re-implemented.

Run from the repository root (CI does, right after the data generators)::

    PYTHONHASHSEED=0 uv run --group recsys python recsys/projects/bookrec/scripts/build_models.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
from bookrec import AnnRetrievalPath, HybridRetrievalPath, NeuralRerankerPath, RerankerModel
from bookrec.system import (
    BUILD_COMMAND,
    CACHE_SCHEMA,
    CACHE_SCHEMA_VERSION,
    FULL8_PATH_NAMES,
    HOLDOUT_FRAC,
    HYBRID_WEIGHT,
    MANIFEST_FILE,
    MODEL_NAMES,
    PICKLE_PROTOCOL,
    POOL,
    READOUTS_FILE,
    RERANKER_RECIPE,
    SEED,
    U11_PATH_NAMES,
    BookData,
    FullSystem,
    check_readouts,
    compute_readouts,
    data_hash,
    default_models_dir,
    eight_path_factory,
    file_sha256,
    fit_cheap_paths,
    load_book_data,
    load_cached_models,
    make_envelope,
    make_feature_tower,
    make_mf,
    make_sasrec,
    make_two_tower,
    six_path_factory,
    write_envelope,
)

#: A reduced configuration for the provenance tests: the same code path, tiny epochs.
REDUCED_CONFIG: dict[str, dict[str, Any]] = {
    "mf": {"n_epochs": 20},
    "two-tower": {"n_epochs": 2},
    "feature-tower": {"n_epochs": 2},
}


class _Unserved:
    """A serving-path placeholder for a reranker built only for its artifact (never retrieves)."""

    def __init__(self, name: str) -> None:
        self.name = name

    def retrieve(self, query: Any, context: Any, k: int) -> list[Any]:
        raise RuntimeError(f"{self.name}: placeholder serving path (artifact-only build)")

    def calibrate(self, candidates: Sequence[Any]) -> list[Any]:
        return list(candidates)


def _say(message: str) -> None:
    print(message, flush=True)


# ------------------------------------------------------------------------------ the rerankers
def assemble_reranker(
    serving: Mapping[str, Any],
    path_factory: Callable[[list[dict[str, Any]]], Mapping[str, Any]],
    catalog_books: Mapping[int, Any],
    rows: list[dict[str, Any]],
    path_names: Sequence[str],
) -> tuple[NeuralRerankerPath, np.ndarray, np.ndarray]:
    """The Unit-11 recipe's leakage-safe assembly: holdout split, profile refit, ``(X, y)``."""
    reranker = NeuralRerankerPath(
        serving,
        path_factory,
        catalog_books,
        pool=POOL,
        holdout_frac=HOLDOUT_FRAC,
        seed=SEED,
        path_names=tuple(path_names),
    )
    X, y = reranker.assemble_training_matrix(rows)
    return reranker, X, y


def build_reranker(
    kind: str,
    data: BookData,
    rows: list[dict[str, Any]] | None = None,
    *,
    serving: Mapping[str, Any] | None = None,
    config: Mapping[str, Any] | None = None,
) -> tuple[NeuralRerankerPath, dict[str, Any]]:
    """Build ``reranker-u11`` (6 paths) or ``reranker-full8`` (8 paths) and its cache envelope.

    ``rows`` defaults to the full main log; ``serving`` to artifact-only placeholders; ``config``
    to the pinned hyperparameters (the provenance tests pass :data:`REDUCED_CONFIG`).
    """
    rows = data.rows if rows is None else rows
    if kind == "reranker-u11":
        names, factory = U11_PATH_NAMES, six_path_factory(data, config)
    elif kind == "reranker-full8":
        names, factory = FULL8_PATH_NAMES, eight_path_factory(data, config)
    else:
        raise ValueError(f"unknown reranker {kind!r}")
    serving = serving if serving is not None else {n: _Unserved(n) for n in names}
    reranker, X, y = assemble_reranker(serving, factory, data.catalog, rows, names)
    model = RerankerModel(seed=SEED).fit(X, y)
    reranker.set_model(model)
    meta = {
        "recipe": RERANKER_RECIPE,
        "holdout_frac": HOLDOUT_FRAC,
        "profile_frac": 1.0 - HOLDOUT_FRAC,
        "path_names": list(names),
        "n_features": int(X.shape[1]),
        "training_rows": int(X.shape[0]),
        "positive_rate": float(y.mean()),
        "training_log": list(model.loss_history),
        "training_matrix": {"X": X.copy(), "y": y.copy()},
        "config": {k: dict(v) for k, v in dict(config or {}).items()},
    }
    return reranker, make_envelope(kind, reranker, reranker.artifact(), meta)


# --------------------------------------------------------------------------------- the build
def build_all(out_dir: str | Path | None = None, *, readouts: bool = True) -> dict[str, Any]:
    """Fit, envelope and write every cached model (+ manifest, + readouts). Returns the manifest."""
    t_total = time.perf_counter()
    out = Path(out_dir) if out_dir is not None else default_models_dir()
    out.mkdir(parents=True, exist_ok=True)
    data = load_book_data()
    rows, ids = data.rows, data.catalog_ids
    timings: dict[str, float] = {}
    files: dict[str, dict[str, Any]] = {}

    def done(name: str, envelope: dict[str, Any], started: float) -> None:
        target = write_envelope(out, envelope)
        timings[name] = round(time.perf_counter() - started, 1)
        files[name] = {
            "file": target.name,
            "path_class": envelope["path_class"],
            "path_name": envelope["path_name"],
            "path_version": envelope["path_version"],
            "sha256": file_sha256(target),
            "bytes": target.stat().st_size,
        }
        _say(f"[build] {name}: {timings[name]:.1f}s ({target.stat().st_size} bytes)")

    started = time.perf_counter()
    cheap = fit_cheap_paths(data)
    timings["cheap-paths"] = round(time.perf_counter() - started, 1)

    started = time.perf_counter()
    mf = make_mf().fit(rows, catalog=ids)
    done("mf", make_envelope("mf", mf, mf.artifact()), started)

    started = time.perf_counter()
    two_tower = make_two_tower().fit(rows, catalog=ids)
    done("two-tower", make_envelope("two-tower", two_tower, two_tower.artifact()), started)

    started = time.perf_counter()
    feature_tower = make_feature_tower(data, "warm").fit(rows, catalog=ids)
    done(
        "feature-tower",
        make_envelope("feature-tower", feature_tower, feature_tower.artifact()),
        started,
    )

    started = time.perf_counter()
    hard = make_feature_tower(data, "hard").fit(rows, catalog=ids)
    done("feature-tower-hard", make_envelope("feature-tower-hard", hard, hard.artifact()), started)

    started = time.perf_counter()
    ann = AnnRetrievalPath(two_tower).fit(rows, catalog=ids)
    done("ann", make_envelope("ann", ann, ann.artifact(), {"dense_source": "two-tower"}), started)

    started = time.perf_counter()
    six = {**cheap, "mf": mf, "two-tower": two_tower}
    _rr, envelope = build_reranker("reranker-u11", data, serving=six)
    done("reranker-u11", envelope, started)

    started = time.perf_counter()
    hybrid_ann = HybridRetrievalPath(cheap["lexical"], ann, weight=HYBRID_WEIGHT, pool=POOL).fit(
        rows
    )
    full8 = {**six, "two-tower": ann, "feature-tower": feature_tower, "hybrid": hybrid_ann}
    _rr, envelope = build_reranker("reranker-full8", data, serving=full8)
    done("reranker-full8", envelope, started)

    started = time.perf_counter()
    sasrec = make_sasrec().fit(data.session_rows, catalog=ids)
    done("sasrec", make_envelope("sasrec", sasrec, sasrec.artifact(), {"log": "sessions"}), started)

    manifest: dict[str, Any] = {
        "schema": CACHE_SCHEMA,
        "schema_version": CACHE_SCHEMA_VERSION,
        "pickle_protocol": PICKLE_PROTOCOL,
        "data_hash": data_hash(data.data_dir),
        "seed": SEED,
        "build_command": BUILD_COMMAND,
        "models": list(MODEL_NAMES),
        "artifacts": files,
        "timings_s": timings,
    }
    (out / MANIFEST_FILE).write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")

    if readouts:
        started = time.perf_counter()
        system = FullSystem.from_cache(load_cached_models(out, data_dir=data.data_dir), data)
        table = compute_readouts(system)
        check_readouts(table)
        (out / READOUTS_FILE).write_text(json.dumps(table, indent=1) + "\n", encoding="utf-8")
        timings["readouts"] = round(time.perf_counter() - started, 1)
        manifest["readouts"] = {"file": READOUTS_FILE, "sha256": file_sha256(out / READOUTS_FILE)}
        _say(f"[build] readouts: {timings['readouts']:.1f}s")
    timings["total"] = round(time.perf_counter() - t_total, 1)
    (out / MANIFEST_FILE).write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    _say(f"[build] total: {timings['total']:.1f}s -> {out}")
    return manifest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out", type=Path, default=None, help="cache directory (default: generated/models)"
    )
    parser.add_argument("--no-readouts", action="store_true", help="skip readouts.json")
    args = parser.parse_args(argv)
    build_all(args.out, readouts=not args.no_readouts)
    return 0


if __name__ == "__main__":
    sys.exit(main())

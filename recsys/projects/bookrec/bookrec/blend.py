"""Merge per-path candidates into one calibrated, de-duplicated pool.

Each path's candidates are calibrated to ``[0, 1]`` (so paths are comparable), then unioned by
item id. An item's blended score is the weighted sum of its calibrated per-path scores; its
provenance records every path that proposed it. The result is deterministically ordered
(score desc, then item id asc).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from bookrec.protocol import Candidate, RetrievalPath, calibrate_scores, order_candidates

if TYPE_CHECKING:
    from bookrec.registry import PathRegistry


def blend(
    per_path: Mapping[str, list[Candidate]],
    weights: Mapping[str, float] | None = None,
    paths: Mapping[str, RetrievalPath] | PathRegistry | None = None,
) -> list[Candidate]:
    """Blend ``{path_name: [Candidate, ...]}`` into one ordered, de-duplicated candidate list.

    ``weights`` defaults to ``1.0`` per path; when supplied it must name *exactly* the blended
    paths — a missing or unknown weight key is an error (a typo'd path name silently contributing
    nothing was a foot-gun), raised as :class:`ValueError`.

    ``paths`` optionally maps each path name to its :class:`~bookrec.protocol.RetrievalPath`
    object (or a :class:`~bookrec.registry.PathRegistry`): when given, each path's own
    ``calibrate`` is honoured (design §5 per-path calibrated score semantics) instead of the
    module-level :func:`~bookrec.protocol.calibrate_scores` default. It must name exactly the
    blended paths. Each path is calibrated independently before the weighted sum, so a path with
    larger raw scores does not dominate. Provenance on a blended candidate is the ``+``-joined,
    name-sorted set of contributing paths.
    """
    if weights is not None:
        missing = set(per_path) - set(weights)
        unknown = set(weights) - set(per_path)
        if missing or unknown:
            raise ValueError(
                "weights must name exactly the blended paths; "
                f"missing={sorted(missing)} unknown={sorted(unknown)}"
            )
    if paths is not None:
        path_names = set(paths) if isinstance(paths, Mapping) else set(paths.names())
        missing = set(per_path) - path_names
        unknown = path_names - set(per_path)
        if missing or unknown:
            raise ValueError(
                "paths must name exactly the blended paths; "
                f"missing={sorted(missing)} unknown={sorted(unknown)}"
            )
    scores: dict[int, float] = {}
    provenance: dict[int, set[str]] = {}
    for name, candidates in per_path.items():
        weight = 1.0 if weights is None else float(weights[name])
        calibrate = calibrate_scores
        if paths is not None:
            calibrate = paths.get(name).calibrate
        for cand in calibrate(candidates):
            scores[cand.item_id] = scores.get(cand.item_id, 0.0) + weight * cand.score
            provenance.setdefault(cand.item_id, set()).add(cand.provenance)
    blended = [
        Candidate(item_id, score, "+".join(sorted(provenance[item_id])))
        for item_id, score in scores.items()
    ]
    return order_candidates(blended)

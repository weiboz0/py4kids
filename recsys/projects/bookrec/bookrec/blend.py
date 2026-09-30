"""Merge per-path candidates into one calibrated, de-duplicated pool.

Each path's candidates are calibrated to ``[0, 1]`` (so paths are comparable), then unioned by
item id. An item's blended score is the weighted sum of its calibrated per-path scores; its
provenance records every path that proposed it. The result is deterministically ordered
(score desc, then item id asc).
"""

from __future__ import annotations

from collections.abc import Mapping

from bookrec.protocol import Candidate, calibrate_scores, order_candidates


def blend(
    per_path: Mapping[str, list[Candidate]],
    weights: Mapping[str, float] | None = None,
) -> list[Candidate]:
    """Blend ``{path_name: [Candidate, ...]}`` into one ordered, de-duplicated candidate list.

    ``weights`` defaults to ``1.0`` per path. Each path is calibrated independently before the
    weighted sum, so a path with larger raw scores does not dominate. Provenance on a blended
    candidate is the ``+``-joined, name-sorted set of contributing paths.
    """
    scores: dict[int, float] = {}
    provenance: dict[int, set[str]] = {}
    for name, candidates in per_path.items():
        weight = 1.0 if weights is None else float(weights.get(name, 0.0))
        for cand in calibrate_scores(candidates):
            scores[cand.item_id] = scores.get(cand.item_id, 0.0) + weight * cand.score
            provenance.setdefault(cand.item_id, set()).add(cand.provenance)
    blended = [
        Candidate(item_id, score, "+".join(sorted(provenance[item_id])))
        for item_id, score in scores.items()
    ]
    return order_candidates(blended)

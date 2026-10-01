"""The ``RetrievalPath`` contract shared by every candidate-generation path.

Forward-designed (design 011 §5) so the neural paths of Part 2 need no rewrite of the interface:

- **Stable integer item ids.** Every candidate is a stable ``int`` book id (never a title or a
  row index), so scores from different paths refer to the same items and can be blended.
- ``fit(interactions, catalog=None)`` / ``load(artifact)``. A path is either trained from data or
  restored from its own fitted artifact.
- ``retrieve(query, context, k) -> list[Candidate]``. Returns at most ``k`` candidates, already
  ordered by the path and carrying a ``provenance`` label naming the path.
- **Deterministic tie-break.** When two candidates share a score, the smaller item id ranks first
  (:func:`order_candidates`), so results are reproducible run to run.
- **Candidate limit ``k``.** Retrieval is always bounded; ``k`` is honoured exactly.
- **Calibrated / normalised scores before blending.** Raw path scores are not comparable across
  paths, so a path exposes :meth:`RetrievalPath.calibrate` (default min-max to ``[0, 1]`` via
  :func:`calibrate_scores`) and blending consumes calibrated scores.
- **Per-path artifact ownership / versioning.** A path owns exactly one artifact, named
  ``{name}-v{version}`` (:meth:`RetrievalPath.artifact_name`); the registry enforces that no two
  registered paths own the same artifact.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=True, order=False)
class Candidate:
    """One retrieved item: a stable int id, a score, and the path that produced it."""

    item_id: int
    score: float
    provenance: str

    def __post_init__(self) -> None:
        if not isinstance(self.item_id, int) or isinstance(self.item_id, bool):
            raise TypeError(f"item_id must be a stable int, got {self.item_id!r}")
        if not math.isfinite(self.score):
            raise ValueError(f"score must be finite, got {self.score!r}")
        if not isinstance(self.provenance, str) or not self.provenance:
            raise ValueError("provenance must be a non-empty string")


def order_candidates(candidates: list[Candidate]) -> list[Candidate]:
    """Order by score descending, breaking ties by ascending item id (deterministic)."""
    return sorted(candidates, key=lambda c: (-c.score, c.item_id))


def calibrate_scores(candidates: list[Candidate]) -> list[Candidate]:
    """Min-max calibrate scores into ``[0, 1]`` so paths are comparable before blending.

    A single candidate, or an all-equal set, calibrates to ``1.0`` (present-but-uninformative).
    Ordering is preserved; ids and provenance are untouched.
    """
    if not candidates:
        return []
    scores = [c.score for c in candidates]
    low, high = min(scores), max(scores)
    span = high - low
    if span == 0:
        return [Candidate(c.item_id, 1.0, c.provenance) for c in candidates]
    return [Candidate(c.item_id, (c.score - low) / span, c.provenance) for c in candidates]


def top_k(candidates: list[Candidate], k: int) -> list[Candidate]:
    """Deterministically order candidates and keep at most ``k`` (``k`` must be positive)."""
    if not isinstance(k, int) or isinstance(k, bool) or k <= 0:
        raise ValueError(f"k must be a positive int, got {k!r}")
    return order_candidates(candidates)[:k]


@runtime_checkable
class RetrievalPath(Protocol):
    """Structural contract for a retrieval path (a candidate generator).

    Implementations set :attr:`name` and :attr:`version` and provide
    ``fit``/``load``/``retrieve``, plus the ``calibrate`` and ``artifact_name`` contract members
    (so a per-path calibrator is honoured by :func:`~bookrec.blend.blend` and artifact ownership
    is enforced by the registry for every path — not only :class:`BaseRetrievalPath` subclasses).
    """

    name: str
    version: str

    def fit(self, interactions: Any, catalog: Any | None = ...) -> RetrievalPath: ...

    def load(self, artifact: Any) -> RetrievalPath: ...

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]: ...

    def calibrate(self, candidates: list[Candidate]) -> list[Candidate]: ...

    def artifact_name(self) -> str: ...


@dataclass
class BaseRetrievalPath:
    """A convenience base that supplies the shared contract behaviour.

    Subclasses set :attr:`name` / :attr:`version` and override :meth:`_score` (or ``retrieve``).
    It provides deterministic ordering, the ``k`` bound, calibration, and artifact naming so every
    path behaves identically where the contract is fixed.
    """

    name: str = "base"
    version: str = "1"
    _fitted: bool = field(default=False, repr=False)

    def fit(self, interactions: Any, catalog: Any | None = None) -> BaseRetrievalPath:
        raise NotImplementedError

    def load(self, artifact: Any) -> BaseRetrievalPath:
        raise NotImplementedError

    def calibrate(self, candidates: list[Candidate]) -> list[Candidate]:
        return calibrate_scores(candidates)

    def artifact_name(self) -> str:
        """The single artifact this path owns and versions."""
        return f"{self.name}-v{self.version}"

    def _finish(self, candidates: list[Candidate], k: int) -> list[Candidate]:
        """Deterministically order and bound raw candidates for ``retrieve``."""
        return top_k(candidates, k)

    def retrieve(self, query: Any, context: Any, k: int) -> list[Candidate]:
        raise NotImplementedError

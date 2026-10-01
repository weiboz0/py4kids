"""A popularity retrieval path used ONLY as a test fixture.

Design 011 §5/§8: a real popularity impl is Unit 2. This fixture exercises the foundation
contract — stable int ids, ``fit``, ``retrieve(q, ctx, k)``, deterministic tie-break, calibrated
scores, artifact ownership — without prejudging Unit 2's design. It is deliberately outside the
shipped ``bookrec`` package.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from bookrec.protocol import BaseRetrievalPath, Candidate


class PopularityPath(BaseRetrievalPath):
    """Rank items by observed interaction count; a fixture, not a shipped path."""

    def __init__(self, name: str = "popularity", version: str = "1") -> None:
        super().__init__(name=name, version=version)
        self._counts: dict[int, int] = {}

    def fit(self, interactions: Iterable[int], catalog: object | None = None) -> PopularityPath:
        self._counts = dict(Counter(int(item_id) for item_id in interactions))
        self._fitted = True
        return self

    def load(self, artifact: dict[int, int]) -> PopularityPath:
        self._counts = {int(k): int(v) for k, v in artifact.items()}
        self._fitted = True
        return self

    def retrieve(self, query: object, context: object, k: int) -> list[Candidate]:
        if not self._fitted:
            raise RuntimeError("PopularityPath.retrieve before fit/load")
        raw = [
            Candidate(item_id, float(count), self.name)
            for item_id, count in self._counts.items()
        ]
        return self._finish(raw, k)

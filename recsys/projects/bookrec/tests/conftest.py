"""Fixtures for the bookrec tests."""

from __future__ import annotations

import pytest
from bookrec import PopularityRetrievalPath


def _train_positive(item_id: int) -> dict[str, object]:
    """One positive train-split interaction row (the shape ``fit`` counts)."""
    return {
        "reader_id": 0,
        "item_id": item_id,
        "session_id": 0,
        "timestamp": 0,
        "split": "train",
        "label": 1,
    }


@pytest.fixture
def interactions() -> list[dict[str, object]]:
    # Positive train rows so item 10 is counted 4x, 20 3x, 30 & 40 tie at 2x, 50 1x.
    counts = {10: 4, 20: 3, 30: 2, 40: 2, 50: 1}
    return [_train_positive(item_id) for item_id, n in counts.items() for _ in range(n)]


@pytest.fixture
def popularity(interactions: list[dict[str, object]]) -> PopularityRetrievalPath:
    return PopularityRetrievalPath().fit(interactions)

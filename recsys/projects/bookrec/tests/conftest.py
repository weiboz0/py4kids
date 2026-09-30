"""Fixtures for the bookrec tests."""

from __future__ import annotations

import pytest
from _popularity_fixture import PopularityPath


@pytest.fixture
def interactions() -> list[int]:
    # item 10 seen 4x, item 20 3x, item 30 & 40 tie at 2x, item 50 1x.
    return [10, 10, 10, 10, 20, 20, 20, 30, 30, 40, 40, 50]


@pytest.fixture
def popularity(interactions: list[int]) -> PopularityPath:
    return PopularityPath().fit(interactions)

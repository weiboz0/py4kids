"""Fixtures for the recsys data-substrate invariant tests."""

from __future__ import annotations

import pytest
from _common import DatasetConfig
from _dataset_fixture import small_config
from gen_interactions import Interactions, build_dataset


@pytest.fixture(scope="module")
def config() -> DatasetConfig:
    return small_config()


@pytest.fixture(scope="module")
def dataset(config: DatasetConfig) -> Interactions:
    return build_dataset(config)

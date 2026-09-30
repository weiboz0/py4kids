"""Shared helpers for the data-substrate tests.

Imported by both ``conftest.py`` and the test module (uniquely named to avoid the ``conftest``
module-name clash with the sibling ``bookrec`` test suite when pytest collects all of ``recsys/``).
Puts ``recsys/data`` on ``sys.path`` so the seeded generators import as plain modules.
"""

from __future__ import annotations

import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1]
if str(DATA_DIR) not in sys.path:
    sys.path.insert(0, str(DATA_DIR))

from _common import DatasetConfig


def small_config() -> DatasetConfig:
    """A small, fast, fully-deterministic dataset config for the invariant tests."""
    return DatasetConfig(
        seed=12345,
        n_books=400,
        n_authors=60,
        n_genres=8,
        latent_dim=8,
        n_readers=120,
        n_cold_items=40,
        n_cold_readers=20,
        mean_sessions_per_reader=6.0,
    )

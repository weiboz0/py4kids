"""Locate the seeded generated data used by the recommendation-system book."""

from __future__ import annotations

from pathlib import Path


def generated_dir() -> Path:
    """Return ``recsys/data/generated`` and fail clearly when it needs regeneration."""
    path = Path(__file__).resolve().parents[3] / "data" / "generated"
    if not path.is_dir():
        raise FileNotFoundError(
            f"generated recsys data is missing at {path}; run the recsys data generators first"
        )
    return path

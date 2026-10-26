"""Put ``roar/data`` on ``sys.path`` for its test suite, so ``gen_tracks`` and ``generate`` import
as plain modules (the recsys/data pattern)."""

from __future__ import annotations

import sys
from pathlib import Path

_DATA_DIR = str(Path(__file__).resolve().parent)
if _DATA_DIR not in sys.path:
    sys.path.insert(0, _DATA_DIR)

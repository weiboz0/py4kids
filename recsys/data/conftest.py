"""Put ``recsys/data`` on ``sys.path`` for its test suite.

pytest imports ancestor-directory conftests before the test modules and their sibling conftest, so
this runs first and the seeded generators (``_common``, ``gen_catalog``, ``gen_interactions``,
``slice_books``) import as plain modules regardless of import order within a test file.
"""

from __future__ import annotations

import sys
from pathlib import Path

_DATA_DIR = str(Path(__file__).resolve().parent)
if _DATA_DIR not in sys.path:
    sys.path.insert(0, _DATA_DIR)

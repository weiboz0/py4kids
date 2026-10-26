"""racekit: the race harness for *Applied Python: Autonomous Racing* (design 013 §4).

A harness and analysis toolkit, never a dependency of a submission. The core (the
``roar_py_interface`` shim, the runner, track loading, cars and ``check_submission``) imports numpy
only; scipy and matplotlib are imported lazily by the analysis modules that need them. Every module
is Python 3.8-compatible.
"""

from __future__ import annotations

from .variants import write_variant

__version__ = "0.1.0"
__all__ = ["write_variant"]

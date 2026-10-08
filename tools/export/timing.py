"""The fixture timing cache: `check.cpu_ms` of every `fixtures` item (plan 104 Phase C, "Budgets").

The site gives each fixture case a budget of max(1 s, 10 x `cpu_ms`), capped at 10 s. `cpu_ms` is the
reference solver's **maximum** CPython CPU time across the item's cases, rounded up to the next
100 ms and clamped to [`MIN_MS`, `MAX_MS`].

The measurements live in a committed cache, `tools/export/timings/<book>.json`, so an export is
deterministic and fast and the bundle's `content_hash` never depends on machine jitter:

    {"version": 1, "book": "<book>",
     "items": {"<item key>": {"cpu_ms": 100, "measured_ms": 23, "cases": 5,
                              "fingerprint": "sha256:..."}}}

`fingerprint` is sha256 over the solver's bytes and every fixture pair's bytes (`answers.py`
computes it, as it does every read of solution material). A plain export reads the cache and FAILs
on a missing or stale entry (never a silent default); only `py4kids-tools --book <b> export
--measure` re-measures (with `tools/judge.py`'s runner, `answers.measure_solver`) and rewrites the
cache, keeping exactly the entries the export used.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

CACHE_DIR = Path("tools") / "export" / "timings"
CACHE_VERSION = 1
STEP_MS = 100
MIN_MS = 100
MAX_MS = 10_000


def cache_path(root: Path, book: str) -> Path:
    return Path(root) / CACHE_DIR / f"{book}.json"


def round_ms(measured_ms: float) -> int:
    """Up to the next 100 ms, clamped to [MIN_MS, MAX_MS]."""
    rounded = math.ceil(max(0.0, float(measured_ms)) / STEP_MS) * STEP_MS
    return int(min(MAX_MS, max(MIN_MS, rounded)))


def _measure_hint(book: str) -> str:
    return f"run `py4kids-tools --book {book} export --measure` and commit {CACHE_DIR}/{book}.json"


class TimingCache:
    """One book's timing cache. With `measure`, `cpu_ms` re-measures every item and `save` rewrites
    the file with exactly the items seen; otherwise `cpu_ms` reads the committed entry."""

    def __init__(self, root: Path, book: str, measure: bool = False):
        self.root, self.book, self.measure = Path(root), book, measure
        self.path = cache_path(root, book)
        self.items: dict[str, dict] = {}
        self.seen: dict[str, dict] = {}
        if self.path.is_file():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or data.get("version") != CACHE_VERSION:
                raise ValueError(f"FAIL: {self.book}: {CACHE_DIR}/{book}.json is not a version "
                                 f"{CACHE_VERSION} timing cache; {_measure_hint(book)}")
            self.items = dict(data.get("items") or {})

    def entry(self, key: str) -> dict | None:
        found = self.items.get(key)
        return found if isinstance(found, dict) else None

    def check(self, key: str, fingerprint: str) -> int:
        """The cached `cpu_ms` of `key`, or a FAIL when the entry is missing or stale."""
        found = self.entry(key)
        if found is None or not isinstance(found.get("cpu_ms"), int):
            raise ValueError(f"FAIL: {key}: no timing in {CACHE_DIR}/{self.book}.json; "
                             f"{_measure_hint(self.book)}")
        if found.get("fingerprint") != fingerprint:
            raise ValueError(f"FAIL: {key}: stale timing in {CACHE_DIR}/{self.book}.json (the "
                             f"solver or its fixtures changed); {_measure_hint(self.book)}")
        return found["cpu_ms"]

    def cpu_ms(self, key: str, fingerprint: str, measure) -> int:
        """`key`'s `cpu_ms`. In measure mode `measure()` gives (the max case time in ms, the
        number of cases) and the entry is replaced."""
        if self.measure:
            measured, cases = measure()
            self.seen[key] = {"cpu_ms": round_ms(measured), "measured_ms": round(float(measured)),
                              "cases": int(cases), "fingerprint": fingerprint}
            return self.seen[key]["cpu_ms"]
        value = self.check(key, fingerprint)
        self.seen[key] = self.items[key]
        return value

    def data(self) -> dict:
        return {"version": CACHE_VERSION, "book": self.book,
                "items": {key: self.seen[key] for key in sorted(self.seen)}}

    def save(self) -> None:
        """Rewrite the cache (measure mode only) with exactly the items this export used."""
        if not self.measure:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data(), sort_keys=True, indent=1) + "\n",
                             encoding="utf-8")

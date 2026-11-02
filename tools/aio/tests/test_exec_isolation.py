"""The invariant behind ci_scope.route_exec's `scoped` route (plan aio-001 Phase E).

A scoped route executes only the changed unit and mock-test folders, so it is sound only while
no aio code cell reads another unit's folder, another mock test's folder, or the other book.
"""

from __future__ import annotations

import json
import re

import yaml
from conftest import ROOT

_REF = re.compile(r"\b(units|mocktests)/([0-9A-Za-z][0-9A-Za-z-]*)")


def _aio_roots() -> list[str]:
    registry = yaml.safe_load((ROOT / "books.yaml").read_text(encoding="utf-8"))
    return [
        book.get("root", book["id"])
        for book in registry["books"]
        if book.get("content_model") == "aio"
    ]


def _code_sources(path):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            source = cell["source"]
            yield "".join(source) if isinstance(source, list) else source


def test_no_aio_code_cell_reads_another_unit_mocktest_or_book():
    roots = _aio_roots()
    assert len(roots) >= 2
    violations = []
    scanned = 0
    for root in roots:
        others = [other for other in roots if other != root]
        for kind in ("units", "mocktests"):
            for folder in sorted((ROOT / root / kind).iterdir()):
                if not folder.is_dir():
                    continue
                for notebook in sorted(folder.rglob("*.ipynb")):
                    if ".ipynb_checkpoints" in notebook.parts:
                        continue
                    scanned += 1
                    relative = notebook.relative_to(ROOT).as_posix()
                    for source in _code_sources(notebook):
                        for match in _REF.finditer(source):
                            if (match[1], match[2]) != (kind, folder.name):
                                violations.append(f"{relative}: {match[0]}")
                        violations += [
                            f"{relative}: names {other}"
                            for other in others
                            if re.search(rf"(?<![\w-]){re.escape(other)}(?![\w-])", source)
                        ]
    assert scanned > 700
    assert violations == []

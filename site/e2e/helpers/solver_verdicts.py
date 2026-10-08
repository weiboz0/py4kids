"""CPython's verdict on every reference solver case, by ``tools/judge.py`` (plan 104 Phase D).

Run from the repository root by ``e2e/solvers.spec.ts`` at test time:
``uv run python site/e2e/helpers/solver_verdicts.py``. It walks every ``judge: true`` book exactly
as ``tools.judge.judge_findings`` does (the same entries, the same solver stems, the same fixture
pairs) and runs each case with the judge's own ``_run_case``, so the verdict is the judge's. It
prints one JSON document: per solver, its book, entry, stem, matching mode (line-exact in ``acsl``
books), the per-case CPython CPU time (the site's budget input) and each case's verdict as a
category (``pass``, ``time limit``, ``failed``, ``no output``, ``wrong output``).

The browser test then runs the same solver against the same pairs in Pyodide through the runner
and requires the same category for every case. Solvers and fixtures are read from the repo here
and by the test; nothing is shipped.
"""

from __future__ import annotations

import json
import os
import resource
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from tools.books import book_flag
from tools.judge import (
    SOLVER_STEM,
    _expected_pids,
    _fixture_pairs,
    _run_case,
)
from tools.notebooks import content_dirs


def _category(problem: str | None) -> str:
    """The judge's finding (or None) as the runner's verdict category."""
    if problem is None:
        return "pass"
    if " exceeded " in problem:
        return "time limit"
    if " produced no output " in problem:
        return "no output"
    if " wrong output " in problem:
        return "wrong output"
    if " failed on " in problem:
        return "failed"
    raise ValueError(f"unrecognised judge finding: {problem}")


def _judge(task: tuple[str, str, str, str, bool]) -> dict:
    """One case through the judge's own runner, with its child CPU time."""
    script, inp, outp, stem, line_exact = task
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    problem = _run_case(Path(script), Path(inp), Path(outp), "parity", stem, line_exact=line_exact)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = 1000 * ((after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime))
    return {"verdict": _category(problem), "problem": problem, "cpu_ms": cpu}


def solvers(root: Path) -> list[dict]:
    """Every judged solver of every judge book, with its fixture pairs (judge_findings' walk)."""
    import yaml

    catalog = yaml.safe_load((root / "books.yaml").read_text(encoding="utf-8"))
    out = []
    for book in [b["id"] for b in catalog["books"]]:
        if not book_flag(root, book, "judge"):
            continue
        line_exact = book_flag(root, book, "acsl")
        entries, findings = content_dirs(root, book)
        if findings:
            raise SystemExit("\n".join(findings))
        for entry_dir, kind in entries:
            assets = entry_dir / "assets"
            if not assets.is_dir():
                continue
            expected = _expected_pids(entry_dir, kind)
            for script in sorted(assets.glob("*.py")):
                stem = script.stem
                if not (stem in expected or SOLVER_STEM.match(stem)):
                    continue
                pairs = _fixture_pairs(assets / stem, entry_dir.name, stem, [])
                out.append({
                    "book": book,
                    "entry": entry_dir.name,
                    "stem": stem,
                    "solver": str(script.relative_to(root)),
                    "match": "line" if line_exact else "token",
                    "cases": [
                        {"name": inp.name, "in": str(inp.relative_to(root)),
                         "out": str(outp.relative_to(root))}
                        for inp, outp in pairs
                    ],
                })
    return out


def main() -> None:
    items = solvers(REPO)
    tasks = [
        (str(REPO / item["solver"]), str(REPO / case["in"]), str(REPO / case["out"]),
         item["stem"], item["match"] == "line")
        for item in items
        for case in item["cases"]
    ]
    with ProcessPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
        verdicts = iter(list(pool.map(_judge, tasks, chunksize=8)))
    for item in items:
        for case in item["cases"]:
            case.update(next(verdicts))
    json.dump(items, sys.stdout)


if __name__ == "__main__":
    main()

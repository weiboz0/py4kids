"""Collision and public-repository safety checks for the pre-merge guard."""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

import yaml

# One-release transition map (plan 091, design 008): branches cut before the book rename still
# carry the old root folders; normalise them so their unit/project/checkpoint ids collide-check
# against the new roots. Remove after one release.
TRANSITION = {"book1b": "python-concepts", "book1": "python-projects", "book2": "usaco-bronze"}  # plan-091-transition


def normalise(path: str) -> str:
    for old, new in TRANSITION.items():
        if path.startswith(old + "/"):
            return new + path[len(old) :]
    return path


def _merged_paths(path_sets: Mapping[str, Iterable[str]]) -> set[str]:
    """Return the pathname-deduplicated union of all injected refs."""
    return {normalise(path) for paths in path_sets.values() for path in paths}


def _duplicate_failure(label: str, names: Iterable[str], pattern: str) -> list[str]:
    numbers = [match.group(0) for name in names if (match := re.match(pattern, name))]
    duplicates = sorted(value for value, count in Counter(numbers).items() if count > 1)
    if not duplicates:
        return []
    return [f"duplicate {label} number(s): {' '.join(duplicates)}"]


def plan_collision_failures(path_sets: Mapping[str, Iterable[str]]) -> list[str]:
    """Find top-level and immediate namespaced plan-number collisions."""
    paths = _merged_paths(path_sets)
    failures = _duplicate_failure(
        "docs/plans",
        {
            path.rsplit("/", 1)[-1]
            for path in paths
            if path.startswith("docs/plans/") and path.count("/") == 2 and path.endswith(".md")
        },
        r"^[0-9]{3}(?=-)",
    )

    namespaces = sorted(
        parts[2]
        for path in paths
        if path.startswith("docs/plans/") and len(parts := path.split("/")) >= 4
    )
    for namespace in dict.fromkeys(namespaces):
        prefix = f"docs/plans/{namespace}/"
        names = {
            path[len(prefix) :]
            for path in paths
            if path.startswith(prefix)
            and path.count("/") == 3
            and path.endswith(".md")
        }
        failures.extend(
            _duplicate_failure(
                f"docs/plans/{namespace}",
                names,
                rf"^{re.escape(namespace)}-[0-9]{{3}}(?=-)",
            )
        )
    return failures


def collision_failures(
    path_sets: Mapping[str, Iterable[str]], book_roots: Iterable[str]
) -> list[str]:
    """Find all document and course-entry number collisions."""
    paths = _merged_paths(path_sets)
    failures: list[str] = []

    for directory in ("docs/proposals", "docs/designs", "docs/reviews"):
        names = {
            path.rsplit("/", 1)[-1]
            for path in paths
            if path.startswith(directory + "/")
            and path.count("/") == directory.count("/") + 1
            and path.endswith(".md")
        }
        failures.extend(_duplicate_failure(directory, names, r"^[0-9]{3}(?=-)"))

    failures.extend(plan_collision_failures({"union": paths}))

    for book_id in book_roots:
        for kind, pattern in (
            ("units", r"^unit-[0-9]{2}(?=-)"),
            ("projects", r"^project-[0-9]{2}(?=-)"),
            ("checkpoints", r"^checkpoint-[0-9]{2}(?=-)"),
        ):
            prefix = f"{book_id}/{kind}/"
            names = {
                path[len(prefix) :].split("/", 1)[0]
                for path in paths
                if path.startswith(prefix) and "/" in path[len(prefix) :]
            }
            failures.extend(_duplicate_failure(f"{book_id}/{kind}", names, pattern))
    return failures


# aio-model books (design 014; plan aio-001 Phase D). Their ids follow usaaio's layout, keyed on
# `content_model: aio`, never on a book id: `units/NN-<code>-<slug>` (teaching-order prefix NN and
# unit code such as `C5`), `units/B2-0NN-<slug>`, and `mocktests/rN-NNN`.
_AIO_UNIT_ORDER = r"^[0-9]{2}(?=-)"
_AIO_UNIT_CODE = re.compile(r"^[0-9]{2}-(?P<code>[A-Z]+[0-9]+)(?=-)")
_AIO_ROUND2_UNIT = r"^B2-[0-9]{3}(?=-)"
_AIO_MOCKTEST = r"^r[0-9]+-[0-9]{3}(?![0-9])"
# The D3 ignore rules as tracked-path refusals (design 014 D3; the repo is PUBLIC): under an aio
# root, `reference/*` other than `.gitkeep`/`analysis.md` (raw past papers, the download cache),
# the two hidden sets and the five C11 grading artifacts, all book-root-relative.
_AIO_REFERENCE_KEEP = frozenset({"reference/.gitkeep", "reference/analysis.md"})
_AIO_IGNORED_FILES = frozenset({
    "units/18-C11-competition-craft/data/heldout.csv",
    "mocktests/r1-001/data/p09_heldout.csv",
    "units/18-C11-competition-craft/practice/p15_contract.csv",
    "units/18-C11-competition-craft/practice/p17_log.csv",
    "units/18-C11-competition-craft/practice/p17_predictions.csv",
    "units/18-C11-competition-craft/practice/p18_audit.csv",
    "units/18-C11-competition-craft/practice/p18_predictions.csv",
})


def _child_names(paths: Iterable[str], prefix: str) -> set[str]:
    return {
        path[len(prefix) :].split("/", 1)[0]
        for path in paths
        if path.startswith(prefix) and "/" in path[len(prefix) :]
    }


def aio_collision_failures(
    path_sets: Mapping[str, Iterable[str]], aio_roots: Iterable[str]
) -> list[str]:
    """Find aio unit-id and mock-test-id collisions under each `content_model: aio` root."""
    paths = _merged_paths(path_sets)
    failures: list[str] = []
    for root in aio_roots:
        units = _child_names(paths, f"{root}/units/")
        failures.extend(_duplicate_failure(f"{root}/units order", units, _AIO_UNIT_ORDER))
        codes = [match["code"] for name in units if (match := _AIO_UNIT_CODE.match(name))]
        duplicates = sorted(code for code, count in Counter(codes).items() if count > 1)
        if duplicates:
            failures.append(f"duplicate {root}/units code(s): {' '.join(duplicates)}")
        failures.extend(_duplicate_failure(f"{root}/units", units, _AIO_ROUND2_UNIT))
        mocktests = _child_names(paths, f"{root}/mocktests/")
        failures.extend(_duplicate_failure(f"{root}/mocktests", mocktests, _AIO_MOCKTEST))
    return failures


def aio_tracked_path_failures(tracked: Iterable[str], aio_roots: Iterable[str]) -> list[str]:
    """Refuse tracked files the D3 ignore rules keep local-only under an aio root."""
    failures: list[str] = []
    roots = list(aio_roots)
    for path in sorted(tracked):
        for root in roots:
            if not path.startswith(root + "/"):
                continue
            relative = path[len(root) + 1 :]
            if relative.startswith("reference/") and relative not in _AIO_REFERENCE_KEEP:
                failures.append(f"tracked local-only aio reference file: {path}")
            elif relative in _AIO_IGNORED_FILES:
                failures.append(f"tracked local-only aio grading file: {path}")
    return failures


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )


def _git_lines(root: Path, *args: str) -> list[str]:
    proc = _git(root, *args)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.splitlines()


def _paths(root: Path, ref: str) -> set[str]:
    if ref == "WORKTREE":
        return {
            path.relative_to(root).as_posix()
            for path in root.rglob("*")
            if path.is_file()
            and ".git" not in path.relative_to(root).parts
            and ".venv" not in path.relative_to(root).parts
        }
    return set(_git_lines(root, "ls-tree", "-r", "--name-only", ref))


def guard_failures(root: Path, refs: Sequence[str]) -> list[str]:
    path_sets = {ref: _paths(root, ref) for ref in refs}
    registry = yaml.safe_load((root / "books.yaml").read_text(encoding="utf-8"))
    # The unit-/project-/checkpoint-NN rules are py4kids layout (design 014 D1); aio roots get
    # their own id rules (aio_collision_failures, keyed on content_model: aio).
    book_roots = [
        book.get("root", book["id"])
        for book in registry["books"]
        if book.get("content_model", "py4kids") == "py4kids"
    ]
    failures = collision_failures(path_sets, book_roots)
    aio_roots = [
        book.get("root", book["id"])
        for book in registry["books"]
        if book.get("content_model", "py4kids") == "aio"
    ]
    failures.extend(aio_collision_failures(path_sets, aio_roots))

    tracked = _git_lines(root, "ls-files")
    failures.extend(aio_tracked_path_failures(tracked, aio_roots))
    for path in sorted(tracked):
        name = path.rsplit("/", 1)[-1].lower()
        if name == ".gh-token" or name.startswith(".env") or name.endswith((".pem", ".key")):
            failures.append(f"tracked secret-like file: {path}")
        if any(segment in ("student-data", "rosters", "grades") for segment in path.split("/")):
            failures.append(f"tracked student-data path: {path}")

    conflicts = _git(
        root,
        "grep",
        "-nE",
        r"^(<{7}|={7}|>{7})( |$)",
        "--",
        ":!scripts/pre-merge-guard.sh",
    )
    if conflicts.returncode == 0:
        failures.append("conflict markers found")
    elif conflicts.returncode != 1:
        raise RuntimeError(f"git grep failed: {conflicts.stderr.strip()}")
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) > 1 or (args and args[0] != "--pr"):
        detail = f"   (unknown argument: {args[0]})" if args else ""
        print(f"usage: pre-merge-guard.sh [--pr]{detail}", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[1]
    refs = ["WORKTREE"]
    if args == ["--pr"]:
        fetch = _git(
            root,
            "fetch",
            "-q",
            "origin",
            "+refs/heads/main:refs/remotes/origin/main",
        )
        if fetch.returncode != 0:
            print("FAIL: origin/main fetch unavailable; --pr union is unverified", file=sys.stderr)
            return 1
        refs.append("origin/main")

    try:
        failures = guard_failures(root, refs)
    except RuntimeError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    for failure in failures:
        print(f"FAIL: {failure}")
    if not failures:
        print("pre-merge-guard: OK")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
# Collision and public-repository safety guard.
set -euo pipefail
cd "$(dirname "$0")/.."

if (($# > 1)); then
  echo "usage: pre-merge-guard.sh [--pr]" >&2
  exit 2
fi
mode=${1:-}
if [[ -n "$mode" && "$mode" != --pr ]]; then
  echo "usage: pre-merge-guard.sh [--pr]   (unknown argument: $mode)" >&2
  exit 2
fi
if [[ "$mode" == --pr ]]; then
  # Explicit refspec: a bare `git fetch origin main` only guarantees FETCH_HEAD,
  # so the guard could read a stale refs/remotes/origin/main and miss collisions.
  if ! git fetch -q origin "+refs/heads/main:refs/remotes/origin/main" 2>/dev/null; then
    echo "FAIL: origin/main fetch unavailable; --pr union is unverified" >&2
    exit 1
  fi
fi

uv run python - "$mode" <<'PY'
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

mode = sys.argv[1]
refs = ["WORKTREE"] + (["origin/main"] if mode == "--pr" else [])
failures: list[str] = []


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False)


def git_lines(*args: str) -> list[str]:
    proc = git(*args)
    if proc.returncode != 0:
        sys.exit(f"FAIL: git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.splitlines()


def paths(ref: str) -> set[str]:
    if ref == "WORKTREE":
        return {
            path.as_posix()
            for path in Path(".").rglob("*")
            if path.is_file() and ".git" not in path.parts and ".venv" not in path.parts
        }
    return set(git_lines("ls-tree", "-r", "--name-only", ref))


def duplicate_numbers(label: str, names: set[str], pattern: str) -> None:
    numbers = [match.group(0) for name in names if (match := re.match(pattern, name))]
    duplicates = sorted(value for value, count in Counter(numbers).items() if count > 1)
    if duplicates:
        failures.append(f"duplicate {label} number(s): {' '.join(duplicates)}")


all_paths = {ref: paths(ref) for ref in refs}

for directory in ("docs/proposals", "docs/designs", "docs/plans", "docs/reviews"):
    names = {
        path.split("/")[-1]
        for ref in refs
        for path in all_paths[ref]
        if path.startswith(directory + "/")
        and path.count("/") == directory.count("/") + 1
        and path.endswith(".md")
    }
    duplicate_numbers(directory, names, r"^[0-9]{3}(?=-)")

for book_id in ("book1", "book2"):
    for kind, pattern in (
        ("units", r"^unit-[0-9]{2}(?=-)"),
        ("projects", r"^project-[0-9]{2}(?=-)"),
        ("checkpoints", r"^checkpoint-[0-9]{2}(?=-)"),
    ):
        prefix = f"{book_id}/{kind}/"
        names = {
            path[len(prefix):].split("/", 1)[0]
            for ref in refs
            for path in all_paths[ref]
            if path.startswith(prefix) and "/" in path[len(prefix):]
        }
        duplicate_numbers(f"{book_id}/{kind}", names, pattern)

tracked = set(git_lines("ls-files"))
for path in sorted(tracked):
    name = path.rsplit("/", 1)[-1].lower()
    if name == ".gh-token" or name.startswith(".env") or name.endswith((".pem", ".key")):
        failures.append(f"tracked secret-like file: {path}")
    if any(segment in ("student-data", "rosters", "grades") for segment in path.split("/")):
        failures.append(f"tracked student-data path: {path}")

conflicts = git("grep", "-nE", r"^(<{7}|={7}|>{7})( |$)", "--", ":!scripts/pre-merge-guard.sh")
if conflicts.returncode == 0:
    failures.append("conflict markers found")
elif conflicts.returncode != 1:
    sys.exit(f"FAIL: git grep failed: {conflicts.stderr.strip()}")

for failure in failures:
    print(f"FAIL: {failure}")
if not failures:
    print("pre-merge-guard: OK")
raise SystemExit(bool(failures))
PY

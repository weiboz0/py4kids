"""Import the usaaio books into py4kids (design 014 D3; plan aio-001 Phase B).

A one-off, recorded migration script. It reads the usaaio repository at a pinned commit
(never its working tree or index, and never writes to it) and writes:

- the live destinations (book roots, `tools/aio/`, `scripts/aio/`, the live docs) into the
  py4kids tree, renamed by RULES;
- the read-only archive (every other `docs/` file, byte-identical) into a staging directory
  outside the repository, to be copied in once its overlap scan passes;
- `docs/history/aio-import/import-report.md`.

Usage:
  python import-usaaio.py --source ../usaaio --sha a20128f --dest <py4kids root> \
      --archive-stage /dev/shm/aio-archive [--dry-run] [--archive-only]

`--dry-run` writes nothing to --dest; it writes the live tree to --dest-dry instead and
evaluates the acceptance outcomes (a)-(d) of the plan. The script exits non-zero when any
outcome fails.
"""
from __future__ import annotations

import argparse
import ast
import collections
import re
import shutil
import subprocess
import sys
from pathlib import Path

MAP = {"1": "aio-ml", "2": "aio-dl"}

# Moved to aio-ml/docs/ (design D3 "live rendered docs"); value = destination file name.
LIVE_DOCS = {
    "docs/unit-standards.md": "unit-standards.md",
    "docs/mocktest-generation.md": "mocktest-generation.md",
    "docs/curriculum-architecture.md": "curriculum-architecture.md",
    "docs/curriculum-roadmap.md": "curriculum-roadmap.md",
    "docs/audits/015-coverage-audit.md": "coverage-audit.md",
    "docs/audits/015-plan014-reconciliation.md": "015-plan014-reconciliation.md",
}

PORTED_SCRIPTS = {
    "scripts/verify-register.py", "scripts/fetch-reference.sh", "scripts/verify-clean-checkout.sh",
    "scripts/verify-comment-only.py", "scripts/build-pdf.sh", "scripts/build-book.sh",
}

# Every dropped path and why (design D4 dispositions; plan aio-001 Phase B).
DROPS = {
    "tools/verify_historical_deferred_policy.py": "D4: historical-policy clock",
    "scripts/verify-historical-deferred-policy.sh": "D4: historical-policy clock",
    "tests/test_historical_deferred_policy.py": "D4: historical-policy clock test",
    "scripts/renumber-book1-units.py": "D4: one-off migration script",
    "scripts/migrate-reference-layout.sh": "D4: one-off migration script",
    "scripts/verify-unit-renumbering.py": "D4: one-off migration script",
    "tests/test_renumber_book1_units.py": "D4: test of a one-off migration script",
    "tests/test_reference_migration.py": "D4: test of a one-off migration script",
    "scripts/verify-staged-scope.py": "D4: replaced by tools/guard.py refusals",
    "tests/fixtures/plan019-path-inventory.yaml": "D4: replaced by tools/guard.py refusals",
    "tests/test_plan031_guard.py": "D4: test of the replaced guard",
    "scripts/pre-merge-guard.sh": "D4: py4kids guard is shared",
    "scripts/ci-local.sh": "D2: routed into py4kids ci-local",
    "docs/proposals/.gitkeep": "empty placeholder (nothing to archive or scan)",
    "docs/reviews/.gitkeep": "empty placeholder (nothing to archive or scan)",
    "output/README.md": "py4kids has its own output/README.md",
    ".gitignore": "ported by hand into py4kids .gitignore (roots renamed)",
    "AGENTS.md": "usaaio governance; superseded by py4kids AGENTS.md + design 014",
    "CLAUDE.md": "usaaio governance pointer",
    "TODO.md": "usaaio backlog",
    "books.yaml": "replaced by py4kids books.yaml entries",
    "pyproject.toml": "replaced by the py4kids `aio` dependency group",
    "uv.lock": "replaced by the py4kids uv.lock",
}

QUOTE = "['\"`]"
RULES: list[tuple[str, re.Pattern[str], object]] = [
    ("qualified id", re.compile(r"(?<![\w-])book([12]):(?=\S)"), lambda m: MAP[m.group(1)] + ":"),
    ("path segment", re.compile(r"(?<![\w-])book([12])/"), lambda m: MAP[m.group(1)] + "/"),
    ("output name", re.compile(r"(?<!\w)book([12])-"), lambda m: MAP[m.group(1)] + "-"),
    ("yaml book value", re.compile(r"(?m)^(\s*(?:-\s*)?book:\s*)book([12])\b"),
     lambda m: m.group(1) + MAP[m.group(2)]),
    ("table cell", re.compile(r"\|\s*book([12])\s*\|"), lambda m: "| " + MAP[m.group(1)] + " |"),
    ("bold Book field", re.compile(r"(\*\*Book:\*\*\s*)book([12])\b"), lambda m: m.group(1) + MAP[m.group(2)]),
    ("quoted literal", re.compile(rf"({QUOTE})book([12])({QUOTE})"),
     lambda m: m.group(1) + MAP[m.group(2)] + m.group(3)),
    ("--book value", re.compile(r"--book book([12])\b"), lambda m: "--book " + MAP[m.group(1)]),
    ("example id", re.compile(r"(e\.g\. )book([12])\b"), lambda m: m.group(1) + MAP[m.group(2)]),
    ("bridge lesson", re.compile(r"00-book1-bridge"), "00-aio-ml-bridge"),
    ("env var", re.compile(r"USAAIO_"), "AIO_"),
]

# tests/test_book_ids.py patterns (the "book name" rule is exempt on aio destinations).
GUARD = (
    ("path segment", re.compile(r"(^|[^-\w])book(1b?|2)/", re.MULTILINE)),
    ("CLI value", re.compile(r"--book book(1b?|2)\b")),
    ("quoted id", re.compile(r"""['"]book(1b?|2)['"]""")),
    ("qualified id", re.compile(r"book(1b?|2):[a-z]")),
    ("old output name", re.compile(r"Book1b-|Book[12]-", re.IGNORECASE)),
)
HISTORICAL_FILE_NAME = re.compile(r"(?:designs|plans)/\d{3}-[\w.-]+")
PRODUCED = re.compile(r"\w+aio-(ml|dl)[:/-]")
RESIDUAL = re.compile(r"\bbook[12]\b")


def destination(path: str) -> tuple[str, str] | None:
    """(kind, destination) for a source path; kind is 'live' or 'archive'; None = dropped."""
    if path in DROPS:
        return None
    if path in LIVE_DOCS:
        return "live", "aio-ml/docs/" + LIVE_DOCS[path]
    for src, dst in (("book1/", "aio-ml/"), ("book2/", "aio-dl/"), ("tests/", "tools/aio/tests/"),
                     ("tools/", "tools/aio/")):
        if path.startswith(src):
            return "live", dst + path[len(src):]
    if path in PORTED_SCRIPTS:
        return "live", "scripts/aio/" + path[len("scripts/"):]
    if path.startswith("docs/"):
        return "archive", path[len("docs/"):]
    raise SystemExit(f"unmapped source path: {path}")


def rename(text: str, counts: collections.Counter[str]) -> str:
    for name, pattern, replacement in RULES:
        text, n = pattern.subn(replacement, text)
        counts[name] += n
    return text


def rename_path(dest: str) -> str:
    """Rename path segments and the bridge file name inside a destination path."""
    return re.sub(r"(?<![\w-])book([12])/", lambda m: MAP[m.group(1)] + "/", dest).replace(
        "00-book1-bridge", "00-aio-ml-bridge")


def read_tree(source: Path, sha: str) -> dict[str, bytes]:
    names = subprocess.run(["git", "-C", str(source), "ls-tree", "-r", "-z", "--name-only", sha],
                           check=True, capture_output=True).stdout.split(b"\0")
    names = [n.decode() for n in names if n]
    batch = subprocess.run(["git", "-C", str(source), "cat-file", "--batch"],
                           input="".join(f"{sha}:{n}\n" for n in names).encode(),
                           check=True, capture_output=True).stdout
    blobs: dict[str, bytes] = {}
    pos = 0
    for name in names:
        header_end = batch.index(b"\n", pos)
        _oid, kind, size = batch[pos:header_end].split()
        assert kind == b"blob", (name, kind)
        start = header_end + 1
        blobs[name] = batch[start:start + int(size)]
        pos = start + int(size) + 1
    return blobs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--dest", type=Path, required=True)
    parser.add_argument("--archive-stage", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--dest-dry", type=Path)
    parser.add_argument("--archive-only", action="store_true")
    args = parser.parse_args(argv)

    blobs = read_tree(args.source, args.sha)
    counts: collections.Counter[str] = collections.Counter()
    live: dict[str, bytes] = {}
    archive: dict[str, bytes] = {}
    dropped: list[tuple[str, str]] = []
    renamed_paths: list[tuple[str, str]] = []
    changed: list[str] = []
    for path, data in sorted(blobs.items()):
        target = destination(path)
        if target is None:
            dropped.append((path, DROPS[path]))
            continue
        kind, dest = target
        if kind == "archive":
            archive[dest] = data  # byte-identical
            continue
        new_dest = rename_path(dest)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            live[new_dest] = data
            continue
        new_text = rename(text, counts)
        if new_text != text:
            changed.append(new_dest)
        if new_dest != path:
            renamed_paths.append((path, new_dest))
        live[new_dest] = new_text.encode("utf-8")

    # Stage the archive (always; volatile staging is regenerated on demand).
    if args.archive_stage.exists():
        shutil.rmtree(args.archive_stage)
    for rel, data in archive.items():
        out = args.archive_stage / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    if args.archive_only:
        print(f"archive staged: {len(archive)} files -> {args.archive_stage}")
        return 0

    # Acceptance outcomes (a)-(d).
    guard_hits, produced, parse_failures, residual = [], [], [], collections.Counter()
    for dest, data in live.items():
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(text.splitlines(), 1):
            scrubbed = HISTORICAL_FILE_NAME.sub("", line)
            for name, pattern in GUARD:
                if pattern.search(scrubbed):
                    guard_hits.append(f"{dest}:{number} [{name}] {line.strip()[:120]}")
        produced += [f"{dest}: {m.group(0)}" for m in PRODUCED.finditer(text)]
        if dest.endswith(".py") and dest in changed:
            try:
                ast.parse(text)
            except SyntaxError as exc:
                parse_failures.append(f"{dest}: {exc}")
        for match in RESIDUAL.finditer(text):
            context = text[max(0, match.start() - 30):match.end() + 30].replace("\n", " ")
            residual[(dest, context)] += 1

    ok = not guard_hits and not produced and not parse_failures
    report = ["# usaaio import report (plan aio-001 Phase B)", "",
              f"Source: `weiboz0/usaaio` at `{args.sha}`; {len(blobs)} paths.",
              f"Live files: {len(live)} ({len(changed)} rewritten by the rename rules); archive: {len(archive)} (byte-identical); dropped: {len(dropped)}.",
              "", "## Rename rule counts", "", "| rule | hits |", "|---|---|"]
    report += [f"| {name} | {counts[name]} |" for name, _, _ in RULES]
    report += ["", "## Acceptance outcomes", "",
               f"- (a) `test_book_ids` patterns on the live set (book-name rule exempt): **{len(guard_hits)} hits**",
               f"- (b) produced `\\w+aio-(ml|dl)[:/-]`: **{len(produced)}**; rewritten `.py` parse failures: **{len(parse_failures)}**",
               f"- (c) remaining `\\bbook[12]\\b` tokens: **{sum(residual.values())}** in {len({d for d, _ in residual})} files (listed below with disposition)",
               "- (d) per-rule counts above; dropped paths are excluded.", ""]
    report += ["## Dropped paths", "", "| path | reason |", "|---|---|"]
    report += [f"| `{p}` | {r} |" for p, r in dropped]
    report += ["", "## Renamed paths", ""] + [f"- `{a}` → `{b}`" for a, b in renamed_paths if a.split("/", 1)[-1] != b.split("/", 1)[-1] or not b.startswith(("aio-ml/", "aio-dl/", "tools/aio/", "scripts/aio/"))][:0]
    moved = collections.Counter((a.split("/", 1)[0], b.split("/", 1)[0] if not b.startswith(("tools/aio", "scripts/aio")) else "/".join(b.split("/")[:2])) for a, b in renamed_paths)
    report += [f"- `{src}/…` → `{dst}/…`: {n} files" for (src, dst), n in sorted(moved.items())]
    special = [(a, b) for a, b in renamed_paths if "bridge" in b or "coverage-audit" in b or "fixtures/two-books-valid" in b]
    report += [f"- `{a}` → `{b}`" for a, b in special]
    report += ["", "## Residual `book1`/`book2` tokens (outcome c)", "",
               "Each is a Python identifier, an inline test registry rewritten in Phase D, or another non-id use.", ""]
    report += [f"- `{d}` ×{n}: `{c.strip()}`" for (d, c), n in sorted(residual.items())]
    for title, items in (("Guard hits", guard_hits), ("Produced patterns", produced), ("Parse failures", parse_failures)):
        if items:
            report += ["", f"## {title} (FAIL)", ""] + [f"- {x}" for x in items]
    report += ["", "## Changed files", ""] + [f"- `{c}`" for c in sorted(changed)]

    out_root = args.dest_dry if args.dry_run else args.dest
    if out_root is None:
        raise SystemExit("--dry-run needs --dest-dry")
    for dest, data in live.items():
        out = out_root / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(data)
    report_path = out_root / "docs/history/aio-import/import-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"live {len(live)} changed {len(changed)} archive {len(archive)} dropped {len(dropped)}")
    print(f"(a) guard hits {len(guard_hits)}  (b) produced {len(produced)} parse-fail {len(parse_failures)}  (c) residual {sum(residual.values())}")
    for x in (guard_hits + produced + parse_failures)[:40]:
        print("  FAIL", x)
    print(f"report: {report_path}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

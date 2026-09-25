"""Command-line entry point for course verification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.checks import CHECKS, UNIT_ONLY_CHECKS
from tools.notebooks import fill_outputs_findings, lesson_outputs_findings, project_dirs


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="py4kids-tools")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="book-registry root (defaults to the repository root)",
    )
    parser.add_argument("--book", required=True)
    parser.add_argument("--unit")
    parser.add_argument("check", choices=(*CHECKS, "fill-outputs", "lesson-outputs-check", "publish", "publish-audit"))
    parser.add_argument("--edition", choices=("student", "teacher"))
    return parser


BOOK_LEVEL_CHECKS = {
    "prereq-check",
    "coverage-check",
    "concept-scan",
    "technique-spiral",
    "pattern-marker",
    "patterns-doc-check",
}


def main(argv=None):
    try:
        arguments = _parser().parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    if arguments.unit and arguments.check in BOOK_LEVEL_CHECKS:
        print(f"usage: --unit does not apply to book-level check {arguments.check}",
              file=sys.stderr)
        return 2
    if arguments.unit and arguments.unit.startswith("project-"):
        _, project_findings = project_dirs(arguments.root, arguments.book, arguments.unit)
        if project_findings:
            for finding in project_findings:
                print(finding)
            return 1
    if (
        arguments.unit
        and arguments.unit.startswith(("checkpoint-", "project-"))
        and arguments.check in (UNIT_ONLY_CHECKS | {"fill-outputs", "lesson-outputs-check"})
    ):
        kind = arguments.unit.split("-", 1)[0]
        print(
            f"usage: --unit {kind} id does not apply to unit-only check {arguments.check}",
            file=sys.stderr,
        )
        return 2
    if arguments.check == "publish":
        from tools.publish import build
        if not arguments.edition:
            print("usage: publish requires --edition", file=sys.stderr)
            return 2
        print(build(arguments.root, arguments.book, arguments.edition))
        return 0
    if arguments.check == "publish-audit":
        from tools.publish_audit import audit
        findings = audit(arguments.root, arguments.book)
        for finding in findings:
            print(finding)
        if findings and any(finding.startswith("FAIL:") for finding in findings):
            return 1
        return 0
    if arguments.check == "fill-outputs":
        findings = fill_outputs_findings(arguments.root, arguments.book, arguments.unit)
    elif arguments.check == "lesson-outputs-check":
        findings = lesson_outputs_findings(arguments.root, arguments.book, arguments.unit)
    else:
        findings = CHECKS[arguments.check](arguments.root, arguments.book, arguments.unit)
    if findings == ["SKIP (plan 086)"]:
        print(f"{arguments.check}: SKIP (plan 086)")
        return 0
    if findings:
        for finding in findings:
            print(finding)
        return 1
    print(f"{arguments.check}: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

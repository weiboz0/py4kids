"""Command-line entry point for course verification."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.books import PublicationConfigError
from tools.checks import CHECKS, UNIT_ONLY_CHECKS
from tools.notebooks import fill_outputs_findings, lesson_outputs_findings, project_dirs

# Mirrors tools.publish.EDITIONS (kept literal so the parser need not import the publisher).
EDITION_CHOICES = ("student", "student-print", "answer-key", "teacher")


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
    parser.add_argument("check", choices=(*CHECKS, "fill-outputs", "lesson-outputs-check", "publish",
                                          "publish-audit", *SITE_COMMANDS))
    parser.add_argument("--edition", choices=EDITION_CHOICES)
    # The site export (design 012; plan 101): `export`, `classify`, `site-check`.
    parser.add_argument("--out", type=Path, help="export: bundle directory (default site/content/<book>)")
    parser.add_argument("--release", default="unreleased", help="export: the release tag (PDF links)")
    parser.add_argument("--update-ledger", action="store_true",
                        help="export: write site/ids/<book>.json from the bundle's keys")
    parser.add_argument("--measure", action="store_true",
                        help="export: re-measure every fixtures solver and rewrite "
                             "tools/export/timings/<book>.json (check.cpu_ms)")
    parser.add_argument("--apply", action="store_true",
                        help="classify: write each proposed check-* tag to its heading cell")
    return parser


SITE_COMMANDS = ("export", "classify", "site-check")


BOOK_LEVEL_CHECKS = {
    "prereq-check",
    "coverage-check",
    "concept-scan",
    "technique-spiral",
    "pattern-marker",
    "patterns-doc-check",
    "milestone-check",
}


def main(argv=None):
    try:
        arguments = _parser().parse_args(argv)
    except SystemExit as error:
        return int(error.code)
    if arguments.check in SITE_COMMANDS:
        return _site_command(arguments)
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
        try:
            print(build(arguments.root, arguments.book, arguments.edition))
        except PublicationConfigError as error:
            print(error, file=sys.stderr)
            return 1
        return 0
    if arguments.check == "publish-audit":
        from tools.publish_audit import audit
        try:
            findings = audit(arguments.root, arguments.book)
        except PublicationConfigError as error:
            print(error, file=sys.stderr)
            return 1
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


def _site_command(arguments) -> int:
    from tools.books import book_flag

    root, book = arguments.root, arguments.book
    try:
        is_site = book_flag(root, book, "site")
    except (KeyError, ValueError):
        is_site = False
    if not is_site:
        print(f"usage: {book} is not a site book (books.yaml site: true)", file=sys.stderr)
        return 2
    if arguments.check == "export":
        from tools.export.bundle import ExportError, export_book
        from tools.export.ids import write_ledger

        out = arguments.out or root / "site" / "content" / book
        try:
            result = export_book(root, book, out, release=arguments.release,
                                 measure=arguments.measure)
        except ExportError as error:
            print("\n".join(error.findings))
            return 1
        except ValueError as error:
            print(error)
            return 1
        if arguments.update_ledger:
            write_ledger(root, book, result.keys)
        print(f"export: {book}: {len(result.keys)} keys, {result.content_hash} -> {out}")
        if arguments.measure:
            from tools.export.timing import cache_path

            print(f"export: {book}: timings measured -> {cache_path(root, book)}")
        return 0
    if arguments.check == "classify":
        from tools.export.classify import apply_proposals, classification_rows

        try:
            if arguments.apply:
                for key in apply_proposals(root, book, arguments.unit):
                    print(f"tagged {key}")
                return 0
            for row in classification_rows(root, book, arguments.unit):
                print("\t".join(row))
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        return 0
    from tools.export.check import site_check_findings

    findings = site_check_findings(root, book)
    for finding in findings:
        print(finding)
    if any(finding.startswith("FAIL:") for finding in findings):
        return 1
    print("site-check: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

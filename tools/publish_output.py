"""Copy built PDFs into the root `output/<book>/` folder (plan 090 D3).

Each build script owns its own files and replaces only those:
- `book` (scripts/build-book.sh): `Book*-*.pdf`, the typeset editions;
- `pdf` (scripts/build-pdf.sh): `syllabus.pdf`, `patterns.pdf` and the `handouts/` folder.
Nothing clears the whole folder, so running both scripts in either order keeps every file,
and a renamed edition leaves no stale book PDF behind.
"""
from __future__ import annotations

import argparse
import fnmatch
import shutil
import sys
from pathlib import Path

BOOK_PATTERN = 'Book*-*.pdf'
PDF_FILES = ('syllabus.pdf', 'patterns.pdf')
HANDOUTS = 'handouts'
OWNERS = ('book', 'pdf')


def _destination(target: Path, owner: str, source: Path) -> Path:
    if owner == 'book':
        if not fnmatch.fnmatchcase(source.name, BOOK_PATTERN):
            raise ValueError(f'build-book owns only {BOOK_PATTERN}, not {source.name}')
        return target / source.name
    if source.name in PDF_FILES:
        return target / source.name
    if source.parent.name == HANDOUTS and source.suffix == '.pdf':
        return target / HANDOUTS / source.name
    raise ValueError(f'build-pdf owns only {", ".join(PDF_FILES)} and {HANDOUTS}/, not {source}')


def refresh_output(root: Path, book_id: str, owner: str, sources: list[Path]) -> list[Path]:
    """Delete the owner's files in `output/<book>/`, then copy `sources` there; return the copies."""
    if owner not in OWNERS:
        raise ValueError(f'owner must be one of {", ".join(OWNERS)}')
    missing = [str(source) for source in sources if not source.is_file() or source.stat().st_size == 0]
    if missing:
        raise ValueError(f'missing or empty PDF: {", ".join(missing)}')
    target = root / 'output' / book_id
    destinations = [_destination(target, owner, source) for source in sources]
    target.mkdir(parents=True, exist_ok=True)
    if owner == 'book':
        for old in target.glob(BOOK_PATTERN):
            old.unlink()
    else:
        for name in PDF_FILES:
            (target / name).unlink(missing_ok=True)
        shutil.rmtree(target / HANDOUTS, ignore_errors=True)
    for source, destination in zip(sources, destinations):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return destinations


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='python -m tools.publish_output')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--book', required=True)
    parser.add_argument('--owner', required=True, choices=OWNERS)
    parser.add_argument('pdfs', nargs='*', type=Path)
    arguments = parser.parse_args(argv)
    try:
        copies = refresh_output(arguments.root, arguments.book, arguments.owner, arguments.pdfs)
    except ValueError as error:
        print(f'FAIL: output/{arguments.book}: {error}', file=sys.stderr)
        return 1
    for copy in copies:
        print(f'output: {copy.relative_to(arguments.root)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

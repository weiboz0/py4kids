"""Missing-glyph check for LaTeX logs (design 010 D4).

A font that lacks a character makes (Lua|Xe)LaTeX write a "Missing character" line to its log
and drop the glyph from the PDF, silently. `scripts/build-pdf.sh` keeps the log of every handout,
syllabus and patterns.pdf build and runs this check on it; the book audit (`publish-audit`)
checks the book editions' logs itself.

Usage: python -m tools.pdf_glyphs LOG [LOG ...]
Exit status 0 when no log reports a missing character, 1 otherwise (each finding on stderr).
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

# LuaTeX: "Missing character: There is no ⊕ (U+2295) in font FiraMono:mode=node;..."
# XeTeX:  "Missing character: There is no ⊕ in font lmroman10-regular!"
# TeX wraps long log lines (max_print_line), so only the start of the line is relied on.
MISSING = re.compile(
    r'^Missing character: There is no (?P<char>.+?)(?: \(U\+(?P<code>[0-9A-Fa-f]{4,6})\))?'
    r' in font (?P<font>[^\n!]*)',
    re.MULTILINE,
)


def missing_characters(log_text: str) -> list[tuple[str, str, str]]:
    """Every missing-character report in a log, as (char, 'U+XXXX', font), in log order."""
    found = []
    for match in MISSING.finditer(log_text):
        char = match.group('char')
        code = match.group('code')
        if code is None and len(char) == 1:
            code = f'{ord(char):04X}'
        font = match.group('font').split(':', 1)[0].strip()
        found.append((char, f'U+{code.upper()}' if code else 'U+?', font))
    return found


def summarize(found: list[tuple[str, str, str]]) -> str:
    """One line: each missing character with its code point, count and fonts."""
    counts = Counter((char, code) for char, code, _ in found)
    fonts: dict[tuple[str, str], set[str]] = {}
    for char, code, font in found:
        fonts.setdefault((char, code), set()).add(font)
    return ', '.join(f'{char} {code} x{count} ({", ".join(sorted(fonts[(char, code)]))})'
                     for (char, code), count in counts.items())


def check_logs(paths: list[Path]) -> list[str]:
    """FAIL lines for every log that is missing or reports a missing character."""
    failures = []
    for path in paths:
        if not path.is_file():
            failures.append(f'FAIL: {path}: LaTeX log not found')
            continue
        found = missing_characters(path.read_text(encoding='utf-8', errors='replace'))
        if found:
            failures.append(f'FAIL: {path}: {len(found)} missing character(s): {summarize(found)}')
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog='python -m tools.pdf_glyphs',
                                     description='Fail when a LaTeX log reports a missing character.')
    parser.add_argument('logs', nargs='+', type=Path)
    args = parser.parse_args(argv)
    failures = check_logs(args.logs)
    for line in failures:
        print(line, file=sys.stderr)
    if failures:
        return 1
    print(f'pdf-glyphs: PASS ({len(args.logs)} log(s), no missing characters)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

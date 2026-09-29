"""Check turtle real-program examples against their referenced solution assets."""
from __future__ import annotations

import io
import math
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import nbformat

from tools import fake_turtle
from tools.notebooks import unit_dirs

PYTHON_FENCE = re.compile(r'```python\s*\n(.*?)\n```', re.DOTALL)
SAMPLE_FENCE = re.compile(r'Sample input:\s*\n\s*```text\s*\n(.*?)\n```', re.DOTALL)
ASSET = re.compile(r'assets/(solutions_ex\d+[\w-]*\.py)')
EXPECTED_PYTHON_CONCEPTS = {(6, n) for n in (*range(1, 13), 16, 17, 18)} | {
    (7, 7), (7, 27), (7, 28), (8, 7), (8, 16), (8, 17),
}


def real_programs(group) -> list[tuple[str, str | None]]:
    """Extract fenced programs and their sample blocks from real-program cells."""
    programs = []
    for cell in group['cells']:
        if cell.cell_type != 'markdown' or '**The real program**' not in cell.source:
            continue
        source = cell.source.split('**The real program**', 1)[1]
        sample = SAMPLE_FENCE.search(source)
        programs.extend((match.group(1), sample.group(1) if sample else None)
                        for match in PYTHON_FENCE.finditer(source))
    return programs


def _run(source: str, stdin: str, name: str):
    fake_turtle.reset()
    previous = sys.modules.get('turtle')
    sys.modules['turtle'] = fake_turtle
    feed = io.StringIO(stdin)
    output = io.StringIO()
    try:
        with patch('sys.stdin', feed), redirect_stdout(output):
            exec(compile(source, name, 'exec'), {'__name__': '__main__'})  # noqa: S102 - course examples
        return fake_turtle.segments(), fake_turtle.final_state(), output.getvalue(), feed.read()
    finally:
        if previous is None:
            sys.modules.pop('turtle', None)
        else:
            sys.modules['turtle'] = previous


def _same_segments(left, right):
    return len(left) == len(right) and all(
        all(math.isclose(a, b, rel_tol=0, abs_tol=1e-6) for a, b in zip(one[:4], two[:4]))
        and one[4:] == two[4:] for one, two in zip(left, right)
    )


def _same_state(left, right):
    return all(math.isclose(a, b, rel_tol=0, abs_tol=1e-6) for a, b in zip(left[:3], right[:3])) and left[3] == right[3]


def turtle_real_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    from tools.publish import item_groups

    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    inventory = set()
    for entry in units:
        exercise_path = entry / 'exercises.ipynb'
        solution_path = entry / 'solutions.ipynb'
        if not exercise_path.exists() or not solution_path.exists():
            continue
        _, statements = item_groups(nbformat.read(exercise_path, as_version=4).cells, 'Exercise')
        _, solutions = item_groups(nbformat.read(solution_path, as_version=4).cells, 'Exercise')
        statement_by_number = {group['number']: group for group in statements}
        unit_number = int(re.search(r'unit-(\d+)', entry.name)[1])
        for group in solutions:
            number = group['number']
            context = f'{entry.name}: Exercise {number}'
            references = set(ASSET.findall('\n'.join(cell.source for cell in group['cells'])))
            turtle_assets = []
            for name in references:
                path = entry / 'assets' / name
                if path.exists() and fake_turtle.imports_turtle(path.read_text(encoding='utf-8')):
                    turtle_assets.append(path)
            programs = real_programs(group)
            statement = statement_by_number.get(number)
            has_real = statement is not None and any(
                '**Real version:**' in cell.source for cell in statement['cells']
                if cell.cell_type == 'markdown')
            if not has_real or not turtle_assets:
                if programs and any(fake_turtle.imports_turtle(source) for source, _ in programs):
                    findings.append(f'FAIL: {context}: extra turtle real-program fence')
                continue
            if programs and not any(fake_turtle.imports_turtle(source) for source, _ in programs):
                # A text-only real program for a turtle exercise (python-projects) is not a drawing program;
                # python-concepts' exact inventory below catches a drawing program that lost its import.
                continue
            inventory.add((unit_number, number))
            if len(turtle_assets) != 1:
                findings.append(f'FAIL: {context}: expected one referenced turtle solution asset')
                continue
            if len(programs) != 1:
                findings.append(f'FAIL: {context}: missing real-program fence' if not programs else
                                f'FAIL: {context}: extra real-program fence')
                continue
            source, sample = programs[0]
            if not fake_turtle.imports_turtle(source):
                findings.append(f'FAIL: {context}: real-program fence does not import turtle')
                continue
            if sample is None:
                findings.append(f'FAIL: {context}: missing Sample input')
                continue
            stdin = sample + '\n'
            try:
                actual = _run(source, stdin, f'{context} real program')
                expected = _run(turtle_assets[0].read_text(encoding='utf-8'), '', str(turtle_assets[0]))
            except Exception as error:  # noqa: BLE001 - report malformed course examples
                findings.append(f'FAIL: {context}: replay failed: {error}')
                continue
            if actual[3]:
                findings.append(f'FAIL: {context}: unconsumed input')
            if not actual[0]:
                findings.append(f'FAIL: {context}: no pen-down segment')
            if not _same_segments(actual[0], expected[0]):
                findings.append(f'FAIL: {context}: segment mismatch')
            if not _same_state(actual[1], expected[1]):
                findings.append(f'FAIL: {context}: final state or pen state mismatch')
            if actual[2] != expected[2]:
                findings.append(f'FAIL: {context}: stdout mismatch')
    # Deliberate content pin (not a feature switch): the 21-row inventory belongs to this one book.
    if book == 'python-concepts' and unit is None and inventory != EXPECTED_PYTHON_CONCEPTS:
        findings.append(f'FAIL: python-concepts turtle real-program inventory: expected 21 rows; '
                        f'missing {sorted(EXPECTED_PYTHON_CONCEPTS - inventory)}, extra {sorted(inventory - EXPECTED_PYTHON_CONCEPTS)}')
    return findings

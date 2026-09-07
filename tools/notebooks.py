"""Notebook verification functions promoted from the Plan 004 interim tests."""

from __future__ import annotations

import ast
import os
import py_compile
import re
import subprocess
import tempfile
from pathlib import Path

import nbformat
import yaml
from nbclient import NotebookClient

REQUIRED_FILES = (
    "manifest.yaml",
    "lesson.ipynb",
    "exercises.ipynb",
    "solutions.ipynb",
    "teacher-notes.md",
)
CHECKPOINT_REQUIRED_FILES = (
    "manifest.yaml",
    "checkpoint.ipynb",
    "solutions.ipynb",
    "teacher-notes.md",
)
MANIFEST_KEYS = {"id", "kind", "blueprint_version", "lessons", "concepts", "provenance"}
NOTES_HEADINGS = (
    "## Goals",
    "## Pacing",
    "## Common mistakes",
    "## Discussion prompts",
    "## Differentiation",
)
CHECKPOINT_NOTES_HEADINGS = (*NOTES_HEADINGS, "## Grading")
INTERACTIVE = re.compile(r"\binput\s*\(")
GUI_IMPORT = re.compile(r"^\s*(import|from)\s+(turtle|tkinter)\b", re.MULTILINE)
RANDOM_FROM_IMPORT = re.compile(r"^\s*from\s+random\s+import\b", re.MULTILINE)
EXERCISE_HEADING = re.compile(r"^## Exercise \d+", re.MULTILINE)
QUESTION_HEADING = re.compile(r"^## Question \d+", re.MULTILINE)
SOLUTION_HEADING = re.compile(r"(?i)^#+\s*solution", re.MULTILINE)
ASSET_REF = re.compile(r"assets/[\w.-]+\.py")


def _fail(scope: str, detail: str) -> str:
    return f"FAIL: {scope}: {detail}"


def book_root(root: Path, book: str) -> Path:
    return Path(root).resolve() / book


def unit_dirs(root: Path, book: str, unit: str | None = None) -> tuple[list[Path], list[str]]:
    # A MISSING book/units directory fails closed (a typo'd --book/--root must not PASS);
    # an existing-but-empty units/ passes (the prefix rule's N=0 case).
    book_dir = book_root(root, book)
    if not book_dir.is_dir():
        return [], [_fail(book, "book root does not exist")]
    units = book_dir / "units"
    if not units.is_dir():
        return [], [_fail(book, "units/ directory does not exist")]
    if unit is not None:
        path = units / unit
        if not path.is_dir():
            return [], [_fail(unit, "unit directory does not exist")]
        return [path], []
    return sorted(path for path in units.glob("unit-*") if path.is_dir()), []


def checkpoint_dirs(
    root: Path, book: str, ident: str | None = None
) -> tuple[list[Path], list[str]]:
    book_dir = book_root(root, book)
    if not book_dir.is_dir():
        return [], [_fail(book, "book root does not exist")]
    checkpoints = book_dir / "checkpoints"
    if not checkpoints.is_dir():
        return [], [_fail(book, "checkpoints/ directory does not exist")]
    if ident is not None:
        path = checkpoints / ident
        if not path.is_dir():
            return [], [_fail(ident, "checkpoint directory does not exist")]
        return [path], []
    return sorted(path for path in checkpoints.glob("checkpoint-*") if path.is_dir()), []


def content_dirs(
    root: Path, book: str, ident: str | None = None
) -> tuple[list[tuple[Path, str]], list[str]]:
    if ident is not None:
        if ident.startswith("checkpoint-"):
            paths, findings = checkpoint_dirs(root, book, ident)
            return [(path, "checkpoint") for path in paths], findings
        paths, findings = unit_dirs(root, book, ident)
        return [(path, "unit") for path in paths], findings
    units, findings = unit_dirs(root, book)
    checkpoints, checkpoint_findings = checkpoint_dirs(root, book)
    findings.extend(checkpoint_findings)
    paths = [(path, "unit") for path in units]
    paths.extend((path, "checkpoint") for path in checkpoints)
    return paths, list(dict.fromkeys(findings))


def read_nb(path: Path):
    return nbformat.read(path, as_version=4)


def code_cells(notebook):
    return [cell for cell in notebook.cells if cell.cell_type == "code"]


def tags(cell) -> list[str]:
    return cell.get("metadata", {}).get("tags", [])


def _strip_markdown_fences(source: str) -> str:
    lines = []
    fence_character = None
    fence_width = 0
    for line in source.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence_character is None:
            if marker:
                fence_character = marker.group(1)[0]
                fence_width = len(marker.group(1))
                lines.append("")
            else:
                lines.append(line)
            continue
        is_closing = (
            marker is not None
            and marker.group(1)[0] == fence_character
            and len(marker.group(1)) >= fence_width
            and not line[marker.end() :].strip()
        )
        lines.append("")
        if is_closing:
            fence_character = None
            fence_width = 0
    return "\n".join(lines)


def _markdown_heading_occurrences(notebook, pattern) -> list[tuple[str, int]]:
    return [
        (match.group(), cell_index)
        for cell_index, cell in enumerate(notebook.cells)
        if cell.cell_type == "markdown"
        for match in pattern.finditer(_strip_markdown_fences(cell.source))
    ]


def _has_markdown_heading(source: str, heading: str) -> bool:
    return bool(
        re.search(
            rf"^{re.escape(heading)}[ \t]*$",
            _strip_markdown_fences(source),
            re.MULTILINE,
        )
    )


def _sanitized_code_source(source: str) -> str:
    return "\n".join(
        "" if line.lstrip().startswith(("%", "!")) else line
        for line in source.splitlines()
    )


def _is_random_attribute(node, random_names: set[str]) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id in random_names
    )


def _is_seed_four_call(node, random_names: set[str]) -> bool:
    return (
        isinstance(node, ast.Call)
        and _is_random_attribute(node.func, random_names)
        and node.func.attr == "seed"
        and len(node.args) == 1
        and not node.keywords
        and isinstance(node.args[0], ast.Constant)
        and isinstance(node.args[0].value, int)
        and not isinstance(node.args[0].value, bool)
        and node.args[0].value == 4
    )


def _solution_policy_findings(scope: str, notebook) -> list[str]:
    findings = []
    codes = code_cells(notebook)
    parsed = []
    for cell_index, cell in enumerate(codes):
        try:
            tree = ast.parse(cell.source)
        except SyntaxError:
            try:
                tree = ast.parse(_sanitized_code_source(cell.source))
            except SyntaxError:
                continue
        parsed.append((cell_index, tree))
    def _non_vacuous_assert(tree) -> bool:
        # An assert whose test is a bare True/constant (or `assert True`) proves nothing.
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert) and not (
                isinstance(node.test, ast.Constant) and bool(node.test.value)
            ):
                return True
        return False

    assert_count = sum(_non_vacuous_assert(tree) for _cell_index, tree in parsed)
    if assert_count < 3:
        findings.append(_fail(scope, "solutions need >=3 non-vacuous assert cells"))
    for cell in codes:
        if INTERACTIVE.search(cell.source):
            findings.append(_fail(scope, "solutions call input()"))
        if GUI_IMPORT.search(cell.source):
            findings.append(_fail(scope, "solutions import a GUI"))
        if RANDOM_FROM_IMPORT.search(cell.source):
            findings.append(_fail(scope, "solutions use 'from random import'"))
    random_names = {"random"}
    seed_attributes = set()
    seed_positions = []
    use_positions = []
    for cell_index, tree in parsed:
        events = [
            node
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.Call, ast.Attribute))
        ]
        events.sort(
            key=lambda node: (
                node.lineno,
                node.col_offset,
                0 if isinstance(node, ast.Import) else 1 if isinstance(node, ast.Call) else 2,
            )
        )
        for node in events:
            if isinstance(node, ast.Import):
                random_names.update(
                    alias.asname
                    for alias in node.names
                    if alias.name == "random" and alias.asname is not None
                )
            elif isinstance(node, ast.Call) and _is_seed_four_call(node, random_names):
                seed_attributes.add(id(node.func))
            elif isinstance(node, ast.Attribute) and _is_random_attribute(node, random_names):
                position = (cell_index, node.lineno, node.col_offset)
                if id(node) in seed_attributes:
                    seed_positions.append(position)
                else:
                    use_positions.append(position)
    if seed_positions or use_positions:
        first_use = min(use_positions, default=None)
        if not seed_positions:
            findings.append(_fail(scope, "solutions use random without random.seed(4)"))
        elif first_use is not None and min(seed_positions) >= first_use:
            findings.append(_fail(scope, "solutions: random.seed(4) must precede first use"))
    return findings


def layout_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        missing = [name for name in REQUIRED_FILES if not (unit_dir / name).is_file()]
        findings.extend(_fail(unit_dir.name, f"missing {name}") for name in missing)
        manifest_path = unit_dir / "manifest.yaml"
        if not manifest_path.is_file():
            continue
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            continue
        concepts = manifest.get("concepts")
        if not isinstance(concepts, dict):
            continue
        introduces = concepts.get("introduces")
        if isinstance(introduces, list) and "turtle-basics" in introduces:
            assets = unit_dir / "assets"
            if not assets.is_dir():
                findings.append(_fail(unit_dir.name, "introduces turtle but has no assets/"))
                continue
            referenced: set[str] = set()
            for name in ("lesson.ipynb", "exercises.ipynb", "solutions.ipynb"):
                path = unit_dir / name
                if path.is_file():
                    for cell in read_nb(path).cells:
                        referenced.update(ASSET_REF.findall(cell.source))
            for reference in sorted(referenced):
                if not (unit_dir / reference).is_file():
                    findings.append(_fail(unit_dir.name, f"references missing {reference}"))
            for script in sorted(assets.glob("*.py")):
                with tempfile.NamedTemporaryFile(suffix=".pyc", delete=False) as compiled:
                    compiled_path = Path(compiled.name)
                try:
                    py_compile.compile(str(script), cfile=str(compiled_path), doraise=True)
                except py_compile.PyCompileError:
                    findings.append(_fail(unit_dir.name, f"asset {script.name} does not compile"))
                finally:
                    compiled_path.unlink(missing_ok=True)
    return findings


def manifest_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    contents, findings = content_dirs(root, book, unit)
    if findings:
        return findings
    map_path = book_root(root, book) / "curriculum/coverage-map.yaml"
    data = yaml.safe_load(map_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return [_fail(book, "coverage-map.yaml must be a mapping")]
    map_entries = data.get("entries")
    if not isinstance(map_entries, list):
        return [_fail(book, "coverage-map entries must be a list")]
    if any(not isinstance(entry, dict) for entry in map_entries):
        return [_fail(book, "coverage-map entries must be mappings")]
    for index, entry in enumerate(map_entries):
        if not isinstance(entry.get("id"), str):
            return [_fail(book, f"coverage-map entry {index} id must be a string")]
    entries = {entry.get("id"): entry for entry in map_entries}
    for content_dir, expected_kind in contents:
        path = content_dir / "manifest.yaml"
        if not path.is_file():
            findings.append(_fail(content_dir.name, "missing manifest.yaml"))
            continue
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            findings.append(_fail(content_dir.name, "manifest must be a mapping"))
            continue
        if set(manifest) != MANIFEST_KEYS:
            findings.append(_fail(content_dir.name, f"manifest keys {set(manifest)}"))
            continue
        if manifest["kind"] != expected_kind:
            findings.append(_fail(content_dir.name, f"kind must be {expected_kind}"))
        if manifest["blueprint_version"] != 1:
            findings.append(_fail(content_dir.name, "blueprint_version must be 1"))
        if manifest["provenance"] != "original":
            findings.append(_fail(content_dir.name, "provenance must be original"))
        if manifest["id"] != content_dir.name:
            findings.append(_fail(content_dir.name, "id does not match directory"))
            continue
        entry = entries.get(manifest["id"])
        if entry is None:
            findings.append(_fail(content_dir.name, "not in coverage map"))
            continue
        if entry.get("kind") != expected_kind:
            findings.append(_fail(content_dir.name, "kind differs from coverage map"))
        if manifest["lessons"] != entry.get("lessons"):
            findings.append(_fail(content_dir.name, "lessons differs from coverage map"))
        concepts = manifest["concepts"]
        if not isinstance(concepts, dict):
            findings.append(_fail(content_dir.name, "manifest concepts must be a mapping"))
            continue
        if set(concepts) != {"introduces", "requires", "practices"}:
            findings.append(_fail(content_dir.name, f"concept keys {set(concepts)}"))
            continue
        for field in ("introduces", "requires", "practices"):
            if not isinstance(concepts[field], list):
                findings.append(
                    _fail(content_dir.name, f"manifest concepts.{field} must be a list")
                )
                continue
            if not all(isinstance(value, str) for value in concepts[field]):
                findings.append(
                    _fail(
                        content_dir.name,
                        f"manifest concepts.{field} must be a list of ids",
                    )
                )
                continue
            map_values = entry.get(field)
            if not isinstance(map_values, list):
                findings.append(
                    _fail(book, f"coverage-map {entry.get('id')}.{field} must be a list")
                )
                continue
            if not all(isinstance(value, str) for value in map_values):
                findings.append(
                    _fail(
                        book,
                        f"coverage-map {entry.get('id')}.{field} must be a list of ids",
                    )
                )
                continue
            if sorted(concepts[field]) != sorted(map_values):
                findings.append(_fail(content_dir.name, f"{field} differs from coverage map"))
    return findings


def hygiene_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    contents, findings = content_dirs(root, book, unit)
    if findings:
        return findings
    for content_dir, kind in contents:
        notebook_name = "exercises.ipynb" if kind == "unit" else "checkpoint.ipynb"
        path = content_dir / notebook_name
        if not path.is_file():
            findings.append(_fail(content_dir.name, f"missing {notebook_name}"))
            continue
        notebook = read_nb(path)
        for index, cell in enumerate(code_cells(notebook)):
            if cell.outputs:
                findings.append(
                    _fail(content_dir.name, f"{notebook_name[:-6]} code cell {index} has outputs")
                )
            if cell.execution_count is not None:
                findings.append(
                    _fail(content_dir.name, f"{notebook_name[:-6]} code cell {index} is executed")
                )
        if kind == "unit":
            has_solution_heading = any(
                SOLUTION_HEADING.search(cell.source) for cell in notebook.cells
            )
        else:
            has_solution_heading = bool(
                _markdown_heading_occurrences(notebook, SOLUTION_HEADING)
            )
        if has_solution_heading:
            detail = (
                "exercises contain a solution heading"
                if kind == "unit"
                else "checkpoint contains a solution heading"
            )
            findings.append(_fail(content_dir.name, detail))
    return findings


def exercise_structure_findings(
    root: Path, book: str, unit: str | None = None, *, stretch_only: bool = False
) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        path = unit_dir / "exercises.ipynb"
        if not path.is_file():
            findings.append(_fail(unit_dir.name, "missing exercises.ipynb"))
            continue
        notebook = read_nb(path)
        if not stretch_only:
            markdown = "\n".join(
                cell.source for cell in notebook.cells if cell.cell_type == "markdown"
            )
            count = len(EXERCISE_HEADING.findall(markdown))
            if count < 6:
                findings.append(_fail(unit_dir.name, f"{count} exercise headings (<6)"))
        stretch = [cell for cell in notebook.cells if "stretch" in tags(cell)]
        if len(stretch) < 2:
            findings.append(_fail(unit_dir.name, f"{len(stretch)} stretch-tagged cells (<2)"))
    return findings


def solutions_structure_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        exercises_path = unit_dir / "exercises.ipynb"
        solutions_path = unit_dir / "solutions.ipynb"
        missing = [p.name for p in (exercises_path, solutions_path) if not p.is_file()]
        if missing:
            findings.extend(_fail(unit_dir.name, f"missing {name}") for name in missing)
            continue
        exercises = read_nb(exercises_path)
        solutions = read_nb(solutions_path)
        markdown = "\n".join(
            cell.source for cell in exercises.cells if cell.cell_type == "markdown"
        )
        headings = EXERCISE_HEADING.findall(markdown)
        sequence = [(cell.cell_type, cell.source) for cell in solutions.cells]
        for heading in headings:
            index = next(
                (
                    i
                    for i, (cell_type, source) in enumerate(sequence)
                    if cell_type == "markdown"
                    and re.search(rf"^{re.escape(heading)}\b", source, re.MULTILINE)
                ),
                None,
            )
            if index is None:
                findings.append(_fail(unit_dir.name, f"solutions missing '{heading}'"))
                continue
            following = []
            for cell_type, source in sequence[index + 1 :]:
                if cell_type == "markdown" and EXERCISE_HEADING.search(source):
                    break
                following.append(cell_type)
            if "code" not in following:
                findings.append(_fail(unit_dir.name, f"solutions: no code under '{heading}'"))
        findings.extend(_solution_policy_findings(unit_dir.name, solutions))
    return findings


def checkpoint_layout_findings(
    root: Path, book: str, ident: str | None = None
) -> list[str]:
    checkpoints, findings = checkpoint_dirs(root, book, ident)
    if findings:
        return findings
    for checkpoint_dir in checkpoints:
        missing = [
            name for name in CHECKPOINT_REQUIRED_FILES if not (checkpoint_dir / name).is_file()
        ]
        findings.extend(_fail(checkpoint_dir.name, f"missing {name}") for name in missing)
    return findings


def checkpoint_question_findings(
    root: Path, book: str, ident: str | None = None
) -> list[str]:
    checkpoints, findings = checkpoint_dirs(root, book, ident)
    if findings:
        return findings
    for checkpoint_dir in checkpoints:
        path = checkpoint_dir / "checkpoint.ipynb"
        if not path.is_file():
            findings.append(_fail(checkpoint_dir.name, "missing checkpoint.ipynb"))
            continue
        notebook = read_nb(path)
        occurrences = _markdown_heading_occurrences(notebook, QUESTION_HEADING)
        count = len(occurrences)
        if count < 6:
            findings.append(_fail(checkpoint_dir.name, f"{count} question headings (<6)"))
        if count > 8:
            findings.append(_fail(checkpoint_dir.name, f"{count} question headings (>8)"))
        # Only judge numbering when the count is in range — otherwise the count finding
        # above is the story and a numbering finding would just pile on.
        if 6 <= count <= 8:
            numbers = [int(re.search(r"\d+", text).group(0)) for text, _idx in occurrences]
            if numbers != list(range(1, len(numbers) + 1)):
                findings.append(
                    _fail(checkpoint_dir.name,
                          f"question numbers must be sequential 1..N, got {numbers}")
                )
        if any("stretch" in tags(cell) for cell in notebook.cells):
            findings.append(_fail(checkpoint_dir.name, "checkpoint contains stretch-tagged cells"))
        if _markdown_heading_occurrences(notebook, SOLUTION_HEADING):
            findings.append(_fail(checkpoint_dir.name, "checkpoint contains a solution heading"))
    return findings


def checkpoint_solutions_findings(
    root: Path, book: str, ident: str | None = None
) -> list[str]:
    checkpoints, findings = checkpoint_dirs(root, book, ident)
    if findings:
        return findings
    for checkpoint_dir in checkpoints:
        checkpoint_path = checkpoint_dir / "checkpoint.ipynb"
        solutions_path = checkpoint_dir / "solutions.ipynb"
        missing = [
            path.name for path in (checkpoint_path, solutions_path) if not path.is_file()
        ]
        if missing:
            findings.extend(_fail(checkpoint_dir.name, f"missing {name}") for name in missing)
            continue
        checkpoint = read_nb(checkpoint_path)
        solutions = read_nb(solutions_path)
        headings = [
            heading
            for heading, _cell_index in _markdown_heading_occurrences(
                checkpoint, QUESTION_HEADING
            )
        ]
        heading_occurrences = _markdown_heading_occurrences(solutions, QUESTION_HEADING)
        solution_headings = [heading for heading, _cell_index in heading_occurrences]
        unmatched_solution_headings = list(solution_headings)
        missing_heading = False
        for heading in headings:
            try:
                unmatched_solution_headings.remove(heading)
            except ValueError:
                findings.append(_fail(checkpoint_dir.name, f"solutions missing '{heading}'"))
                missing_heading = True
        if not missing_heading and solution_headings != headings:
            findings.append(
                _fail(
                    checkpoint_dir.name,
                    "solutions question headings do not mirror checkpoint",
                )
            )
        if solution_headings == headings:
            for occurrence, (heading, cell_index) in enumerate(heading_occurrences):
                next_cell_index = (
                    heading_occurrences[occurrence + 1][1]
                    if occurrence + 1 < len(heading_occurrences)
                    else len(solutions.cells)
                )
                following = solutions.cells[cell_index + 1 : next_cell_index]
                if not any(cell.cell_type == "code" for cell in following):
                    findings.append(
                        _fail(checkpoint_dir.name, f"solutions: no code under '{heading}'")
                    )
        findings.extend(_solution_policy_findings(checkpoint_dir.name, solutions))
    return findings


def checkpoint_teacher_notes_findings(
    root: Path, book: str, ident: str | None = None
) -> list[str]:
    checkpoints, findings = checkpoint_dirs(root, book, ident)
    if findings:
        return findings
    for checkpoint_dir in checkpoints:
        path = checkpoint_dir / "teacher-notes.md"
        if not path.is_file():
            continue
        notes = path.read_text(encoding="utf-8")
        for heading in CHECKPOINT_NOTES_HEADINGS:
            if not _has_markdown_heading(notes, heading):
                findings.append(
                    _fail(checkpoint_dir.name, f"teacher notes missing '{heading}'")
                )
    return findings


def noexec_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        path = unit_dir / "lesson.ipynb"
        if not path.is_file():
            findings.append(_fail(unit_dir.name, "lesson.ipynb does not exist"))
            continue
        notebook = read_nb(path)
        if not notebook.cells:
            findings.append(_fail(unit_dir.name, "lesson is empty"))
            continue
        first = notebook.cells[0]
        if first.cell_type != "markdown" or not first.source.strip():
            findings.append(_fail(unit_dir.name, "lesson must open with non-empty markdown"))
        for index, cell in enumerate(code_cells(notebook)):
            if (INTERACTIVE.search(cell.source) or GUI_IMPORT.search(cell.source)) and (
                "no-exec" not in tags(cell)
            ):
                findings.append(
                    _fail(
                        unit_dir.name,
                        f"lesson code cell {index} is interactive/GUI but not no-exec",
                    )
                )
    return findings


def teacher_notes_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        path = unit_dir / "teacher-notes.md"
        if not path.is_file():
            continue
        notes = path.read_text(encoding="utf-8")
        for heading in NOTES_HEADINGS:
            if heading not in notes:
                findings.append(_fail(unit_dir.name, f"teacher notes missing '{heading}'"))
    return findings


def prefix_findings(root: Path, book: str) -> list[str]:
    book_path = book_root(root, book)
    data = yaml.safe_load((book_path / "curriculum/coverage-map.yaml").read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return [_fail(book, "coverage-map.yaml must be a mapping")]
    entries = data.get("entries")
    if not isinstance(entries, list) or any(not isinstance(entry, dict) for entry in entries):
        return [_fail(book, "coverage-map entries must be a list of mappings")]
    map_units = [entry.get("id") for entry in entries if entry.get("kind") == "unit"]
    existing = sorted(path.name for path in (book_path / "units").glob("unit-*") if path.is_dir())
    if existing != map_units[: len(existing)]:
        findings = [_fail(book, "unit directories are not the coverage-map prefix")]
    else:
        findings = []
    map_checkpoints = [
        entry.get("id") for entry in entries if entry.get("kind") == "checkpoint"
    ]
    existing_checkpoints = sorted(
        path.name
        for path in (book_path / "checkpoints").glob("checkpoint-*")
        if path.is_dir()
    )
    if existing_checkpoints != map_checkpoints[: len(existing_checkpoints)]:
        findings.append(_fail(book, "checkpoint directories are not the coverage-map prefix"))
    return findings


def structure_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    _, scope_errors = content_dirs(root, book, unit)
    if scope_errors:
        return scope_errors
    if unit is not None and unit.startswith("checkpoint-"):
        findings = checkpoint_layout_findings(root, book, unit)
        findings += checkpoint_question_findings(root, book, unit)
        findings += checkpoint_solutions_findings(root, book, unit)
        findings += checkpoint_teacher_notes_findings(root, book, unit)
    else:
        findings = layout_findings(root, book, unit)
        findings += exercise_structure_findings(root, book, unit)
        findings += solutions_structure_findings(root, book, unit)
        findings += teacher_notes_findings(root, book, unit)
    if unit is None:
        findings += checkpoint_layout_findings(root, book)
        findings += checkpoint_question_findings(root, book)
        findings += checkpoint_solutions_findings(root, book)
        findings += checkpoint_teacher_notes_findings(root, book)
        findings += prefix_findings(root, book)
    # Sub-checks and layout may report the same missing file; keep one line each.
    return list(dict.fromkeys(findings))


def execute_notebooks(
    root: Path,
    book: str,
    notebook_name: str,
    unit: str | None = None,
    *,
    include_checkpoints: bool = False,
) -> list[str]:
    if include_checkpoints:
        contents, findings = content_dirs(root, book, unit)
        directories = [path for path, _kind in contents]
    else:
        directories, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for content_dir in directories:
        path = content_dir / notebook_name
        if not path.is_file():
            findings.append(_fail(content_dir.name, f"{notebook_name} does not exist"))
            continue
        notebook = read_nb(path)
        if notebook_name == "lesson.ipynb":
            notebook.cells = [cell for cell in notebook.cells if "no-exec" not in tags(cell)]
        try:
            NotebookClient(
                notebook,
                timeout=120,
                kernel_name="python3",
                resources={"metadata": {"path": str(content_dir)}},
            ).execute()
        except Exception as error:  # noqa: BLE001 - nbclient startup/execution failures vary
            summary = str(error).splitlines()[-1] if str(error) else type(error).__name__
            findings.append(
                _fail(content_dir.name, f"{notebook_name} execution failed: {summary}")
            )
    return findings


def exec_solutions_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    return execute_notebooks(
        root,
        book,
        "solutions.ipynb",
        unit,
        include_checkpoints=True,
    )


def exec_lessons_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    return execute_notebooks(root, book, "lesson.ipynb", unit)


def _ruff_command() -> list[str]:
    return ["uv", "run", "ruff", "check", "--no-cache", "--select", "E9,F63,F7,F82"]


def cell_lint_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    contents, findings = content_dirs(root, book, unit)
    if findings:
        return findings
    for content_dir, kind in contents:
        for path in sorted(content_dir.glob("*.ipynb")):
            notebook = read_nb(path)
            lines: list[str] = []
            line_cells: dict[int, int] = {}
            syntax_error_cells: set[int] = set()
            for cell_index, cell in enumerate(notebook.cells):
                if cell.cell_type != "code":
                    continue
                if kind == "unit" and "no-exec" in tags(cell):
                    continue
                source_lines = _sanitized_code_source(cell.source).splitlines()
                try:
                    compile("\n".join(source_lines), f"{path.name}:cell-{cell_index}", "exec")
                except SyntaxError as error:
                    syntax_error_cells.add(cell_index)
                    findings.append(
                        _fail(
                            content_dir.name,
                            f"{path.name} cell {cell_index}: syntax error: {error.msg}",
                        )
                    )
                for line in source_lines or [""]:
                    line_cells[len(lines) + 1] = cell_index
                    lines.append(line)
                lines.append("")
            if not lines:
                continue
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", encoding="utf-8", delete=False
            ) as temporary:
                temporary.write("\n".join(lines))
                temporary_path = Path(temporary.name)
            try:
                result = subprocess.run(
                    _ruff_command() + [str(temporary_path)],
                    text=True,
                    capture_output=True,
                    env={**os.environ, "UV_NO_SYNC": "1"},
                    check=False,
                    cwd=Path(__file__).resolve().parents[1],
                )
            finally:
                temporary_path.unlink(missing_ok=True)
            parsed = 0
            pending = None
            for line in result.stdout.splitlines():
                if re.match(r"^[A-Z]\d{3}\s+", line):
                    pending = line
                    continue
                pretty = re.search(r"-->\s+.*:(\d+):(\d+)$", line.strip())
                concise = re.search(r":(\d+):(\d+):\s+([A-Z]\d{3}.*)$", line)
                if pretty and pending:
                    source_line = int(pretty.group(1))
                    detail = pending
                elif concise:
                    source_line = int(concise.group(1))
                    detail = concise.group(3)
                else:
                    continue
                cell_index = line_cells.get(source_line, -1)
                parsed += 1
                if cell_index not in syntax_error_cells:
                    findings.append(
                        _fail(content_dir.name, f"{path.name} cell {cell_index}: {detail}")
                    )
                pending = None
            if result.returncode != 0 and parsed == 0:
                detail = result.stderr.strip() or result.stdout.strip()
                findings.append(
                    _fail(content_dir.name, f"ruff failed for {path.name}: {detail}")
                )
    return findings

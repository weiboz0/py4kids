"""Notebook verification functions promoted from the Plan 004 interim tests."""

from __future__ import annotations

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
MANIFEST_KEYS = {"id", "kind", "blueprint_version", "lessons", "concepts", "provenance"}
NOTES_HEADINGS = (
    "## Goals",
    "## Pacing",
    "## Common mistakes",
    "## Discussion prompts",
    "## Differentiation",
)
INTERACTIVE = re.compile(r"\binput\s*\(")
GUI_IMPORT = re.compile(r"^\s*(import|from)\s+(turtle|tkinter)\b", re.MULTILINE)
RANDOM_FROM_IMPORT = re.compile(r"^\s*from\s+random\s+import\b", re.MULTILINE)
EXERCISE_HEADING = re.compile(r"^## Exercise \d+", re.MULTILINE)
ASSET_REF = re.compile(r"assets/[\w.-]+\.py")


def _fail(scope: str, detail: str) -> str:
    return f"FAIL: {scope}: {detail}"


def book_root(root: Path, book: str) -> Path:
    return Path(root).resolve() / book


def unit_dirs(root: Path, book: str, unit: str | None = None) -> tuple[list[Path], list[str]]:
    units = book_root(root, book) / "units"
    if unit is not None:
        path = units / unit
        if not path.is_dir():
            return [], [_fail(unit, "unit directory does not exist")]
        return [path], []
    return sorted(path for path in units.glob("unit-*") if path.is_dir()), []


def read_nb(path: Path):
    return nbformat.read(path, as_version=4)


def code_cells(notebook):
    return [cell for cell in notebook.cells if cell.cell_type == "code"]


def tags(cell) -> list[str]:
    return cell.get("metadata", {}).get("tags", [])


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
    units, findings = unit_dirs(root, book, unit)
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
    for unit_dir in units:
        path = unit_dir / "manifest.yaml"
        if not path.is_file():
            findings.append(_fail(unit_dir.name, "missing manifest.yaml"))
            continue
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            findings.append(_fail(unit_dir.name, "manifest must be a mapping"))
            continue
        if set(manifest) != MANIFEST_KEYS:
            findings.append(_fail(unit_dir.name, f"manifest keys {set(manifest)}"))
            continue
        if manifest["kind"] != "unit":
            findings.append(_fail(unit_dir.name, "kind must be unit"))
        if manifest["blueprint_version"] != 1:
            findings.append(_fail(unit_dir.name, "blueprint_version must be 1"))
        if manifest["provenance"] != "original":
            findings.append(_fail(unit_dir.name, "provenance must be original"))
        if manifest["id"] != unit_dir.name:
            findings.append(_fail(unit_dir.name, "id does not match directory"))
            continue
        entry = entries.get(manifest["id"])
        if entry is None:
            findings.append(_fail(unit_dir.name, "not in coverage map"))
            continue
        if manifest["lessons"] != entry.get("lessons"):
            findings.append(_fail(unit_dir.name, "lessons differs from coverage map"))
        concepts = manifest["concepts"]
        if not isinstance(concepts, dict):
            findings.append(_fail(unit_dir.name, "manifest concepts must be a mapping"))
            continue
        if set(concepts) != {"introduces", "requires", "practices"}:
            findings.append(_fail(unit_dir.name, f"concept keys {set(concepts)}"))
            continue
        for field in ("introduces", "requires", "practices"):
            if not isinstance(concepts[field], list):
                findings.append(
                    _fail(unit_dir.name, f"manifest concepts.{field} must be a list")
                )
                continue
            if not all(isinstance(value, str) for value in concepts[field]):
                findings.append(
                    _fail(
                        unit_dir.name,
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
                findings.append(_fail(unit_dir.name, f"{field} differs from coverage map"))
    return findings


def hygiene_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        path = unit_dir / "exercises.ipynb"
        if not path.is_file():
            continue
        notebook = read_nb(path)
        for index, cell in enumerate(code_cells(notebook)):
            if cell.outputs:
                findings.append(_fail(unit_dir.name, f"exercises code cell {index} has outputs"))
            if cell.execution_count is not None:
                findings.append(_fail(unit_dir.name, f"exercises code cell {index} is executed"))
        if any(
            re.search(r"(?i)^#+\s*solution", cell.source, re.MULTILINE) for cell in notebook.cells
        ):
            findings.append(_fail(unit_dir.name, "exercises contain a solution heading"))
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
        if not exercises_path.is_file() or not solutions_path.is_file():
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
        codes = code_cells(solutions)
        assert_count = sum("assert" in cell.source for cell in codes)
        if assert_count < 3:
            findings.append(_fail(unit_dir.name, "solutions need >=3 assert cells"))
        joined = "\n".join(cell.source for cell in codes)
        for cell in codes:
            if INTERACTIVE.search(cell.source):
                findings.append(_fail(unit_dir.name, "solutions call input()"))
            if GUI_IMPORT.search(cell.source):
                findings.append(_fail(unit_dir.name, "solutions import a GUI"))
            if RANDOM_FROM_IMPORT.search(cell.source):
                findings.append(_fail(unit_dir.name, "solutions use 'from random import'"))
        if "random." in joined:
            seed_position = joined.find("random.seed(4)")
            first_use = next(
                (
                    match.start()
                    for match in re.finditer(r"\brandom\.\w+", joined)
                    if not joined.startswith("random.seed(4)", match.start())
                ),
                None,
            )
            if seed_position == -1:
                findings.append(_fail(unit_dir.name, "solutions use random without random.seed(4)"))
            elif first_use is not None and seed_position >= first_use:
                findings.append(
                    _fail(unit_dir.name, "solutions: random.seed(4) must precede first use")
                )
    return findings


def noexec_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        path = unit_dir / "lesson.ipynb"
        if not path.is_file():
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
        return [_fail(book, "unit directories are not the coverage-map prefix")]
    return []


def structure_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    _, unit_errors = unit_dirs(root, book, unit)
    if unit_errors:
        return unit_errors
    findings = layout_findings(root, book, unit)
    findings += exercise_structure_findings(root, book, unit)
    findings += solutions_structure_findings(root, book, unit)
    findings += teacher_notes_findings(root, book, unit)
    if unit is None:
        findings += prefix_findings(root, book)
    return findings


def execute_notebooks(
    root: Path, book: str, notebook_name: str, unit: str | None = None
) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        path = unit_dir / notebook_name
        if not path.is_file():
            continue
        notebook = read_nb(path)
        if notebook_name == "lesson.ipynb":
            notebook.cells = [cell for cell in notebook.cells if "no-exec" not in tags(cell)]
        try:
            NotebookClient(
                notebook,
                timeout=120,
                kernel_name="python3",
                resources={"metadata": {"path": str(unit_dir)}},
            ).execute()
        except Exception as error:  # noqa: BLE001 - nbclient startup/execution failures vary
            summary = str(error).splitlines()[-1] if str(error) else type(error).__name__
            findings.append(_fail(unit_dir.name, f"{notebook_name} execution failed: {summary}"))
    return findings


def exec_solutions_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    return execute_notebooks(root, book, "solutions.ipynb", unit)


def exec_lessons_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    return execute_notebooks(root, book, "lesson.ipynb", unit)


def _ruff_command() -> list[str]:
    return ["uv", "run", "ruff", "check", "--no-cache", "--select", "E9,F63,F7,F82"]


def cell_lint_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    for unit_dir in units:
        for path in sorted(unit_dir.glob("*.ipynb")):
            notebook = read_nb(path)
            lines: list[str] = []
            line_cells: dict[int, int] = {}
            syntax_error_cells: set[int] = set()
            for cell_index, cell in enumerate(notebook.cells):
                if cell.cell_type != "code" or "no-exec" in tags(cell):
                    continue
                source_lines = [
                    line
                    for line in cell.source.splitlines()
                    if not line.lstrip().startswith(("%", "!"))
                ]
                try:
                    compile("\n".join(source_lines), f"{path.name}:cell-{cell_index}", "exec")
                except SyntaxError as error:
                    syntax_error_cells.add(cell_index)
                    findings.append(
                        _fail(
                            unit_dir.name,
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
                        _fail(unit_dir.name, f"{path.name} cell {cell_index}: {detail}")
                    )
                pending = None
            if result.returncode != 0 and parsed == 0:
                detail = result.stderr.strip() or result.stdout.strip()
                findings.append(_fail(unit_dir.name, f"ruff failed for {path.name}: {detail}"))
    return findings

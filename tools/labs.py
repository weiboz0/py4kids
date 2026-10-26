"""``lab-check``: the real-simulator labs (design 013 §7.2, plan roar-002 Phase 0).

A lab is a unit's ``labs/real-sim.ipynb``: setup and recording cells a student runs against the
official simulator on their own machine (tagged ``no-exec``), and analysis cells that CI runs
against a committed-by-generation sample CSV. The check is BOOK-SCOPED to books with the
``labs: true`` flag in ``books.yaml``. For every unit:

- a unit whose manifest says ``lab: true`` has ``labs/real-sim.ipynb``; a ``labs/`` directory
  without ``lab: true`` is a finding (and so is ``lab: true``, or any ``labs/`` directory, in a
  book without the flag);
- the lab has no outputs or execution counts;
- its first code cell is tagged ``parameters`` and sets
  ``TELEMETRY_PATH = os.environ.get("ROAR_LAB_CSV", "telemetry.csv")``;
- a **code** cell that mentions ``carla``, ``roar_py_carla``, ``competition_runner`` or
  ``subprocess`` (lower case, so prose such as "CARLA" in a comment does not count) is tagged
  ``no-exec``; markdown cells are exempt;
- no code cell other than the parameters cell contains a ``.csv`` string literal;
- in a ``no-exec`` cell, by AST: a ``read_csv`` / ``load_csv`` call is a finding, and so is an
  ``open(...)`` whose mode is absent, not a literal, or read-capable (``r`` or ``+``); a write-only
  ``open(..., "w" / "a" / "x")`` is allowed (the recorder writes the student's CSV);
- then a copy with the ``no-exec`` cells removed is executed with ``ROAR_LAB_CSV`` set to the
  sample CSV named by ``curriculum/labs.yaml`` (``sample_csv:``, a repo-relative path).

``ci-local.sh`` runs it under the book's dependency group, so the analysis cells see the book's
stack. Lab notebooks are never collected by publish or export (``tests/test_labs.py`` pins it).
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path

import yaml
from nbclient import NotebookClient

from tools.books import book_flag, book_path
from tools.notebooks import _fail, code_cells, read_nb, tags, unit_dirs

FLAG = "labs"
LAB_NOTEBOOK = "real-sim.ipynb"
LABS_CONFIG = Path("curriculum") / "labs.yaml"
CSV_ENV = "ROAR_LAB_CSV"
PARAMETERS_TAG = "parameters"
NO_EXEC_TAG = "no-exec"
PARAMETERS_SOURCE = f'TELEMETRY_PATH = os.environ.get("{CSV_ENV}", "telemetry.csv")'
SIMULATOR_MENTION = re.compile(r"carla|competition_runner|subprocess")
READ_CALLS = frozenset({"read_csv", "load_csv"})
# ``<module>.open(file, mode)`` takes the mode second, like the builtin; ``Path(...).open(mode)``
# (any other attribute ``open``) takes it first.
FILE_FIRST_MODULES = frozenset({"io", "codecs", "gzip", "bz2", "lzma"})
_EXPECTED_VALUE = ast.dump(ast.parse(PARAMETERS_SOURCE).body[0].value)
_MISSING = object()


def _python_source(source: str) -> str | None:
    """The cell as Python: IPython line magics and shell escapes dropped; None for a cell magic."""
    if source.lstrip().startswith("%%"):
        return None
    return "\n".join(line for line in source.splitlines() if not line.lstrip().startswith(("%", "!")))


def _sets_telemetry_path(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "TELEMETRY_PATH"
        and ast.dump(node.value) == _EXPECTED_VALUE
        for node in tree.body
    )


def _csv_literals(tree: ast.Module) -> bool:
    return any(
        isinstance(node, ast.Constant) and isinstance(node.value, str) and ".csv" in node.value
        for node in ast.walk(tree)
    )


def _call_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def _open_mode(call: ast.Call):
    """The mode expression of an ``open`` call, or ``_MISSING`` when it has none."""
    for keyword in call.keywords:
        if keyword.arg == "mode":
            return keyword.value
    func = call.func
    file_first = isinstance(func, ast.Name) or (
        isinstance(func.value, ast.Name) and func.value.id in FILE_FIRST_MODULES
    )
    index = 1 if file_first else 0
    return call.args[index] if len(call.args) > index else _MISSING


def _read_findings(tree: ast.Module) -> list[str]:
    """What a no-exec (simulator-side) cell reads: it may only write."""
    details = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        if name in READ_CALLS:
            details.append(f"{name}() reads a CSV")
        elif name == "open":
            mode = _open_mode(node)
            if mode is _MISSING:
                details.append("open() without a mode reads")
            elif not (isinstance(mode, ast.Constant) and isinstance(mode.value, str)):
                details.append("open() mode is not a literal, so it may read")
            elif "r" in mode.value or "+" in mode.value:
                details.append(f"open() mode {mode.value!r} reads")
    return details


def _manifest_lab(unit_dir: Path) -> object:
    path = unit_dir / "manifest.yaml"
    if not path.is_file():
        return None
    try:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError:
        return None  # manifest-check reports it
    return manifest.get("lab") if isinstance(manifest, dict) else None


def sample_csv(root: Path, book: str) -> tuple[Path | None, list[str]]:
    """The sample CSV named by ``curriculum/labs.yaml`` (repo-relative), and any findings."""
    path = book_path(root, book) / LABS_CONFIG
    scope = f"{book}/labs.yaml"
    if not path.is_file():
        return None, [_fail(book, f"{LABS_CONFIG.as_posix()} does not exist")]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return None, [_fail(scope, f"does not parse ({type(error).__name__})")]
    if not isinstance(data, dict) or set(data) != {"sample_csv"} or not isinstance(data["sample_csv"], str):
        return None, [_fail(scope, "must be a mapping with exactly one key, sample_csv (a path)")]
    csv_path = Path(root).resolve() / data["sample_csv"]
    if not csv_path.is_file():
        return None, [_fail(scope, f"sample_csv {data['sample_csv']} does not exist (run the book's data "
                                   "generator first)")]
    return csv_path, []


def lab_notebook_findings(scope: str, path: Path) -> list[str]:
    """The static checks on one lab notebook (everything but the execution)."""
    notebook = read_nb(path)
    findings = []
    cells = code_cells(notebook)
    for index, cell in enumerate(cells):
        if cell.outputs:
            findings.append(_fail(scope, f"lab code cell {index} has outputs"))
        if cell.execution_count is not None:
            findings.append(_fail(scope, f"lab code cell {index} is executed"))
    if not cells:
        return findings + [_fail(scope, "lab has no code cells")]
    for index, cell in enumerate(cells):
        cell_tags = tags(cell)
        python = _python_source(cell.source)
        tree = None
        if python is not None:
            try:
                tree = ast.parse(python)
            except SyntaxError as error:
                findings.append(_fail(scope, f"lab code cell {index} does not parse "
                                             f"(SyntaxError: {error.msg}, line {error.lineno})"))
        if index == 0:
            if PARAMETERS_TAG not in cell_tags or tree is None or not _sets_telemetry_path(tree):
                findings.append(_fail(scope, f"the first code cell must be tagged {PARAMETERS_TAG!r} and set "
                                             f"{PARAMETERS_SOURCE}"))
            continue
        if PARAMETERS_TAG in cell_tags:
            findings.append(_fail(scope, f"lab code cell {index}: only the first code cell is the "
                                         "parameters cell"))
        if SIMULATOR_MENTION.search(cell.source) and NO_EXEC_TAG not in cell_tags:
            findings.append(_fail(scope, f"lab code cell {index} uses the simulator "
                                         f"(carla / competition_runner / subprocess) but is not {NO_EXEC_TAG}"))
        has_csv = _csv_literals(tree) if tree is not None else ".csv" in cell.source
        if has_csv:
            findings.append(_fail(scope, f"lab code cell {index} hard-codes a .csv path "
                                         "(use TELEMETRY_PATH from the parameters cell)"))
        if NO_EXEC_TAG in cell_tags and tree is not None:
            findings.extend(
                _fail(scope, f"lab code cell {index} is {NO_EXEC_TAG} and must only write: {detail}")
                for detail in _read_findings(tree)
            )
    return findings


def _execute_lab(scope: str, path: Path, csv_path: Path) -> list[str]:
    notebook = read_nb(path)
    notebook.cells = [cell for cell in notebook.cells if NO_EXEC_TAG not in tags(cell)]
    previous = os.environ.get(CSV_ENV)
    os.environ[CSV_ENV] = str(csv_path)  # the kernel inherits this process's environment
    try:
        NotebookClient(
            notebook,
            timeout=120,
            kernel_name="python3",
            resources={"metadata": {"path": str(path.parent)}},
        ).execute()
    except Exception as error:  # noqa: BLE001 - nbclient startup/execution failures vary
        summary = str(error).splitlines()[-1] if str(error) else type(error).__name__
        return [_fail(scope, f"{LAB_NOTEBOOK} execution failed: {summary}")]
    finally:
        if previous is None:
            os.environ.pop(CSV_ENV, None)
        else:
            os.environ[CSV_ENV] = previous
    return []


def lab_findings(root: Path, book: str, unit: str | None = None) -> list[str]:
    units, findings = unit_dirs(root, book, unit)
    if findings:
        return findings
    flagged = book_flag(root, book, FLAG)
    labs = []
    for unit_dir in units:
        lab = _manifest_lab(unit_dir)
        has_dir = (unit_dir / "labs").is_dir()
        if lab is not None and not isinstance(lab, bool):
            findings.append(_fail(unit_dir.name, "manifest lab must be true or false"))
            continue
        if lab and not flagged:
            findings.append(_fail(unit_dir.name, f"manifest lab: true needs the {FLAG!r} book flag"))
            continue
        if has_dir and not lab:
            findings.append(_fail(unit_dir.name, "a labs/ directory without manifest lab: true"))
            continue
        if lab:
            path = unit_dir / "labs" / LAB_NOTEBOOK
            if not path.is_file():
                findings.append(_fail(unit_dir.name, f"manifest lab: true but labs/{LAB_NOTEBOOK} does not exist"))
                continue
            labs.append((unit_dir.name, path))
    if not labs:
        return findings
    for scope, path in labs:
        findings.extend(lab_notebook_findings(scope, path))
    csv_path, csv_findings = sample_csv(root, book)
    if csv_findings:
        return findings + csv_findings
    if findings:
        return findings  # a statically broken lab is not executed
    for scope, path in labs:
        findings.extend(_execute_lab(scope, path, csv_path))
    return findings

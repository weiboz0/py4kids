"""The standalone-cell probe (design 012 D3, D6; plan 101 C).

Every executed lesson cell (a code cell without `no-exec`) is run **on its own**, in a fresh
temporary copy of the entry directory that holds only its `git ls-files`-tracked files, under
`sys.executable` with stdin from `/dev/null`, `PYTHONHASHSEED=0` and a timeout. Its stdout is
compared with the stored stdout (trailing whitespace per line and trailing blank lines ignored).

On a miss the cell is run again after a **prelude**: the transitive closure of the earlier executed
cells that bind a name it loads, that mutate a name the closure binds (`random.seed(1)` after
`import random`), or that name the same file (a writer before its reader). If that still misses,
after all earlier executed cells. A status:

- `standalone`: the cell alone matches its stored output (an output-free cell: runs clean, prints
  nothing).
- `prelude`: it matches after `prelude` (cell ids, in notebook order).
- `mismatch`: every run finished, but the output differs (unseeded `random`, say). `prelude`
  holds the closure, so a runner can still run the cell.
- `error` / `timeout`: the last run raised or ran out of time. These are site-check FAILs, never
  bundle data. A cell that times out alone is not run again.

The repo tree is never written: every run happens in a temporary copy.
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from tools.publish import SOLUTION_SOURCE, is_solution_source

SENTINEL = "--py4kids-probe-sentinel-5d1c--"
FILE_NAME = re.compile(r"[\w./-]*\w\.[A-Za-z][A-Za-z0-9]{0,7}")
# Runs with cwd at the copy and sys.path[0] == "" (as a Jupyter kernel does). Each cell is compiled
# and executed on its own, in one shared namespace; the sentinel goes out just before the last one.
_RUNNER = (
    "import json, sys\n"
    "cells = json.load(open(sys.argv[1], encoding='utf-8'))\n"
    "namespace = {'__name__': '__main__'}\n"
    "for index, source in enumerate(cells):\n"
    "    if index == len(cells) - 1:\n"
    "        print(sys.argv[2], flush=True)\n"
    "    exec(compile(source, f'<cell {index}>', 'exec'), namespace)\n"
)


@dataclass(frozen=True)
class ProbeResult:
    status: str  # standalone | prelude | mismatch | error | timeout
    prelude: list[str] = field(default_factory=list)  # cell ids, notebook order
    files: list[str] = field(default_factory=list)  # tracked paths relative to the entry dir
    detail: str = ""  # the last run's error line, for the report


@dataclass(frozen=True)
class _Analysis:
    binds: frozenset[str]
    loads: frozenset[str]
    mutates: frozenset[str]
    files: frozenset[str]


def _tags(cell) -> list[str]:
    return list(cell.get("metadata", {}).get("tags", []) or [])


def executed(cell) -> bool:
    return cell.get("cell_type") == "code" and "no-exec" not in _tags(cell)


def stored_stdout(cell) -> str:
    return "".join(o.get("text", "") for o in cell.get("outputs", [])
                   if o.get("output_type") == "stream" and o.get("name", "stdout") == "stdout")


def clean_output(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def _target_names(target: ast.AST) -> set[str]:
    return {node.id for node in ast.walk(target) if isinstance(node, ast.Name)}


def _base_name(node: ast.AST) -> str | None:
    while isinstance(node, (ast.Attribute, ast.Subscript, ast.Call)):
        node = node.func if isinstance(node, ast.Call) else node.value
    return node.id if isinstance(node, ast.Name) else None


class _Scope(ast.NodeVisitor):
    """Module-level binders and mutators, not descending into function or class bodies."""

    def __init__(self):
        self.binds: set[str] = set()
        self.mutates: set[str] = set()

    def _assigned(self, target: ast.AST) -> None:
        if isinstance(target, (ast.Attribute, ast.Subscript)):
            name = _base_name(target)
            if name:
                self.mutates.add(name)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for element in target.elts:
                self._assigned(element)
        elif isinstance(target, ast.Starred):
            self._assigned(target.value)
        elif isinstance(target, ast.Name):
            self.binds.add(target.id)

    def visit_FunctionDef(self, node):
        self.binds.add(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node):
        self.binds.add(node.name)

    def visit_Lambda(self, node):
        return

    def visit_Assign(self, node):
        for target in node.targets:
            self._assigned(target)
        self.visit(node.value)

    def visit_AugAssign(self, node):
        self._assigned(node.target)
        self.visit(node.value)

    def visit_AnnAssign(self, node):
        self._assigned(node.target)
        if node.value:
            self.visit(node.value)

    def visit_NamedExpr(self, node):
        self._assigned(node.target)
        self.visit(node.value)

    def visit_Import(self, node):
        for alias in node.names:
            self.binds.add(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name != "*":
                self.binds.add(alias.asname or alias.name)

    def visit_For(self, node):
        self._assigned(node.target)
        self.generic_visit(node)

    visit_AsyncFor = visit_For

    def visit_With(self, node):
        for item in node.items:
            if item.optional_vars is not None:
                self._assigned(item.optional_vars)
        self.generic_visit(node)

    visit_AsyncWith = visit_With

    def visit_Delete(self, node):
        for target in node.targets:
            if isinstance(target, (ast.Attribute, ast.Subscript)):
                self._assigned(target)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            name = _base_name(node.func.value)
            if name:
                self.mutates.add(name)
        self.generic_visit(node)


def analyse(source: str) -> _Analysis:
    """What a cell binds, loads, mutates and which file names it mentions (empty if unparsable)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return _Analysis(frozenset(), frozenset(), frozenset(), frozenset())
    scope = _Scope()
    scope.visit(tree)
    loads = {node.id for node in ast.walk(tree)
             if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
    files = {node.value.removeprefix("./") for node in ast.walk(tree)
             if isinstance(node, ast.Constant) and isinstance(node.value, str)
             and FILE_NAME.fullmatch(node.value)}
    return _Analysis(frozenset(scope.binds), frozenset(loads), frozenset(scope.mutates),
                     frozenset(files))


def closure(target: _Analysis, earlier: list[tuple[int, _Analysis]]) -> list[int]:
    """Indexes of the earlier cells the target depends on (binders, mutators, file writers)."""
    included: set[int] = set()
    changed = True
    while changed:
        changed = False
        members = [target] + [a for i, a in earlier if i in included]
        loads = set().union(*(a.loads for a in members))
        files = set().union(*(a.files for a in members))
        bound = set().union(*(a.binds for i, a in earlier if i in included)) if included else set()
        for index, analysis in earlier:
            if index in included:
                continue
            if (analysis.binds & loads or analysis.mutates & bound or analysis.files & files):
                included.add(index)
                changed = True
    return sorted(included)


def tracked_files(entry_dir: Path) -> list[str]:
    """The entry's `git ls-files` paths, relative to `entry_dir` (sorted, existing files only)."""
    result = subprocess.run(["git", "-C", str(entry_dir), "ls-files", "-z", "--cached", "--", "."],
                            capture_output=True, check=False)
    if result.returncode != 0:
        raise ValueError(f"{entry_dir}: git ls-files failed: {result.stderr.decode().strip()}")
    names = [name for name in result.stdout.decode("utf-8").split("\0") if name]
    return sorted(name for name in names if (entry_dir / name).is_file())


def shippable(relative: str) -> bool:
    """A tracked file a block may list: never a solution source, `assets/verify/**` or solution."""
    path = Path(relative)
    return not (is_solution_source(path) or SOLUTION_SOURCE.match(path.name)
                or path.name.startswith("solutions"))


def named_files(constants, tracked: set[str]) -> list[str]:
    """Tracked files that string constants name, in the entry dir or its `assets/`."""
    found = set()
    for constant in constants:
        for candidate in (constant, f"assets/{constant}"):
            if candidate in tracked and shippable(candidate):
                found.add(candidate)
    return sorted(found)


class _Runner:
    def __init__(self, entry_dir: Path, work: Path, timeout_s: float):
        self.pristine = work / "pristine"
        self.work = work
        self.timeout_s = timeout_s
        self.pristine.mkdir()
        for relative in tracked_files(entry_dir):
            destination = self.pristine / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(entry_dir / relative, destination)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        self.env.update(PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")

    def run(self, sources: list[str]) -> tuple[str, str, str]:
        """Run `sources` in a fresh copy; return (outcome ok|error|timeout, stdout after the
        sentinel, detail)."""
        scratch = Path(tempfile.mkdtemp(dir=self.work))
        try:
            copy = scratch / "entry"
            shutil.copytree(self.pristine, copy)
            cells = scratch / "cells.json"
            cells.write_text(json.dumps(sources), encoding="utf-8")
            try:
                done = subprocess.run([sys.executable, "-c", _RUNNER, str(cells), SENTINEL],
                                      cwd=copy, stdin=subprocess.DEVNULL, capture_output=True,
                                      env=self.env, timeout=self.timeout_s, check=False)
            except subprocess.TimeoutExpired:
                return "timeout", "", f"timed out after {self.timeout_s:g} s"
            stdout = done.stdout.decode("utf-8", errors="replace")
            marker = SENTINEL + "\n"
            after = stdout.split(marker, 1)[1] if marker in stdout else ""
            if done.returncode != 0:
                lines = done.stderr.decode("utf-8", errors="replace").strip().splitlines()
                return "error", after, lines[-1] if lines else f"exit {done.returncode}"
            return "ok", after, ""
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


def probe_cells(entry_dir: Path, cells, timeout_s: float = 20, workers: int | None = None
                ) -> dict[str, ProbeResult]:
    """Probe every executed cell of `cells` (a lesson's cells, in order); keyed by cell id."""
    entry_dir = Path(entry_dir)
    order = [(index, cell) for index, cell in enumerate(cells) if executed(cell)]
    if not order:
        return {}
    tracked = set(tracked_files(entry_dir))
    analyses = {index: analyse(cell["source"]) for index, cell in order}
    wanted = {index: clean_output(stored_stdout(cell)) for index, cell in order}
    results: dict[int, ProbeResult] = {}
    with tempfile.TemporaryDirectory(prefix="py4kids-probe-") as temp:
        runner = _Runner(entry_dir, Path(temp), timeout_s)
        pool_size = workers or min(8, os.cpu_count() or 1)
        with ThreadPoolExecutor(max_workers=pool_size) as pool:
            alone = dict(zip([i for i, _ in order],
                             pool.map(lambda pair: runner.run([pair[1]["source"]]), order),
                             strict=True))

        def files_for(indexes: list[int]) -> list[str]:
            constants = set().union(*(analyses[i].files for i in indexes))
            return named_files(constants, tracked)

        for index, cell in order:
            outcome, stdout, detail = alone[index]
            if outcome == "ok" and clean_output(stdout) == wanted[index]:
                results[index] = ProbeResult("standalone", [], files_for([index]))
                continue
            usable = [(i, analyses[i]) for i, _ in order
                      if i < index and results[i].status not in ("error", "timeout")]
            needed = closure(analyses[index], usable)
            if outcome == "timeout":
                results[index] = ProbeResult("timeout", [], files_for([index]), detail)
                continue
            attempts = []
            if needed:
                attempts.append(needed)
            everything = [i for i, _ in usable]
            if everything and everything != needed:
                attempts.append(everything)
            status = None
            for prelude in attempts:
                outcome, stdout, detail = runner.run(
                    [cells[i]["source"] for i in prelude] + [cell["source"]])
                if outcome == "ok" and clean_output(stdout) == wanted[index]:
                    status = ProbeResult("prelude", [cells[i]["id"] for i in prelude],
                                         files_for([*prelude, index]))
                    break
                if outcome == "timeout":
                    break
            if status is None:
                final = {"ok": "mismatch", "error": "error", "timeout": "timeout"}[outcome]
                status = ProbeResult(final, [cells[i]["id"] for i in needed] if final == "mismatch"
                                     else [], files_for([*needed, index]), detail)
            results[index] = status
    return {cells[index]["id"]: result for index, result in results.items()}

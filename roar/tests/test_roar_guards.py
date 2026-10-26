"""Routed guard tests for *Applied Python: Autonomous Racing* (plan roar-001 Phase E).

1. **API order** (design 013 §7.1): every taught callable in ``curriculum/api-order.yaml`` appears
   only at or after the coverage-map entry that introduces its concept; every ``library_methods``
   name is either infrastructure or taught; every ``api-order`` key is in ``library_methods``;
   every concept id is known. Calls are resolved through ``import m``, ``import m as a``,
   ``from m import f``, ``from m import f as g`` and attribute calls. Not resolved (a known limit):
   a callable bound to another name first (``f = scipy.optimize.minimize; f(...)``) and
   ``getattr(module, "name")(...)``. A file or code cell that does not parse is itself a finding.
2. **Deny-list** (design 013 §7.4): no tracked CARLA map, OpenDRIVE or Unreal asset, no vendored
   ``competition_runner.py`` / ``infrastructure.py``, and no waypoint dump outside the gitignored
   ``roar/data/generated/``.
3. **Labs-tracked** (design 013 §7.2): under any ``roar/**/labs/`` only ``*.ipynb`` and
   ``README.md`` may be tracked (the repo is public; lab outputs stay on the student's machine).
4. **The ``_truth`` rule** (plan roar-004): the carla-like car's hidden-parameter module is never
   named in a student-facing source (units, checkpoints, the projects' notebooks and agents, labs,
   learner docs, reference, the syllabus). ``racekit`` itself and its tests are exempt.
"""

from __future__ import annotations

import ast
import fnmatch
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
BOOK = "roar"


# --- 1. API order --------------------------------------------------------------------------------


@dataclass(frozen=True)
class Call:
    module: str | None  # the resolved module, when the callee came through an import
    name: str  # the called name (the last component)
    line: int

    @property
    def canonical(self) -> str:
        return f"{self.module}.{self.name}" if self.module else self.name


def load_api_order(root: Path) -> dict:
    data = yaml.safe_load((root / BOOK / "curriculum" / "api-order.yaml").read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) != {"api_order_version", "infrastructure", "taught"}:
        raise ValueError("api-order.yaml keys must be exactly api_order_version, infrastructure, taught")
    if data["api_order_version"] != 1:
        raise ValueError("api_order_version must be 1")
    if not isinstance(data["infrastructure"], list) or not all(isinstance(n, str) for n in data["infrastructure"]):
        raise ValueError("infrastructure must be a list of names")
    taught = data["taught"]
    if not isinstance(taught, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in taught.items()
    ):
        raise ValueError("taught must map `name` or `module:name` to a concept id")
    return data


def _key_parts(key: str) -> tuple[str | None, str]:
    module, _, name = key.rpartition(":")
    return (module or None), name


def resolve_calls(source: str) -> list[Call]:
    """Every call in ``source``, resolved to a canonical (module, name) where imports allow.

    Raises ``SyntaxError`` when ``source`` does not parse (the caller reports it)."""
    tree = ast.parse(source)
    modules: dict[str, str] = {}  # local name -> module
    functions: dict[str, tuple[str, str]] = {}  # local name -> (module, name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    modules[alias.asname] = alias.name
                else:
                    top = alias.name.split(".")[0]
                    modules[top] = top
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            for alias in node.names:
                functions[alias.asname or alias.name] = (node.module, alias.name)

    def dotted(node: ast.AST) -> list[str] | None:
        if isinstance(node, ast.Name):
            return [node.id]
        if isinstance(node, ast.Attribute):
            inner = dotted(node.value)
            return None if inner is None else [*inner, node.attr]
        return None

    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            if func.id in functions:
                module, name = functions[func.id]
                calls.append(Call(module, name, node.lineno))
            else:
                calls.append(Call(None, func.id, node.lineno))
        elif isinstance(func, ast.Attribute):
            chain = dotted(func.value)
            if chain and chain[0] in modules:
                module = ".".join([modules[chain[0]], *chain[1:]])
                calls.append(Call(module, func.attr, node.lineno))
            elif chain and chain[0] in functions:  # from m import sub; sub.f()
                base_module, base_name = functions[chain[0]]
                module = ".".join([base_module, base_name, *chain[1:]])
                calls.append(Call(module, func.attr, node.lineno))
            else:
                calls.append(Call(None, func.attr, node.lineno))
    return calls


def _notebook_code(path: Path) -> list[str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    sources = []
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        if "verify" in cell.get("metadata", {}).get("tags", []):
            continue  # verification-only, never scanned (mirrors concept-scan)
        source = cell.get("source", "")
        source = "".join(source) if isinstance(source, list) else source
        # IPython magics and shell escapes are not Python
        sources.append("\n".join(line for line in source.splitlines() if not line.lstrip().startswith(("%", "!"))))
    return sources


def entry_files(root: Path, entry: dict) -> list[Path]:
    """The files positioned at a coverage-map entry (design 013 §7.1 scan scope)."""
    book = root / BOOK
    entry_id = entry["id"]
    kind = entry["kind"]
    files: list[Path] = []
    if kind == "unit":
        unit = book / "units" / entry_id
        files += [unit / name for name in ("lesson.ipynb", "exercises.ipynb", "solutions.ipynb")]
        files += sorted((unit / "labs").glob("*.ipynb"))
        number = re.match(r"unit-(\d{2})-", entry_id).group(1)
        files += sorted((book / "projects" / "racekit" / "milestones").glob(f"unit-{number}-*.ipynb"))
        files.append(book / "projects" / "racekit" / "agents" / f"unit-{number}.py")
    elif kind == "checkpoint":
        files += sorted((book / "checkpoints" / entry_id).glob("*.ipynb"))
        files += sorted((book / "checkpoints" / entry_id).glob("*.py"))
    elif kind == "project":
        files += sorted((book / "projects" / entry_id).rglob("*.ipynb"))
        files += sorted((book / "projects" / entry_id).rglob("*.py"))
    return [path for path in files if path.is_file()]


def _sources(path: Path) -> list[str]:
    if path.suffix == ".ipynb":
        return _notebook_code(path)
    return [path.read_text(encoding="utf-8")]


def api_order_findings(root: Path) -> list[str]:
    curriculum = root / BOOK / "curriculum"
    api = load_api_order(root)
    baseline = yaml.safe_load((curriculum / "baseline.yaml").read_text(encoding="utf-8"))
    library = set(baseline.get("library_methods") or [])
    concepts = yaml.safe_load((curriculum / "concepts.yaml").read_text(encoding="utf-8"))
    known = {concept["id"] for concept in concepts["concepts"]}
    entries = yaml.safe_load((curriculum / "coverage-map.yaml").read_text(encoding="utf-8"))["entries"]
    introduced_at: dict[str, int] = {}
    for position, entry in enumerate(entries):
        for concept in entry.get("introduces", []):
            introduced_at.setdefault(concept, position)

    findings = []
    taught_names = set()
    for key, concept in sorted(api["taught"].items()):
        _, name = _key_parts(key)
        taught_names.add(name)
        if name not in library:
            findings.append(f"api-order key {key!r} is not in baseline.yaml library_methods")
        if concept not in known:
            findings.append(f"api-order key {key!r} maps to unknown concept {concept!r}")
        elif concept not in introduced_at:
            findings.append(f"api-order key {key!r}: concept {concept!r} is introduced by no entry")
    for name in sorted(library - taught_names - set(api["infrastructure"])):
        findings.append(f"library_methods name {name!r} is in neither api-order taught nor infrastructure")

    rules = []
    for key, concept in api["taught"].items():
        if concept in introduced_at:
            module, name = _key_parts(key)
            rules.append((key, module, name, introduced_at[concept]))
    for position, entry in enumerate(entries):
        for path in entry_files(root, entry):
            for source in _sources(path):
                try:
                    calls = resolve_calls(source)
                except SyntaxError as error:
                    findings.append(
                        f"{path.relative_to(root)}: cannot parse a code cell or file "
                        f"(SyntaxError: {error.msg}, line {error.lineno}); API order cannot be checked"
                    )
                    continue
                for call in calls:
                    for key, module, name, intro in rules:
                        if call.name != name or position >= intro:
                            continue
                        if module is not None and call.module != module:
                            continue
                        findings.append(
                            f"{path.relative_to(root)}:{call.line}: {call.canonical}() is taught by "
                            f"{entries[intro]['id']} but used in the earlier entry {entry['id']}"
                        )
    return findings


def test_api_order_holds_for_the_real_book():
    assert api_order_findings(REPO) == []


def test_api_order_file_schema():
    api = load_api_order(REPO)
    assert api["api_order_version"] == 1


def _notebook(*cells: tuple[str, list[str]]) -> str:
    return json.dumps({
        "cells": [
            {"cell_type": "code", "metadata": {"tags": tags}, "source": source, "outputs": [],
             "execution_count": None}
            for source, tags in cells
        ],
        "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
    })


def make_book(tmp_path: Path, unit1_code: str = "x = 1\n", *, taught=None, infrastructure=None,
              library=None, verify_code: str | None = None) -> Path:
    """A temp tree of the real book's shape: two units, the second introduces `optimisation`."""
    curriculum = tmp_path / BOOK / "curriculum"
    curriculum.mkdir(parents=True)
    (curriculum / "concepts.yaml").write_text(yaml.safe_dump({"concepts_version": 1, "concepts": [
        {"id": "race-basics", "name": "Race basics", "category": "techniques"},
        {"id": "optimisation", "name": "Optimisation", "category": "techniques"},
    ]}))
    (curriculum / "coverage-map.yaml").write_text(yaml.safe_dump({"map_version": 1, "entries": [
        {"id": "unit-01-start", "kind": "unit", "lessons": 2, "introduces": ["race-basics"],
         "requires": [], "practices": []},
        {"id": "unit-02-tune", "kind": "unit", "lessons": 2, "introduces": ["optimisation"],
         "requires": ["race-basics"], "practices": ["race-basics"]},
    ]}))
    taught = {"scipy.optimize:minimize": "optimisation", "fit": "optimisation"} if taught is None else taught
    infrastructure = ["run_race"] if infrastructure is None else infrastructure
    library = ["run_race", "minimize", "fit"] if library is None else library
    (curriculum / "baseline.yaml").write_text(yaml.safe_dump(
        {"baseline_version": 1, "entries": [], "library_methods": library}))
    (curriculum / "api-order.yaml").write_text(yaml.safe_dump(
        {"api_order_version": 1, "infrastructure": infrastructure, "taught": taught}))
    for unit in ("unit-01-start", "unit-02-tune"):
        (tmp_path / BOOK / "units" / unit).mkdir(parents=True)
    cells = [(unit1_code, [])]
    if verify_code is not None:
        cells.append((verify_code, ["verify"]))
    (tmp_path / BOOK / "units" / "unit-01-start" / "lesson.ipynb").write_text(_notebook(*cells))
    (tmp_path / BOOK / "units" / "unit-02-tune" / "lesson.ipynb").write_text(
        _notebook(("from scipy.optimize import minimize\nminimize(f, 0)\nmodel.fit(x)\n", [])))
    return tmp_path


def test_a_clean_temp_book_passes(tmp_path):
    assert api_order_findings(make_book(tmp_path, "result = run_race(agent)\n")) == []


@pytest.mark.parametrize("code", [
    "import scipy.optimize\nscipy.optimize.minimize(f, 0)\n",  # qualified
    "import scipy.optimize as so\nso.minimize(f, 0)\n",  # import m as a
    "from scipy.optimize import minimize\nminimize(f, 0)\n",  # from m import f
    "from scipy.optimize import minimize as solve_it\nsolve_it(f, 0)\n",  # from m import f as g
    "from scipy import optimize\noptimize.minimize(f, 0)\n",  # from m import sub; sub.f()
    "model.fit(x, y)\n",  # an attribute call on an object
])
def test_premature_use_fails_in_every_call_form(tmp_path, code):
    findings = api_order_findings(make_book(tmp_path, code))
    assert len(findings) == 1 and "used in the earlier entry unit-01-start" in findings[0], findings
    assert "unit-02-tune" in findings[0]


def test_a_qualified_key_ignores_a_same_named_call_from_another_module(tmp_path):
    code = "import mylib\nmylib.minimize(f)\nminimize = min\nminimize(1, 2)\n"
    assert api_order_findings(make_book(tmp_path, code)) == []


def test_a_syntax_error_is_a_finding_not_a_skip(tmp_path):
    findings = api_order_findings(make_book(tmp_path, "def broken(:\n    pass\n"))
    assert len(findings) == 1 and "cannot parse" in findings[0] and "lesson.ipynb" in findings[0]
    book = tmp_path / "second"
    make_book(book)
    agents = book / BOOK / "projects" / "racekit" / "agents"
    agents.mkdir(parents=True)
    (agents / "unit-01.py").write_text("x = = 1\n")
    findings = api_order_findings(book)
    assert len(findings) == 1 and "agents/unit-01.py: cannot parse" in findings[0]


def test_premature_use_in_a_verify_cell_is_ignored(tmp_path):
    book = make_book(tmp_path, "x = 1\n", verify_code="from scipy.optimize import minimize\nminimize(f, 0)\n")
    assert api_order_findings(book) == []


def test_premature_use_in_an_agent_file_fails(tmp_path):
    book = make_book(tmp_path)
    agents = book / BOOK / "projects" / "racekit" / "agents"
    agents.mkdir(parents=True)
    (agents / "unit-01.py").write_text("def step(model):\n    return model.fit(1)\n")
    findings = api_order_findings(book)
    assert len(findings) == 1 and "agents/unit-01.py:2" in findings[0]


def test_an_unmapped_library_method_fails(tmp_path):
    findings = api_order_findings(make_book(tmp_path, library=["run_race", "minimize", "fit", "plot"]))
    assert findings == ["library_methods name 'plot' is in neither api-order taught nor infrastructure"]


def test_an_api_order_key_missing_from_library_methods_fails(tmp_path):
    findings = api_order_findings(make_book(tmp_path, library=["run_race", "minimize"]))
    assert findings == ["api-order key 'fit' is not in baseline.yaml library_methods"]


def test_an_unknown_concept_id_fails(tmp_path):
    findings = api_order_findings(make_book(
        tmp_path, taught={"scipy.optimize:minimize": "optimisation", "fit": "curve-fitting"}))
    assert findings == ["api-order key 'fit' maps to unknown concept 'curve-fitting'"]


def test_the_api_order_schema_is_enforced(tmp_path):
    book = make_book(tmp_path)
    path = book / BOOK / "curriculum" / "api-order.yaml"
    path.write_text("api_order_version: 1\ntaught: {}\n")
    with pytest.raises(ValueError, match="keys must be exactly"):
        load_api_order(book)
    path.write_text("api_order_version: 1\ninfrastructure: []\ntaught: {fit: 3}\n")
    with pytest.raises(ValueError, match="taught must map"):
        load_api_order(book)


# --- 2. The deny-list ----------------------------------------------------------------------------

DENIED_PATTERNS = ("*.umap", "*.xodr", "*.uasset")
DENIED_NAMES = ("competition_runner.py", "infrastructure.py")
GENERATED = "roar/data/generated/"


def tracked_files() -> list[str]:
    return subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True,
    ).stdout.splitlines()


def deny_list_findings(paths: list[str]) -> list[str]:
    findings = []
    for path in paths:
        name = path.rsplit("/", 1)[-1]
        lowered = name.lower()
        if any(fnmatch.fnmatch(lowered, pattern) for pattern in DENIED_PATTERNS):
            findings.append(f"{path}: CARLA map / OpenDRIVE / Unreal assets are never committed")
        elif name in DENIED_NAMES:
            findings.append(f"{path}: ROAR_Competition files are never vendored (it has no licence)")
        elif lowered.startswith("waypoints") and not path.startswith(GENERATED):
            findings.append(f"{path}: waypoint dumps are never committed")
    return findings


def test_no_tracked_maps_waypoints_or_competition_files():
    assert deny_list_findings(tracked_files()) == []


def test_the_deny_list_catches_each_kind():
    paths = [
        "roar/maps/Monza.umap", "roar/maps/monza.XODR", "assets/car.uasset",
        "roar/projects/racekit/competition_runner.py", "vendor/infrastructure.py",
        "roar/data/waypoints_monza.npz", "roar/data/generated/waypoints.npz",
        "roar/projects/racekit/racekit/runner.py", "README.md",
    ]
    findings = deny_list_findings(paths)
    assert [finding.split(":")[0] for finding in findings] == paths[:6]


# --- 3. Labs hold only notebooks and a README ----------------------------------------------------


def labs_findings(paths: list[str]) -> list[str]:
    return [
        f"{path}: only *.ipynb and README.md may be tracked under a labs/ folder (student data stays local)"
        for path in paths
        if path.startswith(f"{BOOK}/") and "/labs/" in path
        and not (path.endswith(".ipynb") or path.rsplit("/", 1)[-1] == "README.md")
    ]


def test_labs_track_only_notebooks_and_readmes():
    assert labs_findings(tracked_files()) == []


def test_the_labs_guard_catches_lab_data():
    paths = [
        "roar/units/unit-01-race/labs/real-sim.ipynb",
        "roar/units/unit-01-race/labs/README.md",
        "roar/units/unit-01-race/labs/telemetry.csv",
        "roar/units/unit-05-steer/labs/out/run.png",
        "recsys/units/unit-01-x/labs/data.csv",
    ]
    assert [finding.split(":")[0] for finding in labs_findings(paths)] == paths[2:4]


# --- 4. The _truth rule (plan roar-004) ----------------------------------------------------------

TRUTH = "_" + "truth"  # spelled in two parts, so this guard does not flag itself
STUDENT_DIRS = ("units", "checkpoints", "labs", "docs", "reference")


def student_facing(path: str) -> bool:
    """Is ``path`` (repo-relative, POSIX) a student-facing source of the book?"""
    parts = path.split("/")
    if parts[0] != BOOK or len(parts) < 2 or "__pycache__" in parts:
        return False
    if parts[1] in STUDENT_DIRS or path == f"{BOOK}/syllabus.md" or "labs" in parts[1:-1]:
        return True
    if parts[1] == "projects":
        if path.startswith((f"{BOOK}/projects/racekit/racekit/", f"{BOOK}/projects/racekit/tests/")):
            return False
        return path.endswith(".ipynb") or "agents" in parts[2:-1]
    return False


def student_sources(root: Path) -> list[str]:
    paths = []
    for file in (root / BOOK).rglob("*"):
        relative = file.relative_to(root).as_posix()
        if file.is_file() and student_facing(relative):
            paths.append(relative)
    return sorted(paths)


def truth_findings(root: Path, paths: list[str]) -> list[str]:
    return [
        f"{path}: names the carla-like car's hidden-parameter module (racekit.{TRUTH}); never in teaching material"
        for path in paths
        if TRUTH in (root / path).read_text(encoding="utf-8", errors="replace")
    ]


def test_no_student_facing_source_names_the_truth_module():
    paths = student_sources(REPO)
    assert any(path.endswith(".ipynb") for path in paths) and f"{BOOK}/syllabus.md" in paths
    assert any("/agents/" in path for path in paths)
    assert truth_findings(REPO, paths) == []


def test_the_truth_rule_scope_and_its_catch(tmp_path):
    assert student_facing("roar/units/unit-06-x/lesson.ipynb")
    assert student_facing("roar/checkpoints/cp-a/checkpoint.ipynb")
    assert student_facing("roar/projects/racekit/milestones/unit-06.ipynb")
    assert student_facing("roar/projects/racekit/agents/unit-06.py")
    assert student_facing("roar/labs/README.md") and student_facing("roar/units/u/labs/real-sim.ipynb")
    assert student_facing("roar/docs/README.md") and student_facing("roar/reference/upstream.md")
    assert student_facing("roar/syllabus.md")
    assert not student_facing("roar/projects/racekit/racekit/cars.py")
    assert not student_facing("roar/projects/racekit/tests/test_racekit_noise.py")
    assert not student_facing("roar/data/gen_sysid.py") and not student_facing("roar/tests/test_roar_guards.py")
    assert not student_facing("docs/plans/roar/roar-004-dynamic-car.md")
    lesson = tmp_path / "roar" / "units" / "unit-08-x" / "lesson.ipynb"
    lesson.parent.mkdir(parents=True)
    lesson.write_text('{"cells": [{"source": "from racekit import ' + TRUTH + '"}]}', encoding="utf-8")
    (tmp_path / "roar" / "syllabus.md").write_text("Unit 8 identifies the car.\n", encoding="utf-8")
    paths = student_sources(tmp_path)
    assert paths == ["roar/syllabus.md", "roar/units/unit-08-x/lesson.ipynb"]
    assert [finding.split(":")[0] for finding in truth_findings(tmp_path, paths)] == [paths[1]]

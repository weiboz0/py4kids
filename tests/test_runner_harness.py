"""The runner's Python harness under CPython (plan 104 Phase A).

``runner/py/harness.py`` and ``runner/py/fake_turtle.py`` run inside Pyodide in the browser; the
logic that does not need a browser is checked here: ``outputs_match`` parity with
``tools/judge.py`` (source and behaviour, line-exact and token modes), stdin and ``EOFError``,
sessions and working directories, fixture and assert grading, and the turtle port and rule
against ``tools/fake_turtle.py``. Process isolation (a fresh worker per check) is the runner
page's, proven by the Playwright suite (site/e2e/runner.spec.ts).
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import pytest

import tools.fake_turtle as original_turtle
from tools import judge

ROOT = Path(__file__).resolve().parents[1]
RUNNER_PY = ROOT / "runner" / "py"
sys.path.insert(0, str(RUNNER_PY))

import fake_turtle  # runner/py, the browser port
import harness

# Pyodide releases and the CPython minor each ships (pyodide-lock.json `info.python`).
PYODIDE_PYTHON = {"0.27.8": "3.12"}


@pytest.fixture
def h(tmp_path, monkeypatch):
    """A fresh harness rooted in a temporary directory; restores sys.modules['turtle'] and sys.path."""
    monkeypatch.setattr(sys, "path", list(sys.path))
    saved_turtle = sys.modules.get("turtle")
    yield harness.Harness(str(tmp_path))
    if saved_turtle is None:
        sys.modules.pop("turtle", None)
    else:
        sys.modules["turtle"] = saved_turtle


def run(h, code, *, stdin="", session="s1", check=None, files=()):
    return h.run(
        {"code": code, "stdin": stdin, "session": session, "check": check, "files": list(files)}
    )


# --- outputs_match parity with tools/judge.py ------------------------------------------------


def test_outputs_match_is_ported_verbatim():
    for name in ("outputs_match", "_output_lines"):
        assert inspect.getsource(getattr(harness, name)) == inspect.getsource(getattr(judge, name))


@pytest.mark.parametrize(
    ("actual", "expected", "line_exact"),
    [
        ("15 10 4\n", "15 10 4\n", True),
        ("15\n10\n4\n", "15 10 4\n", True),
        ("15\n10\n4\n", "15 10 4\n", False),
        ("15 10 4   \n\n\n", "15 10 4\n", True),
        ("  15 10 4\n", "15 10 4\n", True),
        ("a\n\nb\n", "a\nb\n", True),
        ("a\n\nb\n", "a\nb\n", False),
        ("", "", True),
        ("", "\n", False),
        ("1 2", "1  2\r\n", False),
        ("1 2\r\n", "1 2\n", True),
        ("x", "y", False),
    ],
)
def test_outputs_match_agrees_with_the_judge(actual, expected, line_exact):
    assert harness.outputs_match(actual, expected, line_exact=line_exact) == judge.outputs_match(
        actual, expected, line_exact=line_exact
    )


def test_line_exact_rejects_split_lines_and_token_accepts_them():
    assert harness.outputs_match("15\n10\n4\n", "15 10 4\n", line_exact=True) is False
    assert harness.outputs_match("15\n10\n4\n", "15 10 4\n", line_exact=False) is True


def test_pyodide_pin_matches_the_ci_python_minor():
    package = json.loads((ROOT / "runner" / "package.json").read_text(encoding="utf-8"))
    pin = package["devDependencies"]["pyodide"]
    assert pin == "0.27.8"
    minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    assert PYODIDE_PYTHON[pin] == minor
    assert (ROOT / ".python-version").read_text(encoding="utf-8").strip() == minor
    lock = ROOT / "runner" / "node_modules" / "pyodide" / "pyodide-lock.json"
    if lock.is_file():
        info = json.loads(lock.read_text(encoding="utf-8"))["info"]
        assert info["version"] == pin
        assert info["python"].startswith(minor + ".")


# --- running code ----------------------------------------------------------------------------


def test_prints_and_reports_ok(h):
    result = run(h, "print('hello')\nprint(2 + 3)")
    assert result["stdout"] == "hello\n5\n"
    assert result["stderr"] == ""
    assert result["status"] == "ok"
    assert result["results"] == []
    assert result["segments"] == []


def test_input_reads_stdin_and_raises_eoferror_at_end(h):
    result = run(h, "a = input('name? ')\nprint('hi', a)\nb = input()\n", stdin="Ada\n")
    assert result["stdout"] == "name? hi Ada\n"
    assert result["status"] == "error"
    assert result["stderr"].rstrip().endswith("EOFError: EOF when reading a line")


def test_stdin_read_methods(h):
    code = "import sys\nfirst = sys.stdin.readline()\nrest = sys.stdin.read()\nprint(repr(first), repr(rest), repr(sys.stdin.read()))"
    result = run(h, code, stdin="1 2\n3\n4\n")
    assert result["stdout"] == "'1 2\\n' '3\\n4\\n' ''\n"


def test_traceback_names_only_student_frames(h):
    result = run(h, "def f():\n    return 1 / 0\n\nf()\n", check={"kind": "output", "turtle": False})
    assert result["status"] == "error"
    assert "ZeroDivisionError: division by zero" in result["stderr"]
    assert 'File "main.py", line 4' in result["stderr"]
    assert "harness" not in result["stderr"]


@pytest.mark.parametrize(
    ("code", "status", "stderr"),
    [
        ("import sys\nsys.exit()", "ok", ""),
        ("import sys\nsys.exit(0)", "ok", ""),
        ("import sys\nsys.exit(3)", "error", ""),
        ("import sys\nsys.exit('bye')", "error", "bye\n"),
    ],
)
def test_system_exit_as_cpython(h, code, status, stderr):
    result = run(h, code)
    assert (result["status"], result["stderr"]) == (status, stderr)


def test_restores_the_real_streams_and_cwd(h, tmp_path):
    import os

    before = (sys.stdin, sys.stdout, sys.stderr, os.getcwd())
    run(h, "import sys, os\nsys.stdout = None\nos.chdir('/')\n")
    assert (sys.stdin, sys.stdout, sys.stderr, os.getcwd()) == before


def test_output_is_capped(h, monkeypatch):
    monkeypatch.setattr(harness, "OUTPUT_CAP", 10)
    result = run(h, "print('x' * 100)")
    assert result["stdout"] == "x" * 10
    assert result["truncated"] is True


# --- sessions and files ----------------------------------------------------------------------


def test_lesson_session_keeps_state_and_files(h):
    first = run(h, "x = 41\nopen('save.txt', 'w').write('kept')", session="u09")
    assert first["session_new"] is True
    second = run(h, "print(x + 1, open('save.txt').read())", session="u09")
    assert second["stdout"] == "42 kept\n"
    assert second["session_new"] is False
    other = run(h, "print('x' in dir())", session="u10")
    assert other["stdout"] == "False\n"
    assert other["session_new"] is True


def test_a_check_always_starts_fresh(h):
    run(h, "x = 1", session="c1", check={"kind": "output", "turtle": False})
    again = run(h, "print('x' in dir())", session="c1", check={"kind": "output", "turtle": False})
    assert again["stdout"] == "False\n"
    assert again["session_new"] is True


def test_mounted_files_are_readable(h):
    files = [
        {"path": "data/scores.txt", "data": "3 4\n", "encoding": "utf-8"},
        {"path": "blob.bin", "data": "AAEC", "encoding": "base64"},
    ]
    result = run(h, "print(open('data/scores.txt').read().split(), open('blob.bin','rb').read())", files=files)
    assert result["stdout"] == "['3', '4'] b'\\x00\\x01\\x02'\n"


@pytest.mark.parametrize("path", ["../escape.txt", "/abs.txt", "a/../b", ".hidden", "a//b", ""])
def test_unsafe_file_paths_are_refused(h, path):
    with pytest.raises(ValueError):
        run(h, "", files=[{"path": path, "data": "", "encoding": "utf-8"}])


def test_dunder_main_and_dataclasses_work(h):
    code = (
        "from dataclasses import dataclass\n@dataclass\nclass P:\n    x: 'int'\n"
        "print(P(1), __name__)\nimport sys\nprint(sys.modules['__main__'].P is P)"
    )
    assert run(h, code)["stdout"] == "P(x=1) __main__\nTrue\n"


# --- grading ---------------------------------------------------------------------------------


def fixture(expected, match="token"):
    return {"kind": "fixture", "expected": expected, "match": match, "turtle": False}


@pytest.mark.parametrize(
    ("code", "stdin", "check", "verdict"),
    [
        ("print(int(input()) * 2)", "21\n", fixture("42\n"), (True, "")),
        ("print(int(input()) * 2)", "21\n", fixture("43\n"), (False, "wrong output")),
        ("x = 1", "", fixture("1\n"), (False, "no output")),
        ("print('  ')", "", fixture(""), (False, "no output")),
        ("print(1/0)", "", fixture("1\n"), (False, "failed: ZeroDivisionError: division by zero")),
        ("print(15)\nprint(10)\nprint(4)", "", fixture("15 10 4\n", "line"), (False, "wrong output")),
        ("print(15)\nprint(10)\nprint(4)", "", fixture("15 10 4\n", "token"), (True, "")),
        ("print(15, 10, 4)", "", fixture("15 10 4\n", "line"), (True, "")),
        ("print('ok')\nimport sys\nsys.exit(1)", "", fixture("ok\n"), (False, "failed: error")),
        ("print(input())\ninput()", "a\n", fixture("a\n"), (False, "failed: EOFError: EOF when reading a line")),
    ],
)
def test_fixture_case_follows_the_judge(h, code, stdin, check, verdict):
    result = run(h, code, stdin=stdin, check=check)
    assert [(r["name"], r["pass"], r["detail"]) for r in result["results"]] == [("case", *verdict)]


def test_asserts_run_one_by_one_and_never_echo_source(h):
    secret = "assert double(21) == 42 # SECRET-ASSERT-TEXT"
    asserts = [
        secret,
        "assert double(1) == 3",
        "assert triple(1) == 3",
        "assert double('a') == 'aa'",
        "assert double(None) == 0",
        "assert False, 'the expected answer is 99'",
    ]
    code = "def double(x):\n    print('called')\n    return x * 2\n"
    result = run(h, code, check={"kind": "asserts", "asserts": asserts, "turtle": False})
    verdicts = [(r["name"], r["pass"], r["detail"]) for r in result["results"]]
    assert verdicts == [
        ("assert 1", True, ""),
        ("assert 2", False, "assertion failed"),
        ("assert 3", False, "NameError: name 'triple' is not defined"),
        ("assert 4", True, ""),
        ("assert 5", False, "TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'"),
        ("assert 6", False, "assertion failed"),
    ]
    text = json.dumps(result)
    assert "SECRET-ASSERT-TEXT" not in text
    assert "expected answer" not in text
    assert result["stdout"] == ""  # assert-time prints are not the student's run output


# --- turtle ----------------------------------------------------------------------------------

SQUARE = "import turtle\nfor _ in range(4):\n    turtle.forward(50)\n    turtle.left(90)\n"
OPEN = "# turtle-check: open-path\nimport turtle\nturtle.forward(50)\n"
LINE = "import turtle\nturtle.forward(50)\n"
NO_PEN = "import turtle\nturtle.penup()\nturtle.forward(10)\n"
MANY = "import turtle\nfor _ in range(10000):\n    turtle.forward(1)\n    turtle.backward(1)\n"
OO = "from turtle import Turtle, Screen\nt = Turtle()\nt.pencolor('red')\nt.pensize(3)\nfor _ in range(3):\n    t.forward(30)\n    t.left(120)\nScreen().exitonclick()\n"


def turtle_check():
    return {"kind": "output", "turtle": True}


@pytest.mark.parametrize("name", [
    "_Tracker", "reset", "forward", "backward", "left", "right", "penup", "pendown", "pensize",
    "pencolor", "color", "segments", "final_state", "imports_turtle", "speed", "bgcolor", "done",
    "exitonclick", "_Screen", "Screen", "Turtle", "state", "_angular_remainder",
])
def test_turtle_port_is_verbatim(name):
    assert inspect.getsource(getattr(fake_turtle, name)) == inspect.getsource(getattr(original_turtle, name))


@pytest.mark.parametrize("source", [SQUARE, OPEN, LINE, NO_PEN, OO])
def test_turtle_port_draws_as_the_original(source):
    states = []
    for module in (fake_turtle, original_turtle):
        module.reset()
        saved = sys.modules.get("turtle")
        sys.modules["turtle"] = module
        try:
            exec(compile(source, "t.py", "exec"), {"__name__": "__main__"})  # noqa: S102 - turtle replay
        finally:
            if saved is None:
                sys.modules.pop("turtle", None)
            else:
                sys.modules["turtle"] = saved
        states.append((module.state(), module.segments()))
    assert states[0] == states[1]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (SQUARE, [True, True, True]),
        (OO, [True, True, True]),
        (OPEN, [True, True, True]),
        (LINE, [True, True, False]),
        (NO_PEN, [False, True, False]),  # no drawing starts at (0, 0), as tools/fake_turtle.py
        (MANY, [True, False, True]),
    ],
)
def test_turtle_rule(h, source, expected):
    result = run(h, source, check=turtle_check())
    names = [r["name"] for r in result["results"]]
    assert names == ["turtle: draws", "turtle: moves", "turtle: closed path"]
    assert [r["pass"] for r in result["results"]] == expected


def test_turtle_rule_fails_a_program_that_does_not_complete(h):
    result = run(h, SQUARE + "1/0\n", check=turtle_check())
    assert result["results"][0] == {"name": "turtle: runs to the end", "pass": False, "detail": "did not complete"}


def test_turtle_is_installed_for_every_import_and_segments_are_returned(h):
    result = run(h, SQUARE)  # a lesson run: no rule, but the drawing
    assert result["results"] == []
    assert len(result["segments"]) == 4
    assert result["segments"][0] == {"x1": 0.0, "y1": 0.0, "x2": 50.0, "y2": 0.0, "color": "black", "width": 1.0}
    assert sys.modules["turtle"] is fake_turtle
    # a later run in the session starts a new drawing
    again = run(h, "turtle.forward(5)")
    assert len(again["segments"]) == 1


def test_handle_round_trips_json(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "path", list(sys.path))
    request = {"code": "print(input())", "stdin": "hi\n", "session": "s", "check": None, "files": []}
    out = json.loads(harness.handle(json.dumps(request), str(tmp_path)))
    assert out["stdout"] == "hi\n"
    assert out["status"] == "ok"


def test_an_interrupt_during_the_asserts_is_reported(h):
    code = "def f():\n    raise KeyboardInterrupt\n"
    result = run(h, code, check={"kind": "asserts", "asserts": ["assert f()"], "turtle": False})
    assert result["status"] == "interrupted"

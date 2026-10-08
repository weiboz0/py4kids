"""The Python side of the runner's worker (design 012 D7, plan 104 "Architecture").

The worker loads this module into Pyodide once per worker and calls ``handle(request_json)`` for
every ``run``; it returns the result fields as JSON. It runs under plain CPython too, which is how
``tests/test_runner_harness.py`` checks it. Per request it:

- sets up stdin as an ``io.StringIO`` (``input()`` reads from it; at end of input ``input()``
  raises ``EOFError`` and ``sys.stdin.read*`` returns ``''``, as in CPython);
- uses one working directory per ``session`` (lesson cells keep the files they write; a check
  gets a fresh one) and writes the mounted ``files`` there;
- installs the ``fake_turtle`` port as ``turtle`` for every run whose source imports turtle;
- captures stdout and stderr (capped), and runs the code as ``__main__`` in the session's module
  (lesson sessions keep it between runs, like a notebook kernel);
- grades a ``fixture`` check with ``outputs_match`` (ported verbatim from ``tools/judge.py``,
  with its "no output" and failed-run rules), an ``asserts`` check one assert at a time (never
  returning assert source), and a ``turtle`` check with the three-part rule.

Process-state isolation is the runner page's job (a fresh worker per check and per fixture case),
not this module's.
"""

from __future__ import annotations

import base64
import builtins
import io
import json
import linecache
import math
import os
import sys
import traceback
import types

import fake_turtle

OUTPUT_CAP = 1_000_000
DETAIL_CAP = 300
SEGMENT_CAP = 10000


# --- ported verbatim from tools/judge.py (the parity test compares the source) ---------------


def _output_lines(text: str) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def outputs_match(actual: str, expected: str, *, line_exact: bool) -> bool:
    """Judge comparison. Token mode (usaco-bronze's contract) compares whitespace-split tokens.

    Line-exact mode (``acsl`` books, design 009 D4) compares line by line after stripping trailing
    whitespace on each line and ignoring trailing empty lines; everything else must match, so a
    required single line ``15 10 4`` does not accept ``15\n10\n4``.
    """
    if line_exact:
        return _output_lines(actual) == _output_lines(expected)
    return actual.split() == expected.split()


# --- end of the verbatim port --------------------------------------------------------------


class _Capture(io.StringIO):
    """A text stream that keeps at most ``cap`` characters and remembers that it dropped some."""

    def __init__(self, cap: int | None = None):
        super().__init__()
        self.cap = OUTPUT_CAP if cap is None else cap
        self.kept = 0
        self.truncated = False

    def write(self, s):
        if not isinstance(s, str):
            raise TypeError(f"write() argument must be str, not {type(s).__name__}")
        room = self.cap - self.kept
        if len(s) > room:
            self.truncated = True
            part = s[: max(room, 0)]
        else:
            part = s
        self.kept += len(part)
        super().write(part)
        return len(s)


def _short(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= DETAIL_CAP else text[: DETAIL_CAP - 1] + "…"


def _safe_join(root: str, relative: str) -> str:
    """``root/relative`` for a relative path with no dot segment (the envelope's rule), else error."""
    parts = relative.split("/")
    if not relative or any(p == "" or p.startswith(".") for p in parts):
        raise ValueError(f"unsafe file path: {relative!r}")
    return os.path.join(root, *parts)


def _student_traceback(exc: BaseException, filenames: set[str]) -> str:
    """CPython's report of an uncaught exception, without the harness's own frames."""
    tb = exc.__traceback__
    while tb is not None and tb.tb_frame.f_code.co_filename not in filenames:
        tb = tb.tb_next
    return "".join(traceback.format_exception(type(exc), exc, tb))


class Harness:
    def __init__(self, root: str):
        self.root = root
        self.sessions: dict[str, types.ModuleType] = {}
        self.cells = 0

    def _session(self, session: str, fresh: bool) -> tuple[types.ModuleType, str, bool]:
        cwd = os.path.join(self.root, session)
        new = fresh or session not in self.sessions
        if new:
            module = types.ModuleType("__main__")
            module.__dict__["__builtins__"] = builtins
            self.sessions[session] = module
        os.makedirs(cwd, exist_ok=True)
        return self.sessions[session], cwd, new

    def run(self, request: dict) -> dict:
        code: str = request["code"]
        check = request["check"]
        module, cwd, session_new = self._session(request["session"], fresh=check is not None)
        for file in request["files"]:
            path = _safe_join(cwd, file["path"])
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if file["encoding"] == "base64":
                with open(path, "wb") as handle:
                    handle.write(base64.b64decode(file["data"]))
            else:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(file["data"])

        # The turtle port: installed for every run whose source imports turtle; a fresh drawing
        # for every run while it is installed.
        if fake_turtle.imports_turtle(code):
            sys.modules["turtle"] = fake_turtle
        turtle_active = sys.modules.get("turtle") is fake_turtle
        if turtle_active:
            fake_turtle.reset()

        self.cells += 1
        filename = "main.py" if check is not None else f"<cell {self.cells}>"
        out, err = _Capture(), _Capture()
        status = self._execute(module, code, filename, request["stdin"], cwd, out, err)

        results: list[dict] = []
        if check is not None:
            if check["kind"] == "fixture":
                results.append(self._grade_case(status, out.getvalue(), err.getvalue(), check))
            elif check["kind"] == "asserts":
                try:
                    results.extend(self._grade_asserts(module, check["asserts"], cwd))
                except KeyboardInterrupt:
                    # An assert that hangs (a call into a looping function) uses up the budget.
                    status = "interrupted"
            if check["turtle"]:
                if status != "ok":
                    results.append(
                        {"name": "turtle: runs to the end", "pass": False, "detail": "did not complete"}
                    )
                results.extend(fake_turtle.turtle_rule(fake_turtle.state(), code))

        segments = []
        if turtle_active or sys.modules.get("turtle") is fake_turtle:
            segments = [
                {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "color": str(c)[:100], "width": float(w)}
                for x1, y1, x2, y2, c, w in fake_turtle.segments()[:SEGMENT_CAP]
                if _finite(x1, y1, x2, y2) and isinstance(w, (int, float))
            ]
        return {
            "stdout": out.getvalue(),
            "stderr": err.getvalue(),
            "status": status,
            "results": results,
            "session_new": session_new,
            "truncated": out.truncated or err.truncated,
            "segments": segments,
        }

    def _execute(self, module, code, filename, stdin, cwd, out, err) -> str:
        """Run ``code`` as ``__main__``; the status is ``ok``, ``error`` or ``interrupted``."""
        saved = (sys.stdin, sys.stdout, sys.stderr, sys.modules.get("__main__"), os.getcwd())
        lines = code.splitlines(keepends=True)
        linecache.cache[filename] = (len(code), None, lines, filename)
        module.__dict__["__file__"] = os.path.join(cwd, "main.py")
        status = "ok"
        try:
            sys.stdin, sys.stdout, sys.stderr = io.StringIO(stdin), out, err
            sys.modules["__main__"] = module
            os.chdir(cwd)
            if cwd not in sys.path:
                sys.path.insert(0, cwd)
            try:
                compiled = compile(code, filename, "exec")
                exec(compiled, module.__dict__)  # noqa: S102 - running student code is the point
            except SystemExit as stop:
                # As CPython: None or 0 is success; an int is the exit status; anything else is
                # printed to stderr with status 1.
                if stop.code is None or stop.code == 0:
                    status = "ok"
                else:
                    status = "error"
                    if not isinstance(stop.code, int):
                        err.write(f"{stop.code}\n")
            except KeyboardInterrupt:
                status = "interrupted"
                err.write("KeyboardInterrupt\n")
            except BaseException as exc:  # noqa: BLE001 - every student error is reported
                status = "error"
                err.write(_student_traceback(exc, {filename}))
        except KeyboardInterrupt:
            status = "interrupted"
        finally:
            for stream in (out, err):
                # Flushing a capture never fails; restore the real streams.
                stream.flush()
            sys.stdin, sys.stdout, sys.stderr = saved[0], saved[1], saved[2]
            if saved[3] is not None:
                sys.modules["__main__"] = saved[3]
            try:
                os.chdir(saved[4])
            except OSError:
                pass
        return status

    @staticmethod
    def _grade_case(status: str, stdout: str, stderr: str, check: dict) -> dict:
        """One fixture case, by ``tools/judge.py``'s ``_run_case`` rules."""
        if status == "interrupted":
            return {"name": "case", "pass": False, "detail": "time limit"}
        if status != "ok":
            last = stderr.strip().splitlines()[-1] if stderr.strip() else "error"
            return {"name": "case", "pass": False, "detail": _short(f"failed: {last}")}
        if stdout.strip() == "":
            return {"name": "case", "pass": False, "detail": "no output"}
        if not outputs_match(stdout, check["expected"], line_exact=check["match"] == "line"):
            return {"name": "case", "pass": False, "detail": "wrong output"}
        return {"name": "case", "pass": True, "detail": ""}

    def _grade_asserts(self, module, asserts: list[str], cwd: str) -> list[dict]:
        """Each shipped assert alone in the student's namespace; never echoes assert source."""
        verdicts = []
        for number, source in enumerate(asserts, start=1):
            name = f"assert {number}"
            filename = f"<{name}>"
            saved = (sys.stdin, sys.stdout, sys.stderr, os.getcwd())
            try:
                sys.stdin, sys.stdout, sys.stderr = io.StringIO(""), _Capture(), _Capture()
                os.chdir(cwd)
                try:
                    exec(compile(source, filename, "exec"), module.__dict__)  # noqa: S102 - shipped asserts
                    verdicts.append({"name": name, "pass": True, "detail": ""})
                except AssertionError:
                    verdicts.append({"name": name, "pass": False, "detail": "assertion failed"})
                except KeyboardInterrupt:
                    raise
                except BaseException as exc:  # noqa: BLE001 - one assert's error never stops the rest
                    message = str(exc)
                    detail = type(exc).__name__ + (f": {message}" if message else "")
                    verdicts.append({"name": name, "pass": False, "detail": _short(detail)})
            finally:
                sys.stdin, sys.stdout, sys.stderr = saved[0], saved[1], saved[2]
                try:
                    os.chdir(saved[3])
                except OSError:
                    pass
        return verdicts


def _finite(*values) -> bool:
    return all(isinstance(v, (int, float)) and math.isfinite(v) for v in values)


_HARNESS: Harness | None = None


def handle(request_json: str, root: str = "/home/pyodide/sessions") -> str:
    """The worker's entry point: one ``run`` request (the envelope fields) in, result fields out."""
    global _HARNESS
    if _HARNESS is None or _HARNESS.root != root:
        _HARNESS = Harness(root)
    return json.dumps(_HARNESS.run(json.loads(request_json)))

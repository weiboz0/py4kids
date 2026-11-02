"""`py4kids-tools aio …` delegates to the ported usaaio CLI (plan aio-001 Phase D)."""

import subprocess
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_importing_tools_cli_does_not_load_the_aio_package():
    probe = "import sys, tools.cli; print(any(m.startswith('tools.aio') for m in sys.modules))"
    result = subprocess.run(
        [sys.executable, "-c", probe], cwd=REPO, capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "False"


def test_aio_prefix_is_intercepted_before_argparse_and_passes_exit_codes(monkeypatch):
    from tools import cli

    calls = []
    fake = types.ModuleType("tools.aio.cli")

    def fake_main(argv):
        calls.append(argv)
        return 3

    fake.main = fake_main
    monkeypatch.setitem(sys.modules, "tools.aio.cli", fake)

    # No --book, which the py4kids parser would require: the delegate runs first.
    assert cli.main(["aio", "--book", "aio-x", "overlap-scan"]) == 3
    assert calls == [["--book", "aio-x", "overlap-scan"]]


def test_aio_delegate_reads_sys_argv_when_argv_is_none(monkeypatch):
    from tools import cli

    calls = []
    fake = types.ModuleType("tools.aio.cli")
    fake.main = lambda argv: calls.append(argv) or 0
    monkeypatch.setitem(sys.modules, "tools.aio.cli", fake)
    monkeypatch.setattr(sys, "argv", ["py4kids-tools", "aio", "--all", "prereq-check"])

    assert cli.main() == 0
    assert calls == [["--all", "prereq-check"]]


def test_non_aio_arguments_still_use_the_py4kids_parser():
    from tools import cli

    assert cli.main(["--book"]) == 2

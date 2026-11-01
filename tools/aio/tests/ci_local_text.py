"""Read the py4kids `scripts/ci-local.sh` aio routing (plan aio-001 Phase E).

usaaio's own tests asserted the wiring of usaaio's ci-local; their py4kids equivalents assert the
same wiring in the py4kids gate, through these helpers. They read the script only (no aio deps).
"""

from __future__ import annotations

from conftest import ROOT

CI_LOCAL = ROOT / "scripts" / "ci-local.sh"
AIO_SUITE = ROOT / "tools" / "aio" / "tests"
AIO_SUITE_COMMAND = "uv run --group aio pytest -q tools/aio/tests"
# usaaio's per-notebook exec command, with the AIO_BOOK_ROOT rename and the aio group.
TIMED_EXEC = 'timeout 20s uv run --project .. --group aio jupyter execute "$relative"'
PLAIN_EXEC = (
    '(cd "$book_root" && AIO_BOOK_ROOT="$book_root" '
    'uv run --project .. --group aio jupyter execute "$relative")'
)


def ci_text() -> str:
    return CI_LOCAL.read_text(encoding="utf-8")


def ci_noncomment_lines() -> list[str]:
    return [
        line.strip()
        for line in ci_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def ci_step(start: str, end: str) -> str:
    """The script text from `step "<start>` up to `step "<end>`."""
    text = ci_text()
    return text[text.index(f'step "{start}') : text.index(f'step "{end}')]


def aio_suite_runs(module: str) -> bool:
    """True when step 2's single routed aio suite runs `module` (usaaio ran it again in step 7).

    The routed command runs the whole `tools/aio/tests` directory, unfiltered, so a module is run
    exactly when it lives there.
    """
    step2 = ci_step("2/7", "3/7")
    routed = [line.strip() for line in step2.splitlines() if line.strip() == AIO_SUITE_COMMAND]
    return len(routed) == 1 and (AIO_SUITE / module).is_file()

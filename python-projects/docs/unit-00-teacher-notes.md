# Teacher Notes — Unit 0: Getting Set Up

## Goals

Every student leaves the session with a working setup: Python 3.12 or newer from python.org, JupyterLab
installed into that Python, and Thonny.
Success looks like: each student shows you the four ticks on the Unit 0 checklist — the version command,
a JupyterLab cell with its output, `hello.py` running in Thonny, and `hello.py` running from the terminal.

## Before the session

- **Rights:** installing Python and Thonny needs permission to install software. On school-managed
  machines, ask IT to pre-install Python (3.12+), JupyterLab and Thonny, or to grant install rights for
  the session.
- **Downloads:** a class downloading at once can be slow. Put the Windows and macOS installers for
  Python and Thonny on a USB stick or shared drive as a backup. `pip install jupyterlab` pulls roughly
  100 MB per machine; on slow school Wi-Fi, pre-download the packages once
  (`py -m pip download jupyterlab -d wheels`) and install from them
  (`py -m pip install --no-index --find-links wheels jupyterlab`). Web filters or proxies may block
  pypi.org — check with IT.
- **Course files:** decide where students keep the course folder (the chapter assumes
  `Documents/py4kids`) and copy it to every machine beforehand.
- **Try it yourself** on one Windows and one Mac machine the day before; installer wording changes over
  time. On Windows, python.org now provides the **Python install manager** (the classic installer with
  the "Add python.exe to PATH" box is deprecated from 3.14 and will not exist for 3.16+); students then
  run `py install default`. `py list` shows the installed runtimes. Some school machines block app
  packages (MSIX) — IT can deploy the install manager or its MSI package instead.

## Setup-day plan (60–90 minutes)

1. **5 min — Why three tools.** Python runs programs; JupyterLab holds the lessons; Thonny runs `.py`
   files. Show the "run it three ways" goal.
2. **20 min — Install Python.** Walk through the Windows and Mac steps together. On Windows, everyone
   runs `py install default` (the optional PATH question can be answered either way); on a Mac, everyone runs Install
   Certificates. Everyone runs the version command before moving on.
3. **20 min — JupyterLab.** Install with `-m pip`, start it from the course folder, open Unit 1's
   lesson, run the first cell with Shift+Enter, add a new cell, restart the kernel, and stop the server
   with Ctrl+C.
4. **15 min — Thonny.** Install, save and run `hello.py`.
5. **10 min — Terminal run.** `cd` into the folder and run `hello.py`. This is the Unit 3 workflow, so
   it is worth practising once now. In Unit 3, students `cd` into
   `python-projects/units/unit-03-turtle-art-studio` and run its turtle programs from the `assets`
   folder with `py` (Windows) or `python3` (Mac).
6. **Remaining time — Checklist sign-off.** Walk the room and tick each student's checklist.

**60-minute cut:** install Python and JupyterLab in class (students need them for Unit 1); set Thonny and
the terminal run as homework before Unit 3.

## Common problems

- **Windows, an older launcher owns `py`:** on machines with an earlier Python, `py` may still be the old
  launcher; `pymanager install default` always reaches the install manager. If `py --version` keeps picking an old
  version, uninstall **Python launcher** from **Settings ▸ Apps ▸ Installed apps**, open a new Command
  Prompt, and check `py --version` again (ask IT on managed machines).
- **Windows, `py` missing or no runtime:** open a new Command Prompt after installing the install
  manager; if `py --version` reports no Python, run `py install default`. If `python` opens the Microsoft
  Store, use `py` (the book always does).
- **Windows OneDrive:** Documents is often redirected into OneDrive, so `cd Documents/py4kids` fails.
  Use `cd OneDrive/Documents/py4kids`, or open a terminal from File Explorer's address bar (`cmd`).
- **Thonny's own Python:** Thonny ships its own Python, which may be older than the course's 3.12 floor.
  If a `.py` program needs a newer feature, point Thonny at the python.org install with **Tools ▸ Options
  ▸ Interpreter**.
- **Mac, `python` vs `python3`:** students type `python`, and it fails. The book always uses `python3`.
- **Two Pythons:** students who already had Python (or Anaconda) install JupyterLab into one Python and
  start it with another. Always use `py -m …` / `python3 -m …` so the same Python does both.
- **Wrong folder:** `No such file or directory` almost always means the terminal is in another folder.
  Teach `cd` and, on a Mac, dragging a folder onto the Terminal window to paste its path.
- **JupyterLab closes:** closing the terminal stops the server. Keep it open (minimised).
- **Mac security prompt for Thonny:** System Settings ▸ Privacy & Security ▸ **Open Anyway**.

## Devices that cannot install Python

Chromebooks, iPads and some locked-down laptops cannot run this setup. Pair those students with a
classmate for the session, and arrange a lab machine or a school-approved browser-based notebook service
for the course. Check that service runs the turtle programs of Unit 3 before relying on it.

## Discussion prompts

- Why does the book use `py -m` / `python3 -m` instead of just `jupyter`?
- What is the difference between running a notebook cell and running a `.py` file?
- Where did the output appear in each of the three ways you ran your program?

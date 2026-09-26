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
  Python and Thonny on a USB stick or shared drive as a backup.
- **Course files:** decide where students keep the course folder (the chapter assumes
  `Documents/py4kids`) and copy it to every machine beforehand.
- **Try it yourself** on one Windows and one Mac machine the day before; installer wording changes over
  time.

## Setup-day plan (60–90 minutes)

1. **5 min — Why three tools.** Python runs programs; JupyterLab holds the lessons; Thonny runs `.py`
   files. Show the "run it three ways" goal.
2. **20 min — Install Python.** Walk through the Windows and Mac steps together. On Windows, stop the
   class at the **Add python.exe to PATH** checkbox and check every screen. Everyone runs the version
   command before moving on.
3. **20 min — JupyterLab.** Install with `-m pip`, start it from the course folder, open Unit 1's
   lesson, run the first cell with Shift+Enter, add a new cell, restart the kernel, and stop the server
   with Ctrl+C.
4. **15 min — Thonny.** Install, save and run `hello.py`.
5. **10 min — Terminal run.** `cd` into the folder and run `hello.py`. This is the Unit 6 workflow, so
   it is worth practising once now.
6. **Remaining time — Checklist sign-off.** Walk the room and tick each student's checklist.

**60-minute cut:** install Python and JupyterLab in class (students need them for Unit 1); set Thonny and
the terminal run as homework before Unit 6.

## Common problems

- **Windows, PATH not ticked:** `python` opens the Microsoft Store and `py` may be missing. Re-run the
  installer, choose **Modify**, and tick **Add Python to environment variables** — or reinstall with the
  checkbox ticked.
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
for the course. Check that service runs the turtle programs of Unit 6 before relying on it.

## Discussion prompts

- Why does the book use `py -m` / `python3 -m` instead of just `jupyter`?
- What is the difference between running a notebook cell and running a `.py` file?
- Where did the output appear in each of the three ways you ran your program?

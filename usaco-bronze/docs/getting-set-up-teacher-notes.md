# Teacher Notes — Getting Set Up

## Goals

Every student can run a stdin program with an input file from a terminal opened in a unit folder, and can check its output against a `.out` file.
Installing Python and JupyterLab is not part of this session: students who worked through *Python by Projects* already have them (its Unit 0).
Success looks like: each student shows you the four ticks on the chapter's checklist, ending with a program of their own run with `<` and an input file.

## Before the session

- **Check the setup still works.** Each machine needs Python 3.12 or newer and JupyterLab from *Python by Projects* Unit 0.
  New students, or students on a new machine, need that chapter first; budget a separate session for them.
- **Update the course folder.** Students need a copy of the course folder that includes `usaco-bronze/`.
  If they downloaded it for *Python by Projects*, have them download it again or copy the new folder in.
- **Decide what to hand out.** Each `assets` folder holds the reference solver for every lesson program, exercise (`exN.py`), checkpoint question (`qN.py`) and the Grand Mock Contest (`p1.py`), next to its test cases.
  The chapter never points students at those solvers.
  For self-paced homework that is usually fine; for the timed Mock Contests, consider handing out a copy of each checkpoint folder with the `qN.py` files removed.
- **Windows terminals.** The `<` redirection works in Command Prompt but not in PowerShell (`The '<' operator is reserved for future use`).
  JupyterLab's own terminal and Windows Terminal often open PowerShell; typing `cmd` inside them starts Command Prompt in the same folder.
  The PowerShell equivalent, if a student insists, is `Get-Content assets/l1/1.in | py assets/l1.py`.
- **Try it yourself** on one Windows and one Mac machine: `cd` into `usaco-bronze/units/unit-01-reading-the-input` and run `py assets/l1.py < assets/l1/1.in` (Windows) or `python3 assets/l1.py < assets/l1/1.in` (Mac); both print `15 9`.

## Session plan (30–45 minutes)

This fits at the start of the first Unit 1 lesson; Unit 1's Lesson 1 ends with exactly this run.

1. **5 min — Why a terminal.** Contest programs read standard input and print exact output; a judge feeds each program a file.
   Show one `.in` file and its `.out` file side by side.
2. **10 min — Open a terminal in the unit folder.** Command Prompt on Windows (or the File Explorer address-bar trick), Terminal on a Mac (or drag the folder).
   Everyone runs `cd` into Unit 1's folder.
3. **10 min — Run with an input file.** Everyone runs Lesson 1's program on `assets/l1/1.in`, then on `2.in` and `3.in`, and compares each with its `.out` file using `cat` (Mac) or `type` with backslashes (Windows).
   Then run it once without `<`, type the input by hand, and end it with Ctrl+D (Mac) or Ctrl+Z, Enter (Windows).
4. **10 min — Their own program.** Each student creates `my_ex1.py`, types a first attempt at Exercise 1, and runs it on `assets/ex1/1.in`.
5. **Remaining time — Checklist sign-off.** Walk the room and tick each student's checklist.

**Short on time:** do steps 2 and 3 in class, and set step 4 as the first homework problem.

## Common problems

- **PowerShell:** `The '<' operator is reserved for future use`. Switch to Command Prompt (`cmd`).
- **`python` vs `py` / `python3`:** the lessons print `python assets/lN.py < assets/lN/1.in` because that is what a contest environment shows.
  Students on Windows type `py`, students on a Mac type `python3`, exactly as in *Python by Projects*.
- **Wrong folder:** `can't open file` or `The system cannot find the file specified` almost always means the terminal is not in the unit folder.
  Paths in this book are relative to the unit folder, never the course folder.
- **`type` with forward slashes:** Command Prompt's `type` reads `/` as a switch and says `The syntax of the command is incorrect`; use backslashes.
  (`py` and `<` accept forward slashes.)
- **A program that "hangs":** it is waiting for keyboard input because `<` was left out. Ctrl+C stops it.
- **Output that looks right but is not:** extra words (`Answer: 15`), a trailing debugging `print`, or values on the wrong lines.
  The course's own judge compares whitespace-separated tokens, so spacing slips alone do not fail a case there, but real judges can be stricter; teach students to match the sample layout exactly.
- **Passing only the sample:** remind students that every `k.in` must pass, and that the extra cases are chosen to break common mistakes (off-by-one limits, a single value, the last row or column).

## Differentiation

- **Students who finish early:** have them write their own edge case in `case.txt` (the smallest allowed input, say), predict the answer, and run Lesson 1's program on it.
- **Students who find the terminal hard:** pair them with a confident partner for the first run, and give them a card with the three commands they need (`cd …`, the run line, and `cat` or `type`).

## Discussion prompts

- What does the `<` sign change about where the program's input comes from?
- Why is passing the sample not enough to be sure a program is right?
- Why does a contest judge care about the exact output, and not only the numbers in it?

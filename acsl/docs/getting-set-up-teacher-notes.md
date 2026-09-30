# Teacher Notes — Getting Set Up

## Goals

Every Junior, Intermediate and Senior student can open a terminal in a unit folder, run a program and type its input, run a program with an input file, and check its output against a `.out` file.
Every student, whatever the division, knows how to practise a short answer: pencil first, one exact answer, then check.
Installing Python and JupyterLab is not part of this session: students who worked through *Python by Projects* already have them (its Unit 0).
Success looks like: each programming-division student shows you the four ticks on the chapter's checklist, ending with a program of their own run with `<` and an input file.

## Before the session

- **Check the setup still works.** Each machine needs Python 3.12 or newer and JupyterLab from *Python by Projects* Unit 0.
  New students, or students on a new machine, need that chapter first; budget a separate session for them.
- **Update the course folder.** Students need a copy of the course folder that includes `acsl/`.
  If they downloaded it for *Python by Projects*, have them download it again or copy the new folder in.
- **Elementary and Classroom students.** Their papers have no programming problem, and every Elementary lesson is pencil-and-paper work.
  They can skip the terminal steps; the self-checkers in Units 1, 4 and 8 are optional extras for students who can already run a program.
  Give them the short-answer routine and a first Unit 1 or Unit 4 warm-up instead.
- **Decide what to hand out.** Each `assets` folder holds the reference solver for every lesson program and programming exercise (`exN.py`) and each practice contest's programming question (`qN.py`), next to its test cases, plus the `traceN.py` programs behind the short-answer items.
  The chapter never points students at those files.
  For self-paced homework that is usually fine; for a timed practice contest, consider handing out a copy of the checkpoint folder with the `qN.py` and `traceN.py` files removed.
- **Windows terminals.** The `<` redirection works in Command Prompt but not in PowerShell (`The '<' operator is reserved for future use`).
  JupyterLab's own terminal and Windows Terminal often open PowerShell; typing `cmd` inside them starts Command Prompt in the same folder.
  The PowerShell equivalent, if a student insists, is `Get-Content assets/l1/1.in | py assets/l1.py`.
- **Try it yourself** on one Windows and one Mac machine: `cd` into `acsl/units/unit-00-acsl-foundations` and run `py assets/l1.py < assets/l1/1.in` (Windows) or `python3 assets/l1.py < assets/l1/1.in` (Mac); both print `15`.

## Session plan (30–45 minutes)

This fits at the start of Unit 0's Lesson 1, which ends with exactly these two runs of `assets/l1.py`.

1. **5 min — Two kinds of answer.** A short answer is one exact line worked on paper; a programming answer is a program judged on several input files.
   Show one `.in` file and its `.out` file side by side.
2. **10 min — Open a terminal in the unit folder.** Command Prompt on Windows (or the File Explorer address-bar trick), Terminal on a Mac (or drag the folder).
   Everyone runs `cd` into Unit 0's folder.
3. **5 min — Type the input.** Everyone runs Lesson 1's program with no `<`, types `12345`, presses Enter, and sees `15`.
   Point out that each `input()` reads one line, so the program is waiting, not frozen.
4. **10 min — Run with an input file.** Everyone runs it on `assets/l1/1.in`, then `2.in` and `3.in`, and compares each with its `.out` file using `cat` (Mac) or `type` with backslashes (Windows).
5. **10 min — Their own program.** Each student creates `my_ex4.py`, types a first attempt at Exercise 4, and runs it on `assets/ex4/1.in`.
6. **Remaining time — Checklist sign-off.** Walk the room and tick each student's checklist.
   Elementary and Classroom students trace Unit 0's Lesson 1 example on paper meanwhile, or start a Unit 1 warm-up.

**Short on time:** do steps 2 to 4 in class, and set step 5 as the first homework problem.

## Common problems

- **PowerShell:** `The '<' operator is reserved for future use`. Switch to Command Prompt (`cmd`).
- **`python` vs `py` / `python3`:** the lessons print `python assets/lN.py < assets/lN/1.in` because that is the neutral form.
  Students on Windows type `py`, students on a Mac type `python3`, exactly as in *Python by Projects*.
- **Wrong folder:** `can't open file` or `The system cannot find the file specified` almost always means the terminal is not in the unit folder.
  Paths in this book are relative to the unit folder, never the course folder.
- **`type` with forward slashes:** Command Prompt's `type` reads `/` as a switch and says `The syntax of the command is incorrect`; use backslashes.
  (`py` and `<` accept forward slashes.)
- **A program that "hangs":** it is waiting at an `input()` for a typed line. Type the line and press Enter, or stop it with Ctrl+C.
- **`EOFError: EOF when reading a line`:** the program reads more lines than the file holds, usually a loop that reads one line too many.
- **Prompts in `input()`:** `input("Enter N: ")` prints its prompt, so the output no longer matches. Contest programs call `input()` with empty brackets.
- **Output that looks right but is not:** extra words (`Answer: 15`), a trailing debugging `print`, or values on the wrong lines.
  The course's own checker for this book compares line by line, ignoring only spaces at the ends of lines and blank lines at the end, so `15 10 4` on one line does not match three lines; ACSL judges exact output too, so teach students to match the sample layout exactly.
- **Checking a short answer too early:** students who run the program before committing to an answer learn nothing about tracing.
  Ask for the written answer first, then let them check.

## Differentiation

- **Students who finish early:** have them write their own edge case in `sample.txt` (the smallest allowed input, say), predict the answer, and run Lesson 3's program `assets/l3.py` on it.
- **Students who find the terminal hard:** pair them with a confident partner for the first run, and give them a card with the three commands they need (`cd …`, the run line, and `cat` or `type`).
- **Elementary and Classroom students:** the terminal is optional for them; spend the time on the short-answer routine, with one worked trace.

## Discussion prompts

- What does the `<` sign change about where the program's input comes from?
- Why is passing the sample not enough to be sure a program is right?
- Why does ACSL insist on the exact answer, on paper and in a program, and not only the numbers in it?

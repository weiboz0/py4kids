# Getting Set Up

This book asks for two kinds of work, just like an ACSL contest.
Short answers are worked with pencil and paper, and programming problems are solved by programs that read their input and print an exact answer.
This chapter shows you how to run those programs from a terminal, how to feed them input, how to check what they print, and how to practise short answers on paper.

You need the same setup as *Python by Projects*: Python 3.12 or newer, JupyterLab, and the course folder.
Unit 0 of *Python by Projects* shows how to install them.
If you have already worked through that book on this computer, you are ready.

If you are preparing for the Elementary or Classroom division, there is no programming problem on your paper.
Read the section on short answers below; the terminal sections are only for the optional self-checkers in Units 1, 4 and 8, and you can come back to them whenever you like.

## What is in a unit folder

Each unit of this book has its own folder inside the course folder, such as
`py4kids/acsl/units/unit-00-acsl-foundations`.
The lesson and the exercises are notebooks, and the programs and their test files are in the `assets` folder:

| Path | What it holds |
|---|---|
| `lesson.ipynb` | the lesson |
| `exercises.ipynb` | the exercises |
| `assets/l1.py` | the full program from Lesson 1 |
| `assets/l1/1.in` | an input file for that program |
| `assets/l1/1.out` | the output that program should print for `1.in` |
| `assets/ex4/1.in` and `assets/ex4/1.out` | one test case for the programming problem in Exercise 4 |

Each programming problem has several test cases, numbered `1`, `2`, `3`, and so on.
Usually one of them is the problem's sample; the others try edges, such as the smallest input, and larger inputs.
The practice contests at the end of each part work the same way: the programming question has its own folder, named after its number, such as `assets/q9`.

## Open a terminal in a unit folder

Run every command in this book from the unit's folder, so that paths such as `assets/l1.py` point to the right files.

On **Windows**, open **Command Prompt** (Start menu, type `cmd`) and move into the unit folder:

```text
cd Documents/py4kids/acsl/units/unit-00-acsl-foundations
```

Use Command Prompt, not PowerShell.
PowerShell does not understand the `<` sign that this book uses to feed a program its input.
If you want to skip the typing, open the unit folder in File Explorer, click the address bar, type `cmd`, and press Enter.

On a **Mac**, open **Terminal** and type the same command:

```text
cd Documents/py4kids/acsl/units/unit-00-acsl-foundations
```

On a Mac you can also type `cd ` (with a space), drag the unit folder from Finder onto the Terminal window, and press Enter.

Notice: when you move on to Unit 1, move the terminal into Unit 1's folder, and so on.

## Run a program and type its input

Unit 0's first program reads one line holding a whole number and prints the sum of its digits.
The lessons write the run like this:

```text
python assets/l1.py
```

Type `py` in place of `python` on Windows, and `python3` on a Mac, as in *Python by Projects*.
So on Windows you type `py assets/l1.py`, and on a Mac `python3 assets/l1.py`.

The program starts and waits, because its `input()` is waiting for a line.
Type `12345` and press Enter; it prints `15`.

Each call to `input()` reads one line, so a program that reads three lines waits for you to type three lines, pressing Enter after each one.
The self-checkers in Units 1, 4 and 8 work this way: run one, type what the lesson says, such as `45` in Unit 1, and read its answer.

## Run a program with an input file

Typing the input again and again is slow, and a typing slip changes the answer.
Instead, you can feed the program a file:

```text
python assets/l1.py < assets/l1/1.in
```

The `<` sign sends the file `assets/l1/1.in` to the program as if you had typed its contents, so every `input()` reads the next line of the file.
This program prints `15`, because the file holds the line `12345`.

## Run your own solution

Write each programming solution as a complete program in its own `.py` file, and save it in the unit folder.
In JupyterLab choose **File ▸ New ▸ Python File**; in Thonny choose **File ▸ New**.
Give the file a name you will recognise, such as `my_ex4.py`.

Then run it with a test case from the `assets` folder:

```text
python my_ex4.py < assets/ex4/1.in
```

You can also make an input of your own.
Save the sample input from the problem, or any case you invent, in a text file such as `sample.txt`, and run:

```text
python my_solution.py < sample.txt
```

Remember that a contest program calls `input()` with nothing in the brackets.
A prompt such as `input("Enter a number: ")` prints its words too, and then the output is wrong.

## Compare with the expected output

Show the output the program should print next to your own.
On a Mac, `cat` shows a file:

```text
cat assets/ex4/1.out
```

On Windows, `type` shows a file; it needs backslashes in the path:

```text
type assets\ex4\1.out
```

Your program is right for that case when it prints exactly the same thing: the same values, in the same order, on the same lines.
Print exactly the answer: no extra words such as `Answer:`, and no values that the problem did not ask for.
Close does not count.

## How the test cases check a program

A program solves a problem when it passes every test case, not only the sample.
For each case, the program runs with `k.in` as its input, and its output is compared with `k.out`.
Run your program on `1.in`, then `2.in`, `3.in`, and so on, and compare each output with the matching `.out` file.

The book's programs were checked this way: every one of them prints the matching `.out` answer for each of its `.in` files.
An ACSL programming problem is judged the same way, on several test inputs, and each one counts only if the output is exactly right.
So match the sample output's layout exactly, spaces and lines included.

## Practise short answers on paper

The short-answer part of a contest has no computer, so practise it the same way.

- Work with a pencil and a sheet of paper, and keep the notebook closed until you have an answer.
- Trace programs with a table of variables, one line at a time, as Unit 0 shows.
- Write one exact answer in the form the lesson asks for, such as `10 30`, `0111` or `(0,1), (1,0)`.
- Only then check it: against the book's answer when there is one, or by running the program, typed into a notebook cell (an ACSL program translated into Python first, as Unit 3 shows).
- When an answer is wrong, find the first line of your working that went wrong before you try the next question.

## If something goes wrong

Find what you see, then do what it says.

- **`The '<' operator is reserved for future use`**  
  You are in PowerShell. Type `cmd` and press Enter to start Command Prompt in the same folder, then run the command again.
- **`can't open file … No such file or directory`**  
  The terminal is in a different folder. Use `cd` to move into the unit folder, then try again.
- **`The system cannot find the file specified` or `no such file or directory: assets/…`**  
  The input file's path is wrong, or the terminal is in a different folder. Check the spelling, and check that you are in the unit folder.
- **The program seems to hang and prints nothing**  
  It is waiting for you to type a line. Type the input and press Enter, or press **Ctrl+C** to stop it and run it again with `<` and an input file.
- **`EOFError: EOF when reading a line`**  
  The program called `input()` more times than the input file has lines. Check how many lines your program reads.
- **`'python' is not recognized…` or `command not found: python`**  
  Type `py` on Windows or `python3` on a Mac.
- **`The syntax of the command is incorrect` after `type`**  
  Use backslashes in the path, as in `type assets\ex4\1.out`.
- **`ValueError: invalid literal for int()`**  
  The program turned a piece of text that is not a whole number into an `int`. Check which piece each line of your program reads.

## Checklist

You are ready for Unit 0 when you can tick every box:

☐ A terminal is open in Unit 0's folder.\
☐ `python assets/l1.py` (with `py` or `python3`) waits, and prints `15` when you type `12345`.\
☐ `python assets/l1.py < assets/l1/1.in` prints `15`, which matches `assets/l1/1.out`.\
☐ You can run a program of your own with an input file.

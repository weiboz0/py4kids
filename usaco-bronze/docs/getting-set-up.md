# Getting Set Up

Every program in this book is a contest program: it reads its whole input from standard input, works out the answer, and prints it.
You will run these programs from a terminal and feed each one an input file, just as a contest judge does.
This chapter shows you how to do that, and how to check that a program prints the right answer.

You need the same setup as *Python by Projects*: Python 3.12 or newer, JupyterLab, and the course folder.
Unit 0 of *Python by Projects* shows how to install them.
If you have already worked through that book on this computer, you are ready.

## What is in a unit folder

Each unit of this book has its own folder inside the course folder, such as
`py4kids/usaco-bronze/units/unit-01-reading-the-input`.
The lesson and the exercises are notebooks, and the programs and their test files are in the `assets` folder:

| Path | What it holds |
|---|---|
| `lesson.ipynb` | the lesson |
| `exercises.ipynb` | the exercises |
| `assets/l1.py` | the full program from Lesson 1 |
| `assets/l1/1.in` | an input file for that program |
| `assets/l1/1.out` | the output that program should print for `1.in` |
| `assets/ex1/1.in` and `assets/ex1/1.out` | one test case for Exercise 1 |

Each problem has several test cases, numbered `1`, `2`, `3`, and so on.
Usually one of them is the problem's sample; the others try edges, such as the smallest input, and larger inputs.
The Mock Contest checkpoints work the same way, with folders `assets/q1`, `assets/q2`, … for their questions, and so does the Grand Mock Contest, with `assets/p1`.

## Open a terminal in a unit folder

Run every command in this book from the unit's folder, so that paths such as `assets/l1.py` point to the right files.

On **Windows**, open **Command Prompt** (Start menu, type `cmd`) and move into the unit folder:

```text
cd Documents/py4kids/usaco-bronze/units/unit-01-reading-the-input
```

Use Command Prompt, not PowerShell.
PowerShell does not understand the `<` sign that this book uses to feed a program its input.
If you want to skip the typing, open the unit folder in File Explorer, click the address bar, type `cmd`, and press Enter.

On a **Mac**, open **Terminal** and type the same command:

```text
cd Documents/py4kids/usaco-bronze/units/unit-01-reading-the-input
```

On a Mac you can also type `cd ` (with a space), drag the unit folder from Finder onto the Terminal window, and press Enter.

Notice: when you move on to Unit 2, move the terminal into Unit 2's folder, and so on.

## Run a program with an input file

The lessons write each run like this:

```text
python assets/l1.py < assets/l1/1.in
```

Type `py` in place of `python` on Windows, and `python3` on a Mac, as in *Python by Projects*.
So on Windows you type `py assets/l1.py < assets/l1/1.in`, and on a Mac `python3 assets/l1.py < assets/l1/1.in`.

The `<` sign feeds the file `assets/l1/1.in` to the program as its standard input, as if you had typed the file's contents.
The program reads that input with `sys.stdin.read()` and prints its answer:

```text
15 9
```

If you leave out `<` and the file name, the program waits for you to type the input yourself.
Type it, then end the input: press **Ctrl+D** on a Mac, or **Ctrl+Z** and then **Enter** on Windows.

## Run your own solution

Write each solution as a complete program in its own `.py` file, and save it in the unit folder.
In JupyterLab choose **File ▸ New ▸ Python File**; in Thonny choose **File ▸ New**.
Give the file a name you will recognise, such as `my_ex1.py`.

Then run it with a test case from the `assets` folder:

```text
python my_ex1.py < assets/ex1/1.in
```

You can also make an input of your own.
Save the sample input from the problem, or any case you invent, in a text file such as `case.txt`, and run:

```text
python my_solution.py < case.txt
```

## Compare with the sample output

Show the output the program should print next to your own.
On a Mac, `cat` shows a file:

```text
cat assets/ex1/1.out
```

On Windows, `type` shows a file; it needs backslashes in the path:

```text
type assets\ex1\1.out
```

Your program is right for that case when it prints the same values, in the same order, on the same lines.
Print exactly the answer: no extra words such as `Answer:`, and no values that the problem did not ask for.

## How the test cases check a program

A program passes a problem when it passes every test case, not only the sample.
For each case, the program runs with `k.in` as its standard input, and its output is compared with `k.out`.
Run your program on `1.in`, then `2.in`, `3.in`, and so on, and compare each output with the matching `.out` file.

The book's programs were checked this way: every one of them prints the matching `.out` answer for each of its `.in` files.
Real contest judges can be strict about spaces and blank lines, so match the sample output's layout exactly.

Notice: a case can pass on a small input and still be too slow on a large one.
Unit 3 shows how to tell, before you write the code, whether a plan is fast enough.

## If something goes wrong

Find what you see, then do what it says.

- **`The '<' operator is reserved for future use`**  
  You are in PowerShell. Type `cmd` and press Enter to start Command Prompt in the same folder, then run the command again.
- **`can't open file … No such file or directory`**  
  The terminal is in a different folder. Use `cd` to move into the unit folder, then try again.
- **`The system cannot find the file specified` or `no such file or directory: assets/…`**  
  The input file's path is wrong, or the terminal is in a different folder. Check the spelling, and check that you are in the unit folder.
- **The program seems to hang and prints nothing**  
  It is waiting for input. Press **Ctrl+C** to stop it, then run it again with `<` and an input file.
- **`'python' is not recognized…` or `command not found: python`**  
  Type `py` on Windows or `python3` on a Mac.
- **`The syntax of the command is incorrect` after `type`**  
  Use backslashes in the path, as in `type assets\ex1\1.out`.
- **`ValueError: invalid literal for int()`**  
  The program read a token that is not a number. Check which token each line of your parsing reads.
- **`IndexError: list index out of range`**  
  The program read past the end of the tokens. Check how many values the input really has.

## Checklist

You are ready for Unit 1 when you can tick every box:

☐ A terminal is open in Unit 1's folder.\
☐ `python assets/l1.py < assets/l1/1.in` (with `py` or `python3`) prints `15 9`.\
☐ Its output matches `assets/l1/1.out`.\
☐ You can run a program of your own with an input file.

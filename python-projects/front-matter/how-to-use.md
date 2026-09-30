# How to Use This Book

Begin with Unit 0 to set up Python and open the course files.
Each later unit opens with a project, then teaches the ideas you need to build it.
Read, run, change, and rerun the examples before you start the exercises.

## Reading the page

- **Program / Output:** Program shows Python code; Output shows what it prints when run with the shown values.
- **Notice:** A short explanation of the idea the example just used.
- **Try it yourself:** Run the code and supply your own input or make the suggested change.
- **Read the error:** The code is broken on purpose; use the message to find the mistake.
- **Drawing made by the program above:** A turtle drawing, printed right after the program that makes it.
<!-- edition: student|teacher -->
- **Starter:** A beginning for your exercise program; finish the missing work yourself.
<!-- /edition -->
<!-- edition: student-print -->
- **Starter:** Starting code printed only when it is not already on the page, such as a broken program to repair; all other starting code is in your exercises notebook.
<!-- /edition -->
- **Check lines:** A call and its expected result for checking your code.
- **Real version:** The same task using values entered while the program runs, instead of fixed sample values.
- **You will learn / Recap:** A short guide to the unit's goals and a reminder of what you can now do.

## Challenges

Challenges are optional stretch problems; later lessons never depend on them.
You will meet them in two places.

- A numbered exercise marked **Challenge** is part of the exercise set.
  When its number is odd, its answer is with the other odd-numbered answers.
- The **Challenge 1**, **Challenge 2** problems at the end of a unit are extra puzzles for when you have finished the exercises.
  They print no answers; test your program against their samples to check it.

## Projects

The two projects, Arcade Night and Grand Adventure, are bigger builds.
Each is split into milestones, and most milestones start from a Starter program that you grow step by step.
Finish one milestone before you start the next, and run your game after every change.

## Work in the course files

Your course folder contains the `python-projects` folder.
Here is the map for each numbered unit:

```text
python-projects/
  units/
    unit-NN-…/
      lesson.ipynb       read and run the lesson
      exercises.ipynb    write and save your answers here
      assets/            program files or data, when used
```

`NN` is the unit number, such as `03`.
For example, Unit 3's turtle files are in `python-projects/units/unit-03-turtle-art-studio/assets/`.
Open the unit's `exercises.ipynb` in JupyterLab, add your code there, run it, and save your work.
When an exercise asks for a `.py` file, save it in that unit's folder unless the exercise gives another location.

Turtle programs open their own drawing window, so Units 3 and 5 run them as `.py` files from a terminal.
First move into the unit folder.
On Windows, type `py assets/l1_square.py`; on a Mac, type `python3 assets/l1_square.py`.
Replace `assets/l1_square.py` with the file named in your lesson or exercise.
Unit 0 shows how to open a terminal, move into a folder, and run a file.

## Check your work

Do the exercises in order; the More Practice exercises in most sets give extra drill, and Challenges are there when you want an extra puzzle.
Run your program with each worked sample and compare every printed line, space, and number with the page.
Make the sample version work before trying a Real version.

<!-- edition: student -->
At the back, **Answers to Selected Exercises** gives worked answers to the odd-numbered unit exercises.
<!-- /edition -->
<!-- edition: student-print -->
Answers to the odd-numbered exercises are in the separate Answer Key.
It and the full edition are online at the course page, github.com/weiboz0/py4kids.
<!-- /edition -->
<!-- edition: teacher -->
In this Teacher's Edition, the answers follow each exercise set in its answer key; the end-of-unit Challenges, checkpoints and projects have answer keys too.
Student books give answers only to the odd-numbered unit exercises.
<!-- /edition -->

Try an exercise and test its samples before looking.
If you get stuck, read just enough of the answer to spot the next step, close it, and finish your own program.
Then compare your result and ask why any differences matter.

<!-- edition: student -->
The four checkpoints and the two projects are self-tests, so they have no printed answers.
<!-- /edition -->
<!-- edition: student-print -->
The four checkpoints and the two projects are self-tests, so the Answer Key does not include them.
<!-- /edition -->
<!-- edition: teacher -->
For students, the four checkpoints and the two projects are self-tests, so their books print no answers for them.
<!-- /edition -->

When a question gives worked samples, run your program against all of them and check that its result matches each sample exactly.
When it gives none, make up a few inputs of your own and predict each result before you run it.
Change the input and predict what should happen to test your understanding further.

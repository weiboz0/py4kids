"""A tiny judge + site book for the plan 101 Phase D tests (items, classification, answers).

`build_demo_root(path)` writes the registry, the `demo` book and its entries under `path`, then
`git init`s it and stages everything, because the export reads only git-tracked files.

- unit-01-demo: Exercise 1 fixtures (assets/ex1.py, assets/ex1/{1,2}.in|.out; the Sample Input
  fence follows prose), 2 answer (short-answer, authored answer_format), 3 predict, 4 asserts
  (function in the starter), 5 expected-output (names a tracked lesson asset), 6 self-check
  (input()), and one unnumbered challenge after a `## Challenge` lead-in.
- unit-02-more: the asserts portability cases, a turtle "trace by hand" item, a silent trace
  program and unseeded random.
- checkpoint-01-demo: a short answer and a function question.
- project-01-demo: Problem mode with `## Milestone` interludes and a "Make it yours" outro.
- project-02-demo: Milestone mode; Milestone 1's solution is a named section (self-check).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

BOOK = "demo"


def md(cell_id: str, source: str, tags=(), **metadata):
    cell = new_markdown_cell(source, id=cell_id)
    if tags:
        cell.metadata["tags"] = list(tags)
    cell.metadata.update(metadata)
    return cell


def code(cell_id: str, source: str, tags=(), outputs=None):
    cell = new_code_cell(source, id=cell_id)
    if tags:
        cell.metadata["tags"] = list(tags)
    if outputs:
        cell.outputs = outputs
    return cell


def write_nb(path: Path, cells) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    notebook = new_notebook(cells=cells)
    notebook.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3",
                                       "language": "python"}
    nbformat.write(notebook, path)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


EX1 = """## Exercise 1

### Doubler

Read a whole number and print twice its value.

### Sample Input

The program reads one line:

```text
3
```

### Sample Output

```text
6
```"""


def unit_01(base: Path) -> None:
    entry = base / "units" / "unit-01-demo"
    write(entry / "manifest.yaml", "id: unit-01-demo\nkind: unit\nconcepts:\n"
          "  introduces: [print, for-loop, def-function]\n  requires: [variable]\n"
          "  practices: [range-function]\n")
    write_nb(entry / "exercises.ipynb", [
        md("u1e00", "# Demo Exercises\n\nWork through every exercise."),
        md("u1e01", EX1),
        code("u1e02", ""),
        md("u1e03", "## Exercise 2\n\n### Stripes\n\nWhich animal has black and white stripes? "
           "Write one word.", tags=["short-answer"],
           answer_format={"case": "insensitive", "hint": "one word"}),
        md("u1e04", "**Your answer:** _(write your answer here)_"),
        md("u1e05", "## Exercise 3\n\n### Loop Trace\n\nWhat does this code print?"),
        code("u1e06", "for i in range(3):\n    print(i * 2)"),
        md("u1e07", "## Exercise 4\n\n### Double It\n\nWrite `double(n)` so it returns twice `n`."),
        code("u1e08", "def double(n):\n    pass"),
        md("u1e09", "## Exercise 5\n\n### Count Up\n\nPrint the numbers 1, 2 and 3 on separate "
           "lines, then `done`. You may start from `assets/count_helper.py`."),
        code("u1e10", ""),
        md("u1e11", "## Exercise 6\n\n### Greeter\n\nAsk for a name and greet the person.\n\n"
           "- asks for a name with `input()`\n- prints a **greeting** that uses the name"),
        code("u1e12", ""),
        md("u1e13", "## Challenge\n\nThese are extra.", tags=["stretch"]),
        md("u1e14", "### Challenge 1: Triple It\n\n**Challenge:** write `triple(n)`.", tags=["stretch"]),
        code("u1e15", "def triple(n):\n    pass", tags=["stretch"]),
    ])
    write_nb(entry / "solutions.ipynb", [
        md("u1s00", "# Demo Solutions"),
        md("u1s01", "## Exercise 1"),
        code("u1s02", "print(int(input()) * 2)\n"),
        md("u1s03", "## Exercise 2"),
        md("u1s04", "Zebras have black and white stripes.\n\n**Answer:** `ZEBRA`"),
        md("u1s05", "## Exercise 3"),
        md("u1s06", "The loop prints 0, 2 and 4."),
        code("u1s07", "for i in range(3):\n    print(i * 2)"),
        md("u1s08", "## Exercise 4"),
        code("u1s09", "def double(n):\n    return n * 2\n\n\nassert double(3) == 6\nassert double(0) == 0"),
        md("u1s10", "## Exercise 5"),
        code("u1s11", "for number in range(1, 4):\n    print(number)\nprint('done')"),
        md("u1s12", "## Exercise 6"),
        code("u1s13", "name = input('Name? ')\nprint(f'Hello, {name}!')"),
        md("u1s14", "## Challenge"),
        md("u1s15", "### Challenge 1: Triple It"),
        code("u1s16", "def triple(n):\n    return n * 3\n\n\nassert triple(2) == 6"),
    ])
    write(entry / "assets" / "ex1.py", "print(int(input()) * 2)\n")
    write(entry / "assets" / "ex1" / "1.in", "3\n")
    write(entry / "assets" / "ex1" / "1.out", "6\n")
    write(entry / "assets" / "ex1" / "2.in", "10\n")
    write(entry / "assets" / "ex1" / "2.out", "20\n")
    write(entry / "assets" / "count_helper.py", "# Count from 1 to 3 here.\n")


def unit_02(base: Path) -> None:
    entry = base / "units" / "unit-02-more"
    write(entry / "manifest.yaml", "id: unit-02-more\nkind: unit\nconcepts:\n"
          "  introduces: [variable]\n  requires: [print, for-loop]\n  practices: []\n")
    write_nb(entry / "exercises.ipynb", [
        md("u2e00", "# More Exercises"),
        md("u2e01", "## Exercise 1\n\nMake a list of three numbers in any order and print it."),
        code("u2e02", ""),
        md("u2e03", "## Exercise 2\n\nAdd the numbers 1 through 5 and store the sum in `total`."),
        code("u2e04", ""),
        md("u2e05", "## Exercise 3\n\nMake a list `names` holding three names."),
        code("u2e06", ""),
        md("u2e07", "## Exercise 4\n\nRun the turtle program below and trace their counter "
           "values by hand."),
        code("u2e08", "import turtle\n\nfor side in range(4):\n    print(side)\n"
             "    turtle.forward(50)\n    turtle.left(90)"),
        md("u2e09", "## Exercise 5\n\nWhat does this code print?"),
        code("u2e10", "x = 1"),
        md("u2e11", "## Exercise 6\n\nRoll a die and print the roll."),
        code("u2e12", "", outputs=[nbformat.v4.new_output("stream", name="stdout", text="4\n")]),
    ])
    write_nb(entry / "solutions.ipynb", [
        md("u2s00", "# More Solutions"),
        md("u2s01", "## Exercise 1"),
        code("u2s02", "my_list = [3, 1, 2]\nprint(my_list)\nassert my_list == [3, 1, 2]"),
        md("u2s03", "## Exercise 2"),
        code("u2s04", "total = 0\nfor i in range(1, 6):\n    total += i\nassert total == 15"),
        md("u2s05", "## Exercise 3"),
        code("u2s06", "names = ['Ana', 'Bo', 'Cy']\nassert len(names) == 3"),
        md("u2s07", "## Exercise 4"),
        code("u2s08", "import turtle\n\nfor side in range(4):\n    print(side)\n"
             "    turtle.forward(50)\n    turtle.left(90)"),
        md("u2s09", "## Exercise 5"),
        code("u2s10", "x = 1"),
        md("u2s11", "## Exercise 6"),
        code("u2s12", "import random\n\nprint(random.randint(1, 6))"),
    ])


def checkpoint_01(base: Path) -> None:
    entry = base / "checkpoints" / "checkpoint-01-demo"
    write(entry / "manifest.yaml", "id: checkpoint-01-demo\nkind: checkpoint\nconcepts:\n"
          "  introduces: []\n  requires: [def-function]\n  practices: []\n")
    write_nb(entry / "checkpoint.ipynb", [
        md("c1c00", "# Checkpoint 1 — Demo\n\nShow what you know."),
        md("c1c01", "## Question 1\n\nHow many legs does a spider have? Write the number.",
           tags=["short-answer"]),
        md("c1c02", "## Question 2\n\nWrite `square(n)` that returns `n * n`."),
        code("c1c03", "def square(n):\n    pass"),
    ])
    write_nb(entry / "solutions.ipynb", [
        md("c1s00", "# Checkpoint 1 Solutions"),
        md("c1s01", "## Question 1\n\nA spider has eight legs.\n\n**Answer:** `8`"),
        md("c1s02", "## Question 2"),
        code("c1s03", "def square(n):\n    return n * n\n\n\nassert square(4) == 16"),
    ])


def project_01(base: Path) -> None:
    entry = base / "projects" / "project-01-demo"
    write(entry / "manifest.yaml", "id: project-01-demo\nkind: project\nconcepts:\n"
          "  introduces: []\n  requires: [def-function]\n  practices: []\n")
    write_nb(entry / "brief.ipynb", [
        md("p1b00", "# Demo Project\n\nBuild two helpers."),
        md("p1b01", "## Milestone 1\n\nStart small."),
        md("p1b02", "### Problem 1 — Adder\n\nWrite `add(a, b)`."),
        code("p1b03", "def add(a, b):\n    pass"),
        md("p1b04", "## Milestone 2"),
        md("p1b05", "### Problem 2 — Shouter\n\nWrite `shout(text)` that returns the text in "
           "capitals."),
        code("p1b06", ""),
        md("p1b07", "## Make it yours\n\nAdd a helper of your own."),
        md("p1b08", "## Requirements checklist\n\n- both helpers work"),
    ])
    write_nb(entry / "solutions.ipynb", [
        md("p1s00", "# Demo Project Solutions"),
        md("p1s01", "## Problem 1"),
        code("p1s02", "def add(a, b):\n    return a + b\n\n\nassert add(2, 3) == 5"),
        md("p1s03", "## Problem 2"),
        code("p1s04", "def shout(text):\n    return text.upper()\n\n\nassert shout('hi') == 'HI'"),
    ])


def project_02(base: Path) -> None:
    entry = base / "projects" / "project-02-demo"
    write(entry / "manifest.yaml", "id: project-02-demo\nkind: project\nconcepts:\n"
          "  introduces: []\n  requires: [print, variable]\n  practices: []\n")
    write_nb(entry / "brief.ipynb", [
        md("p2b00", "# Demo Arcade\n\nA tiny arcade."),
        md("p2b01", "## Milestone 1\n\n### Lucky Guess\n\nWrite a guessing round."),
        code("p2b02", "secret = 4"),
        md("p2b03", "## Milestone 2\n\n### Scoreboard\n\nPrint the final score.\n\n"
           "- keeps a score\n- prints it"),
        code("p2b04", "score = 0"),
        md("p2b05", "## Make it yours\n\nChange the prizes."),
    ])
    write_nb(entry / "solutions.ipynb", [
        md("p2s00", "# Demo Arcade Reference"),
        md("p2s01", "## Lucky Guess"),
        code("p2s02", "def lucky_guess(guess):\n    return guess == 4"),
        md("p2s03", "## Milestone 2"),
        code("p2s04", "score = 3\nprint(score)"),
    ])


SYLLABUS = """# Demo syllabus

| # | id | title |
|---|---|---|
| 1 | `unit-01-demo` | Demo |
| 2 | `unit-02-more` | More |
| 3 | `checkpoint-01-demo` | Checkpoint |
| 4 | `project-01-demo` | Project |
| 5 | `project-02-demo` | Arcade |
"""

CONCEPTS = """concepts_version: 1
concepts:
- {id: print, name: Printing output, category: io}
- {id: input, name: Reading user input, category: io}
- {id: variable, name: Variables and assignment, category: data}
- {id: for-loop, name: for loops, category: loops}
- {id: range-function, name: range, category: loops}
- {id: def-function, name: Defining functions, category: functions}
"""


def build_demo_root(root: Path) -> Path:
    root = Path(root)
    write(root / "books.yaml", "books_version: 2\nbooks:\n- id: demo\n  number: 1\n  root: demo\n"
          "  title: Demo Book\n  depends_on: []\n  judge: true\n  site: true\n")
    base = root / BOOK
    write(base / "site.yaml", "classification: proposed\nfixture_budget_kb: 130\n")
    write(base / "syllabus.md", SYLLABUS)
    write(base / "curriculum" / "concepts.yaml", CONCEPTS)
    unit_01(base)
    unit_02(base)
    checkpoint_01(base)
    project_01(base)
    project_02(base)
    git_add(root)
    return root


def git_add(root: Path) -> None:
    if not (Path(root) / ".git").exists():
        subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)


# --- the whole-bundle fixture (plan 101 E) ------------------------------------------------------

GLOSSARY = """# Glossary

**print** — Shows a value on the screen. *(Unit 1)*
<!-- concept: print -->

**variable** — A name for a value. *(Units 1–2)*
<!-- concept: variable -->

**for loop** — Repeats code once per value. *(Unit 2)*
<!-- concept: for-loop -->

**range** — Makes a run of whole numbers. *(Unit 2)*
<!-- concept: range-function -->
"""

QUICK_REFERENCE = "# Quick Reference\n\n| Code | Meaning |\n|---|---|\n| `print(x)` | show x |\n"


def unit_01_lesson(base: Path, extra_cells=()) -> None:
    entry = base / "units" / "unit-01-demo"
    stream = nbformat.v4.new_output
    write_nb(entry / "lesson.ipynb", [
        md("l1m0", "# Unit 1 — Demo\n\nThe fair needs a scoreboard. By the end you will print one."),
        md("l1m1", "### You will learn\n\n- Print a value.\n- Store a value in a variable."),
        code("l1c1", "x = 3"),
        code("l1c2", "print(x * 2)", outputs=[stream("stream", name="stdout", text="6\n")]),
        code("l1c3", "print('hi')", outputs=[stream("stream", name="stdout", text="hi\n")]),
        code("l1c4", "open('scratch.txt', 'w').write('a')"),
        md("l1m2", "## Counting\n\nThe helper `assets/count_helper.py` counts for you.\n\n"
           "### Try it\n\nChange the numbers."),
        *extra_cells,
    ])
    # A verify helper is a solution source (design 010 D3): tracked, but never shipped.
    write(entry / "assets" / "verify" / "check.py", "def check(value):\n    return value == 6\n")


def unit_02_lesson(base: Path) -> None:
    entry = base / "units" / "unit-02-more"
    stream = nbformat.v4.new_output
    write_nb(entry / "lesson.ipynb", [
        md("l2m0", "# Unit 2 — More\n\nCount the prizes."),
        code("l2c1", "for i in range(2):\n    print(i)",
             outputs=[stream("stream", name="stdout", text="0\n1\n")]),
        md("l2m1", "### Recap\n\n- `for` repeats."),
    ])


def build_site_root(root: Path, extra_lesson_cells=()) -> Path:
    """The demo book plus lessons and back matter: every part of a bundle (plan 101 E)."""
    root = build_demo_root(root)
    base = root / BOOK
    unit_01_lesson(base, extra_lesson_cells)
    unit_02_lesson(base)
    write(base / "back-matter" / "glossary.md", GLOSSARY)
    write(base / "back-matter" / "quick-reference.md", QUICK_REFERENCE)
    git_add(root)
    return root

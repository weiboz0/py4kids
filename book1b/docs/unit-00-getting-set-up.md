# Unit 0 — Getting Set Up

Before you write your first program, your computer needs three things: **Python**, which runs your
programs; **JupyterLab**, where you will open this course's lessons and exercises; and **Thonny**, a
simple editor for programs saved as `.py` files.
By the end of this unit you will have run the same tiny program three different ways.

Ask an adult before installing software, and ask your teacher first if you are using a school computer —
many school computers are already set up for you.

## What you will install

| Tool | What it is for | Where you get it |
|---|---|---|
| Python 3.12 or newer | Runs every program in this book | python.org |
| JupyterLab | Opens the lesson and exercise notebooks | installed with Python's `pip` tool |
| Thonny | Writes and runs `.py` files, such as the turtle drawings in Unit 6 | thonny.org |

You will type a few commands into a **terminal**: a window where you type instructions for the computer.
On Windows it is called **Command Prompt** or **PowerShell**; on a Mac it is called **Terminal**.
Commands in this chapter are shown in grey boxes. Type them exactly and press Enter.

## Install Python on Windows

1. Open a web browser and go to **python.org/downloads**.
2. Click the big **Download Python 3.x.x** button (any version 3.12 or newer is fine).
3. Open the downloaded installer.
4. **Important:** at the bottom of the first screen, tick the box **Add python.exe to PATH**.
5. Click **Install Now** and wait until you see **Setup was successful**. Click **Close**.
6. Check that it worked. Open the Start menu, type `cmd`, and open **Command Prompt**. Type:

```text
py --version
```

You should see something like `Python 3.13.2`. The exact numbers do not matter, as long as it starts with
`Python 3` and the second number is 12 or more.

Notice: on Windows, this book always starts Python with the command `py`.
It is the Python launcher, and it finds the Python you just installed even when other copies exist.

## Install Python on a Mac

1. Open a web browser and go to **python.org/downloads**.
2. Click the big **Download Python 3.x.x** button. It downloads a file ending in `.pkg`.
3. Open the `.pkg` file and click **Continue** through the screens, then **Install**. Enter the Mac's
   password if asked.
4. When it finishes, a Finder window opens showing the **Python 3.x** folder. Double-click
   **Install Certificates.command** once. A Terminal window runs for a moment; you can close it when it
   says it is done. (This lets Python download things safely.)
5. Check that it worked. Open **Terminal** (press Command-Space, type `Terminal`, press Enter). Type:

```text
python3 --version
```

You should see something like `Python 3.13.2`.

Notice: on a Mac, this book always types `python3`, not `python`.
Many Macs have no `python` command at all, and typing it only gives an error.

## Install and start JupyterLab

JupyterLab is where you read each lesson, run its examples, and do the exercises. You install it with
`pip`, Python's tool for adding extra packages. Use the command for your computer.

On **Windows** (Command Prompt):

```text
py -m pip install jupyterlab
```

On a **Mac** (Terminal):

```text
python3 -m pip install jupyterlab
```

Wait until the text stops and you see a line starting with `Successfully installed`.

To start JupyterLab, first move the terminal into the folder that holds the course files. If your teacher
gave you a folder called `py4kids` in your Documents folder, type:

```text
cd Documents/py4kids
```

Then start JupyterLab — Windows:

```text
py -m jupyterlab
```

Mac:

```text
python3 -m jupyterlab
```

After a few seconds your web browser opens JupyterLab. If it does not, look in the terminal for a line
starting with `http://localhost:8888/` and copy that whole line into your browser.

Notice: keep the terminal window open while you work — JupyterLab stops when that window closes.

### Run your first cell

1. In the file list on the left, double-click `book1b`, then `units`, then
   `unit-01-output-and-variables`, then `lesson.ipynb`.
2. Click into the first grey code cell. It holds a short program.
3. Press **Shift+Enter**. Python runs the cell, and its result appears just below it.

Try it with a new cell of your own. Click **+** in the toolbar to add a cell, type the program below,
and press Shift+Enter:

```python
print("Hello from JupyterLab!")
```

The output below the cell should read `Hello from JupyterLab!`.

Two more things to know:

- If a notebook seems stuck or confused, choose **Kernel ▸ Restart Kernel** and run the cells again from
  the top.
- To stop JupyterLab at the end of a session, save your work, then click the terminal window and press
  **Ctrl+C**. If it asks `Shutdown this Jupyter server (y/[n])?`, type `y` and press Enter.

## Install Thonny and run a program file

Some programs in this book, such as the turtle drawings in Unit 6, are saved as files that end in `.py`
and run on their own, outside a notebook. Thonny is a friendly editor for those files.

1. Go to **thonny.org** and click the download link for your computer (**Windows** or **Mac**).
2. Open the downloaded installer and follow the steps, keeping every choice as it is.
   On a Mac, if a message says the app cannot be opened, open **System Settings ▸ Privacy & Security**,
   scroll down, and click **Open Anyway**.
3. Start Thonny. The top part is the **editor**, where you write a program. The bottom part is the
   **Shell**, where its output appears.
4. Type this program into the editor:

```python
print("Hello from Thonny!")
```

5. Choose **File ▸ Save**, name the file `hello.py`, and save it in your course folder.
6. Click the green **Run** button (or press **F5**). The Shell shows `Hello from Thonny!`.

Notice: Thonny comes with its own copy of Python, so it works even before anything else is set up.

## Run a program file from the terminal

You can also run `hello.py` straight from the terminal — Unit 6 uses this for turtle drawings.
Move into the folder where you saved it, then run it — Windows:

```text
cd Documents/py4kids
py hello.py
```

Mac:

```text
cd Documents/py4kids
python3 hello.py
```

The terminal prints `Hello from Thonny!` — the same program, run a third way.

## If something goes wrong

| What you see | What to do |
|---|---|
| Windows: `'python' is not recognized…`, or the Microsoft Store opens | Use `py` instead of `python`. If `py` also fails, run the Python installer again, choose **Modify**, and tick **Add Python to environment variables**. |
| Mac: `command not found: python` | Type `python3`, not `python`. |
| `No module named jupyterlab` | Run the install command again (`py -m pip install jupyterlab` or `python3 -m pip install jupyterlab`) and read the last lines for an error. |
| `No such file or directory` when you run `hello.py` | The terminal is in a different folder. Use `cd` to move into the folder where you saved the file, then try again. |
| JupyterLab starts but no browser opens | Copy the `http://localhost:8888/…` line from the terminal into your browser. |
| The install is blocked or asks for a password you do not know | Stop and ask your teacher or a parent — school computers often need an administrator. |

## Checklist

You are ready for Unit 1 when you can tick every box:

- [ ] `py --version` (Windows) or `python3 --version` (Mac) shows Python 3.12 or newer.
- [ ] JupyterLab opens in your browser, and a cell you ran printed its output.
- [ ] Thonny runs `hello.py` and the Shell shows the output.
- [ ] You can run `hello.py` from the terminal.

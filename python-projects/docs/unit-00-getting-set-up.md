# Unit 0 — Getting Set Up

Before you write your first program, your computer needs three things: **Python**, which runs your
programs; **JupyterLab**, where you will open this course's lessons and exercises; and **Thonny**, a
simple editor for programs saved as `.py` files.
By the end of this unit you will have run the same tiny program three different ways.

Ask a parent or whoever manages the computer before installing software.
If you use a school computer, check whether it is already set up.

You also need the **course folder**, which holds every lesson and exercise.
Download it from the course's GitHub page, **github.com/weiboz0/py4kids** (**Code ▸ Download ZIP**).
Unzip it and name the folder `py4kids`.
This chapter assumes it is in your **Documents** folder.

## What you will install

| Tool | What it is for | Where you get it |
|---|---|---|
| Python 3.12 or newer | Runs every program in this book | python.org |
| JupyterLab | Opens the lesson and exercise notebooks | installed with Python's `pip` tool |
| Thonny | Writes and runs `.py` files, such as the turtle drawings in Unit 3 | thonny.org |

You will type a few commands into a **terminal**: a window where you type instructions for the computer.
On Windows it is called **Command Prompt** or **PowerShell**; on a Mac it is called **Terminal**.
Commands in this chapter are shown in grey boxes. Type them exactly and press Enter.

## Install Python on Windows

On Windows, python.org gives you the **Python install manager**: a small app that installs Python and
keeps it up to date.

1. Open a web browser, go to **python.org/downloads**, and choose **Python install manager** for
   Windows. It downloads a small installer app.
2. Open the downloaded file and click **Install**. Wait until it finishes.
3. Open the Start menu, type `cmd`, and open **Command Prompt**. Type this command and press Enter:

```text
py install default
```

It downloads and installs the newest Python. If it asks whether to add a folder to your **PATH**, you
can answer either way — that only adds extra command names, and this book always uses `py`.

4. Check that it worked. In the same window, type:

```text
py --version
```

You should see something like `Python 3.14.2`. The exact numbers do not matter, as long as it starts with
`Python 3` and the second number is 12 or more.

If `py install default` gives an error, the computer may have an older Python launcher. Type
`pymanager install default` instead — `pymanager` always means the new install manager. If `py --version`
then still shows a version older than 3.12, ask a parent or whoever manages the computer for help.

Notice: on Windows, this book always starts Python with the command `py`.

## Install Python on a Mac

1. Open a web browser and go to **python.org/downloads**.
2. Click the big **Download Python 3.x.x** button. It downloads a file ending in `.pkg`.
3. Open the `.pkg` file and click **Continue** through the screens, click **Agree** to accept the licence,
   then click **Install**. Enter the Mac's
   password if asked.
4. When it finishes, a Finder window opens showing the **Python 3.x** folder (if it does not, open
   **Applications ▸ Python 3.x** in Finder). Double-click **Install Certificates.command** once. A Terminal window runs for a moment; you can close it when it
   says it is done. (This lets Python download things safely.)
5. Check that it worked. Open **Terminal** (press Command-Space, type `Terminal`, press Enter). Type:

```text
python3 --version
```

You should see something like `Python 3.14.2`.

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

Wait until the text stops and you see a line starting with `Successfully installed` (or
`Requirement already satisfied`, which means it was already there).
Yellow lines such as `WARNING: The script … is not on PATH` or `A new release of pip is available` are
fine — you can ignore them.

To start JupyterLab, first move the terminal into the folder that holds the course files.
If the `py4kids` folder is in your Documents folder, type:

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
starting with `http://localhost:` (the number after it may differ) and copy that whole line into your
browser.

Notice: keep the terminal window open while you work — JupyterLab stops when that window closes.

### Run your first cell

1. In the file list on the left, double-click `python-projects`, then `units`, then
   `unit-01-story-machine`, then `lesson.ipynb`.
2. Click into the first grey code cell. It holds a short program: `print("The Story Machine is awake!")`.
3. Press **Shift+Enter**. Python runs the cell, and its result, `The Story Machine is awake!`, appears just below it.

Try it with a new cell of your own. Click **+** in the toolbar to add a cell, type the program below,
and press Shift+Enter:

```python
print("Hello, Python!")
```

The output below the cell should read `Hello, Python!`.

Three more things to know:

- Save your work with **File ▸ Save Notebook** (Ctrl+S, or Cmd+S on a Mac). JupyterLab also saves
  automatically every couple of minutes.
- If a notebook seems stuck or confused, choose **Kernel ▸ Restart Kernel** and run the cells again from
  the top.
- To stop JupyterLab at the end of a session, save your work, then click the terminal window and press
  **Ctrl+C** (on Windows you may need to press it twice). If it asks
  `Shutdown this Jupyter server (y/[n])?`, type `y` and press Enter.

## Install Thonny and run a program file

Some programs in this book, such as the turtle drawings in Unit 3, are saved as files that end in `.py`
and run on their own, outside a notebook. Thonny is a friendly editor for those files.

1. Go to **thonny.org** and click the download link for your computer. There is more than one per
   system — pick the right one:
   - **Windows:** most computers need the ordinary 64-bit (Intel/AMD) installer. Choose the **Arm**
     one only if **Settings ▸ System ▸ About** says the computer has an Arm-based processor.
   - **Mac:** open the Apple menu ▸ **About This Mac**. If it says **Chip: Apple M…**, choose the Apple
     Silicon installer; if it says **Processor: Intel**, choose the Intel installer.
2. Open the downloaded installer and follow the steps, keeping every choice as it is.
   On Windows, if a blue box says **Windows protected your PC**, click **More info**, then **Run anyway**.
   On a Mac, if a message says the app cannot be opened, open **System Settings ▸ Privacy & Security**,
   scroll down, and click **Open Anyway**.
3. Start Thonny. The top part is the **editor**, where you write a program. The bottom part is the
   **Shell**, where its output appears.
4. Type this program into the editor:

```python
print("Hello, Python!")
```

5. Choose **File ▸ Save**, name the file `hello.py`, and save it in your course folder.
6. Click the green **Run** button (or press **F5**). The Shell shows `Hello, Python!`.

Notice: Thonny comes with its own copy of Python, so it works even before anything else is set up.

## Run a program file from the terminal

You can also run `hello.py` straight from the terminal — Unit 3 uses this for turtle drawings.
If you are still in the terminal where you started JupyterLab (after stopping it with Ctrl+C), you are
already in the course folder, so just run the file — Windows:

```text
py hello.py
```

Mac:

```text
python3 hello.py
```

In a **new** terminal window, first move into the course folder with `cd Documents/py4kids`, then run the
same command.

The terminal prints `Hello, Python!` — the same program, run a third way.

On a Mac there is a shortcut for `cd`: type `cd ` (with a space), drag the folder from Finder onto the
Terminal window, and press Enter.

Notice: JupyterLab has a terminal of its own. Choose **File ▸ New ▸ Terminal** and it opens inside the
browser, already in the course folder. The same `py` (Windows) or `python3` (Mac) commands work there — Unit
3 uses it for the turtle drawings.

## If something goes wrong

Find what you see, then do what it says.

- **Windows: `'py' is not recognized…`**  
  Close Command Prompt and open a new one. If it still fails, download the Python install manager from python.org again and click **Install**.
- **Windows: `py --version` says no Python is installed**  
  Run `py install default` again and wait for it to finish.
- **Windows: `py install default` fails, or `py --version` shows an old version**  
  Type `pymanager install default`.
  If `py --version` still shows a version older than 3.12, ask a parent or whoever manages the computer.
- **Windows: `'python' is not recognized…`, or the Microsoft Store opens**  
  Use `py` instead of `python` — this book always does.
- **Windows: `The system cannot find the path specified`**  
  This can happen after `cd Documents/py4kids`: your Documents folder may live inside OneDrive: try `cd OneDrive/Documents/py4kids`. Or open the folder in File Explorer, click the address bar, type `cmd`, and press Enter — a terminal opens in that folder.
- **Mac: `cd: no such file or directory`**  
  Type `cd ` and drag the course folder from Finder onto the Terminal window, then press Enter.
- **Mac: `command not found: python`**  
  Type `python3`, not `python`.
- **`No module named jupyterlab`**  
  Run the install command again (`py -m pip install jupyterlab` or `python3 -m pip install jupyterlab`) and read the last lines for an error.
- **`No such file or directory` when you run `hello.py`**  
  The terminal is in a different folder. Use `cd` to move into the folder where you saved the file, then try again.
- **JupyterLab starts but no browser opens**  
  Copy the whole `http://localhost:…` line from the terminal into your browser.
- **The install is blocked or asks for a password you do not know**  
  Stop and ask a parent or whoever manages the computer — school computers often need an administrator.

## Checklist

You are ready for Unit 1 when you can tick every box:

☐ `py --version` (Windows) or `python3 --version` (Mac) shows Python 3.12 or newer.\
☐ JupyterLab opens in your browser, and the first cell of Unit 1's lesson printed `The Story Machine is awake!`.\
☐ Thonny runs `hello.py` and the Shell shows the output.\
☐ You can run `hello.py` from the terminal.

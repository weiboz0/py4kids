# Glossary

**Accumulator** — A variable that collects a result, such as a score, one step at a time: `score = score + 1`. *(Unit 4)*
<!-- concept: accumulator; index: accumulating -->

**Append** — `items.append(value)` adds a new item to the end of a list. *(Unit 7)*
<!-- concept: list-append; index: `.append` -->

**Arithmetic operators** — The symbols `+`, `-`, `*`, `/`, `//`, and `%` calculate with numbers. *(Units 2–3)*
<!-- concept: arithmetic; index: arithmetic symbols; arithmetic -->

**Attribute** — A value stored on an object, reached with a dot, such as `buddy.name`. *(Unit 10)*
<!-- concept: attributes; index: object attribute -->

**Boolean** — One of the two truth values, `True` or `False`. *(Unit 2)*
<!-- concept: boolean; index: True; False -->

**Break** — `break` leaves a loop at once, jumping to the first line after it. *(Unit 4)*
<!-- concept: break-statement; index: break -->

**Built-in function** — A ready-to-use Python function such as `len()`, `min()`, or `max()`. *(Unit 7)*
<!-- concept: builtin-functions; index: len; min; max -->

**Class** — A set of instructions for making objects with the same kinds of attributes and methods. *(Unit 10)*
<!-- concept: class-def; index: `class` -->

**Code comment** — Words after `#` that explain code to a reader; Python does not run them. *(Unit 1)*
<!-- concept: comment; index: comment -->

**Comparison** — A test such as `a < b` or `a == b` that gives `True` or `False`. *(Unit 2)*
<!-- concept: comparison; index: comparing values -->

**Conditional inside a conditional** — An `if` block placed inside another decision to ask a second question only on one path. *(Unit 4)*
<!-- concept: conditional-nesting; index: nested conditional; conditional nesting -->

**Count by condition** — Add one to a count only when an item passes a test. *(Unit 4)*
<!-- concept: count-by-condition; index: conditional count; counting by condition -->

**Counter variable** — The variable that counts a loop's turns, such as `side_number` in `for side_number in range(4):`; it can do work inside the loop too. *(Unit 3)*
<!-- concept: loop-counter; index: loop counter; counter variable; counter -->

**Dictionary** — A collection that connects each key to a value, written like `{"cat": "gato"}`. *(Unit 8)*
<!-- concept: dict-literal; index: dictionary -->

**Dictionary lookup and update** — `translations["cat"]` gets the value for a key, and assigning to that place adds or changes it; `.get(key, default)` gives the default instead of an error when the key is missing. *(Unit 8)*
<!-- concept: dict-access; index: dictionary key; look up -->

**Else and elif** — Extra branches of an `if` decision: `elif` tests another condition, and `else` catches the remaining cases. *(Unit 2)*
<!-- concept: elif-else; index: else; elif -->

**Error message** — Python's clue about where and why a program stopped. *(Unit 1)*
<!-- concept: error-messages; index: traceback -->

**File reading** — Getting saved text from a file with `read()` or a loop over its lines, after opening it without `"w"`. *(Unit 9)*
<!-- concept: file-read; index: `read`; reading a file -->

**File writing** — Saving text with `write()` after opening a file in `"w"` mode. *(Unit 9)*
<!-- concept: file-write; index: `write`; writing a file -->

**Filter into a list** — Loop over items and append only the ones that pass a test to a new list. *(Unit 7)*
<!-- concept: filter-into-list; index: filter; filtering; items that pass a test -->

**Find the best** — Keep the largest or smallest value seen so far, and sometimes the item that owns it. *(Unit 7)*
<!-- concept: find-extreme; index: champion; best value; best so far; find-extreme -->

**Float** — A Python number that can have a decimal part, such as `2.5`; dividing with `/` always gives one. *(Unit 3)*
<!-- concept: float-type; index: decimal number; decimal -->

**For loop** — A loop that visits each value from a range or collection in turn. *(Unit 3)*
<!-- concept: for-loop; index: for -->

**Formatted string** — Text starting with `f` that puts a value inside braces, as in `f"Score: {score}"`. *(Unit 1)*
<!-- concept: f-string; index: f-string; formatted string -->

**Function definition** — A named group of instructions begun with `def` and run when you call it. *(Unit 5)*
<!-- concept: def-function; index: def -->

**If statement** — `if` runs an indented block only when its condition is true. *(Unit 2)*
<!-- concept: if-statement; index: if -->

**Import** — `import` brings a module's tools into your program, as in `import random`. *(Unit 2)*
<!-- concept: import-statement; index: import -->

**Input** — `input()` waits for someone to type a value and gives the program that value as text. *(Unit 1)*
<!-- concept: input; index: user input -->

**Integer** — A whole number such as `-2`, `0`, or `17`; Python calls its type `int`. *(Unit 2)*
<!-- concept: int-type; index: int -->

**List** — An ordered collection of values written with square brackets, such as `[4, 7]`. *(Unit 7)*
<!-- concept: list-literal; index: `list`; list literal; many items in order; lists -->

**List indexing** — `items[0]` gets the first item and `items[-1]` the last. *(Unit 7)*
<!-- concept: list-index; index: list index; list positions -->

**Local scope** — A name made inside a function is local and belongs there; a name made outside functions is global. *(Unit 5)*
<!-- concept: scope; index: scope; local variable -->

**Logical operators** — `and`, `or`, and `not` combine or reverse truth tests. *(Unit 4)*
<!-- concept: logical-ops; index: and; or; not -->

**Loop over a dictionary** — Visit its keys, or its key/value pairs with `.items()`. *(Unit 8)*
<!-- concept: dict-loop; index: `items` -->

**Loop over a list** — `for item in items:` visits each list item in order. *(Unit 7)*
<!-- concept: list-loop; index: list iteration; value loop; each item in a list -->

**Method** — A function written inside a class and called through an object, such as `buddy.play()`. *(Unit 10)*
<!-- concept: methods; index: object method -->

**Name** — A clear, meaningful word you choose for a variable or function so its job is easy to see. *(Unit 1)*
<!-- concept: naming; index: -Name; naming; clear variable name; meaningful names -->

**Nested loops** — A loop inside another loop; the inner loop completes its turns for each outer turn. *(Unit 3)*
<!-- concept: nested-loops; index: loop nesting -->

**Object creation** — `__init__` runs when you make a new object and usually saves its first attributes through `self`. *(Unit 10)*
<!-- concept: init-method; index: `__init__`; `self` -->

**Parameter** — A blank in a function's definition, such as `name` in `def greeting_card(name):`; each call fills it with a value, in order. *(Unit 5)*
<!-- concept: parameters; index: parameter -->

**Print** — `print()` displays a value in the program's output. *(Unit 1)*
<!-- concept: print; index: `print` -->

**Random numbers** — `random.randint(a, b)` picks an integer from `a` through `b`; both ends can be picked. *(Unit 2)*
<!-- concept: random-module; index: `random.randint` -->

**Range** — `range(n)` supplies the integers from `0` up to, but not including, `n`. *(Unit 3)*
<!-- concept: range-function; index: `range` -->

**Return value** — A result a function sends back with `return`. *(Unit 5)*
<!-- concept: return-value; index: return -->

**Running a program** — Asking Python to follow the instructions in a cell or a `.py` file. *(Unit 1)*
<!-- concept: run-program; index: run a Python cell; running a notebook cell; running a cell -->

**Running total** — Add each new number to a total as you visit it. *(Unit 4)*
<!-- concept: running-total; index: running totals -->

**Scan until found** — Check items one by one and stop as soon as the wanted item appears. *(Unit 6)*
<!-- concept: linear-search; index: linear search; search for a match; one by one -->

**Sentinel loop** — Keep repeating until a stop signal, such as a correct guess or a typed word, ends the loop. *(Unit 2)*
<!-- concept: sentinel-loop; index: sentinel -->

**Sort a list** — `items.sort()` puts the items of that list in order, lowest first; `items.sort(reverse=True)` puts the highest first. *(Unit 7)*
<!-- concept: list-sort; index: `sort` -->

**String** — Text between quotes, such as `"hello"` or `'hello'`. *(Unit 1)*
<!-- concept: string-literal; index: -String; string literal; string literals -->

**String combining** — `+` joins strings into one longer string. *(Unit 1)*
<!-- concept: string-concat; index: string concatenation -->

**String index** — A position in text; `word[0]` gets its first character and `word[-1]` its last. *(Unit 6)*
<!-- concept: string-index; index: character position; numbered position -->

**String methods** — Tools called on text that give a changed copy, such as `.lower()`, `.upper()`, `.strip()`, and `.replace()`. *(Unit 6)*
<!-- concept: string-methods; index: `lower`; `upper`; `strip`; `replace`; string methods -->

**String slice** — `word[start:stop]` takes characters from `start` up to, but not including, `stop`. *(Unit 6)*
<!-- concept: string-slice; index: slicing; run of characters -->

**Test with in** — `"m" in letters` asks whether one value appears inside another. *(Unit 6)*
<!-- concept: in-operator; index: membership -->

**Transform each item** — Visit every item and make a changed value for each one. *(Unit 6)*
<!-- concept: transform-each; index: transform each; same to each -->

**Turtle drawing** — Pen commands such as `turtle.color("blue")`, `turtle.pensize(4)`, `turtle.penup()`, and `turtle.pendown()` change the lines a turtle makes. *(Unit 3)*
<!-- concept: turtle-drawing; index: turtle pen; pen color -->

**Turtle movement** — Commands such as `turtle.forward(100)` and `turtle.right(90)` move and turn the drawing turtle. *(Unit 3)*
<!-- concept: turtle-basics; index: turtle -->

**Type conversion** — `int()` turns digit-text into an integer, and `str()` turns a number into text. *(Unit 2)*
<!-- concept: type-conversion; index: converting types -->

**Variable** — A named place to keep a value, made with an assignment such as `score = 3`. *(Unit 1)*
<!-- concept: variable; index: assignment -->

**While loop** — A loop that repeats its indented block while a condition is true. *(Unit 2)*
<!-- concept: while-loop; index: while -->

**With statement** — `with open(...) as f:` gives a block a file and closes it when that block ends. *(Unit 9)*
<!-- concept: with-statement; index: with -->

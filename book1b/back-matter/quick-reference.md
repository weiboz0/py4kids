# Quick Reference

Use this as a reminder after you have met an idea in its unit.
The indented lines belong to the line above them.

## Output and variables · Unit 1

```python
print("Ready!")           # show a value
name = "Maya"             # save a value
name = input("Name? ")   # read text
print(f"Hello, {name}!") # put a value in text
```

`#` begins a comment.
Use names that tell you what each value means.

## Numbers · Unit 2

```python
count = int(input("Count? "))
price = float(input("Price? "))
label = str(count)
answer = 7 + 3 * 2
quotient = 7 // 3       # whole-number quotient: 2
remainder = 7 % 3      # leftover: 1
```

`/` gives a decimal result; `//` and `%` handle whole-number division and leftovers.

## Decisions · Unit 3

```python
if score >= 10 and score < 20:
    print("middle")
elif score >= 20:
    print("high")
else:
    print("low")
```

Compare with `==`, `!=`, `<`, `<=`, `>`, or `>=`.
Combine tests with `and`, `or`, and `not`.

## Loops · Units 4–5

```python
count = 0
while count < 3:
    print(count)
    count = count + 1

for number in range(3):  # 0, 1, 2
    print(number)
for row in range(2):
    for column in range(3):
        print(row, column)
```

`break` leaves a loop; `continue` moves to its next turn.
For a running total, start `total = 0` and add each new value inside the loop.

## Turtle · Unit 6

```python
import turtle
turtle.pencolor("blue")
turtle.pensize(3)
for side in range(4):
    turtle.forward(80)
    turtle.left(90)
turtle.done()
```

Run a turtle program as a `.py` file; close its drawing window when finished.

## Functions · Unit 7

```python
def double(number):
    return number * 2

print(double(4))  # 8
print(len("cat")) # 3
```

A parameter such as `number` gets the argument from the call.
Names made inside a function belong to that function.
`min()` and `max()` find the smallest and largest supplied values.

## Random choices · Unit 8

```python
import random
random.seed(4)                  # repeatable sequence
roll = random.randint(1, 6)    # both ends included
pick = random.choice("HT")      # one character: H or T
```

## Strings · Unit 9

```python
word = "Python"
first = word[0]            # "P"
part = word[1:4]           # "yth"
clean = word.lower().strip()
found = "th" in word.lower()
pieces = "red,blue".split(",")
joined = "-".join(pieces)
position = word.find("th")
```

Strings also have `.upper()`, `.replace(old, new)`, and tests such as `.isdigit()`.

## Lists · Unit 10

```python
items = [3, 1]
first = items[0]
items.append(2)
items.insert(0, 4)
items.remove(1)
last = items.pop()
items.sort()
for item in items:
    print(item)
```

`items.index(value)` finds a value's position.
To keep only matching items, start a new empty list and append inside an `if` in a loop.

## Dictionaries · Unit 11

```python
scores = {"Maya": 3}
scores["Maya"] = scores["Maya"] + 1
scores["Leo"] = 2
for name, score in scores.items():
    print(name, score)
```

Each key leads to one value.
Use `if name in scores:` before a lookup when the key might be missing.

## Files · Unit 12

```python
with open("scores.txt", "w") as f:
    f.write("840\n")
with open("scores.txt", "r") as f:
    for line in f:
        score = int(line.strip())
        print(score)
```

`"w"` replaces the file's old contents; `"r"` reads an existing file.
`f.read()` gets all its text, and `f.readline()` gets the next line.

## Classes and objects · Unit 13

```python
class Counter:
    def __init__(self, start):
        self.value = start

    def increment(self, amount):
        self.value = self.value + amount
        return self.value

counter = Counter(2)
print(counter.increment(3))  # 5
```

`Counter(2)` makes one object; `self.value` is a value stored on that object.

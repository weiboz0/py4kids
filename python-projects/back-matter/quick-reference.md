# Quick Reference

Use this as a reminder after you have met an idea in its unit.
The indented lines belong to the line above them.

## Output and variables · Unit 1

```python
print("Ready!")              # show a value
hero = "Captain Pickle"      # save a value
name = input("Name? ")      # read text
print("Meet " + hero + "!")  # join strings
print(f"Hello, {name}!")    # put a value in text
```

`#` begins a comment.
Use names that tell you what each value means.

## Numbers · Unit 2

```python
guess = int(input("Guess? "))  # text to integer
label = str(guess)             # integer to text
answer = 7 + 3 * 2             # 13: * before +, as in math
groups = 17 // 5               # whole groups: 3
left_over = 17 % 5             # leftover: 2
```

`input()` always gives text; use `int()` before doing arithmetic with it.

## Decisions and while loops · Unit 2

```python
import random
secret = random.randint(1, 100)  # both ends included
guess = int(input("Guess? "))
while guess != secret:
    if guess > secret:
        print("Too high!")
    elif guess < secret:
        print("Too low!")
    guess = int(input("Guess again: "))
print("Correct!")
```

Compare with `==`, `!=`, `<`, or `>`; each comparison gives `True` or `False`.
Python takes the first branch whose test is `True`; `else` catches the rest.

## Turtle and for loops · Unit 3

```python
import turtle
n = 6
angle = 360 / n           # / always gives a float
turtle.color("blue")
turtle.pensize(3)
for shape in range(12):
    for side in range(n):  # 0, 1, ..., n - 1
        turtle.forward(80)
        turtle.right(angle)
    turtle.right(30)
turtle.done()
```

`turtle.penup()` lifts the pen and `turtle.pendown()` drops it again.
Run a turtle program as a `.py` file; close its drawing window when finished.

## Scores and rules · Unit 4

```python
score = 0
alive = True
answer = 8
if answer == 8 and alive:
    score = score + 1          # accumulator
if score >= 1:
    if not alive:              # an if inside an if
        print("Close call!")
count = 0
while count < 5:
    if count == 2:
        break                  # leave the loop now
    count = count + 1
```

`and` needs both sides `True`; `or` needs at least one; `not` flips `True` and `False`.
Compare with `<=` and `>=` for "at most" and "at least".
For a running total, start `total = 0` and add each new value inside the loop.

## Functions · Unit 5

```python
def area(w, h):
    return w * h

card_area = area(7, 4)  # 28
print(card_area)
```

A parameter such as `w` gets the argument from the call.
`return` hands a value back; `print` only shows it.
Names made inside a function are local to that function.

## Strings · Unit 6

```python
word = "Python"
first = word[0]            # "P"
last = word[-1]            # "n"
part = word[1:4]           # "yth"
backward = word[::-1]      # "nohtyP"
clean = "  MEET_ME ".strip().lower().replace("_", " ")
found = "th" in word
for letter in word:
    print(letter.upper())
```

String methods give a changed copy; the original string stays the same.

## Lists · Unit 7

```python
scores = [1200, 850]
scores.append(990)
first = scores[0]
scores.sort(reverse=True)  # highest first
for score in scores:
    print(score)
print(len(scores), max(scores), min(scores))
```

`.sort()` changes the list itself, so call it on its own line.
To keep only matching items, start a new empty list and append inside an `if` in a loop.

## Dictionaries · Unit 8

```python
translations = {"hello": "hola"}
translations["cat"] = "gato"
print(translations["cat"])
print(translations.get("fish", "???"))
for word, meaning in translations.items():
    print(word, meaning)
```

Each key leads to one value.
Use `.get()` or `if word in translations:` when the key might be missing.

## Files · Unit 9

```python
with open("savegame.txt", "w") as f:
    f.write("1200\n")
with open("savegame.txt") as f:
    for line in f:
        score = int(line.strip())
        print(score)
```

`"w"` replaces the file's old contents; opening without `"w"` reads a file that already exists.
`f.read()` gets all of its text as one string.

## Classes and objects · Unit 10

```python
class Pet:
    def __init__(self, name):
        self.name = name
        self.happiness = 5

    def play(self):
        self.happiness = self.happiness + 1

buddy = Pet("Buddy")
buddy.play()
print(buddy.happiness)  # 6
```

`Pet("Buddy")` makes one object; `self.happiness` is a value stored on that object.

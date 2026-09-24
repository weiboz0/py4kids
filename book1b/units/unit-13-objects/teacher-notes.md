# Teacher Notes — Unit 13: Objects

## Goals

Students leave able to define a class with `class`, an `__init__` that sets attributes on `self`, and methods
that use those attributes and RETURN a value — and to reason about object identity (each instance carries its
own attributes).
Success looks like: every student defines a small class (a `Point`/`Rectangle`/`Counter`), creates instances,
calls a method that computes from the attributes, and can explain what `self` refers to.
The surface is deliberately small: `class Name:` + `__init__` + plain methods + `self.attr` — NO inheritance,
NO dunder methods other than `__init__` (a `describe()` method returns a string instead of `__str__`), NO
decorators. `distance` uses `** 0.5`, never `math.sqrt`.

## Pacing

Budget: three lessons of 60–90 minutes (OOP is the hardest unit — go slowly). Hook: "a map editor needs each
marker to carry its x and y together and keep them after the program ends — a class bundles them into one
object."

- **Lesson 1 — Build Objects with a Class (`class-def`, `init-method`, `attributes`).** A new first rung
  makes an object with ONE attribute (`class Marker:` with `self.label = label`); then `class Point:` with
  `def __init__(self, x, y): self.x = x; self.y = y`; create instances; read `p.x`. Explain **`self` as "THIS
  particular object"** (do NOT call it "scope"). The **identity beat:** make TWO instances, change one's
  attribute, show the other is untouched. A `no-exec` cell reads `x` and `y` and builds a `Point`. Trap:
  forgetting `self`.
- **Lesson 2 — Methods Compute with Attributes (`methods`).** Methods that use attributes and RETURN a value:
  first a Rectangle with only `area` (one method), then `area`/`perimeter`/`describe` together, `distance` via `** 0.5`, `describe()` returning an f-string (not `__str__`); a
  `string-slice` on an attribute string (`short_code()` → `self.code[0:2]`). Contrast a method with a plain
  function that takes the object; then **a method that draws** — `draw()` builds rows of `"#" * self.width`
  and returns `"\n".join(rows)` (`Rectangle("D-1", 5, 2)`), with a `no-exec` cell that reads a width and
  height.
- **Lesson 3 — Save and Load an Object.** A class with a `save(path)` method (`file-write`) and a
  **module-level `load_point(path)`** that reads (`open(path, "r")`) and RETURNS a new object — the file reuse
  from Unit 12. Mutating methods (`Counter.increment`) are fine; assert the attribute after the call. New
  rungs: **a list as an attribute** (`Shelf` with `self.books = []` and `add`), **a dictionary as an
  attribute** (`Scoreboard` with `self.points = {}` and `record`), **objects in a list** (a loop over three
  `Point`s), and **a state machine** (`Lamp` switching `"off"` ↔ `"on"` with `press()`). A `no-exec` cell
  reads `n` book titles into a `Shelf`.

**60-minute cut:** teach L1 (class + attributes + identity) and L2's `area`/`describe` live; the persistence
lesson (L3) and `distance` can wait / go to fast-finishers.

## Exercises — core vs. More Practice vs. challenge

24 exercises, all in the class/function form.

- **Core (1–10):** Two Separate Points, Rectangle Record, Rectangle Measurements, Distance Between Points,
  Short Code & Description, Score Counter, Save and Load a Point, plus **Draw a Rectangle** (8:
  `"####\n####"`), **Bank Account** (9: deposit 30 → 80, a refused withdrawal, withdraw 25 → 55) and
  **Traffic Light** (10: green → yellow → red → green). Exercises 8–10 require a purpose comment.
- **More Practice (11–20)**, grouped by genre:
  - *Modeling & state:* Playlist (a list attribute), Vending Machine (`Insert 2 more` … `Vend! Change: 1`),
    Stockroom (a dict attribute), Student Grades (85.0), Game Board (`render()` → `X..` / `...` / `..O`).
  - *Objects in a list:* Total Area (26), Closest Point (`1 1`).
  - *Debug & predict:* Fix the Missing self (`TypeError: Rect.area() takes 0 positional arguments but 1 was
    given`), Fix the Attribute Typo (`AttributeError: 'Crate' object has no attribute 'height'`), Predict
    Two Counters (`0 5`).
- **Challenges (21–24, `stretch`):** Rectangle Size Band, Counter Snapshot, **Rover Commands**
  (`FFRFF` → `(2, 2) facing E`), **Save the Stockroom**.

**Real versions.** Every exercise except the two Fix exercises and the predict has a real program: it
reads the constructor and method arguments with bare `input()`, builds the object, and prints the results.

## Common mistakes

- Forgetting `self` in a method signature or when reading an attribute (`x` vs `self.x`).
- Thinking two instances share attributes — each object carries its own (the identity beat).
- Forgetting to create the list/dict attribute in `__init__` (`self.books = []`) before a method appends
  to it.
- A state machine that forgets to store the new state (`self.state = "yellow"`), so `next()` always
  returns the same answer.
- Calling a method without `self` in its definition (`TypeError … takes 0 positional arguments but 1 was
  given`) — Python passes the object automatically.
- Reaching for `math.sqrt` (untaught import) — use `** 0.5`.
- Writing `__str__`/inheritance/`@property`/`@classmethod` — not taught; a `describe()` method returns the
  string, and the loader is a plain module-level function.
- A method that PRINTS instead of RETURNS (the caller can't use a printed value) — same lesson as Unit 07.

## Discussion prompts

- What does `self` mean inside a method? Why does each `Point` remember its own `x` and `y`?
- When is a method better than a plain function that takes the object as an argument?
- Why can a class `save` itself with a method, but loading is a separate function that returns a new object?
- `describe()` returns a string instead of printing — what can the caller do with the returned string?

## Differentiation

- Strugglers: Core 1–3 (identity, a record class, `area`/`perimeter`); give `__init__` and have them write one
  method.
- Fast finishers: the state-machine exercises (Traffic Light, Vending Machine), then the Challenges (Rover
  Commands is the capstone); then add a method that compares two
  objects (e.g. which rectangle is larger).
- Middle tier: rewrite a plain function from Unit 07 as a method on a class and confirm identical results.

## Value plan (sample inputs)

Each exercise uses distinct instances; solutions assert construct-then-check (and attribute-after-call for
mutating methods).
- Ex1 `Point(2,6)` and `Point(9,4)`; then `start.x = 5` leaves `finish.x` at 9 (the identity beat).
- Ex2 `small = Rectangle("N-12",6,4)`, `large = Rectangle("S-30",12,7)`: `small.code`→"N-12", `small.width`→6, `large.height`→7.
- Ex3 `tile.area()`→36, `tile.perimeter()`→26 (`Rectangle(9,4)`). Ex4 `Point(1,2).distance(Point(4,6))`→5.0; `Point(2,1).distance(Point(2,6))`→5.0.
- Ex5 `crate.short_code()`→"NE", `crate.describe()`→"NE-48: 7 by 3". Ex6 `blue.increment(3)`→3, then `increment(2)`→5.
- Ex7 `Point(14,9).save("ex7_point.txt")`→"ex7_point.txt"; the loaded point has `x`=14, `y`=9.
- Ex21 (stretch) `Rectangle(10,7).size_band()`→"large", `Rectangle(7,5)`→"medium". Ex22 (stretch)
  `visitors = Counter("north gate",12)`: `increment(4)`→16, `save("ex22_counter.txt")`→"ex22_counter.txt", then
  `load_counter(...)` gives back `label`="north gate", `count`=16.
- New exercises 8–24: fixtures as in the exercise statements (plan 084's tables), grep-distinct from shipped
  Book 1b content.

## More Practice ideas (design 006 D9 genres)

- **State machines:** a `Door` that is `"locked"`, `"closed"` or `"open"` with `unlock()`/`open()` rules.
- **Modeling:** a `Library` whose `books` dict maps titles to copies, with `lend(title)`.
- **ASCII art:** a `Frame` object whose `draw()` returns a hollow box around a word.

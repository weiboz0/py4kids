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

Budget: three lessons of 60–90 minutes (OOP is the hardest unit — go slowly). Hook: "a scoreboard needs each
player to carry name + score + wins together — a class bundles them into one object."

- **Lesson 1 — Build Objects with a Class (`class-def`, `init-method`, `attributes`).** `class Point:` with
  `def __init__(self, x, y): self.x = x; self.y = y`; create instances; read `p.x`. Explain **`self` as "THIS
  particular object"** (do NOT call it "scope"). The **identity beat:** make TWO instances, change one's
  attribute, show the other is untouched. Trap: forgetting `self`.
- **Lesson 2 — Methods Compute with Attributes (`methods`).** Methods that use attributes and RETURN a value:
  `area`/`perimeter`, `distance` via `** 0.5`, `describe()` returning an f-string (not `__str__`); a
  `string-slice` on an attribute string (`short_code()` → `self.code[0:2]`). Contrast a method with a plain
  function that takes the object.
- **Lesson 3 — Save and Load an Object.** A class with a `save(path)` method (`file-write`) and a
  **module-level `load_point(path)`** that reads (`open(path, "r")`) and RETURNS a new object — the file reuse
  from Unit 12. Mutating methods (`Counter.increment`) are fine; assert the attribute after the call.

**60-minute cut:** teach L1 (class + attributes + identity) and L2's `area`/`describe` live; the persistence
lesson (L3) and `distance` can wait / go to fast-finishers.

## Exercises — core vs. extra vs. challenge

Core (1–7): Two Separate Points (identity), Rectangle Record (`__init__`/attributes), Rectangle Measurements
(`area`/`perimeter`), Distance Between Points (`** 0.5`), Short Code & Description (`string-slice` +
`describe()` f-string), Score Counter (a mutating `increment`), Save and Load a Point (persistence).
Challenges (8–9, `stretch`): Rectangle Size Band (an `elif` method); Counter Snapshot (increment + save).

## Common mistakes

- Forgetting `self` in a method signature or when reading an attribute (`x` vs `self.x`).
- Thinking two instances share attributes — each object carries its own (the identity beat).
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
- Fast finishers: the two Challenges (size-band, counter snapshot), then add a method that compares two
  objects (e.g. which rectangle is larger).
- Middle tier: rewrite a plain function from Unit 07 as a method on a class and confirm identical results.

## Value plan (sample inputs)

Each exercise uses distinct instances; solutions assert construct-then-check (and attribute-after-call for
mutating methods).
- Ex1 `Point(2,6)` and `Point(9,4)`; then `start.x = 5` leaves `finish.x` at 9 (the identity beat).
- Ex2 `Rectangle("N-12",6,4)` and `Rectangle("S-30",12,7)` — read `.code`/`.width`/`.height`.
- Ex3 `tile.area()`→36, `tile.perimeter()`→26 (`Rectangle(9,4)`). Ex4 `Point(0,0).distance(Point(3,4))`→5.0; `Point(2,1).distance(Point(2,6))`→5.0.
- Ex5 `crate.short_code()`→"NE", `crate.describe()`→"NE-48: 7 by 3". Ex6 `blue.increment(3)`→3, then `increment(2)`→5.
- Ex7 `Point(14,9).save("ex7_point.txt")`→"ex7_point.txt"; the loaded point has `x`=14, `y`=9.
- Ex8 (stretch) `Rectangle(10,7).size_band()`→"large", `Rectangle(7,5)`→"medium". Ex9 (stretch) `increment(4)`→16 then `save(...)`.

# Teacher Notes — Unit 10: Pet Simulator

## Goals

Students leave able to write their first CLASS: define `class Pet:` with an `__init__` that gives
each pet its own attributes (name, hunger, happiness), add methods that read and change those
attributes (`feed`, `play`, `pass_time`, `status`), make pet OBJECTS with `Pet("Buddy")`, and drive
a small simulation. The big idea: a class is a blueprint, and each object made from it carries its
OWN data. Success looks like: every student adopts a pet, feeds and plays with it, and reads its
mood change. This is the last unit of Year 1 — the first taste of object-oriented programming.

## Pacing

Budget: three lessons of 60–90 minutes (objects are a new mental model). Each concept is a short **worked-example ladder** (minimal → one step up → real simulator, with a *Notice* per rung); the lesson-count is advisory. `class-def` and `__init__` are co-taught; the `methods` ladder GROWS the class one method at a time — re-make the pet (`buddy = Pet(...)`) after each change so it has the new methods. The foods dict, the multi-pet loop, and the while-play loop are the Lesson-3 "put it together" applications, not new concepts.

The **in-class path is Exercises 1–8 and 12**.
Exercises 9–11 are the labelled **More Practice** homework tier; they deepen repetition but introduce nothing new.
Exercise 12 returns to class for the final full-class simulation, so every practiced idea — including `pass_time` and the prompt-only `input()` practice — appears at least once on the in-class path.
The Challenge exercises 13–14 are optional stretch work and do not carry core coverage.

- **Lesson 1 — a class is a blueprint (class-def, __init__, attributes) (60–90 min).**
  Open on the hook: adopt a virtual pet. 20 min: `class Pet:` + `def __init__(self, name):` setting
  `self.name`, `self.hunger`, `self.happiness`. Explain `self` means "this particular pet". 15 min:
  make `buddy = Pet("Buddy")`; read `buddy.name`, `buddy.hunger`. 20 min: make a SECOND pet and show
  its hunger is separate from Buddy's — each object carries its OWN attributes. (Do NOT call this
  "scope"; it is object identity — each `Pet(...)` is its own thing.)
  Use Exercises 1–2 in class.
  60-MINUTE CUT: one pet is enough for L1; the two-pets independence beat can open L2.
- **Lesson 2 — methods change a pet (methods) (60–90 min).**
  Open on the thread: our pet just sits there — let's give it actions. Grow the class one method at a
  time, each taking `self`, re-making `buddy` after each change: first the method idea itself with two
  same-shape mutators — `play(self)` raises `self.happiness`, `pass_time(self)` RAISES `self.hunger`
  (time makes a pet hungry); then `feed(self, amount)` to add a PARAMETER (lower hunger by `amount`);
  then give `feed` a `return` so it hands back the new hunger; finally `status(self)` to add a
  DECISION — an if/elif/else ladder on `self.hunger` that builds a `mood` and prints it. Call
  `buddy.play()`, `buddy.feed(2)`, `buddy.status()`.
  Use Exercises 3–4 in class.
  60-MINUTE CUT: the method idea (`play`/`pass_time`) + `feed` are the core; `status` can be quick.
- **Lesson 3 — a little simulation (60–90 min).**
  A `foods` dictionary feeds by name (`buddy.feed(foods["steak"])`). A LIST of pets, grown with
  `.append`, walked with ONE `for pet in pets:` loop giving each a `pass_time()` + `status()`. A
  SEPARATE `while buddy.happiness < 10: buddy.play()` loop plays one pet until it is happy. Then the
  deliberate AttributeError bug (`buddy.hapiness` — a typo) — read the traceback together and name
  why the attribute must match the one set in `__init__`.
  Use Exercises 5–8 in class, including running the tagged broken cell manually and copying its traceback into the markdown response cell.
  Finish with Exercise 12, **Run a Pet Day**, in class.
  Assign Exercises 9–11 as More Practice homework after this lesson.
  60-MINUTE CUT: skip the while loop; the pets-list pass is the core.

Practices reappearance: `arithmetic`/`int-type`/`accumulator` are the hunger/happiness changes
(`self.hunger = self.hunger - amount`); `comparison`/`elif-else`/`if-statement` are the mood ladder;
`dict-literal`/`dict-access` are the foods table; `list-literal`/`list-append`/`list-loop`/`for-loop`/
`list-index` build and walk the pet list; `while-loop` is the play-until-happy loop; `f-string`/
`print`/`variable`/`string-literal` throughout; `error-messages` is the active AttributeError run-read-copy-fix beat.
Because staging three deliberate failures would be artificial in this gentle unit, `error-messages` has the plan's justified peripheral count exemption: one genuine in-class authoring-and-debugging exercise instead of three.
`input` is authored only in tagged `no-exec` prompt cells in Exercises 7, 9, and 12; regular executable cells stay input-free.
Everything comes together in the Year-1 capstone.

## Common mistakes

- Forgetting `self` — either in the method signature (`def feed(amount):` misses `self`) or in the
  body (`hunger = hunger - amount` instead of `self.hunger = self.hunger - amount`). Name `self`
  every time: it is how a method reaches THIS pet's attributes.
- A typo'd attribute → `AttributeError` (e.g. `buddy.hapiness`). The name must match exactly the one
  set in `__init__`. This is the planned Lesson-3 bug.
- Expecting two pets to share a stat — feeding Buddy does not change Rex. Each object is separate.
- Forgetting to `return` from `feed` when the caller wants the new hunger value (the method changes
  `self.hunger` either way, but `x = buddy.feed(2)` needs the `return`).
- Writing methods OUTSIDE the class body (indentation) so they are plain functions, not methods.

## Discussion prompts

- A class is a blueprint and an object is one thing built from it. What real-world blueprint/object
  pairs can you name (cookie cutter / cookie, blueprint / house)?
- Why does each pet need its OWN hunger instead of one shared number?
- `feed` lowers hunger and `pass_time` raises it. What other methods would a real pet game need?

## Differentiation

- Strugglers: give the finished `Pet` class and have them only MAKE pets and CALL methods
  (`buddy = Pet("Buddy"); buddy.feed(2); buddy.status()`) — seeing the stats change is the win.
- Fast finishers: the Challenge exercises 13–14 — happiest-pet (loop the pets, track the highest happiness
  with a running best) and play-until-happy (a `while` loop). Adding a new method (a `nap` that
  lowers hunger a little) is a good no-new-concepts extension.
- Middle tier: writing the `status` mood-ladder method before the Challenges.

# Teacher Notes — Project 02: Grand Adventure

## Goals

Students combine the full Year 1 toolkit — variables, conditionals, loops, lists,
dictionaries, functions, files, and one class — into the year's biggest program.
The graded path includes a student-authored `Hero` method, a student-authored list index,
and a final assembly milestone that connects the four scaffolds into one program.
The world deliberately uses THREE FLAT dictionaries, with each exit stored under one
composite `"room direction"` key; there is no nested dictionary.
Success looks like: every student demos a hero exploring a connected world, collecting an
item, quitting safely, and saving and loading the same progress.

## Pacing

Budget: four lessons of 60–90 minutes; Milestones 4 and 5 share the final lesson.

- **Lesson 1 — Milestone 1: meet the hero.**
  Goal: every student creates one `Hero` object with a name, health, and inventory, prints
  the starting stats first, then authors and calls `take_damage(self, amount)`, stores its
  return value, and prints that returned health.
  Open with the hook: this is the class's biggest program of the year, and the hero is the
  piece that will travel through every later milestone.
- **Lesson 2 — Milestone 2: build the world.**
  Goal: every student can explain the three flat dictionaries, follow a composite
  `"room direction"` exit key, and extend the world without changing its shape.
  Have partners trace a short journey on paper before adding one new room.
- **Lesson 3 — Milestone 3: explore.**
  Goal: every student has a playable loop that moves through valid exits, handles a missing
  exit, collects items, retrieves and uses one inventory item by list index, and always
  offers a quit branch.
  Pair-test each map by trying both a valid direction and a direction that cannot work.
- **Lesson 4 — Milestone 4: save and load.**
  Goal: every student writes the fixed one-value-per-line layout, reads it back, restores
  the saved types, and confirms that name, health, and inventory match.
  Close with **Milestone 5: Assemble the Grand Adventure**: students run the same hero and
  state through the world, exploration, quit, save, and load path without manually replacing
  values between scaffolds. End with a showcase in which students close and reload their
  adventures.

## Common mistakes

- Forgetting `self` in the initializer or when assigning a hero attribute.
- Defining `take_damage` outside `Hero`, forgetting its `amount` parameter, or changing
  health without returning the new value.
- Building a missing exit key and reaching the "can't go that way" branch — or causing a
  `KeyError` when the program looks up that key without checking first.
- Forgetting `.strip()` before comparing a loaded string or converting health to an integer.
- Writing an infinite exploration loop with no quit branch.
- Typing an attribute name differently in two places, such as a typo in the inventory name.
- Replacing the Milestone 1 hero with a new `Hero` later instead of preserving its state.
- Appending to the inventory but never indexing it to retrieve and use an item.
- Changing the exit dictionary into a nested structure, which no longer matches the brief's
  flat composite-key world.

## Discussion prompts

- Why does one composite `"room direction"` key identify an exit? What two facts does it
  combine?
- Which information belongs to the hero, and which belongs to the world dictionaries?
- Why does saved health need to be converted back to an integer after the file is read?
- What makes a world feel interesting even when it has only a few rooms?

## Differentiation

- Strugglers: keep the three-room world, provide a paper map with its valid directions, and
  ask them to trace `current` and the hero's inventory after each move.
- Middle tier: add one connected room and one item while preserving all three dictionary
  shapes, then improve the exploration messages.
- Fast finishers: add more rooms, a healing method on the existing `Hero` class, a score, or
  a seeded random trap event. Keep every extension inside the Year 1 concept set.

## Rubric

Total: **100 points**. Award full credit when every listed behavior for a milestone works;
award partial credit for a working portion that clearly contributes to that milestone.

1. **Milestone 1 — Hero (20 points):** one `Hero` class stores the hero's name, health, and
   inventory; the student authors and calls `take_damage(self, amount)`, which subtracts the
   amount and returns the new `self.health`; and the program displays the starting stats
   before that call, stores its return value, and displays the returned health.
2. **Milestone 2 — World (20 points):** the three flat dictionaries preserve the required
   shapes, composite exit keys work, and the starting room description is displayed.
3. **Milestone 3 — Exploration (20 points):** the loop moves through valid exits, reports an
   invalid direction, collects room items, retrieves and uses an inventory element with a
   student-authored list index, and has a reliable quit branch.
4. **Milestone 4 — Save and load (20 points):** the fixed line layout is written and read in
   separate file blocks, loaded values have the right types, and all restored values match.
5. **Milestone 5 — Assemble the Grand Adventure (20 points):** the four scaffolds form one
   coherent program in which the hero created in Milestone 1 is never re-instantiated and
   its state flows through world setup, exploration, item collection, the method and
   list-index requirements, quitting, saving, and loading; the full path runs without
   manually replacing values between milestones.

Traceback readiness is resolved upstream; do not re-derive or separately deduct it in this
project rubric.

Do not award credit for replacing a milestone with untaught tools such as `.split()`, sets,
comprehensions, or a second class, even if the student's version runs. Help the student
rework that part with the Year 1 tools the project is meant to demonstrate.

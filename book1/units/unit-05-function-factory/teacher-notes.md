# Teacher Notes — Unit 05: Function Factory

## Goals

Students leave able to define a function with `def`, pass information in through parameters,
hand a value back with `return`, and reason about what a name means inside vs outside a
function (scope).
Success looks like: every student writes a function they call more than once — a greeting
card for any name, a turtle stamp repeated in a loop — and can explain why a function beats
copy-paste.

## Pacing

Budget: three lessons of 60–90 minutes. This is Term 2's capstone concept — functions are
the year's biggest idea, so it gets three lessons and a gentle plain-Python-first ramp. Each
concept is a short **worked-example ladder** (simplest first, then one step up, with a *Notice*
per rung); the lesson-count is advisory. Executable rungs are PLAIN PYTHON (they run in the
notebook); the turtle programs stay as fenced ```python excerpts + runnable `assets/`, framed
as the "put it together" application, and the `NameError` scope bug is `no-exec`.

- **Lesson 1 — def-function, parameters (60–90 min). FUNCTIONS FIRST IN PLAIN PYTHON.**
  Open on the project thread: a card FACTORY — the same card for the whole class without
  retyping. Teach functions in plain text output FIRST (no turtle), so the idea lands without
  window management.
  20 min: the `def` ladder — define a NO-parameter `blank_card()` and call it (defining ≠
  running; the call prints), then call it several times (define once, call many).
  20 min: the `parameters` ladder — one blank (`greeting_card(name)`), then two blanks
  (`name, message`); call each for classmates. (Kept separate from `def` so the function idea
  lands before a blank is added.)
  25 min: THEN apply it to turtle — `stamp` is a user-defined function called in a loop that
  sets each stamp's size (fenced excerpt + `assets/l1_cards.py`, run from the terminal).
  60-MINUTE CUT: cut the turtle-stamp application (it returns in exercises); the plain
  `def`/parameter core is non-negotiable. Differentiation protects the turtle part, never
  the core.
- **Lesson 2 — return-value (60–90 min).**
  Open on the thread: some machines hand you something BACK.
  25 min: `return` vs printing — `area(w, h)` returns a number you can USE (in a message,
  in more math); print just shows it and is gone. This is the year's most important
  functions distinction — spend the time.
  20 min: a `polygon_points(n)` helper returns `360 / n` (arithmetic + float-type) used by
  the drawing script assets/l2_shapes.py.
  Rest: return exercises.
- **Lesson 3 — scope (60–90 min).**
  Open on the thread: why doesn't a name from inside the factory leak out?
  25 min: local vs global — trace what's visible where; a DELIBERATE scope bug (using a
  local name outside → NameError) and read the traceback together.
  20 min: a nested-loops stamp pattern (assets/l3_stamps.py) where each function call is
  self-contained.
  Rest: scope-trace exercises; the stamp gallery.

Practices reappearance: range-function + loop-counter drive the L1 stamp loop; arithmetic
+ float-type live in L2's `360/n`; nested-loops is L3's pattern. All reappear in project 01.

## Common mistakes

- `print` inside a function when `return` was needed — the value is shown but can't be used
  again (the L2 core distinction; expect it and re-teach on the spot).
- Forgetting the parameter, or calling `greeting_card()` with no argument (TypeError — a
  planned traceback moment).
- Expecting a name defined inside a function to exist outside it (NameError — the L3 bug).
- Calling a function before it's defined (define at top, call below).
- Turtle scripts using `turtle.write`/`goto` — the classroom fake-turtle check only knows
  pen-movement commands; keep cards drawn with strokes.

## Discussion prompts

- Where have you seen a "machine you build once, use many times" outside code?
- `return` vs `print`: when do you need the value back, and when is showing it enough?
- Why might a function keep its own names private? What would break if every name were global?

## Differentiation

- Strugglers: give the L1 card function as a fill-in-the-parameter skeleton; the plain-text
  version is a complete lesson on its own — the turtle stamp is a bonus, not a requirement.
- Fast finishers: the Challenge exercises — a two-parameter name-badge function and a flower
  stamp that calls a petal function inside a loop.
- Middle tier: the design-a-stamp exercise before the Challenges.

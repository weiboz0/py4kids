# Teacher Notes — Unit 07: Functions

## Goals

Students leave able to define a function with `def`, pass it `parameters`, `return` a value the caller uses,
and reason about `scope` (a parameter and the names in a function body are local).
They also meet Python's built-in number tools (`max`, `min`, `sum`, `abs`, `round`) as named shortcuts for
loops they can already write by hand.
Success looks like: every student writes a function that returns a value, calls it on several inputs, and can
explain why a function that only `print`s cannot be used in `total = f(3) + 1`.
This is the unit that turns "a script that runs once" into "a tool you call again and again," and it is the
prerequisite for everything after it (Unit 08 packages every simulation as a function).

## Pacing

Budget: three lessons of 60–90 minutes.

- **Lesson 1 — Define & Call (`def-function`, `parameters`, `return-value`).** The new first rungs are
  functions that only print: `def greet():` and a call (one idea), then `def greet(name):` (a
  parameter). Then build a reusable temperature-converter tool and call it on several temperatures (the payoff: one definition, many uses).
  Then small one-job tools. Close with the **"printing is not returning"** Notice: a function that only
  `print`s returns `None`, so `total = f(3) + 1` raises `TypeError: unsupported operand type(s) for +:
  'NoneType' and 'int'` — read the error together and fix it with `return`. This is the year's most important
  idea about functions; give it time. A `no-exec` real-input cell reads a Celsius value and prints
  `celsius_to_f(celsius)`.
- **Lesson 2 — Functions that Compute.** A new rung first: **leave early with `return`**
  (`first_multiple(start, k)` returns the moment it finds a match). Then `is_prime(n)` (plus a `no-exec`
  cell that reads a number and tests it), `gcd(a, b)` (Euclid's `while`), `fib(n)` (carry two
  values with a **temp variable** — `nxt = a + b; a = b; b = nxt`, never the untaught `a, b = b, a + b`),
  and a hand-written running total contrasted with `sum(range(1, n + 1))`; then **composition** — one of
  your functions calling another (`sum_of_squares(n)` calls `square(x)`); then `max`/`min`/`abs`/`round`,
  **`len` on a string** (`len("banner")` → 6 — lists come in Unit 10), and a **default parameter**
  (`def rule(n, symbol="-"):`).
- **Lesson 3 — Scope.** A parameter and the names created in a function body are local; a function returns a
  result rather than reaching out to a caller's variables. The polygon tool `draw_polygon(n, side)` is the
  application — `n`, `side`, and `angle = 360 / n` are local names inside the function (this is the turtle
  practice site, run as `assets/*.py` from the terminal). The lesson ends with a `no-exec` cell that reads a
  Celsius value and prints `safe_temperature(celsius)`.

**60-minute cut (Lesson 2 is the densest):** defer `gcd` (Euclid, the least intuitive — cp03 does not need
it; core Ex 10 Least Common Multiple and Challenge 29 do, so a deferred `gcd` moves Ex 10 to homework
with the lesson cell as its reference), and move the `round(2.5) == 2` banker's-rounding tie rule to a
discussion prompt / fast-finisher aside; keep `is_prime`, `fib`, `sum_to_n`, and the core built-ins.

## Exercises — core vs. More Practice vs. challenge

32 exercises, all in the **function form** — "define `f(...)` meeting this spec" with worked sample calls;
each solution asserts several distinct input cases.

- **Core (1–10):** Garden Border, **Repair the Ride-Cost Tool** (print vs. return), Exact-Multiple Test,
  Score Span (`max`/`min`), Total through an Endpoint, Fibonacci Signal, **Turtle Polygon Tool** (run it in
  the terminal), plus **Triangle Picture** (8: `draw_triangle(3)` returns `"*\n**\n***"`), **Name
  Banner** (9: `banner("Hi")` → a 6-wide `*` frame, width `len(text) + 4`) and **Least Common Multiple**
  (10: `lcm(4, 6)` → 12 by calling `gcd`).
- **More Practice (11–28)**, grouped by genre:
  - *Number theory & composition:* Digital Root (9875 → 2, calling `digit_sum`), Primes Below (100 → 25,
    calling `is_prime`), Roman Numeral (38 → `XXXVIII`, 14 → `XIV`), Rounded Fahrenheit (21 → 70).
  - *Calendar & time:* Days in a Month (February 2000 → 29, 2100 → 28; calls `is_leap`), Weekday Name
    (0 = Sunday; `day_of_week(15, 3)` → 3).
  - *Built-ins & defaults:* Bar with a Default (`bar(5)`, `bar(3, "=")`), Distance Apart (`abs`), Clamp a
    Score (`min(max(score, 0), 100)`).
  - *Scope, debug & predict:* Fix the Scope Bug (`NameError`), Fix the Missing Argument (`TypeError: area()
    missing 1 required positional argument: 'height'`), Fix the Call Before Define (`NameError`), Shadowed
    Parameter (`6 10`), Fresh Locals (`1 1`), Predict the Scope (`5`), Two Totals (`6 100`).
  - *Turtle:* Star Function (`draw_star(80)`), Polygon Row (three hexagons, travel 70, back 210).
- **Challenges (29–32, `stretch`):** Euclid's GCD Tool, Prime Gate, **Month Calendar**
  (`month_calendar(30, 3)` — a whole month grid built as one string), **Longest Collatz** (below 20 → 18).

**Real versions.** Every exercise has a real program except the repairs (2, and the three Fix exercises),
the predict/trace exercises (Shadowed Parameter, Fresh Locals, Predict the Scope) and the turtle exercises
(7, Star Function, Polygon Row — turtle drawings run as scripts). A real program defines the same
function, reads its arguments with bare `input()` (one per line), calls it and prints the result.

## Common mistakes

- Forgetting `return`, so the function prints but returns `None`; then the caller's `f(...) + 1` blows up
  with a `TypeError` — the print-vs-return trap.
- Confusing "the function shows the answer" with "the function gives back the answer the caller can use."
- **Jupyter trap that hides the print-vs-return difference:** a bare `ticket_cost(4)` on a cell's LAST line
  displays `12` whether the function `return`s or merely `print`s, so the two look identical in the output.
  During this lesson, test with `total = ticket_cost(4) + 2` (blows up if it only prints) or
  `x = ticket_cost(4); print(x)` (shows `None` if it only prints) — never let the bare call be the last line.
- Expecting a name created inside a function to be visible outside it (scope), or expecting a function to see
  the caller's loop variable.
- `is_prime`: forgetting that `n < 2` is not prime, or an off-by-one in the divisor range; `gcd`: a wrong
  `while` condition (loops forever or stops early).
- Reaching for tuple assignment (`a, b = b, a + b`) in `fib` — use a temp variable; multiple assignment is
  not taught yet.
- In the polygon tool: running from the wrong directory, or using `//` for the angle (use `360 / n`).
- Calling a function before its `def` has run (`NameError`), or with too few arguments (`TypeError` naming
  the missing parameter) — read the last line of the traceback.
- A default parameter must come after the parameters without defaults (`def bar(n, symbol="#")`).
- Assuming a function can change a caller's variable by assigning to a parameter of the same name — it
  makes a new local name (Shadowed Parameter).

## Discussion prompts

- When should a function `return` a value instead of `print`ing it? What can the caller do with a returned
  value that it cannot do with printed text?
- What does `gcd` count down toward, and how does the `while` loop know to stop?
- Why should the polygon tool take what it needs through `parameters` rather than relying on names from
  outside it? (`draw_polygon` does its work by drawing and returns `None` — its `angle`/`corner` names live
  only inside it, which is why `print(angle)` after the call raises a `NameError`.)
- When is a built-in like `sum` better than writing the loop, and when is the loop clearer?

## Differentiation

- Strugglers: keep to Core 1–5 (define/return, the repair, a boolean test, `max`/`min`, a running total);
  give the function header and have them fill only the body.
- Fast finishers: More Practice by genre (calendar and Roman numerals are favourites), then the
  Challenges (the Month Calendar is the capstone); then extend the polygon tool to draw a
  second polygon at a new size/colour.
- Middle tier: rewrite one Lesson-2 hand loop (e.g. the running total) as a call to the matching built-in and
  confirm identical results.

## Value plan (sample inputs)

- Exercise 1 — `rectangle_perimeter(width, height)`: `(8, 5)`, `(12, 3)`, `(7.5, 2)`.
- Exercise 2 — `ticket_cost(rides)`: `4`, `7`, `5` (the last call is used in `ticket_cost(5) + 2`).
- Exercise 3 — `is_multiple(number, divisor)`: `(42, 7)`, `(43, 7)`, `(18, 3)`.
- Exercise 4 — `score_span(a, b, c)`: `(4, 11, 7)`, `(9, 2, 13)`, `(6, 6, 6)`.
- Exercise 5 — `sum_to_n(n)`: `4`, `8`, `1`.
- Exercise 6 — `fib(n)`: `2`, `5`, `9`.
- Exercise 7 — `draw_polygon(n, side)`: `(6, 48)`.
- Exercise 29 — `gcd(a, b)`: `(54, 24)`, `(35, 15)`, `(81, 27)`.
- Exercise 30 — `is_prime(n)`: `17`, `21`, `2`.
- New exercises 10–32: fixtures as in the exercise statements (plan 082's tables), all grep-distinct from
  shipped Book 1b content.

## More Practice ideas (design 006 D9 genres)

- **Calendar & time:** `minutes_between(h1, m1, h2, m2)` for two clock times on the same day.
- **Sequences & bases:** `to_binary(n)` returning a string of 0s and 1s (reuse the Unit 04 loop inside a
  function).
- **ASCII art:** `draw_box(w, h)` returning a hollow box string.
- **Debug & repair:** hand out a function whose `return` sits inside its loop by mistake.

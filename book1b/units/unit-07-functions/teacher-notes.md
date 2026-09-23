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

- **Lesson 1 — Define & Call (`def-function`, `parameters`, `return-value`).** Build a reusable
  temperature-converter tool and call it on several temperatures (the payoff: one definition, many uses).
  Then small one-job tools. Close with the **"printing is not returning"** Notice: a function that only
  `print`s returns `None`, so `total = f(3) + 1` raises `TypeError: unsupported operand type(s) for +:
  'NoneType' and 'int'` — read the error together and fix it with `return`. This is the year's most important
  idea about functions; give it time.
- **Lesson 2 — Functions that Compute.** `is_prime(n)`, `gcd(a, b)` (Euclid's `while`), `fib(n)` (carry two
  values with a **temp variable** — `nxt = a + b; a = b; b = nxt`, never the untaught `a, b = b, a + b`),
  and a hand-written running total contrasted with `sum(range(1, n + 1))`; then `max`/`min`/`abs`/`round`.
- **Lesson 3 — Scope.** A parameter and the names created in a function body are local; a function returns a
  result rather than reaching out to a caller's variables. The polygon tool `draw_polygon(n, side)` is the
  application — `n`, `side`, and `angle = 360 / n` are local names inside the function (this is the turtle
  practice site, run as `assets/*.py` from the terminal).

**60-minute cut (Lesson 2 is the densest):** defer `gcd` (Euclid, the least intuitive — nothing in core or
cp03 needs it; it lives only in stretch Ex8), and move the `round(2.5) == 2` banker's-rounding tie rule to a
discussion prompt / fast-finisher aside; keep `is_prime`, `fib`, `sum_to_n`, and the core built-ins.

## Exercises — core vs. extra vs. challenge

Core (1–7): Garden Border (define + return a perimeter), **Repair the Ride-Cost Tool** (the print-vs-return
fix — the function must `return`, not `print`), Exact-Multiple Test (a boolean `%` function), Score Span
(`max`/`min` on arguments), Total through an Endpoint (`sum`/running total), Fibonacci Signal (temp-variable
`fib`), **Turtle Polygon Tool** (the `draw_polygon(n, side)` practice site — run it in the terminal).
Challenges (8–9, `stretch`): Euclid's GCD Tool; Prime Gate.
Every exercise is stated in the **function form** — "define `f(...)` meeting this spec" with worked sample
calls — and its solution asserts several distinct input cases. Turtle exercises are checked by running them,
not by asserts.

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
- Fast finishers: the two Challenges (Euclid's GCD, Prime Gate), then extend the polygon tool to draw a
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
- Exercise 8 — `gcd(a, b)`: `(54, 24)`, `(35, 15)`, `(81, 27)`.
- Exercise 9 — `is_prime(n)`: `17`, `21`, `2`.

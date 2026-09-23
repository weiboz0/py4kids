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

**60-minute cut (any lesson):** in Lesson 2, `gcd` (Euclid) is the least intuitive — make it the item to
defer or leave as a challenge; keep `is_prime`, `sum_to_n`, and the built-ins.

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
- Why can't the polygon tool see a variable you made outside it? What does it give back instead?
- When is a built-in like `sum` better than writing the loop, and when is the loop clearer?

## Differentiation

- Strugglers: keep to Core 1–5 (define/return, the repair, a boolean test, `max`/`min`, a running total);
  give the function header and have them fill only the body.
- Fast finishers: the two Challenges (Euclid's GCD, Prime Gate), then extend the polygon tool to draw a
  second polygon at a new size/colour.
- Middle tier: rewrite one Lesson-2 hand loop (e.g. the running total) as a call to the matching built-in and
  confirm identical results.

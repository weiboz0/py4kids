# Teacher Notes — Unit 05: For & Range

## Goals

Students leave able to write a counting loop with `for` over `range`, read `range(n)` (from 0) and
`range(a, b)` (stop value excluded), reuse the accumulator/counting techniques from Unit 04 over a range,
and stack one loop inside another (nested loops) to build tables and triangles. Success looks like: every
student replaces a hand-written `while` counter with a `for`/`range` loop and builds a small grid with a
nested loop. `for i in range(n)` is introduced as a **named shorthand** for the manual `while` counter
students already built in Unit 04.

## Pacing

Budget: three lessons of 60–90 minutes; ladders with a *Notice* per rung.

- **Lesson 1 — Visit a Range (`for`, `range`).** Reproduce Unit 04's 5050 sum as
  `for n in range(1, 101): total = total + n` — same result, less typing (the motivation for `range`).
  Teach `range(n)` and `range(a, b)` with the Notice **"the stop value is not included"**; contrast with a
  bound-sensitive example.
- **Lesson 2 — Calculate across a Range.** Running total and count-by-condition over a range → **FizzBuzz**
  (an `elif` ladder inside a `for`) → **primality LAST** (a boolean flag `is_prime`, `break`, spec `n ≥ 2`,
  and the Notice that `range(2, 2)` is empty so `n == 2` stays prime). Primality is the natural 60-MINUTE
  CUT casualty.
- **Lesson 3 — Put One Loop inside Another (`nested-loops`).** Build a times table / number triangle by
  accumulating each `row` string in the inner loop and `print(row)` once (Notice on the 8-space inner body
  and the dedent trap; use `row`/`col`, not `i`/`j`; `break` exits only the inner loop). Then a
  nested-classify exercise (`if` inside `if` inside the `for`). Final build.

60-MINUTE CUT (any lesson): teach rungs 1–2 live and leave the last as a "try it"; primality can wait.

## Exercises — core vs. extra vs. challenge

Core (1–7): The 5050 Total, Stop-Bound Inspector (range bounds), Divisible-by-Four Census, FizzBuzz Board
(elif), Prime-Flag Test (primality), Four-by-Four Times Table (nested), Nested Classification Count
(`conditional-nesting`). Extra (8–9): Growing Signal Triangle, Factorial over a Range. Challenges (10–11):
Step-Range Total, Count the Primes. No core exercise depends on a Challenge. Pre-function; `x = x + 1` only;
same-line/tabular output via string accumulation (no `end=`/`sep=`/format specs, no `"*" * i` in core).

## Common mistakes

- `range` bounds: `range(1, 5)` gives 1–4, not 1–5 — the stop value is excluded.
- Nested-loop indentation: the inner body is 8 spaces; `print(row)` belongs at 4 (after the inner loop).
- Primality flag: forgetting to `break`, or a wrong upper bound; `range(2, 2)` is empty so `2` stays prime.
- FizzBuzz `elif` order: test `% 15` (or `% 3 and % 5`) before `% 3`/`% 5`.
- Rebinding the `for` variable inside its body, or expecting `range` to include the stop value.

## Discussion prompts

- How is `for i in range(n)` the same as the Unit 04 `while` counter? How is it shorter?
- Why does `range(1, 5)` stop at 4?
- In a times table, which loop is the row and which is the column?
- What does the `is_prime` flag remember, and when do you set it to `False`?

## Differentiation

- Strugglers: give the outer loop and have them write only the inner loop / the `row` accumulation.
- Fast finishers: Extra (8–9), then the Challenges (10–11).
- Middle tier: rewrite a `while` counter from Unit 04 as a `for`/`range` loop and confirm identical output.

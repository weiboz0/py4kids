# Teacher Notes — Checkpoint 03: Functions & Randomness

## Goals

A short mixed assessment proving Units 01–08, with the load on functions (`def`, parameters, `return`,
scope, built-in number tools) and the `random` module.
It introduces nothing new and assesses only what has been taught.
Students work solo; it is solution-free like a unit's exercises, and every question is in the **function
form** — define a function to a spec, then it is checked by calling it on fixed inputs.

The checkpoint stays otherwise strict: **no lists, no dictionaries, no strings-as-sequences, no files, no
classes**, and built-ins limited to `print`/`int`/`float`/`str` plus the Unit-07 number set
(`max`/`min`/`sum`/`abs`/`round`) — no `len`/`sorted`. Text is joined with f-strings (no `+`), and no boolean
operators (`and`/`or`) are needed.

## Pacing

Budget: half a lesson (~30–45 minutes). Hand out after Unit 08. The seven questions and their targets:
1. **Prime Test** — define `is_prime(n)`, return a boolean (U07). *Pass-bar (define-and-return).*
2. **Parameterized Travel Cost** — a function of two parameters using local names (U07 parameters + scope).
3. **Running-Total Function** — a `for`/`range` accumulator inside a function (U05/U07).
4. **Count Primes** — count how many of `1..n` are prime (count-by-condition, calls `is_prime`).
5. **Award Ladder** — an `if`/`elif`/`else` ladder inside a function (U03 recap).
6. **Number-Tool Score** — use `max`/`min`/`sum`/`abs`/`round` on numbers (U07 built-ins).
7. **Seeded High-Roll Count** — `import random` + `random.seed(4)` then count rolls over a threshold (U08).
   *The statement tells the student to seed with 4 first so the answer is reproducible.*

## Common mistakes

- A function that `print`s instead of `return`ing, so the caller cannot use its value.
- Q1/Q4: treating `n < 2` as prime, or an off-by-one in the divisor or count range.
- Q7: forgetting `random.seed(4)` (or seeding after the first roll), so the count does not match the key.
- `random.randint(a, b)` includes both ends; miscounting the threshold in Q7.
- Reaching for a list, `len`, `sorted`, `+` string-concatenation, or `and`/`or` — none are needed and all are
  out of scope for this checkpoint.

## Discussion prompts

- Which questions define a function that must `return` a value, and which one *calls* another function to do
  its job (Q4 calls `is_prime`)? What breaks if `is_prime` prints instead of returns?
- In Q7, why does `random.seed(4)` make the answer checkable? What would the grader see without it?
- Where does a local name in Q2's travel-cost function live, and why can't the rest of the program see it?

## Grading

Pass = at least 5 of 7 correct, with **Q1 (define-and-return)** and one *call-and-use-the-result* question
(**Q4**, which must call the `is_prime` it relies on) among them — those are the load-bearing function skills.
Key each question to its concept(s) above. Full marks require the exact returned values for the fixed inputs
(and, for Q7, the seed-4 result). Partial credit: award a function whose logic is right but whose return type
is wrong (e.g. prints instead of returns) at half, noting the fix.

## Differentiation

- Strugglers: prioritize Q1–Q3 and Q5 — a boolean function, a two-parameter formula, a running total, and
  the `elif` ladder; treat Q4/Q6/Q7 as reach.
- Fast finishers: after Q7, ask them to re-run it with a different seed and explain why the count changes but
  the method does not.

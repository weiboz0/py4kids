# Teacher Notes — Unit 04: Loops & Counting

## Goals

Students leave able to repeat work with a `while` loop, drive it with a counter
(`i = 0; while i < n: … ; i = i + 1`), accumulate a running total or a count
(`total = total + n`, `count = count + 1`), stop early or at a computed goal
(`break`, sentinel loops), and read the tracebacks/off-by-one bugs loops invite. The three technique ideas
land as plain concepts: **running-total**, **count-by-condition**, and **sentinel-loop** ("repeat until a
computed stop value"). Success looks like: every student writes a loop that counts or accumulates and can
explain why it stops. This is the first unit where the **accumulator idiom `x = x + …` is student-authored**
(it was previewed once, read-only, in Unit 02's boxed 5050 example — now they write it).

## Pacing

Budget: three lessons of 60–90 minutes; worked-example ladders with a *Notice* per rung.

- **Lesson 1 — Repeat and Keep Count (`while`, `loop-counter`).** Open on a real repetition problem. Teach
  the **reassignment rung first** (`count = 0; count = count + 1; print(count)`, Notice: "the right side is
  computed with the OLD value, then saved"). Then the counter loop. Two deliberate beats: (a) the
  **infinite-loop** cell (a `no-exec` cell that forgot `i = i + 1`) — Notice on why it never stops and **how
  to stop it: Kernel → Interrupt (or Ctrl-C)**; (b) an **off-by-one** repair (`while i < 5` prints 0–4 vs
  `while i <= 5` prints 0–5) and a `NameError` traceback beat (using `total` before `total = 0`).
- **Lesson 2 — Accumulate Totals and Counts (`accumulator`, running-total, count-by-condition).** Point back
  to Unit 02's 5050 peek ("you saw this — now you write it"). Build a running total, then count how many
  values pass a test (elif tiers).
- **Lesson 3 — Stop at a Computed Goal (`break`, `sentinel-loop`).** Plain-condition sentinel first
  (`while n != 1` — Collatz steps), THEN `while True: … break` as the exit-from-the-middle shape. The loop
  is controlled by `n` / the `break` condition; the `steps` counter counts the passes and supplies the
  printed summary (`Steps: N`). Final build. (Digit-peel `while n != 0` is taught in Lesson 2.)

60-MINUTE CUT: L1 — keep the reassignment rung, the counter loop, and the infinite-loop/off-by-one beats
live; run the `NameError` beat as a "try it". L2 — cut the digit-sum rung. L3 — cut the GCD extra.

## Exercises — core vs. extra vs. challenge

Core (1–7): Training-Lap Counter, Repair the Last Number (off-by-one), Fundraiser Running Total,
Multiples-of-Four Count, Factorial Machine, Digit-Sum Scanner, Computed Stop: Collatz Steps (sentinel).
Extra (8–9): Shared-Tile Size (GCD-by-subtraction), Score-Tier Census. Challenges (10–11): Remainder GCD,
Probe Mission 19. No core exercise depends on a Challenge. Pre-function; `x = x + 1` only (never `+=`);
`while`-only (no `for`/`range` yet). `input()` only via a fenced try-it, never in graded code.

## Common mistakes

- Infinite loop from forgetting to advance the counter/condition — know how to interrupt the kernel.
- Off-by-one: `<` vs `<=` in the `while` condition; count the trips on paper.
- Forgetting to initialize before the loop (`total = 0`, `count = 0`) → `NameError` or a wrong total.
- Factorial initialized to `0` instead of `1` (silently prints 0) — a `product = 1` Notice.
- Reassignment confusion: `count = count + 1` reads the OLD value first, then saves the new one.

## Discussion prompts

- When do you use a `while` loop instead of many `if`s?
- What is the difference between a running total and a count?
- A sentinel loop stops when a value appears — how is that different from counting to `n`?
- How can you tell, before running, whether a loop will ever stop?

## Differentiation

- Strugglers: give the loop skeleton (`i = 0`, the `while` header) and have them fill the body + the advance.
- Fast finishers: Extra (8–9), then the Challenges (10–11).
- Middle tier: convert a counter loop into a running-total loop and predict the output.

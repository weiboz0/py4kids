# Teacher Notes — Unit 04: Loops & Counting

## Goals

Students leave able to repeat work with a `while` loop, drive it with a counter
(`i = 0; while i < n: … ; i = i + 1`), accumulate a running total or a count
(`total = total + n`, or the shorthand `total += n`), peel the digits of a number, remember a best-so-far
value, stop early or at a computed goal (`break`, sentinel loops), and read the tracebacks and off-by-one
bugs loops invite. The three technique ideas land as plain concepts: **running-total**,
**count-by-condition**, and **sentinel-loop** ("repeat until a computed stop value").
Success looks like: every student writes a loop that counts or accumulates, can explain why it stops, and
runs a real program that keeps reading numbers until a `0` arrives.
This is the first unit where the **accumulator idiom `x = x + …` is student-authored**
(it was previewed once, read-only, in Unit 02's boxed 5050 example — now they write it).

## Pacing

Budget: three lessons of 60–90 minutes; worked-example ladders, one new idea per code cell, a *Notice* per
rung.

- **Lesson 1 — Repeat and Keep Count (`while`, `loop-counter`).** Open on a real repetition problem. Teach
  the **reassignment rung first** (`count = 0; count = count + 1; print(count)`, Notice: "the right side is
  computed with the OLD value, then saved"). Then the counter loop. Two deliberate beats: (a) the
  **infinite-loop** cell (a `no-exec` cell that forgot `i = i + 1`) — Notice on why it never stops and **how
  to stop it: Kernel → Interrupt (or Ctrl-C)**; (b) an **off-by-one** repair (`while i < 5` prints 0–4 vs
  `while i <= 5` prints 0–5) and a `NameError` traceback beat (using `total` before `total = 0`).
  A `no-exec` real-input cell reads a starting number and counts down from it.
- **Lesson 2 — Accumulate Totals and Counts (`accumulator`, running-total, count-by-condition).** Point back
  to Unit 02's 5050 peek ("you saw this — now you write it"). Build a running total, then the new
  **`+=` rung** (`total += number` is shorthand for `total = total + number` — either form is accepted
  from here on). Count how many values pass a test (elif tiers). The digit tools now climb in three rungs:
  **count the digits** (`4827` → 4), then the digit sum, then **best-so-far** (largest digit of 4827:
  `if d > best: best = d`). A `no-exec` cell reads numbers until 0 and prints their total — written with a
  plain condition (`while number != 0:`, reading again at the end of the body), because `break` comes in
  Lesson 3.
- **Lesson 3 — Stop at a Computed Goal (`break`, `sentinel-loop`).** `break` now arrives in two steps: first
  inside an ordinary `while n <= 100:` loop (leave early when a goal is met), then the `while True: … break`
  exit-from-the-middle shape. The final build is a plain `while n != 1:` Collatz loop; the `steps` counter
  counts the passes and supplies the printed summary (`Steps: N`). A `no-exec` cell reads `n` and prints
  its Collatz steps, and another lets a human play the guessing game against the computer's secret.

60-MINUTE CUT: L1 — keep the reassignment rung, the counter loop, and the infinite-loop/off-by-one beats
live; run the `NameError` beat as a "try it". L2 — teach `+=` and the digit count live; leave the
largest-digit rung as a "try it". L3 — teach `break` in the ordinary loop live; the `while True:` rung and
the guessing-game cell are good self-serve rungs.

## Exercises — core vs. More Practice vs. challenge

34 exercises. Pre-function form; `while` only (no `for`/`range` yet); `x = x + 1` or `x += 1`.

- **Core (1–12)** — the in-class path: Training-Lap Counter, Repair the Last Number (off-by-one),
  Fundraiser Running Total, Multiples-of-Four Count, Factorial Machine, Digit-Sum Scanner, Computed Stop:
  Collatz Steps (sentinel), Shared-Tile Size (GCD by subtraction), Score-Tier Census, plus the new
  **Countdown Liftoff** (10: `5 4 3 2 1 Liftoff!`), **Count the Digits** (11: 90210 → `Digits: 5`) and
  **Reverse a Number** (12: 3721 → `Reversed: 1273`). Exercises 10–12 require a purpose comment.
- **More Practice (13–29)** — homework / fast finishers, grouped by genre:
  - *Digit tricks:* Palindrome Number (12321 — save the original first), Sum of Even Digits (482615 →
    `Even digits: 4` / `Even-digit sum: 20`), Count the Odd Digits (73185 → 4), Largest Digit (58193 → 9),
    Lucky Sevens (707172 → 3).
  - *Stop at a goal:* Doubling Past a Limit (5 → `640 after 7 doublings`, `while True` + `break`), First
    Square Over 300 (`18 squared is 324`, `break` inside an ordinary loop).
  - *Sequences & bases:* Savings Streak (`Week 8 total: 220`), Triangular Numbers
    (`1 3 6 10 15 21 28 36 45`), Decimal to Binary (37 → `100101`, prepending `str(n % 2)`).
  - *Games:* Guessing Robot (secret 42, always guesses the middle → `Guesses: 50 25 37 43 40 41 42` /
    `Found 42 in 7 guesses`).
  - *ASCII art:* Loop-Built Star Bar (`Stars: *******`), Countdown Bars (`4 ####` … `1 #`).
  - *Debug & repair:* Fix the Infinite Loop, Fix the Missing Starting Value (`NameError`), Fix the
    Missing Colon (`SyntaxError: expected ':'`), Fix the Unindented Body (`IndentationError`).
- **Challenges (30–34)** — optional: Remainder GCD, Probe Mission 19, Collatz Peak (15 → `Peak: 160`),
  Powers of Two (`2^0 = 1` … `2^7 = 128`, `Total: 255`), Count the Steps (GCD of 270 and 192 both ways →
  10 subtraction steps vs 4 remainder steps — a first look at efficiency).

No core exercise depends on a More Practice or Challenge exercise.

**Real versions.** Every exercise except the five repairs (2 and 20–23) has a Real version. U04's real programs are
**sentinel loops** — the unit's own concept: Fundraiser Running Total and Score-Tier Census keep reading
numbers until a `0` line (`while True:` + `break`); the others read their starting value(s) one per line.
The Guessing Robot's real program reads the secret and prints the same transcript. Graded solution cells
never call `input()`; run one or two real programs live by typing the sample input.

## Common mistakes

- Infinite loop from forgetting to advance the counter/condition — know how to interrupt the kernel.
- Off-by-one: `<` vs `<=` in the `while` condition; count the trips on paper.
- Forgetting to initialize before the loop (`total = 0`, `count = 0`) → `NameError` or a wrong total.
- Factorial initialized to `0` instead of `1` (silently prints 0) — a `product = 1` Notice.
- Reassignment confusion: `count = count + 1` reads the OLD value first, then saves the new one.
- Peeling digits destroys the number — Palindrome Number and Reverse a Number must save `original` first.
- Missing colon or unindented body after `while` — read the `SyntaxError`/`IndentationError` line.
- A sentinel real program that adds the final `0` or counts it as a value — test the stop value first.

## Discussion prompts

- When do you use a `while` loop instead of many `if`s?
- What is the difference between a running total and a count?
- A sentinel loop stops when a value appears — how is that different from counting to `n`?
- How can you tell, before running, whether a loop will ever stop?
- Count the Steps: both methods find the same GCD — why does one need fewer steps?

## Differentiation

- Strugglers: give the loop skeleton (`i = 0`, the `while` header) and have them fill the body and the
  advance; Countdown Liftoff and Count the Digits are short.
- Fast finishers: the More Practice genres (digit tricks, then games and bases), then the Challenges; type
  in the Fundraiser real program and feed it their own numbers ending in `0`.
- Middle tier: convert a counter loop into a running-total loop and predict the output; rewrite one
  `x = x + 1` line as `x += 1` and confirm nothing changes.

## More Practice ideas (design 006 D9 genres)

- **Sequences:** print the Fibonacci numbers below 100 with two running variables.
- **Number theory:** count how many times 2 divides a number (`while n % 2 == 0`).
- **Games:** a "Nim countdown" where two fixed moves alternate until the pile reaches 0.
- **Tracing & efficiency:** predict how many passes `while n > 1: n = n // 2` makes for 64, then 100.

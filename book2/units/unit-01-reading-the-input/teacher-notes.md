# Teacher Notes — Book 2 Unit 01: Reading the Input

## Goals

Students learn the Book-2 judge contract: `solve(data)` receives the whole problem input as
one string, parses everything inside the function, and returns the exact output string.
The function does not ask the user for input and does not print its answer.
At submission time, a small wrapper imports `sys`, reads all standard input, passes that text
to `solve`, and prints the returned string.
Students should leave able to use `.split()` for whitespace-separated tokens, convert number
tokens with `int()`, read `N` followed by `N` values, rebuild an `R` by `C` grid as a list of
lists, and construct space-separated output with f-strings or a loop.

The intended complexity for every exercise is linear in the amount of input it processes:

- Exercise 1, sum and maximum: **O(N)** time.
- Exercise 2, values greater than a threshold: **O(N)** time.
- Exercise 3, per-line sums: **O(N)** time, where `N` is the total number of values across all
  `K` lists.
- Exercise 4, target presence and first position: **O(N)** time with a manual loop scan.
- Exercise 5, grid row sums: **O(R*C)** time.
- Exercise 6, grid column sums: **O(R*C)** time.
- Exercise 7, doubled values: **O(N)** time.
- Exercise 8, chosen name: **O(N)** time to read the `K` names.
- Exercise 9, grid border sum: **O(R*C)** time using the same full-grid reading pattern as the
  other grid exercises.

## Pacing

Budget: one 60–90 minute lesson.

- **Hook and contract (10 min).**
  Put the running sample on the board as raw text.
  Ask what the judge gives our program and what exact text it expects back.
  Introduce `solve(data)` as the boundary used throughout Book 2.
- **Tokens and integers (15 min).**
  Run the `.split()` and `int()` demonstrations.
  Have students predict the token list, then emphasize that number-looking tokens are still
  strings until converted.
- **N values and the running solution (15 min).**
  Trace token positions for `N` followed by `N` integers.
  Build the sum-and-maximum solver and check its exact returned string.
- **Grid reading (15 min).**
  Draw a 2-by-3 grid and track the token-position counter while building each inner row list.
  Connect this representation directly to Exercises 5, 6, and 9.
- **Exact output (10 min).**
  Contrast a fixed f-string with loop-built output for a variable-length list.
  Point out where spaces are added and why there is no extra space at the beginning.
- **Independent practice (15–25 min).**
  Start everyone on Exercises 1 and 2, then route students through 3–7.
  Exercises 8 and 9 are stretch work.
  60-MINUTE CUT: demonstrate only the first grid row together and assign Exercises 5–9 for a
  later practice block.

## Common mistakes

- Off-by-one errors when reading `N`: token 0 holds `N`, so the `N` values begin at token 1,
  and a loop over `range(n)` reads each value from `position + 1`.
- Forgetting to call `int()` on parsed tokens, leaving values as strings and causing text-like
  behavior or failed numeric comparisons.
- Worrying that trailing whitespace or a final newline must be removed first.
  Plain `.split()` already ignores surrounding whitespace.
- Mishandling blank or empty lines by expecting them to become meaningful tokens.
  Whitespace splitting skips blank lines, so parsing should follow the promised counts rather
  than physical empty lines.
- Reaching for untaught shortcuts such as `.join()` to build output or `.index()` to find a
  target.
  Use string concatenation in a loop for output and a manual loop scan for a position.
- Printing inside `solve` instead of returning a string, or returning a number instead of the
  exact requested output text.

## Discussion prompts

- Why is the entire input delivered as one string instead of one question at a time?
- What information do `N`, `R`, and `C` give us before we read the values that follow?
- How can one `.split()` handle both spaces and newlines?
- Why might `"9"` and `9` look similar to a person but behave differently in Python?
- What tiny output differences could make a correct idea fail an exact judge?

## Differentiation

- Strugglers: provide a printed token-position table for the running example and let students
  annotate which token becomes `N` and which tokens become values.
- Grid support: use sticky notes or index cards for tokens, then arrange each group of `C`
  cards into an inner row list before adding it to the grid.
- Middle tier: complete Exercises 1–4, then choose either row sums or column sums before moving
  to Exercise 7.
- Fast finishers: complete both stretch exercises and explain aloud how their loop avoids
  double-counting grid corners.
- Pair check: one student reads the input contract and sample while the other traces the token
  counter; switch roles before writing code.

# Teacher Notes — Book 2 Unit 02: Boolean Logic & Algebra

## Goals

Students learn to turn gate checks and contest rules into precise Boolean expressions.
Students should leave able to build and read truth tables, trace `and`/`or`/`not` expressions using Python's precedence, verify both De Morgan transformations, explain short-circuit evaluation, and simplify a Boolean expression without changing its result.
The recurring predict-then-run warm-ups make code tracing an explicit habit rather than an occasional quiz.
Every solver follows the Book-2 contract: `solve(data)` receives the whole input string, parses inside the function, and returns exact output text.

For the complexity notes below, `N` means the total amount of input read, including a fixed small input when an exercise has only a few flags.

- Exercise 1, access gate: **O(N)** time and **O(N)** parsing space.
- Exercise 2, De Morgan demonstration: **O(N)** time and **O(N)** parsing space.
- Exercise 3, at least one signal: **O(N)** time and **O(N)** parsing space.
- Exercise 4, every check passed: **O(N)** time and **O(N)** parsing space.
- Exercise 5, majority with a dissenter: **O(N)** time and **O(N)** parsing space.
- Exercise 6, club vote: **O(N)** time and **O(N)** parsing space.
- Exercise 7, skip safe numbers: **O(N)** time and **O(N)** parsing space.
- Exercise 8, robot lab rule engine: **O(N)** time and **O(N)** parsing space.
- Exercise 9, truth-table row evaluator: **O(N)** time and **O(N)** parsing space.

## Pacing

Budget: two lessons of 60–90 minutes each.

- **Lesson 1 — truth tables, operators, and De Morgan's laws (60–90 min).**
  Open with a gate-checking scenario and build the four-row truth table together.
  Trace `not`, then `and`, then `or`, and use parentheses to compare alternate groupings.
  Run the first predict-then-run warm-up before checking both De Morgan laws across every truth-table row.
  Use Exercises 1–4 for independent practice with access rules, equivalence, at-least-one flags, and all-flags checks.
  **60-minute cut:** complete the truth table and De Morgan demonstration, solve Exercise 1 together, and assign Exercises 2–4 for the next practice block.
- **Lesson 2 — short-circuiting, simplification, and code tracing (60–90 min).**
  Run the side-effect demonstration and ask students to explain why two function calls never occur.
  Work through the gate-expression simplification one transformation at a time, then use the second predict-then-run warm-up.
  Review the worked majority solver before students tackle Exercises 5–7, with Exercises 8–9 reserved as stretch challenges.
  **60-minute cut:** keep the short-circuit demo and worked simplification, begin Exercise 5 in pairs, and assign Exercises 6–9 for a later practice block.

## Common mistakes

- Students may read `and` and `or` strictly from left to right even though `and` has higher precedence.
  Ask them to add parentheses around the group Python evaluates first.
- Students may move `not` through parentheses without flipping `and` to `or`, or flip the operator without applying `not` to both values.
  Rebuild the four-row truth table when a De Morgan sign-flip error appears.
- Students may reach for the untaught `all` or `any` builtins in Exercises 3 and 4.
  At this point they must use a manual `for` loop with a Boolean flag variable instead.
- Students may make an off-by-one error when `N` is given by looping over too few answers or reading token `position` instead of token `position + 1`.
  Exercise 3 deliberately places its decisive flag last so this mistake changes the sample result.
- Students may convert `SKIP` with `int()` before the short-circuit guard in Exercise 7.
  Have them trace the left side of `and` first and say whether the right side is safe to evaluate.
- Students may confuse a strict majority with half or more.
  The expression `yes_count * 2 > n` must be false for a tie.
- Students may print from inside `solve` or return a Boolean value instead of the requested exact text.
  Reconnect the decision result to the problem's required output word.

## Discussion prompts

- How does a truth table prove that two Boolean expressions agree in every possible case?
- Why does moving `not` inward change `and` to `or`, and vice versa?
- When can short-circuit evaluation prevent an error rather than merely save time?
- Which version of the gate rule is easier to explain: the original expression or its simplified form?
- How can a single last-position flag reveal an off-by-one loop bug?
- Why is a strict majority different when `N` is even and when `N` is odd?

## Differentiation

- Strugglers: give each pair four cards labeled with the possible `a` and `b` rows, then have them fill one result column at a time.
- Precedence support: let students draw small boxes around each operation in evaluation order before predicting output.
- De Morgan support: use the spoken pattern "flip the connector, flip both facts" and immediately verify it against a truth-table row.
- Loop support: provide a three-column trace sheet for position, current flag, and remembered Boolean state without supplying solver code.
- Middle tier: complete Exercises 1–7 and explain one solver's final combined condition to a partner.
- Fast finishers: complete Exercises 8–9, then invent one additional input row that makes each solver return its opposite sample result.
- Pair check: one student traces and predicts while the other runs the cell, then they switch roles for the next warm-up.

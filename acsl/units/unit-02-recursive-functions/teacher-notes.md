# Teacher Notes — Unit 02: Recursive Functions

## Goals

Students learn ACSL's second Contest 1 category.
By the end they can:

- read a recursive definition in ACSL's "cases" notation and tell the base case from the recursive case;
- evaluate it by hand with the **call table**: go down to the base case (pass 1), then substitute values back up (pass 2);
- handle conditions that use `mod`, `abs` and the floor of a division (ACSL `int(x/2)`), including negative arguments;
- evaluate functions of two variables, **multiple recursion** (`f(x−1) + 2·f(x−2)`, built bottom-up in a table) and, at Intermediate and above, **indirect recursion** (f calls g calls f);
- write the same definitions as Python functions that call themselves, trace the calls, and explain the call stack and `RecursionError`.

The hook, "The Shrinking Function", asks for f(20) where f(x) = f(x−3) + x when x > 10, else 2x − 5. The answer is 73; Lesson 1 works it by hand and Lesson 3 writes the program.

## Pacing

Budget: three lessons of 60–90 minutes, still inside the Contest 1 run-up.

- **Lesson 1.**
  - Cases notation, the dialect table (`mod`, `abs`, floor), and the call-table method on f(8) and the hook.
  - Insist on the two passes written out in a table; it is the method that prevents most contest errors.
- **Lesson 2.**
  - Two-variable functions, then multiple recursion: first the call tree for f(4), which is 9 calls and shows why it grows, then the faster bottom-up table.
  - Indirect recursion is marked Intermediate and above.
- **Lesson 3.**
  - The hook as a Python `def`. Add start/return prints so students see the "down, then up" order match the call table.
  - The call stack, a deliberately broken definition (no-exec) that raises `RecursionError`, and Python's `//` flooring for negatives.
- **Exercises:** 1–9 Junior (short answers and three programs), 10–14 Intermediate, 15–16 Senior Challenges.

**60-minute cut:** keep the call-table method and multiple recursion; move the call-stack discussion and the tuple-returning Challenge to homework.

## Common mistakes

- Stopping at the base case and giving its value as the answer, instead of substituting back up.
- Adding the wrong value on the way up (e.g. adding `x` of the base case instead of the `x` of each level).
- Missing one of the two calls in multiple recursion, or recomputing the same values by hand instead of using a table.
- Translating ACSL's floor of a division wrongly: write `floor(x / 2)` as `x // 2` (it floors: `-7 // 2` is −4), never as `int(x / 2)` (it truncates: `int(-3.5)` is −3).
- Forgetting a base case when writing the Python function, which produces `RecursionError`.
- In indirect recursion, switching to the wrong function at a step.

## Discussion prompts

- What makes a recursive definition stop? What would happen without a base case?
- Why does the call tree for multiple recursion grow so fast, and how does the bottom-up table avoid that?
- When would you rather write a loop than a recursive function?
- In indirect recursion, how do you keep track of which function you are in?

## Differentiation

- **Junior:** Lessons 1–3 without the indirect-recursion section; Exercises 1–9.
- **Intermediate and Senior:** everything, including indirect recursion and the Challenges.
- **Classroom:** the short-answer items at Junior and Intermediate level.
- **Elementary:** not part of the Elementary path (Recursive Functions is not an Elementary category).
- **Support:** a printed call-table template (columns: call, condition, value) that students fill in line by line.
- **Extension:** write a definition of your own for a partner to evaluate, then check each other's answers with Python.

# Teacher Notes — Unit 07: Simulation & Ad Hoc

## Goals

By the end of this unit students can:

- Read a problem that says "follow these rules" and turn it into code that faithfully carries out each step.
- Choose a **state representation** (a few variables, a list, or a 2D grid) that makes the rules easy to
  apply.
- Apply updates in the **correct order**, and guard the **edges**: staying in bounds, stopping at the right
  step, and knowing the loop terminates.
- Trace their own simulation by hand for a few steps to check it against the sample.

Simulation problems reward carefulness over cleverness: there is usually no trick, just the discipline to
model the state and step it correctly.

## Pacing

Two 60–90 minute lessons.

**Lesson 1 — State and one-step rules.**
Open with the project hook: a robot on a grid following a string of move commands.
Model the state (row, col) and apply one move at a time, clamping or wrapping at the walls exactly as the
problem says.
Do a second, non-grid example — a tick-by-tick counter that rises and falls with a cap/floor — to show
that "state" can be a couple of variables.
Stress hand-tracing the first few steps against the sample.
Class works Exercises 1–4 (robot, battery ticks, event log, wrap-around dial).

**Lesson 2 — Grids, automata, and edges.**
Work a one-step cellular rule (each cell's next value depends on its neighbors) and the classic edge
question: read all neighbors from the OLD grid before writing the new one.
Discuss termination: every loop here is bounded (a fixed number of steps, or a walk that must leave the
grid) — name the bound.
Class works Exercises 5–9 (tile transformation, edge-light automaton, turn game, and the two grid stretch
problems).

## Common mistakes

- **Updating state in the wrong order** — for a cellular/automaton step, reading and writing the same grid
  in place corrupts later cells; compute the next state from a snapshot of the current one.
- **Off-by-one on the last step** — running one tick too few or too many; several exercises put the decisive
  change on the final step to catch this.
- **Going out of bounds** — moving off the grid, or indexing `-1`/`len` without a guard.
- **Forgetting the wrap** — a dial/counter that should wrap with `%` but is clamped instead (or vice versa).
- **Rebuilding the whole state when only part changes** — correct but slow; and easy to get subtly wrong.

## Discussion prompts

- In Exercise 1, what happens when a move would take the robot off the grid? Where in your code is that
  decision made, and did the statement tell you to clamp, wrap, or ignore?
- For the automaton (Exercise 6), why must you read all the inputs before writing any outputs? Show an input
  where updating in place gives the wrong answer.
- Which of these problems has a loop whose length you know in advance, and which runs until a condition?
  How do you know each one terminates?
- What is the smallest hand-traceable input that would have caught your last bug?

## Differentiation

- **More support:** give the state variables for Exercises 1 and 2 and let students write only the per-step
  update; provide a filled-in bounds check.
- **More challenge:** the stretch problems (8 Rolling Grains, 9 Turning Ant Automaton) have richer state and
  a termination condition to reason about; ask students to state the loop bound and the Big-O.
- **Extension:** ask fast finishers to add an assertion inside their loop that must hold every step (an
  invariant) — a great way to catch a wrong-order update early.

### Big-O per exercise

1. Museum Robot — O(M) over the M move commands (walk the grid, clamp at walls).
2. Battery Ticks — O(T) over the T ticks (add/subtract with a cap and floor).
3. Jumping Event Log — O(E) over the E events (apply each rule in order).
4. Mood Dial — O(S) over the S steps (wrap with `%`).
5. Neighbor Tiles — O(L + K) for a length-L tile string and K operations.
6. Edge-Light Automaton — O(C·S) for C cells over S steps (snapshot then update).
7. Odd-Card Turn Game — O(N) over the N cards (simulate the turns).
8. Rolling Grains *(stretch)* — O(R·C + G·H) (build the R×C grid, then settle G grains over fall height H).
9. Turning Ant Automaton *(stretch)* — O(R·C + S) (build the R×C grid and count at the end, plus S simulated steps; terminates by the step cap).

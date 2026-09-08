# Teacher Notes — Unit 10: Stacks, Queues & Deques

## Goals

By the end of this unit students can:

- Explain the difference between a **stack** (LIFO — last in, first out) and a **queue** (FIFO — first in,
  first out), and choose the right one for a problem.
- Use `from collections import deque` and the course idioms: a **stack** is a `deque` with `.appendleft`
  (push) and `.popleft` (pop); a **queue** is a `deque` with `.append` (enqueue) and `.popleft` (dequeue).
- **Peek** at the top of a stack with the subscript `stack[0]` — no method call — and use that to build a
  **monotonic stack** for nearest-greater/nearest-smaller problems.
- Apply a stack to two classic patterns: **bracket matching** and **postfix (RPN) evaluation**.

This is the first unit with a named data structure whose *shape* (which end you add to and remove from) is
the whole idea. Stress that a `deque` is one tool that becomes a stack or a queue depending on which methods
you use — the LIFO/FIFO choice is a decision the programmer makes, not a different type.

**A note on `.pop()`:** this course deliberately never teaches `list.pop()` or `deque.pop()`. Removal is
always `.popleft`, and the top-of-stack is read with `stack[0]`. Keep to that so the notebooks stay inside
the taught surface; a student who reaches for `.pop()` should be redirected to `.popleft`.

## Pacing

Two 60–90 minute lessons.

**Lesson 1 — Stacks, queues & the deque.**
Open with the hook ("are these brackets balanced?"). Live-code the two idioms side by side: push/pop a stack
with `appendleft`/`popleft`, enqueue/dequeue a queue with `append`/`popleft`, and read the top with
`stack[0]`. Make the LIFO-vs-FIFO distinction concrete by running the *same* sequence of adds/removes through
both and showing the different output order. Then work bracket matching together — push each opener, and on a
closer check it against `stack[0]` before removing.
Class works Exercises 1, 3, 5 (brackets; undo stack; help-desk queue — the FIFO case).

**Lesson 2 — Postfix evaluation & harder stack problems.**
Introduce postfix (RPN): push numbers, and on an operator remove the right operand first, then the left,
apply, and push the result. Then build to the monotonic stack — a stack that only ever holds indices whose
answer is still unknown — for the next-greater problem. Discuss why each item is pushed once and removed at
most once, so the whole scan is linear.
Class works Exercises 2, 4, 6, 7 and the two stretch problems (8, 9).

## Common mistakes

- **Reaching for `.pop()`.** It is untaught here — removal is `.popleft`, and the top is `stack[0]`. This is
  the single most common slip; catch it early.
- **Popping an empty stack.** A closing bracket (Ex 1) or a departure (Ex 9) when the stack is empty must be
  handled — check `len(stack)` or `if stack:` before reading `stack[0]` or calling `.popleft`.
- **Mixing up LIFO and FIFO.** Using a stack where the problem needs a queue (Ex 5) serves the newest waiter
  instead of the oldest. Ask "which one should come out first?" before choosing the idiom.
- **Postfix operand order (Ex 2).** For non-commutative `-`, the *first* value popped is the **right**
  operand; popping in the wrong order flips the sign of subtractions.
- **Building the monotonic stack wrong (Ex 4).** The stack holds *indices*, not values, and you resolve and
  remove every index that the current value is greater than — not just the top one.

## Discussion prompts

- Exercise 5 vs Exercise 1: one needs FIFO and one needs LIFO. How do you decide which, and what goes wrong
  if you swap them? (Ex 5's own sample shows the LIFO answer is wrong.)
- In postfix evaluation, why must the right operand be popped before the left? Show it on `5 3 -`.
- The next-greater scan (Ex 4) looks at each position once yet answers every position. Where does the work
  for a position actually happen, and why is the total still O(N)?
- Exercise 6 builds a queue out of two stacks. Trace a few commands and explain why moving values across only
  when the output stack is empty still returns items oldest-first.

## Differentiation

- **More support:** give the push/pop and enqueue/dequeue idiom lines as a reference card; pre-write the
  input parsing for Exercises 3, 5, 6 so students focus on the stack/queue logic.
- **More challenge:** the stretch problems (8 Adjacent Pair Cascade, 9 Rail Yard Departure) require reasoning
  about *why* a stack captures the rule — ask students to state what invariant the stack maintains and to
  give the Big-O.
- **Extension:** ask fast finishers to explain why the two-stack queue (Ex 6) is O(1) *amortized* per
  operation even though a single dequeue can move many values.

### Big-O per exercise

1. Balanced Bracket Check — O(N) (each bracket pushed/removed at most once).
2. Postfix Score — O(T) over T tokens (each token handled once).
3. Typing With Undo — O(Q) over Q commands (one push or one pop each).
4. Next Greater Signal — O(N) (each index pushed once and removed at most once from the monotonic stack).
5. Help Desk Line — O(Q) (one enqueue or one dequeue per command).
6. Queue From Two Stacks — O(Q) amortized (each value moved across the two stacks at most once).
7. Reverse the Card Line — O(N) (each label moved a constant number of times).
8. Adjacent Pair Cascade *(stretch)* — O(N) (each character pushed once and removed at most once).
9. Rail Yard Departure *(stretch)* — O(N) (each car pushed once and departs once).

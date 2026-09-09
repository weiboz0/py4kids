# Teacher Notes — Unit 12: Binary Trees & Traversals

## Goals

By the end of this unit students can:

- Represent a **binary tree WITHOUT a class** — parallel arrays (`left[i]`, `right[i]`, `val[i]`, with `-1`
  meaning "no child") or a dict of nodes — and follow it from a given root index.
- Write a **recursive traversal** (pre-order, in-order, post-order) and explain how the visit order differs.
- Use **recursive aggregation** — height/depth, leaf count, and sum/min/max over the whole tree — where the
  base case returns the identity (an empty subtree contributes nothing).
- Work with a **binary search tree (BST)**: the ordering property, recursive search, building one by
  inserting a sequence, and **validating** it with propagated `(low, high)` bounds.

Recursion (Unit 9) is the core tool here: a function handles the current node, then calls itself on the left
and right children, with the empty child (`-1`) as the base case.

## Pacing

Two 60–90 minute lessons.

**Lesson 1 — Representation, traversals & aggregation (≈60–75 min instruction).**
Introduce the parallel-array representation and the root index; stress that the `-1` sentinel must be checked
with `child == -1` BEFORE indexing, because `arr[-1]` silently reads the last element (a wrong answer, not a
crash). Live-code the three recursive traversals on a small tree so the pre/in/post orders are concrete, then
recursive aggregation (height, leaf count, sum/min/max) with the empty-subtree base case.
Class works Exercises 1, 2, 3, 4 (traversal order; height; leaf count; score summary).

**Lesson 2 — Binary search trees.**
Introduce the BST ordering property; recursive membership search (go left/right by comparison, O(height));
building a BST by inserting a sequence of values (state the duplicate-key policy up front); and BST
**validation** with propagated `(low, high)` bounds — emphasize that checking only a node against its
immediate children is NOT enough. Note that an in-order walk of a BST emits values in sorted order (a fact,
not a shortcut — the graded traversals are pre/post-order).
Class works Exercises 5, 6, 7 (membership; build the index; validate the index). Assign the stretch
problems (8, 9) as extension.

## Common mistakes

- **Missing base case on the `-1` sentinel** — recursing into `arr[-1]` reads the LAST array element and
  produces a silent wrong answer; always test `child == -1` first.
- **Confusing pre/in/post-order** — be precise about when the node is visited relative to its subtrees.
- **Recursion-limit on a deep skew** — a degenerate (list-like) tree has height N; the constraints bound the
  height so a simple recursive walk is safe, but students should know why depth matters.
- **Shallow BST validation** — comparing a node only to its direct children accepts invalid trees; the bound
  must be propagated down (`low < val < high`, tightened at each step per the duplicate policy).
- **Mutating the shared arrays during a walk** — read-only traversal; don't overwrite `left`/`right`/`val`.
- **Sorting instead of traversing** — a traversal order must come from walking the tree, never from
  `sorted()`.

## Discussion prompts

- For the same tree, why do pre-order, in-order, and post-order visit the nodes in different sequences, and
  when would you want each?
- Why does an in-order walk of a BST come out sorted? Does that hold for a non-BST binary tree?
- In BST validation, why isn't it enough to check each node against only its left and right child? Show a
  tree that passes the shallow check but is not a valid BST.
- Building a BST by inserting `[4, 2, 6, 1, 3]` vs `[1, 2, 3, 4, 6]` gives different shapes — why, and how
  does shape affect search cost?

## Differentiation

- **More support:** give the recursive-traversal skeleton (visit node, recurse left, recurse right) and the
  parsing of the parallel arrays for Exercises 1–4; provide the `(low, high)` signature for validation.
- **More challenge:** the stretch problems (8 Closing Audit Order, 9 Target Record Depth) combine a traversal
  with a second condition; ask students to state the Big-O and identify the base case.
- **Extension:** ask fast finishers to explain why a balanced BST gives O(log N) search while a skewed one
  degrades to O(N), and to build the worst-case insert order.

### Big-O per exercise

_(reconciled against the shipped reference solutions in Phase C)_

1. Record Inspection Order — O(N) (visit each node once).
2. Tallest Reporting Chain — O(N) (height via one post-order pass).
3. Terminal Record Count — O(N) (count leaves in one pass).
4. Score Summary — O(N) (aggregate over every node).
5. BST Membership — O(h) for height h (follow one root-to-leaf path).
6. Build the Search Index — O(N·h) (insert N values, each an O(h) descent).
7. Validate the Search Index — O(N) (one bounded pass).
8. Closing Audit Order *(stretch)* — O(N) (a single traversal).
9. Target Record Depth *(stretch)* — O(N) (one pass tracking depth).

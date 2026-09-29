# Teacher Notes — Unit 09: Data Structures

## Goals

Students learn the Contest 3 Data Structures category, which every programming division takes.
By the end they can:

- trace `PUSH` and `POP` scripts on a stack (last in, first out) and on a queue (first in, first out), including `POP` on an empty structure (`NIL`) and arithmetic on popped values;
- build a binary search tree from a word or list by ACSL's rules: duplicates go left, as if less than their equal key, and the root has depth 0;
- read a tree's depths, height, leaves and internal path length; and, Intermediate and above, its external nodes (n + 1 of them), external path length, and inorder, preorder and postorder traversals;
- build a min-heap or max-heap by inserting one item at a time, read its rows and 1-based positions;
- (Senior) remove a heap's root, and delete a BST node by ACSL's rule, then report on the new tree;
- write these structures in Python with lists: a stack with a `top` count, a queue with a `head` index, a BST as parallel `key`/`left`/`right` lists, and a heap with slot 0 unused.

The hook is "The Library Robot": three puzzles, one for each lesson — a returns cart and a help-desk line (stacks and queues), a letter tree for the shelves (BSTs), and an urgent pile (heaps).

## Pacing

Budget: three lessons of 60–90 minutes in the Contest 3 window.

- **Lesson 1, Junior.**
  - Stacks and queues by hand, `NIL`, and the Intermediate section on arithmetic with popped values (the wiki sample, Z = −2).
  - The stack and queue idioms in Python (no `.pop`).
- **Lesson 2, Junior.**
  - Building a BST with duplicates to the left; depth, height, leaves and internal path length.
  - The BST in Python with a `while` insert.
  - Intermediate: external nodes and external path length (EPL = IPL + 2n), and the three traversals as recursive functions, on the wiki's AMERICAN tree.
- **Lesson 3, Intermediate.**
  - Heaps by insertion (min and max), rows and positions, and a heap in Python with a tuple swap.
  - Senior: heap root removal, and ACSL's BST deletion rule, worked on MOUNTAINS.
- **Exercises:** 21 items. Exercises 1–8 are Junior (programs 7 and 8), 9–17 Intermediate (programs 16 and 17), and 18–21 Senior (20–21 are Challenges; 21 is a program).

**60-minute cut:** keep stacks, queues and BST building with internal path length; set heaps and traversals as reading plus Exercises 11 and 14.

## Common mistakes

- Treating a queue as a stack, or the reverse.
- Sending a duplicate key to the right; ACSL puts it to the left.
- Starting depth at 1: the root has depth 0.
- Counting leaves as external nodes; external nodes are the empty places where a new key could hang (n + 1 of them).
- Building a heap by sorting the list instead of inserting one item at a time and swapping up.
- Swapping equal keys during heap insertion; a swap happens only when the parent is strictly larger (min-heap).
- In BST deletion with two children: the left child takes the deleted node's place, and the right subtree hangs off the right-most node of the left subtree.

## Discussion prompts

- Where do you meet stacks and queues in daily life (undo, a print queue, a lunch line)?
- Why does the inorder traversal of a BST come out sorted?
- Why does a tree built from a sorted word look like a chain, and what does that do to its path length?
- A heap is not sorted, yet its root is always the smallest. Why is that enough for a priority queue?

## Differentiation

- **Junior:** Lessons 1–2 without the Intermediate sections; Exercises 1–8.
- **Intermediate:** everything except the Senior sections; Exercises 1–17.
- **Senior:** the whole unit, including Exercises 18–21.
- **Classroom:** Classroom's Contest 3 includes Data Structures, so do the short-answer items at Junior and Intermediate level.
- **Elementary:** not part of the Elementary path.
- **Support:** printed tree templates with depth labels, and a strip of boxes for stacks, queues and heap arrays.
- **Extension:** find a 7-letter word whose BST has the smallest possible internal path length, and explain why no word can do better.

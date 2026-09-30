"""Plan 095 A1: pre-written tests for unit 09's data-structure evaluator (``assets/verify/ds_eval.py``).

The evaluator's author implements this interface and does NOT edit this file.

``ds_eval.run(script: list[str], kind: str) -> dict``
    Runs ``script`` on an initially empty ``"stack"`` (LIFO) or ``"queue"`` (FIFO), one statement
    per list item. The statements are ``PUSH(e)``, ``POP()`` and ``V = POP()`` (``V`` a one-letter
    capital variable). ``e`` is an integer, a variable assigned earlier, or ``a op b`` with ``op``
    one of ``+ - *`` over those (spaces around ``op`` optional: ``PUSH(X-Y)``, ``PUSH(B * 3)``);
    any other bare word (a letter never assigned, such as ``A``, or a word such as ``CAT``) is
    pushed as that string. A ``POP`` of an empty structure gives the string ``"NIL"``.
    Returns ``{"popped": [...], "vars": {...}}``: every popped value in order (numbers as ``int``,
    words as ``str``, ``"NIL"`` when empty) and the final variables (name -> value).

``ds_eval.bst(keys: list) -> dict``
    Inserts ``keys`` (a word is passed as ``list("PROGRAM")``; numbers as ints) in order into a
    binary search tree with ACSL's convention: a key goes LEFT when it is less than OR EQUAL to a
    node's key (duplicates go left), right when greater. The root has depth 0. Report fields:

    * ``depths: list[int]``: the depth of each inserted node, in insertion order (duplicates
      stay distinct nodes)
    * ``ipl: int``: internal path length, the sum of the depths of all nodes
    * ``external: int``: the number of external nodes (empty places where a node could be
      attached; ``n + 1`` for ``n`` nodes)
    * ``epl: int``: external path length, the sum of the depths of the external nodes
    * ``leaves: int``: nodes with no children; ``height: int``: the greatest node depth
    * ``leaf_keys``, ``inorder``, ``preorder``, ``postorder: str``: canonical row text, leaves
      left to right; letters run together (``"AACEIMNR"``), numbers separated by single spaces
      (``"20 30 35"``)

``ds_eval.bst_delete(keys: list, key) -> dict``
    The same report minus ``depths``, after inserting ``keys`` and then deleting the SHALLOWEST
    node holding ``key`` (the first met in a top-down, level-by-level search) by ACSL's rule, with
    ``p`` the node and ``f`` its parent: no children, delete ``p``; one child, the child takes
    ``p``'s place under ``f``; two children, the left child ``l`` takes ``p``'s place and ``p``'s
    right subtree ``r`` becomes the right child of the right-most node of ``l``'s subtree. When
    ``p`` is the root, the replacement becomes the root.

``ds_eval.heap(keys: list, kind: str = "min") -> list[str]``
    The rows of a heap built by inserting ``keys`` one at a time, top row first, each in
    canonical row text. Insertion puts the item in the next free place (bottom row, left to
    right) and swaps it with its parent while the parent is strictly larger (``"min"``) or
    strictly smaller (``"max"``); equal keys do not swap.

``ds_eval.heap_pop(keys: list, kind: str = "min") -> list[str]``
    The rows after building ``heap(keys, kind)`` and removing the root by ACSL's rule: the
    bottom-most, right-most item moves to the root, then swaps with its smaller child (larger, for
    ``"max"``) while that child is strictly smaller (larger). When the two children are equal,
    it swaps with the LEFT one (the wiki's pseudo-code leaves this tie open; pinned here).

Expected values are the ACSL wiki's ("Data Structures", categories.acsl.org: its text and its
drawn trees and heaps), or hand-computed where the wiki gives none (working in comments). All were
re-checked by an independent throwaway implementation. Not covered: the wiki's pre-2018 syntax
``POP(X)``. Skips until the module exists.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

VERIFY_DIR = (
    Path(__file__).resolve().parents[1] / "acsl/units/unit-09-data-structures/assets/verify"
)
sys.path.insert(0, str(VERIFY_DIR))
ds_eval = pytest.importorskip("ds_eval")

AMERICAN = list("AMERICAN")
# The wiki's AMERICAN tree (duplicates left):
#            A
#          /   \
#         A     M
#             /   \
#            E     R
#           / \   /
#          C   I N
# Insertion depths A0 M1 E2 R2 I3 C3 A1 N3.
NUMS = [50, 30, 70, 20, 40, 60, 80, 35]
# Hand-built tree:
#              50
#           /      \
#         30        70
#        /  \      /  \
#      20    40   60   80
#           /
#         35
# depths 50:0 30:1 70:1 20:2 40:2 60:2 80:2 35:3 -> ipl = 0+1+1+2+2+2+2+3 = 13
# external nodes: 20 has 2 at depth 3, 40 has 1 (right) at depth 3, 35 has 2 at depth 4,
# 60 and 80 have 2 each at depth 3 -> count 2+1+2+2+2 = 9 (= n + 1),
# epl = 6 + 3 + 8 + 6 + 6 = 29 (= ipl + 2n = 13 + 16).

WIKI_STACK = [
    "PUSH(3)",
    "PUSH(6)",
    "PUSH(8)",
    "Y = POP()",
    "X = POP()",
    "PUSH(X-Y)",
    "Z = POP()",
]
# The wiki's 14-operation example, PUSH("A") written as PUSH(A).
WIKI_AMERICAN_SCRIPT = [
    "PUSH(A)",
    "PUSH(M)",
    "PUSH(E)",
    "X = POP()",
    "PUSH(R)",
    "X = POP()",
    "PUSH(I)",
    "X = POP()",
    "X = POP()",
    "X = POP()",
    "X = POP()",
    "PUSH(C)",
    "PUSH(A)",
    "PUSH(N)",
]


# ---------------------------------------------------------------- stacks and queues


def test_wiki_sample_1_stack():
    result = ds_eval.run(WIKI_STACK, "stack")
    assert result["vars"]["Z"] == -2
    assert result["popped"] == [8, 6, -2]
    assert result["vars"] == {"Y": 8, "X": 6, "Z": -2}


def test_wiki_sample_1_on_a_queue():
    # Hand: queue 3 6 8; Y = 3, X = 6; push 6-3 = 3 -> queue 8 3; Z = 8.
    result = ds_eval.run(WIKI_STACK, "queue")
    assert result["popped"] == [3, 6, 8]
    assert result["vars"] == {"Y": 3, "X": 6, "Z": 8}


def test_wiki_fourteen_operations():
    # Wiki: a stack pops E, R, I, M, A and NIL; a queue pops A, M, E, R, I and NIL.
    stack = ds_eval.run(WIKI_AMERICAN_SCRIPT, "stack")
    assert stack["popped"] == ["E", "R", "I", "M", "A", "NIL"]
    assert stack["vars"] == {"X": "NIL"}
    queue = ds_eval.run(WIKI_AMERICAN_SCRIPT, "queue")
    assert queue["popped"] == ["A", "M", "E", "R", "I", "NIL"]
    assert queue["vars"] == {"X": "NIL"}


@pytest.mark.parametrize("kind", ["stack", "queue"])
def test_nil_on_empty_pop(kind):
    assert ds_eval.run(["POP()"], kind)["popped"] == ["NIL"]
    assert ds_eval.run(["X = POP()"], kind)["vars"] == {"X": "NIL"}
    result = ds_eval.run(["PUSH(5)", "A = POP()", "B = POP()"], kind)
    assert result["popped"] == [5, "NIL"]
    assert result["vars"] == {"A": 5, "B": "NIL"}


def test_words_variables_and_arithmetic():
    # Hand (stack): push 4, push "CAT"; A = CAT, B = 4; push B * 3 = 12; C = 12; D = NIL.
    script = [
        "PUSH(4)",
        "PUSH(CAT)",
        "A = POP()",
        "B = POP()",
        "PUSH(B * 3)",
        "C = POP()",
        "D = POP()",
    ]
    result = ds_eval.run(script, "stack")
    assert result["popped"] == ["CAT", 4, 12, "NIL"]
    assert result["vars"] == {"A": "CAT", "B": 4, "C": 12, "D": "NIL"}


def test_arithmetic_on_popped_values():
    # Hand (stack): X = 2, Y = 7; push 7+2 = 9, push 7 - 2 = 5, push 5 (a literal);
    # pops: 5, 5, 9.
    script = [
        "PUSH(7)",
        "PUSH(2)",
        "X = POP()",
        "Y = POP()",
        "PUSH(Y+X)",
        "PUSH(Y - X)",
        "PUSH(5)",
        "POP()",
        "A = POP()",
        "B = POP()",
    ]
    result = ds_eval.run(script, "stack")
    assert result["popped"] == [2, 7, 5, 5, 9]
    assert result["vars"] == {"X": 2, "Y": 7, "A": 5, "B": 9}


# ---------------------------------------------------------------- binary search trees


def test_wiki_american_tree():
    report = ds_eval.bst(AMERICAN)
    # Wiki: depth 3; 4 leaves A, C, I, N; 9 external nodes; ipl 15; epl 31.
    assert report["height"] == 3
    assert report["leaves"] == 4
    assert report["leaf_keys"] == "ACIN"
    assert report["external"] == 9
    assert report["ipl"] == 15
    assert report["epl"] == 31


def test_wiki_american_traversals():
    report = ds_eval.bst(AMERICAN)
    assert report["inorder"] == "AACEIMNR"
    assert report["preorder"] == "AAMECIRN"
    assert report["postorder"] == "ACIENRMA"


def test_duplicate_depths_keep_both_nodes():
    # The second A goes left of the root A (depth 1); both A nodes are reported.
    assert ds_eval.bst(AMERICAN)["depths"] == [0, 1, 2, 2, 3, 3, 1, 3]


def test_wiki_sample_3_program():
    # Wiki: P 0; O and R 1; G and R 2; A and M 3 -> ipl 2*1 + 2*2 + 2*3 = 12.
    report = ds_eval.bst(list("PROGRAM"))
    assert report["ipl"] == 12
    assert report["depths"] == [0, 1, 1, 2, 2, 3, 3]  # P R O G R A M
    # Hand, from the wiki's drawing: leaves A, M (under G) and the second R (left of R).
    assert report["leaf_keys"] == "AMR"
    assert report["inorder"] == "AGMOPRR"
    assert report["preorder"] == "POGAMRR"
    assert report["postorder"] == "AMGORRP"
    assert report["external"] == 8
    assert report["epl"] == 26  # ipl + 2n = 12 + 14


def test_duplicate_goes_left():
    # 5 root; 3 left; the second 5 is <= 5 so goes left, then > 3 so right of 3: depth 2.
    # (Duplicates-right would put it at depth 1.)
    report = ds_eval.bst([5, 3, 5])
    assert report["depths"] == [0, 1, 2]
    assert report["inorder"] == "3 5 5"
    assert report["preorder"] == "5 3 5"
    assert report["leaf_keys"] == "5"


def test_hand_checked_numeric_tree():
    report = ds_eval.bst(NUMS)
    assert report["depths"] == [0, 1, 1, 2, 2, 2, 2, 3]
    assert report["height"] == 3
    assert report["ipl"] == 13
    assert report["external"] == 9  # n + 1
    assert report["epl"] == 29
    assert report["leaves"] == 4
    assert report["leaf_keys"] == "20 35 60 80"
    assert report["inorder"] == "20 30 35 40 50 60 70 80"
    assert report["preorder"] == "50 30 20 40 35 70 60 80"
    assert report["postorder"] == "20 35 40 30 60 80 70 50"


# ---------------------------------------------------------------- BST deletion


def test_wiki_delete_leaf():
    # Wiki drawing: delete I (no children).
    report = ds_eval.bst_delete(AMERICAN, "I")
    assert "depths" not in report
    assert report["preorder"] == "AAMECRN"
    assert report["inorder"] == "AACEMNR"
    assert report["postorder"] == "ACENRMA"
    assert report["leaf_keys"] == "ACN"
    assert report["ipl"] == 12  # A0 A1 M1 E2 R2 C3 N3
    assert report["external"] == 8
    assert report["epl"] == 26
    assert report["height"] == 3


def test_wiki_delete_one_child():
    # Wiki drawing: delete R (one child N): N becomes M's right child.
    report = ds_eval.bst_delete(AMERICAN, "R")
    assert report["preorder"] == "AAMECIN"
    assert report["inorder"] == "AACEIMN"
    assert report["postorder"] == "ACIENMA"
    assert report["leaf_keys"] == "ACIN"
    assert report["ipl"] == 12  # A0 A1 M1 E2 N2 C3 I3
    assert report["height"] == 3


def test_wiki_delete_two_children():
    # Wiki drawing: delete M (children E and R): E takes M's place, and the R subtree becomes the
    # right child of I, the right-most node of E's subtree:
    #        A
    #       / \
    #      A   E
    #         / \
    #        C   I
    #             \
    #              R
    #             /
    #            N
    report = ds_eval.bst_delete(AMERICAN, "M")
    assert report["preorder"] == "AAECIRN"
    assert report["inorder"] == "AACEINR"
    assert report["postorder"] == "ACNRIEA"
    assert report["leaf_keys"] == "ACN"
    assert report["leaves"] == 3
    assert report["ipl"] == 13  # A0 A1 E1 C2 I2 R3 N4
    assert report["height"] == 4
    assert report["external"] == 8
    assert report["epl"] == 27  # ipl + 2n = 13 + 14


def test_numeric_delete_two_children():
    # Hand: delete 30 (children 20 and 40): 20 takes its place; 20 has no right child, so the
    # 40 subtree (with 35) becomes 20's right child. Depths 50:0 20:1 70:1 40:2 60:2 80:2 35:3.
    report = ds_eval.bst_delete(NUMS, 30)
    assert report["preorder"] == "50 20 40 35 70 60 80"
    assert report["inorder"] == "20 35 40 50 60 70 80"
    assert report["ipl"] == 11
    assert report["leaf_keys"] == "35 60 80"


def test_delete_removes_shallower_duplicate_one_child():
    # M root; A left; the second M goes left (<= M), then right of A. Deleting the shallower M
    # (the root, one child A) leaves A with M on its right: preorder "AM".
    # Deleting the deeper M instead would leave M with A on its left: preorder "MA".
    report = ds_eval.bst_delete(list("MAM"), "M")
    assert report["preorder"] == "AM"
    assert report["postorder"] == "MA"
    assert report["ipl"] == 1


def test_delete_removes_shallower_duplicate_two_children():
    # C root; A left; E right; the second C goes left, then right of A. Deleting the root C
    # (two children): A takes its place, and E becomes the right child of A's right-most node,
    # the second C: A -> C -> E down the right side, ipl 0 + 1 + 2 = 3.
    # Deleting the deeper C (a leaf) would leave C(A, E): preorder "CAE", ipl 2.
    report = ds_eval.bst_delete(list("CAEC"), "C")
    assert report["preorder"] == "ACE"
    assert report["ipl"] == 3
    assert report["height"] == 2


def test_delete_duplicate_in_american():
    # The shallower A is the root (children: the second A and M). The second A takes its place
    # and the M subtree becomes its right child: the tree reads as AMERICAN's without one A.
    report = ds_eval.bst_delete(AMERICAN, "A")
    assert report["preorder"] == "AMECIRN"
    assert report["inorder"] == "ACEIMNR"
    assert report["ipl"] == 14


# ---------------------------------------------------------------- heaps


def test_wiki_sample_2_programming_heap():
    rows = ds_eval.heap(list("PROGRAMMING"))
    assert rows[-1] == "RORN"
    # The wiki's drawing of the whole heap.
    assert rows == ["A", "GG", "MIPM", "RORN"]


def test_wiki_american_heap_and_insert_c():
    # The wiki's two drawings: AMERICAN, then the same heap after a C is added.
    assert ds_eval.heap(AMERICAN) == ["A", "IA", "NMEC", "R"]
    assert ds_eval.heap(AMERICAN + ["C"]) == ["A", "CA", "IMEC", "RN"]


def test_numeric_min_heap_rows():
    # Hand: 5 -> [5]; 3 swaps up -> [3 5]; 8 -> [3 5 8]; 1 at slot 4 swaps with 5, then 3
    # -> [1 3 8 5]; 9 at slot 5 stays (parent 3); 2 at slot 6 swaps with 8, stops under 1
    # -> [1 3 2 5 9 8].
    assert ds_eval.heap([5, 3, 8, 1, 9, 2]) == ["1", "3 2", "5 9 8"]
    assert ds_eval.heap([5, 3, 8, 1, 9, 2], "min") == ["1", "3 2", "5 9 8"]


def test_numeric_max_heap_rows():
    # Hand: 5; 3 -> [5 3]; 8 swaps up -> [8 3 5]; 1 -> [8 3 5 1]; 9 at slot 5 swaps with 3,
    # then 8 -> [9 8 5 1 3]; 2 at slot 6 stays (parent 5) -> [9 8 5 1 3 2].
    assert ds_eval.heap([5, 3, 8, 1, 9, 2], "max") == ["9", "8 5", "1 3 2"]


def test_letter_max_heap_rows():
    # Hand, insertion into a max-heap: A; M up -> M A; E -> M A E; R up twice -> R M E A;
    # I up past M -> R I E A M; C -> R I E A M C; A -> ... A; N up past A and I, stops under R
    # -> R N E I M C A A.
    assert ds_eval.heap(AMERICAN, "max") == ["R", "NE", "MICA", "A"]


def test_min_heap_root_removal():
    # Hand: [1 3 2 5 9 8]; 8 moves to the root -> [8 3 2 5 9]; smaller child 2 -> [2 3 8 5 9].
    assert ds_eval.heap_pop([5, 3, 8, 1, 9, 2]) == ["2", "3 8", "5 9"]


def test_max_heap_root_removal():
    # Hand: [9 8 5 1 3 2]; 2 moves to the root -> [2 8 5 1 3]; larger child 8 -> [8 2 5 1 3];
    # larger child of slot 2 is 3 -> [8 3 5 1 2].
    assert ds_eval.heap_pop([5, 3, 8, 1, 9, 2], "max") == ["8", "3 5", "1 2"]


def test_american_heap_root_removal():
    # Hand: A / IA / NMEC / R; R moves to the root -> R / IA / NMEC; smaller child A (slot 3)
    # -> A / IR / NMEC; smaller child of slot 3 is C -> A / IC / NMER.
    assert ds_eval.heap_pop(AMERICAN) == ["A", "IC", "NMER"]


def test_heap_root_removal_equal_children_goes_left():
    # Hand: A / GG / MIPM / RORN; N moves to the root -> N / GG / MIPM / ROR. The children tie
    # (G, G): swap with the LEFT -> G / NG / MIPM / ROR; slot 2's children M, I: I is smaller
    # -> G / IG / MNPM / ROR; slot 5's child R is larger than N: stop.
    # (Going right on the tie would give G / GM / MIPN / ROR.)
    assert ds_eval.heap_pop(list("PROGRAMMING")) == ["G", "IG", "MNPM", "ROR"]

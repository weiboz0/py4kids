"""Seeded generator for the practice checkpoints' programming-question fixtures (plan 100, Phase B).

Run from the repository root:

    python acsl/reference/fixture_gen.py

Plan 100 replaced the programming questions CP1 Q8, CP2 Q9, CP3 Q9 and CP4 Q9.
For each one this script writes the input cases (`N.in`, case 1 being the sample), then pipes
every case through the question's reference solver (`assets/<stem>.py`) to write the expected
output (`N.out`).
Each set holds the sample, edge cases, and one modest scale case: large enough to punish a
program that re-does work on every step, small enough for a public repository (every input is
a few kilobytes at most).
The random data is seeded, so every run produces byte-identical files.
"""

from __future__ import annotations

import random
import shutil
import subprocess
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
CP1 = BOOK / "checkpoints/checkpoint-01-contest-1-practice/assets"
CP2 = BOOK / "checkpoints/checkpoint-02-contest-2-practice/assets"
CP3 = BOOK / "checkpoints/checkpoint-03-contest-3-practice/assets"
CP4 = BOOK / "checkpoints/checkpoint-04-contest-4-practice/assets"
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def lines(*rows) -> str:
    return "\n".join(str(r) for r in rows) + "\n"


# ---------------------------------------------------------------- Checkpoint 1, Question 8
def cp1_q8():
    """Same Digit All Through: the smallest base in which N is one digit repeated."""
    return [
        lines(400),  # the sample: 1111 in base 7
        lines(1),  # one digit already in base 2
        lines(2),  # base 2 fails (10), base 3 gives the single digit 2
        lines(3),  # 11 in base 2
        lines(21),  # 10101 in base 2 has equal end digits but is not all one digit; 111 in base 4
        lines(300),  # the repeated digit is 15, in base 19
        lines(2730),  # 222222 in base 4
        lines(99999),  # 99999 in base 10
        lines(100000),  # the largest N: base 399, digit 250
        lines(99991),  # the scale case: a prime, first all-one-digit in base N - 1
    ]


# ---------------------------------------------------------------- Checkpoint 2, Question 9
def bracketed(size: int, rng: random.Random, operands: str) -> str:
    """A random fully bracketed infix expression with `size` operators."""
    if size == 0:
        return rng.choice(operands)
    left = rng.randint(0, size - 1)
    return (
        "(" + bracketed(left, rng, operands) + rng.choice("+-*/^")
        + bracketed(size - 1 - left, rng, operands) + ")"
    )


def cp2_q9():
    """Brackets Away: a fully bracketed infix expression to postfix and prefix."""
    rng = random.Random(10029)
    medium = bracketed(12, rng, LETTERS[:8] + "123456789")
    large = bracketed(99, rng, LETTERS + "0123456789")
    return [
        lines("((A+B)*(C-(D/E)))"),  # the sample
        lines("A"),  # one operand and no brackets
        lines("(9-4)"),  # the operands keep their order
        lines("(((A-B)-C)-D)"),  # every bracket opens on the left
        lines("(A^(B^(C^D)))"),  # every bracket opens on the right
        lines("((1+2)*(3+4))"),  # digit operands
        lines("(A/((B-C)*(D+(E^2))))"),
        lines("((((A+B)+(C+D))*((E-F)/(G-H)))^2)"),
        lines(medium),
        lines(large),  # the scale case: 99 operators
    ]


# ---------------------------------------------------------------- Checkpoint 3, Question 9
def cp3_q9():
    """The Counting Line: players leave a queue after every K moves to the back."""
    return [
        lines("7 3"),  # the sample
        lines("1 1"),  # one player, who leaves at once
        lines("1 500"),  # one player, who keeps moving to the back of an empty line
        lines("5 1"),  # K = 1: the players leave from the front, in order
        lines("2 2"),
        lines("6 7"),  # K larger than N
        lines("10 2"),
        lines("41 3"),
        lines("300 17"),
        lines("500 500"),  # the scale case: the largest N and K
    ]


# ---------------------------------------------------------------- Checkpoint 4, Question 9
def random_graph(names: str, count: int, rng: random.Random) -> list[str]:
    pairs = [a + b for a in names for b in names if a != b]
    rng.shuffle(pairs)
    return sorted(pairs[:count])


def walk(names: str, edges: list[str], length: int, rng: random.Random) -> str:
    """A route that follows edges for up to `length` steps (it stops early at a dead end)."""
    route = rng.choice(names)
    for _ in range(length):
        nexts = [e[1] for e in edges if e[0] == route[-1]]
        if not nexts:
            break
        route += rng.choice(nexts)
    return route


def simple(names: str, edges: list[str], length: int, rng: random.Random) -> str:
    """A route that follows edges and never repeats a vertex."""
    route = rng.choice(names)
    for _ in range(length):
        nexts = [e[1] for e in edges if e[0] == route[-1] and e[1] not in route]
        if not nexts:
            break
        route += rng.choice(nexts)
    return route


def routes_case(names: str, edges: list[str], count: int, rng: random.Random) -> str:
    routes = []
    while len(routes) < count:
        kind = rng.randint(0, 3)
        if kind == 0:
            route = walk(names, edges, rng.randint(1, 25), rng)
        elif kind == 1:
            route = simple(names, edges, rng.randint(1, 25), rng)
        elif kind == 2:
            route = simple(names, edges, rng.randint(1, 25), rng)
            end = len(route)
            while end >= 2 and route[end - 1] + route[0] not in edges:
                end -= 1
            if end >= 2:
                route = route[:end] + route[0]  # cut it where it can close into a cycle
        else:
            route = walk(names, edges, rng.randint(1, 25), rng)
            spot = rng.randint(0, len(route) - 1)
            route = route[:spot] + rng.choice(names) + route[spot + 1:]  # one letter changed
        if len(route) >= 2:
            routes.append(route)
    return lines(names, " ".join(edges), len(routes), *routes)


def cp4_q9():
    """What Kind of Route?: each route is not a path, a path, a simple path or a cycle."""
    rng = random.Random(10049)
    ten = LETTERS[:10]
    return [
        lines("ABCDE", "AB BC CA CD DB DE EA", 6,
              "ABCA", "DEAB", "ABCDBC", "ACDE", "ABCABCA", "CDEABC"),  # the sample
        lines("AB", "AB BA", 6, "AB", "BA", "ABA", "BAB", "ABAB", "AA"),  # two-vertex cycles
        lines("PQRS", "PQ QR RS SP", 5, "PQRSP", "SPQ", "QP", "PQRSPQ", "RSPQR"),
        lines("ABC", "AB CB", 4, "ABC", "CB", "AB", "BA"),  # an edge only goes one way
        lines("ABCDEF", "AB BC CD DE EF FA CA", 6,
              "ABCDEFA", "ABCABCDEFA", "ABCDEF", "BCAB", "CABCD", "FABCAB"),
        lines("ABCDEFG", "AB BC CD DE", 3, "ABCDE", "EDCBA", "FG"),  # dead ends and lone vertices
        routes_case(ten, random_graph(ten, 30, rng), 40, rng),
        routes_case(LETTERS, random_graph(LETTERS, 120, rng), 400, rng),  # the scale case
    ]


REPLACED = [
    (CP1, "q8", cp1_q8),
    (CP2, "q9", cp2_q9),
    (CP3, "q9", cp3_q9),
    (CP4, "q9", cp4_q9),
]


def solve(assets: Path, stem: str, case: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(assets / f"{stem}.py")],
        input=case.read_text(encoding="utf-8"),
        capture_output=True,
        text=True,
        check=True,
    )
    case.with_suffix(".out").write_text(result.stdout, encoding="utf-8")


def main() -> None:
    for assets, stem, make in REPLACED:
        folder = assets / stem
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir()
        for number, text in enumerate(make(), start=1):
            case = folder / f"{number}.in"
            case.write_text(text, encoding="utf-8")
            solve(assets, stem, case)


if __name__ == "__main__":
    main()

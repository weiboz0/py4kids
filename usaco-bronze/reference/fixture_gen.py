"""Seeded generator for the Mock Contest and Grand Mock Contest judge fixtures (plan 099, content r1).

Run from the repository root:

    python usaco-bronze/reference/fixture_gen.py

For every problem listed below it writes the input cases (`N.in`), then pipes each case through the
problem's reference solver (`assets/<stem>.py`) to write the expected output (`N.out`).
Replaced problems get their whole fixture set rewritten; earlier problems only gain the listed extra
case (a scale case).
Scale cases use thousands to tens of thousands of items (each input at most about 130 KB): large
enough to expose a quadratic or per-query approach and to reach deep recursion, small enough for
a public repository.
The random data is seeded, so every run produces byte-identical files.
"""

from __future__ import annotations

import random
import shutil
import subprocess
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
CP1 = BOOK / "checkpoints/checkpoint-01-mock-contest-1/assets"
CP2 = BOOK / "checkpoints/checkpoint-02-mock-contest-2/assets"
CP3 = BOOK / "checkpoints/checkpoint-03-mock-contest-3/assets"
CP4 = BOOK / "checkpoints/checkpoint-04-mock-contest-4/assets"
PRJ = BOOK / "projects/project-03-mock-contest/assets"


def lines(*rows) -> str:
    return "\n".join(str(r) for r in rows) + "\n"


def nums(values) -> str:
    return " ".join(str(v) for v in values)


def names(count: int, rng: random.Random) -> list[str]:
    heads = ["B", "D", "F", "G", "K", "L", "M", "N", "P", "R", "S", "T", "V", "Z"]
    vowels = ["a", "e", "i", "o", "u"]
    tails = ["n", "r", "l", "s", "x", "", "m"]
    found: set[str] = set()
    while len(found) < count:
        word = rng.choice(heads) + rng.choice(vowels)
        for _ in range(rng.randint(1, 3)):
            word += rng.choice("bdfgklmnprstvz") + rng.choice(vowels)
        found.add(word + rng.choice(tails))
    return sorted(found)


# ---------------------------------------------------------------- Checkpoint 1
def cp1_q4():
    rng = random.Random(10104)
    pool = names(400, rng)
    rows = []
    for _ in range(7000):
        a = rng.choice(pool)
        if rng.random() < 0.3 and rows:
            b, a = rows[rng.randrange(len(rows))]  # reverse an earlier pick
        else:
            b = rng.choice(pool)
            while b == a:
                b = rng.choice(pool)
        rows.append((a, b))
    return [
        lines(7, "Mia Zoe", "Ava Ben", "Zoe Mia", "Ben Cy", "Mia Zoe", "Cy Ben", "Ben Ava"),
        lines(3, "Ava Ben", "Ben Cy", "Cy Ava"),
        lines(4, "Zed Amy", "Amy Zed", "Zed Amy", "Amy Zed"),
        lines(6, "Bo Cy", "Dee Al", "Cy Bo", "Al Dee", "Bo Al", "Al Bo"),
        lines(1, "Ava Ben"),
        lines(len(rows), *(a + " " + b for a, b in rows)),
    ]


def cp1_q5():
    rng = random.Random(10105)
    stations = rng.sample(range(0, 1000001), 6000)
    houses = [rng.randint(0, 1000000) for _ in range(6000)]
    return [
        lines("4 5", "12 3 20 8", "1 9 16 20 30"),
        lines("1 3", "10", "0 10 25"),
        lines("3 4", "500 100 900", "700 0 1000000 300"),
        lines("6000 6000", nums(stations), nums(houses)),
    ]


def cp1_q6():
    rng = random.Random(10106)
    big = rng.sample(range(1, 401), 150)
    return [
        lines(6, "2 8 5 11 4 14"),
        lines(5, "9 1 6 20 3"),
        lines(3, "1 2 4"),
        lines(3, "10 20 30"),
        lines(150, nums(big)),
    ]


# ---------------------------------------------------------------- Checkpoint 2
def cp2_q1():
    rng = random.Random(10201)
    needs = [rng.randint(1, 1000000) for _ in range(6000)]
    snacks = [rng.randint(1, 1000000) for _ in range(6000)]
    return [
        lines("4 5", "3 1 7 5", "2 4 1 6 8"),
        lines("2 2", "5 6", "1 4"),
        lines("3 5", "2 2 2", "2 2 1 1 3"),
        lines("1 1", "7", "7"),
        lines("6000 6000", nums(needs), nums(snacks)),
    ]


def cp2_q2():
    rng = random.Random(10202)
    kinds = ["FILL A", "FILL B", "EMPTY A", "EMPTY B", "POUR A B", "POUR B A", "POUR A B", "POUR B A"]
    commands = [rng.choice(kinds) for _ in range(10000)]
    return [
        lines("5 3", 6, "FILL A", "POUR A B", "EMPTY B", "POUR A B", "FILL A", "POUR A B"),
        lines("4 4", 4, "POUR A B", "FILL B", "POUR A B", "POUR B A"),
        lines("1000000000 999999999", 3, "FILL A", "POUR A B", "EMPTY B"),
        lines("7 3", 5, "FILL B", "POUR B A", "FILL B", "POUR B A", "FILL B"),
        lines("999999937 123456791", 10000, *commands),
    ]


def cp2_q3():
    rng = random.Random(10203)
    earn = [rng.randint(1, 1000) for _ in range(6000)]
    total = sum(earn)
    goals = [rng.randint(1, total + 10000) for _ in range(6000)]
    return [
        lines("5 5", "3 1 4 1 5", "4 1 9 14 15"),
        lines("1 3", "5", "1 5 6"),
        lines("4 4", "2 2 2 2", "2 3 8 9"),
        lines("3 2", "1000 1000 1000", "1000000000000 3000"),
        lines("6000 6000", nums(earn), nums(goals)),
    ]


def cp2_q4():
    rng = random.Random(10204)
    spots = sorted(rng.sample(range(1, 1000000000), 7000))
    tank = 0
    last = 0
    for s in spots:
        tank = max(tank, s - last)
        last = s
    tank = max(tank, 1000000000 - last)
    rng.shuffle(spots)
    return [
        lines("20 6 5", "5 11 2 8 16"),
        lines("10 10 0"),
        lines("30 10 3", "5 10 21"),
        lines("20 5 3", "15 5 10"),
        lines("1000000000 " + str(tank) + " 7000", nums(spots)),
    ]


def cp2_q5():
    rng = random.Random(10205)
    events = []
    for _ in range(12000):
        events.append(rng.choice("AB") + " " + str(rng.randint(1, 1000)))
    return [
        lines(7, "A 2", "B 2", "B 1", "A 3", "B 2", "A 1", "B 3"),
        lines(2, "A 1", "B 1"),
        lines(4, "A 1", "B 2", "A 2", "B 2"),
        lines(1, "B 5"),
        lines(12000, *events),
    ]


def cp2_q6_scale():
    rng = random.Random(10206)
    rows = []
    for _ in range(200):
        rows.append(nums(rng.randint(-9, 9) for _ in range(200)))
    return lines("200 200 100", *rows)


# ---------------------------------------------------------------- Checkpoint 3
def cp3_q1():
    return [
        lines("3 4", "....", ".#..", "...."),
        lines("1 1", "."),
        lines("2 2", ".#", "#."),
        lines("1 5", "....."),
        lines("4 4", "....", "#.#.", "....", ".#.."),
        lines("5 5", ".....", ".....", ".....", ".....", "....."),
    ]


def cp3_q2_scale():
    rng = random.Random(10302)
    tokens = []
    depth = 0
    for _ in range(18000):
        tokens.append(rng.choice("01"))
        depth += 1
        if rng.random() < 0.2:
            tokens.append("NOT")
    while depth > 1:
        tokens.append(rng.choice(["AND", "OR", "IMP", "IMP"]))
        depth -= 1
        if rng.random() < 0.15:
            tokens.append("NOT")
    return lines(" ".join(tokens))


def cp3_q3_scale():
    rng = random.Random(10303)
    half = "1" + "".join(rng.choice("01") for _ in range(28))
    text = half + "1" + half[::-1]
    return lines(str(int(text, 2)) + " 2")


def cp3_q4():
    rng = random.Random(10304)
    masks = []
    for _ in range(15):
        lamps = rng.sample(range(30), rng.randint(3, 12))
        masks.append(sum(1 << lamp for lamp in lamps))
    last = (1 << 30) - 1
    for i in rng.sample(range(15), 6):
        last ^= masks[i]
    masks.append(last)
    switches = []
    for mask in masks:
        lamps = [lamp for lamp in range(30) if mask >> lamp & 1]
        rng.shuffle(lamps)
        switches.append(str(len(lamps)) + " " + nums(lamps))
    return [
        lines("5 4", "3 1 2 4", "1 3", "2 0 2", "2 1 4"),
        lines("3 2", "2 0 1", "2 0 1"),
        lines("1 1", "1 0"),
        lines("5 3", "5 0 1 2 3 4", "2 1 3", "3 0 2 4"),
        lines("4 3", "2 0 1", "2 2 3", "4 0 1 2 3"),
        lines("30 16", *switches),
    ]


def cp3_q5():
    rng = random.Random(10305)
    points = []
    while len(points) < 4000:
        p = (rng.randint(-10**9, 10**9), rng.randint(-10**9, 10**9))
        if rng.random() < 0.3:
            step = rng.randint(1, 1000)
            p = (rng.randint(-10**6, 10**6) * step, rng.randint(-10**6, 10**6) * step)
        if not points or points[-1] != p:
            points.append(p)
    return [
        lines(4, "0 0", "4 6", "4 1", "-2 -2"),
        lines(2, "0 0", "5 0"),
        lines(3, "0 0", "3 5", "-2 -7"),
        lines(3, "0 0", "2 2", "0 0"),
        lines(2, "-1000000000 -1000000000", "1000000000 1000000000"),
        lines(len(points), *(str(x) + " " + str(y) for x, y in points)),
    ]


def random_tree(n: int, height: int, rng: random.Random):
    """Node 0 is the root; nodes 0..height-1 form a left spine, so the height is exactly `height`."""
    left = [-1] * n
    right = [-1] * n
    depth = [0] * n
    for i in range(1, height):
        left[i - 1] = i
        depth[i] = i
    slots = list(range(height - 1))
    for i in range(height, n):
        while True:
            k = rng.randrange(len(slots))
            parent = slots[k]
            if left[parent] == -1:
                left[parent] = i
                break
            if right[parent] == -1:
                right[parent] = i
                break
            slots[k] = slots[-1]
            slots.pop()
        depth[i] = depth[parent] + 1
        if depth[i] < height - 1:
            slots.append(i)
    return left, right


def cp3_q7_scale():
    rng = random.Random(10307)
    n = 6000
    left, right = random_tree(n, 900, rng)
    order = list(range(n))
    rng.shuffle(order)
    new_id = {old: new for new, old in enumerate(order)}
    new_id[-1] = -1
    rows = [""] * n
    for old in range(n):
        rows[new_id[old]] = f"{rng.randint(-1000, 1000)} {new_id[left[old]]} {new_id[right[old]]}"
    return lines(str(n) + " " + str(new_id[0]), *rows)


# ---------------------------------------------------------------- Checkpoint 4
def cp4_q1():
    rng = random.Random(10401)
    grid = ["".join("#" if rng.random() < 0.3 else "." for _ in range(20)) for _ in range(20)]
    queries = [str(rng.randrange(20)) + " " + str(rng.randrange(20)) for _ in range(12000)]
    return [
        lines("4 5 4", "..#..", ".##.#", "#...#", "##.#.", "0 0", "0 3", "1 1", "3 4"),
        lines("1 1 2", ".", "0 0", "0 0"),
        lines("2 3 3", "###", "#.#", "0 0", "1 1", "1 2"),
        lines("3 3 2", ".#.", "#.#", ".#.", "0 0", "1 1"),
        lines("20 20 12000", *grid, *queries),
    ]


def cp4_q2():
    rows, cols = 200, 400
    grid = []
    for r in range(rows):
        if r % 2 == 0:
            grid.append("." * cols)
        elif r % 4 == 1:
            grid.append("#" * (cols - 1) + ".")
        else:
            grid.append("." + "#" * (cols - 1))
    grid[0] = "M" + grid[0][1:]
    return [
        lines("3 4", "M..#", ".#..", "#..M"),
        lines("1 2", "M#"),
        lines("2 3", "M#.", "##."),
        lines("1 1", "M"),
        lines("2 5", "M...M", "....."),
        lines(str(rows) + " " + str(cols), *grid),
    ]


def cp4_q3():
    rng = random.Random(10403)
    n = 500
    edges = set()
    for i in range(1, n):
        edges.add((i, i + 1))
    while len(edges) < 9000:
        u = rng.randint(1, n)
        v = rng.randint(1, n)
        if u % 2 != v % 2:
            edges.add((min(u, v), max(u, v)))
    edge_list = sorted(edges)
    rng.shuffle(edge_list)
    return [
        lines("6 6", "1 2", "2 3", "3 4", "4 5", "5 6", "1 6"),
        lines("4 0"),
        lines("3 3", "1 2", "2 3", "3 1"),
        lines("7 5", "1 2", "2 3", "4 5", "5 6", "6 4"),
        lines("5 4", "1 2", "3 2", "3 4", "5 4"),
        lines(str(n) + " " + str(len(edge_list)), *(str(u) + " " + str(v) for u, v in edge_list)),
    ]


def cp4_q4_scale():
    rng = random.Random(10404)
    heights = [rng.randint(0, 1000000) for _ in range(12000)]
    return lines(12000, nums(heights))


def cp4_q5():
    rng = random.Random(10405)
    flavors = [rng.randint(1, 300) for _ in range(20000)]
    return [
        lines(8, "2 2 1 1 3 3 1 2"),
        lines(1, "42"),
        lines(4, "7 7 7 7"),
        lines(5, "5 4 3 2 1"),
        lines(6, "1 2 1 2 1 3"),
        lines(20000, nums(flavors)),
    ]


def cp4_q6():
    return [
        lines("3 6 100"),
        lines("5 0 1000"),
        lines("7 9 1"),
        lines("0 5 7"),
        lines("1 1000000000000000000 999999999999999989"),
        lines("2 63 1000000000000000000"),
        lines("123456789123456789 1000000000000000000 999999999999999999"),
    ]


# ---------------------------------------------------------------- Grand Mock Contest
def p1():
    rng = random.Random(10501)
    values = [rng.randint(-10**9, 10**9) for _ in range(7000)]
    return [
        lines(6, "4 -1 7 3 -2 5"),
        lines(2, "5 5"),
        lines(3, "-3 -3 6"),
        lines(4, "1000000000 -1000000000 1000000000 -1000000000"),
        lines(7000, nums(values)),
    ]


def p2():
    rows = cols = 300
    grid = [["."] * cols for _ in range(rows)]
    for r in range(rows):
        if r % 2 == 0:
            grid[r][cols - 1] = "\\"
            if r > 0:
                grid[r][0] = "\\"
        else:
            grid[r][cols - 1] = "/"
            grid[r][0] = "/"
    grid[rows - 1][0] = "."
    return [
        lines("3 3 1", "/.\\", "../", "..."),
        lines("1 1 0", "/"),
        lines("2 5 1", ".....", "....."),
        lines("3 4 0", "..\\.", "/./.", "\\..."),
        lines("300 300 0", *("".join(row) for row in grid)),
    ]


def p3():
    rng = random.Random(10503)
    spots = rng.sample(range(0, 1000000001), 7000)
    return [
        lines("6 3", "1 12 3 7 10 15"),
        lines("2 2", "5 100"),
        lines("4 4", "0 3 9 10"),
        lines("5 2", "8 1 4 9 2"),
        lines("7000 200", nums(spots)),
    ]


def p4():
    rng = random.Random(10504)
    values = rng.sample(range(0, 40000), 12000)
    return [
        lines("6 3", "1 7 4 10 5 13"),
        lines("3 2", "1 4 8"),
        lines("2 1000000000", "1000000000 0"),
        lines("5 1", "5 4 3 2 1"),
        lines("12000 7", nums(values)),
    ]


def p5():
    width, height = 70, 60
    edges = []

    def node(r, c):
        return r * width + c + 1

    for r in range(height):
        for c in range(width):
            if c + 1 < width:
                edges.append((node(r, c), node(r, c + 1)))
            if r + 1 < height:
                edges.append((node(r, c), node(r + 1, c)))
    rng = random.Random(10505)
    rng.shuffle(edges)
    n = width * height
    grid20 = []
    for r in range(20):
        for c in range(20):
            if c + 1 < 20:
                grid20.append(str(r * 20 + c + 1) + " " + str(r * 20 + c + 2))
            if r + 1 < 20:
                grid20.append(str(r * 20 + c + 1) + " " + str(r * 20 + c + 21))
    return [
        lines("6 7 1 6", "1 2", "1 3", "2 4", "3 4", "4 6", "3 5", "5 6"),
        lines("3 2 2 2", "1 2", "2 3"),
        lines("4 2 1 4", "1 2", "3 4"),
        lines("400 " + str(len(grid20)) + " 1 400", *grid20),
        lines(f"{n} {len(edges)} 1 {n}", *(str(u) + " " + str(v) for u, v in edges)),
    ]


def p6():
    rng = random.Random(10506)
    grid = ["".join("." if rng.random() < 0.45 else "#" for _ in range(20)) for _ in range(20)]
    return [
        lines("5 6", "######", "#..#.#", "#.##.#", "####..", "#.####"),
        lines("2 2", "..", ".."),
        lines("1 1", "#"),
        lines("7 7", "#######", "#.....#", "#.###.#", "#.#.#.#", "#.###.#", "#.....#", "#######"),
        lines("20 20", *grid),
    ]


def p8():
    rng = random.Random(10508)
    n = 6000
    left, right = random_tree(n, 500, rng)
    rows = []
    for i in range(n):
        rows.append(f"{rng.randint(0, 10**6)} {left[i] + 1 if left[i] != -1 else -1} "
                    f"{right[i] + 1 if right[i] != -1 else -1}")
    return [
        lines(7, "5 2 3", "3 4 -1", "8 5 6", "1 -1 -1", "2 7 -1", "6 -1 -1", "4 -1 -1"),
        lines(1, "1000000000 -1 -1"),
        lines(3, "1 2 -1", "2 3 -1", "3 -1 -1"),
        lines(7, "10 2 3", "20 4 -1", "30 -1 5", "1 6 7", "2 -1 -1", "3 -1 -1", "4 -1 -1"),
        lines(n, *rows),
    ]


REPLACED = [
    (CP1, "q4", cp1_q4), (CP1, "q5", cp1_q5), (CP1, "q6", cp1_q6),
    (CP2, "q1", cp2_q1), (CP2, "q2", cp2_q2), (CP2, "q3", cp2_q3), (CP2, "q4", cp2_q4),
    (CP2, "q5", cp2_q5),
    (CP3, "q1", cp3_q1), (CP3, "q4", cp3_q4), (CP3, "q5", cp3_q5),
    (CP4, "q1", cp4_q1), (CP4, "q2", cp4_q2), (CP4, "q3", cp4_q3), (CP4, "q5", cp4_q5),
    (CP4, "q6", cp4_q6),
    (PRJ, "p1", p1), (PRJ, "p2", p2), (PRJ, "p3", p3), (PRJ, "p4", p4), (PRJ, "p5", p5),
    (PRJ, "p6", p6), (PRJ, "p8", p8),
]

EXTRA = [
    (CP2, "q6", 6, cp2_q6_scale),
    (CP3, "q2", 6, cp3_q2_scale),
    (CP3, "q3", 9, cp3_q3_scale),
    (CP3, "q7", 6, cp3_q7_scale),
    (CP4, "q4", 7, cp4_q4_scale),
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
    for assets, stem, number, make in EXTRA:
        case = assets / stem / f"{number}.in"
        case.write_text(make(), encoding="utf-8")
        solve(assets, stem, case)


if __name__ == "__main__":
    main()

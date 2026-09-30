import sys


def pair_key(pair):
    return (pair[0], pair[1])


data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
picks = set()
order = []
i = 0
while i < n:
    picker = tokens[1 + 2 * i]
    picked = tokens[2 + 2 * i]
    if (picker, picked) not in picks:
        picks.add((picker, picked))
        order.append((picker, picked))
    i = i + 1

pairs = []
i = 0
while i < len(order):
    picker = order[i][0]
    picked = order[i][1]
    if picker < picked and (picked, picker) in picks:
        pairs.append((picker, picked))
    i = i + 1

ranked = sorted(pairs, key=pair_key)
print(str(len(ranked)))
i = 0
while i < len(ranked):
    print(ranked[i][0] + " " + ranked[i][1])
    i = i + 1

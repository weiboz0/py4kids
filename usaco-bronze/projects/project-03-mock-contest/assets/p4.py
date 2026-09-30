import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
gap = int(tokens[1])
values = []
i = 0
while i < n:
    values.append(int(tokens[2 + i]))
    i = i + 1
values.sort()

pairs = 0
hi = 0
lo = 0
while lo < n:
    while hi < n and values[hi] - values[lo] < gap:
        hi = hi + 1
    if hi < n and values[hi] - values[lo] == gap:
        pairs = pairs + 1
    lo = lo + 1
print(str(pairs))

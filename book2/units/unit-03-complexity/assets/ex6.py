import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
values = []
i = 0
while i < n:
    values.append(int(parts[i + 1]))
    i = i + 1
values.sort()
best = values[1] - values[0]
i = 2
while i < n:
    gap = values[i] - values[i - 1]
    if gap < best:
        best = gap
    i = i + 1
print(str(best))

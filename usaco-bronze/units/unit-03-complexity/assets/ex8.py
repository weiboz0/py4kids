import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
limit = int(parts[1])
positions = []
i = 0
while i < n:
    positions.append(int(parts[i + 2]))
    i = i + 1
positions.sort()
best = -1
i = 1
while i < n:
    gap = positions[i] - positions[i - 1]
    if gap <= limit and gap > best:
        best = gap
    i = i + 1
print(str(best))

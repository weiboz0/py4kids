import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
first = int(parts[1])
current = first
best = first
i = 1
while i < n:
    value = int(parts[i + 1])
    if current + value < value:
        current = value
    else:
        current = current + value
    if current > best:
        best = current
    i = i + 1
print(str(best))

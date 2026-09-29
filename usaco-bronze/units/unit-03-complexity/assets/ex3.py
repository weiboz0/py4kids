import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
target = int(parts[1])
current = 0
best = 0
i = 0
while i < n:
    score = int(parts[i + 2])
    if score >= target:
        current = current + 1
        if current > best:
            best = current
    else:
        current = 0
    i = i + 1
print(str(best))

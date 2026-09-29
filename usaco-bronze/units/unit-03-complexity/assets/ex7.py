import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
seen = {}
answer = -1
i = 0
while i < n:
    value = int(parts[i + 1])
    if answer == -1 and seen.get(value, 0) > 0:
        answer = value
    seen[value] = 1
    i = i + 1
print(str(answer))

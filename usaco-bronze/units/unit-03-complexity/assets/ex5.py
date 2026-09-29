import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
target = int(parts[1])
seen = {}
found = False
i = 0
while i < n:
    value = int(parts[i + 2])
    needed = target - value
    if seen.get(needed, 0) > 0:
        found = True
    seen[value] = seen.get(value, 0) + 1
    i = i + 1
answer = "NO"
if found:
    answer = "YES"
print(answer)

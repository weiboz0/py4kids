import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
waiting = {}
pairs = 0
i = 0
while i < n:
    grade = int(parts[i * 2 + 1])
    color = parts[i * 2 + 2]
    group = (grade, color)
    waiting[group] = waiting.get(group, 0) + 1
    if waiting[group] == 2:
        pairs = pairs + 1
        waiting[group] = 0
    i = i + 1
print(str(pairs))

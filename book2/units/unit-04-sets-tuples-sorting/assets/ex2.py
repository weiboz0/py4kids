import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
m = int(parts[1])
robotics = set()
i = 0
while i < n:
    robotics.add(parts[i + 2])
    i = i + 1
both = set()
i = 0
while i < m:
    name = parts[n + i + 2]
    if name in robotics:
        both.add(name)
    i = i + 1
print(str(len(both)))

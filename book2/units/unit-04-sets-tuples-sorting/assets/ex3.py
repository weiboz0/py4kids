import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
m = int(parts[1])
first = set()
i = 0
while i < n:
    first.add(parts[i + 2])
    i = i + 1
second = set()
i = 0
while i < m:
    second.add(parts[n + i + 2])
    i = i + 1
only_first = first - second
print(str(len(only_first)))

import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
m = int(tokens[1])
first = set()
second = set()
for position in range(n):
    first.add(tokens[position + 2])
for position in range(m):
    second.add(tokens[position + n + 2])
only_first = first - second
print(str(len(only_first)))

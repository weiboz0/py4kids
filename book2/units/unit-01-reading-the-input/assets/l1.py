import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
values = []
for position in range(n):
    values.append(int(tokens[position + 1]))
total = sum(values)
biggest = max(values)
print(f"{total} {biggest}")

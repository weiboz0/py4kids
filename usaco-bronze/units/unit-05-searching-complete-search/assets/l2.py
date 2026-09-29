import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
target = int(tokens[1])
values = []
for position in range(n):
    values.append(int(tokens[position + 2]))

answer = "NO"
for first in range(n):
    for second in range(first + 1, n):
        if values[first] + values[second] == target:
            answer = "YES"
print(answer)

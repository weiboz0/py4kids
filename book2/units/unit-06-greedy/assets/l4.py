import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
budget = int(tokens[1])
costs = []
for position in range(n):
    costs.append(int(tokens[position + 2]))
costs.sort()

spent = 0
selected = 0
for cost in costs:
    if spent + cost <= budget:
        spent = spent + cost
        selected = selected + 1
print(str(selected))

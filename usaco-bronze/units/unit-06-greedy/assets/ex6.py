import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
budget = int(parts[1])
costs = []
i = 0
while i < n:
    costs.append(int(parts[i + 2]))
    i = i + 1
costs.sort()
spent = 0
selected = 0
i = 0
while i < n and spent + costs[i] <= budget:
    spent = spent + costs[i]
    selected = selected + 1
    i = i + 1
print(str(selected))

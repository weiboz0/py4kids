import sys

data = sys.stdin.read()
parts = data.split()
item_count = int(parts[0])
budget = int(parts[1])
costs = []
i = 0
while i < item_count:
    costs.append(int(parts[i + 2]))
    i = i + 1

ordered_costs = sorted(costs)
spent = 0
bought = 0
can_buy = 1
i = 0
while i < item_count and can_buy == 1:
    if spent + ordered_costs[i] <= budget:
        spent = spent + ordered_costs[i]
        bought = bought + 1
    else:
        can_buy = 0
    i = i + 1
print(str(bought))

import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
budget = int(tokens[1])
cost = []
i = 0
while i < n:
    cost.append(int(tokens[2 + i]))
    i = i + 1
left = 0
window = 0
best = 0
right = 0
while right < n:
    window = window + cost[right]
    while window > budget:
        window = window - cost[left]
        left = left + 1
    span = right - left + 1
    if span > best:
        best = span
    right = right + 1
print(str(best))

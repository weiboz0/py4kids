import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
day_limit = int(tokens[1])
weights = []
for position in range(n):
    weights.append(int(tokens[position + 2]))

lo = max(weights)
hi = sum(weights)
while lo < hi:
    mid = (lo + hi) // 2
    days = 1
    load = 0
    for weight in weights:
        if load + weight > mid:
            days = days + 1
            load = 0
        load = load + weight
    if days <= day_limit:
        hi = mid
    else:
        lo = mid + 1
print(str(lo))

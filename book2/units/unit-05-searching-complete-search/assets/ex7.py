import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
allowed_days = int(parts[1])
weights = []
i = 0
while i < n:
    weights.append(int(parts[i + 2]))
    i = i + 1
lo = max(weights)
hi = sum(weights)
while lo < hi:
    mid = (lo + hi) // 2
    days = 1
    load = 0
    i = 0
    while i < n:
        if load + weights[i] > mid:
            days = days + 1
            load = weights[i]
        else:
            load = load + weights[i]
        i = i + 1
    if days <= allowed_days:
        hi = mid
    else:
        lo = mid + 1
print(str(lo))

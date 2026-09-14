import sys

data = sys.stdin.read()
parts = data.split()
value_count = int(parts[0])
target = int(parts[1])
values = []
i = 0
while i < value_count:
    values.append(int(parts[i + 2]))
    i = i + 1

lo = 0
hi = value_count - 1
best_distance = abs(values[lo] + values[hi] - target)
while lo < hi:
    pair_sum = values[lo] + values[hi]
    distance = abs(pair_sum - target)
    if distance < best_distance:
        best_distance = distance
    if pair_sum < target:
        lo = lo + 1
    else:
        hi = hi - 1
print(str(best_distance))

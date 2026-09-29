import sys

data = sys.stdin.read()
parts = data.split()
student_count = int(parts[0])
limit = int(parts[1])
weights = []
i = 0
while i < student_count:
    weights.append(int(parts[i + 2]))
    i = i + 1
weights = sorted(weights)

lo = 0
hi = student_count - 1
boat_count = 0
while lo <= hi:
    if lo < hi and weights[lo] + weights[hi] <= limit:
        lo = lo + 1
    hi = hi - 1
    boat_count = boat_count + 1
print(str(boat_count))

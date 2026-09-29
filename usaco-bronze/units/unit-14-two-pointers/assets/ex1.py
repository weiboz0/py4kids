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

answer = "NO"
lo = 0
hi = value_count - 1
while lo < hi and answer == "NO":
    pair_sum = values[lo] + values[hi]
    if pair_sum == target:
        answer = "YES"
    elif pair_sum < target:
        lo = lo + 1
    else:
        hi = hi - 1
print(answer)

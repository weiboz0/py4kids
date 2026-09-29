import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
target = int(tokens[1])
values = []
i = 0
while i < n:
    values.append(int(tokens[i + 2]))
    i = i + 1

answer = "NO"
lo = 0
hi = n - 1
while lo < hi and answer == "NO":
    pair_sum = values[lo] + values[hi]
    if pair_sum == target:
        answer = "YES"
    elif pair_sum < target:
        lo = lo + 1
    else:
        hi = hi - 1
print(answer)

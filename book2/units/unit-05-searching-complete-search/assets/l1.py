import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
values = []
for position in range(n):
    values.append(int(tokens[position + 1]))
target = int(tokens[n + 1])
ordered = sorted(values)

answer = "NO"
lo = 0
hi = n - 1
while lo <= hi and answer == "NO":
    mid = (lo + hi) // 2
    if ordered[mid] == target:
        answer = "YES"
    elif ordered[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1
print(answer)

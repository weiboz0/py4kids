import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
target = int(parts[1])
values = []
i = 0
while i < n:
    values.append(int(parts[i + 2]))
    i = i + 1
values = sorted(values)
answer = "NO"
i = 0
while i < n - 1 and answer == "NO":
    complement = target - values[i]
    lo = i + 1
    hi = n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if values[mid] == complement:
            answer = "YES"
            lo = hi + 1
        elif values[mid] < complement:
            lo = mid + 1
        else:
            hi = mid - 1
    i = i + 1
print(answer)

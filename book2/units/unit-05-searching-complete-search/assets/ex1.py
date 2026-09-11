import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
q = int(parts[1])
values = []
i = 0
while i < n:
    values.append(int(parts[i + 2]))
    i = i + 1
values = sorted(values)
output = ""
i = 0
while i < q:
    target = int(parts[n + i + 2])
    lo = 0
    hi = n - 1
    answer = "NO"
    while lo <= hi:
        mid = (lo + hi) // 2
        if values[mid] == target:
            answer = "YES"
            lo = hi + 1
        elif values[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    if i > 0:
        output = output + "\n"
    output = output + answer
    i = i + 1
print(output)

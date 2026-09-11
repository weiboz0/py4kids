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

def lower_bound(target):
    lo = 0
    hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

def upper_bound(target):
    lo = 0
    hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

output = ""
i = 0
while i < q:
    target = int(parts[n + i + 2])
    count = upper_bound(target) - lower_bound(target)
    if i > 0:
        output = output + "\n"
    output = output + str(count)
    i = i + 1
print(output)

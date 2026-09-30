import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
q = int(tokens[1])
prefix = [0]
i = 0
while i < n:
    prefix.append(prefix[i] + int(tokens[2 + i]))
    i = i + 1

i = 0
while i < q:
    goal = int(tokens[2 + n + i])
    lo = 1
    hi = n + 1
    while lo < hi:
        mid = (lo + hi) // 2
        if prefix[mid] >= goal:
            hi = mid
        else:
            lo = mid + 1
    if lo == n + 1:
        print("-1")
    else:
        print(str(lo))
    i = i + 1

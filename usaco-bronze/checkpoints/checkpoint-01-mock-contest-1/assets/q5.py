import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
q = int(tokens[1])
stations = []
i = 0
while i < n:
    stations.append(int(tokens[2 + i]))
    i = i + 1
stations.sort()

i = 0
while i < q:
    house = int(tokens[2 + n + i])
    lo = 0
    hi = n
    while lo < hi:
        mid = (lo + hi) // 2
        if stations[mid] < house:
            lo = mid + 1
        else:
            hi = mid
    best = -1
    if lo < n:
        best = stations[lo] - house
    if lo > 0:
        gap = house - stations[lo - 1]
        if best == -1 or gap < best:
            best = gap
    print(str(best))
    i = i + 1

import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0]); k = int(tokens[1])
w = []
i = 0
while i < n:
    w.append(int(tokens[2 + i]))
    i = i + 1

def groups_needed(cap):
    groups = 1
    current = 0
    j = 0
    while j < n:
        if current + w[j] > cap:
            groups = groups + 1
            current = w[j]
        else:
            current = current + w[j]
        j = j + 1
    return groups

lo = max(w)
hi = sum(w)
while lo < hi:
    mid = (lo + hi) // 2
    if groups_needed(mid) <= k:
        hi = mid
    else:
        lo = mid + 1
print(str(lo))

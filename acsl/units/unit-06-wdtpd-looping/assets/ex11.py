parts = input().split()
n = int(parts[0])
m = int(parts[1])
best = -1
at = 0
for k in range(n, 0, -1):
    r = m % k
    if r > best:
        best = r
        at = k
print(best, at)

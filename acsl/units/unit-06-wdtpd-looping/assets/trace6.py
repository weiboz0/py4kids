n = int(input())
best = 0
where = 0
for k in range(1, 9):
    v = (n * k) % 11
    if v > best:
        best = v
        where = k
print(best, where)

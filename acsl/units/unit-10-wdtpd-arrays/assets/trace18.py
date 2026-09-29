F = [0]
for i in range(1, 31):
    F.append(0)
for i in range(2, 31):
    if F[i] == 0:
        for j in range(2 * i, 31, i):
            F[j] = F[j] + 1
count = 0
best = 0
where = 0
for i in range(1, 31):
    if F[i] == 2:
        count = count + 1
    if F[i] > best:
        best = F[i]
        where = i
print(count, best, where)

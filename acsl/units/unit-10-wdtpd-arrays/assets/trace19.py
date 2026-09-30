A = []
for r in range(5):
    row = []
    for c in range(5):
        row.append(0)
    A.append(row)
k = 1
for r in range(1, 5):
    if r % 2 == 1:
        for c in range(1, 5):
            A[r][c] = k
            k = k + 1
    else:
        for c in range(4, 0, -1):
            A[r][c] = k
            k = k + 1
s = 0
for i in range(1, 5):
    s = s + A[i][i] - A[i][5 - i]
print(A[3][2], s)

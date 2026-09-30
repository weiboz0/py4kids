A = []
for r in range(5):
    row = []
    for c in range(5):
        row.append((r * c) % 3 + r)
    A.append(row)
h = 0
v = 0
for r in range(1, 5):
    for c in range(1, 4):
        if A[r][c] == A[r][c + 1]:
            h = h + 1
        if A[c][r] == A[c + 1][r]:
            v = v + 1
print(h, v)

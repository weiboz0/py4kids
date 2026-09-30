A = []
for r in range(5):
    row = []
    for c in range(5):
        row.append(0)
    A.append(row)
for r in range(1, 5):  # ACSL: FOR r = 1 TO 4
    for c in range(1, 5):  # ACSL: FOR c = 1 TO 4
        A[r][c] = (r * c + r) % 5
s = 0
for k in range(1, 5):  # ACSL: FOR k = 1 TO 4
    s = s + A[k][k] - A[k][5 - k]
print(s)

A = []
for r in range(5):
    row = []
    for c in range(5):
        row.append(r * c - (r + c))
    A.append(row)
d1 = 0
d2 = 0
for i in range(1, 5):
    d1 = d1 + A[i][i]
    d2 = d2 + A[i][5 - i]
print(d1, d2)

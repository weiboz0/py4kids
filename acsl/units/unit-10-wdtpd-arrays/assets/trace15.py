A = [[1, 2, 3],
     [4, 5, 6],
     [7, 8, 9]]
for r in range(3):
    for c in range(r + 1, 3):
        t = A[r][c]
        A[r][c] = A[c][r]
        A[c][r] = t
print(A[0][2], A[2][1], A[1][0])

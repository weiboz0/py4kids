A = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]
for r in range(1, 5):
    for c in range(1, 5):
        if r == c:
            A[r][c] = r * 2
        elif r < c:
            A[r][c] = c - r
        else:
            A[r][c] = A[r - 1][c] + c
s = 0
for k in range(1, 5):
    s = s + A[k][5 - k]
print(s)

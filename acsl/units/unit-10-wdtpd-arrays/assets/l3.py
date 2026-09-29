n = int(input())
A = []
row = []
for c in range(n + 1):
    row.append(0)
A.append(row)
for r in range(n):
    row = [0]
    for piece in input().split():
        row.append(int(piece))
    A.append(row)
d1 = 0
d2 = 0
for i in range(1, n + 1):
    d1 = d1 + A[i][i]
    d2 = d2 + A[i][n + 1 - i]
same = 0
for r in range(1, n + 1):
    s = 0
    for c in range(1, n + 1):
        s = s + A[r][c]
    if s == d1:
        same = same + 1
print(d1, d2, same)

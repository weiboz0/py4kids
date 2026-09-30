first = input().split()
n = int(first[0])
k = int(first[1])
P = []
for r in range(n + 1):
    row = []
    for c in range(n + 1):
        row.append(0)
    P.append(row)
P[0][0] = 1
for r in range(1, n + 1):
    P[r][0] = 1
    for c in range(1, r + 1):
        P[r][c] = P[r - 1][c - 1] + P[r - 1][c]
s = 0
for c in range(n + 1):
    s = s + P[n][c]
print(P[n][k], s)

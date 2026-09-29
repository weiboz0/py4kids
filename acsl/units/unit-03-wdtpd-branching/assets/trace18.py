S = "PYTHON"
A = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
for r in range(1, 4):
    for c in range(1, 4):
        A[r][c] = (r * 2 + c * 3) % 6
r = 1
c = 1
out = ""
steps = 0
while steps < 6:
    v = A[r][c]
    out = out + S[v]
    if v % 2 == 0:
        r = r % 3 + 1
    else:
        A[r][c] = v - 1
        c = c % 3 + 1
    steps = steps + 1
print(out)

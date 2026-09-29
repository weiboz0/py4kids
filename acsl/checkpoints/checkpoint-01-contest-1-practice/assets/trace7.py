import math

S = "COMPUTERS"
A = []
for r in range(4):
    A.append([0, 0, 0, 0])
for r in range(1, 4):
    for c in range(1, 4):
        A[r][c] = r * c - 2
t = 0
for k in range(1, 4, 2):
    t = t + A[k][4 - k]
x = math.floor((t - 7) / 2)
y = math.floor(math.sqrt(A[3][3] + 2))
while abs(x) < 10:
    x = x * y
p = abs(x) % 4
w = S[p:p + 3]  # ACSL S[p:p + 2] = positions p through p + 2
print(w)

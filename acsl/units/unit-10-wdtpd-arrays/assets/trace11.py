A = [0, 9, 4, 7, 1, 6, 3, 8]
n = 7
for i in range(1, n // 2 + 1):
    t = A[i]
    A[i] = A[n + 1 - i]
    A[n + 1 - i] = t
s = 0
for i in range(1, n + 1):
    s = s + i * A[i]
print(A[1], A[4], s)

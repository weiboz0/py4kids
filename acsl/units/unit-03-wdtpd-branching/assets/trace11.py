A = [0, 4, 9, 2, 7, 5, 8]
n = 6
for j in range(1, n):
    if A[j] > A[j + 1]:
        t = A[j]
        A[j] = A[j + 1]
        A[j + 1] = t
print(A[2], A[4], A[6])

A = [0, 2, 5, 1, 4, 3]
for i in range(2, 6):
    A[i] = A[i] + A[i - 1]
print(A[3], A[5], A[5] - A[2])

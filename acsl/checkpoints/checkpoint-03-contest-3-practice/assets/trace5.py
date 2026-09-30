A = [4, 7, 1, 8, 3, 6, 2]
n = len(A)
for i in range(n // 2):
    temp = A[i]
    A[i] = A[n - 1 - i]
    A[n - 1 - i] = temp
for i in range(1, n):
    if A[i] < A[i - 1]:
        A[i] = A[i] + A[i - 1]
print(A[n - 1] - A[0], A[3])

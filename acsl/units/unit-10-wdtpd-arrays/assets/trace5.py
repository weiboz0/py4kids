A = [6, 2, 8, 5, 1, 7]
swaps = 0
for i in range(len(A) - 1):
    if A[i] > A[i + 1]:
        t = A[i]
        A[i] = A[i + 1]
        A[i + 1] = t
        swaps = swaps + 1
print(A[0], A[2], A[5], swaps)

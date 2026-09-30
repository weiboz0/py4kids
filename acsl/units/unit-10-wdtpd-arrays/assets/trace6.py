A = [0, 3, 7, 2, 9, 4]
for k in range(1, 3):
    t = A[1]
    for i in range(1, 5):
        A[i] = A[i + 1]
    A[5] = t
print(A[1], A[3], A[5])

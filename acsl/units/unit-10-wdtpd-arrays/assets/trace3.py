A = [0, 5, 8, 1, 6, 3]
n = 5
B = [0]
for i in range(1, n + 1):
    B.append(A[i] - A[n + 1 - i])
print(B[1], B[2], B[3], B[4], B[5])

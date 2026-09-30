parts = input().split()
A = []
for piece in parts:
    A.append(int(piece))
C = [0, 0, 0, 0, 0, 0, 0]
for i in range(len(A)):
    C[A[i]] = C[A[i]] + 1
most = 0
for v in range(1, 7):
    if C[v] > C[most]:
        most = v
print(most, C[most], C[4])

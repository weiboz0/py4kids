first = input().split()
n = int(first[0])
k = int(first[1])
parts = input().split()
A = [0]
for piece in parts:
    A.append(int(piece))
for j in range(k):
    t = A[n]
    for i in range(n, 1, -1):
        A[i] = A[i - 1]
    A[1] = t
line = str(A[1])
for i in range(2, n + 1):
    line = line + " " + str(A[i])
print(line)

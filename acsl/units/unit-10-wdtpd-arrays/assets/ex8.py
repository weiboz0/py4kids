n = int(input())
parts = input().split()
A = [0]
for piece in parts:
    A.append(int(piece))
count = 1
best = A[n]
for i in range(n - 1, 0, -1):
    if A[i] > best:
        count = count + 1
        best = A[i]
print(count, best)

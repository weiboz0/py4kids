n = int(input())
parts = input().split()
A = [0]
for piece in parts:
    A.append(int(piece))
best = A[1] + A[n]
at = 1
for i in range(2, n // 2 + 1):
    if A[i] + A[n + 1 - i] > best:
        best = A[i] + A[n + 1 - i]
        at = i
print(best, at)

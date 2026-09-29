n = int(input())
A = [0]
for i in range(1, n + 1):
    A.append(i * i - 3 * i)
s = 0
for i in range(1, n + 1):
    if A[i] > 0:
        s = s + A[i]
print(s, A[3])

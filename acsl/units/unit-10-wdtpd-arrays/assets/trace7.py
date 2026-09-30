A = [0, 4, 1, 6, 3, 8]
for i in range(2, 6):
    A[i] = A[i - 1]
s = 0
for i in range(1, 6):
    s = s + A[i]
print(s)

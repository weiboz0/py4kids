A = [7, 3, 9, 3, 8, 1, 6]
count = 0
total = 0
for i in range(len(A)):
    if A[i] > i:
        count = count + 1
        total = total + i
print(count, total)

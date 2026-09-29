n = int(input())
total = 0
for i in range(1, n + 1):
    for j in range(i, 0, -2):
        total = total + j
print(total)

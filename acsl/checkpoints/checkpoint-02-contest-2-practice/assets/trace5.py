n = int(input())
total = 0
for i in range(1, n + 1):
    for j in range(i, n + 1, 2):
        if (i + j) % 3 == 0:
            total = total + i * j
print(total)

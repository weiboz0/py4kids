import math

n = int(input())
total = 0
for i in range(n, 0, -2):
    for j in range(1, math.floor(i / 2) + 1):
        if i % j == 0:
            total = total + j
        else:
            total = total - 1
print(total)

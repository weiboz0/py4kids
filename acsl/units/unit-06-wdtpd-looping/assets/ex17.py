parts = input().split()
n = int(parts[0])
m = int(parts[1])
count = 0
for i in range(1, n):
    for j in range(i + 1, n + 1):
        if (i * j) % m == 0:
            count = count + 1
print(count)

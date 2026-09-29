n = int(input())
best = -1
for i in range(n):
    parts = input().split()
    value = int(parts[0], int(parts[1]))
    if value > best:
        best = value
print(best)

n = int(input())
parts = input().split()
values = []
for i in range(n):
    values.append(int(parts[i]))
best = values[0] * values[1]
for i in range(n):
    for j in range(i + 1, n):
        product = values[i] * values[j]
        if product > best:
            best = product
print(best)

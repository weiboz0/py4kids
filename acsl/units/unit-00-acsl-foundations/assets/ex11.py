n = int(input())
parts = input().split()
values = []
for i in range(n):
    values.append(int(parts[i]))
count = 0
for i in range(n):
    for j in range(i + 1, n):
        if values[i] > values[j]:
            count = count + 1
print(count)

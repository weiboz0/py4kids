first = input().split()
n = int(first[0])
target = int(first[1])
parts = input().split()
values = []
for position in range(n):
    values.append(int(parts[position]))
count = 0
found = (0, 0)
for i in range(n):
    for j in range(i + 1, n):
        if values[i] + values[j] == target:
            count = count + 1
            if count == 1:
                found = (values[i], values[j])
print(count)
if count == 0:
    print("NONE")
else:
    a, b = found
    print(a, b)

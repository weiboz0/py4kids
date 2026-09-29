values = []
for part in input().split():
    values.append(int(part))
count = 0
last = (0, 0)
for i in range(len(values)):
    for j in range(i + 1, len(values)):
        if values[i] + values[j] == 10:
            count = count + 1
            last = (i + 1, j + 1)
print(count, last[0], last[1])

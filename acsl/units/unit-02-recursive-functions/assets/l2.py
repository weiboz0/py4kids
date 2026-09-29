n = int(input())
table = []
for x in range(n + 1):
    if x <= 1:
        table.append(x)
    else:
        table.append(table[x - 1] + 2 * table[x - 2])
row = str(table[0])
for x in range(1, n + 1):
    row = row + " " + str(table[x])
print(row)

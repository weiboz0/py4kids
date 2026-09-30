def spot(names, letter):
    for i in range(len(names)):
        if names[i] == letter:
            return i
    return -1


def zeros(n):
    grid = []
    for r in range(n):
        row = []
        for c in range(n):
            row.append(0)
        grid.append(row)
    return grid


def multiply(x, y):
    n = len(x)
    product = zeros(n)
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(n):
                total = total + x[i][k] * y[k][j]
            product[i][j] = total
    return product


names = input()
edges = input().split()
p = int(input())

n = len(names)
m = zeros(n)
for edge in edges:
    m[spot(names, edge[0])][spot(names, edge[1])] = 1

power = m
for step in range(p - 1):
    power = multiply(power, m)

for r in range(n):
    line = names[r] + ":"
    for c in range(n):
        line = line + " " + str(power[r][c])
    print(line)

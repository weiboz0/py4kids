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
ends = input().split()

m = zeros(len(names))
for edge in edges:
    m[spot(names, edge[0])][spot(names, edge[1])] = 1

square = multiply(m, m)
cube = multiply(square, m)
x = spot(names, ends[0])
y = spot(names, ends[1])
print(square[x][y])
print(cube[x][y])

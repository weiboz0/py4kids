def spot(names, letter):
    for i in range(len(names)):
        if names[i] == letter:
            return i
    return -1


names = input()
edges = input().split()

n = len(names)
matrix = []
for r in range(n):
    row = []
    for c in range(n):
        row.append(0)
    matrix.append(row)

for edge in edges:
    a = spot(names, edge[0])
    b = spot(names, edge[1])
    matrix[a][b] = 1
    matrix[b][a] = 1

for r in range(n):
    line = ""
    for c in range(n):
        if c > 0:
            line = line + " "
        line = line + str(matrix[r][c])
    print(names[r] + ": " + line + "  degree " + str(sum(matrix[r])))

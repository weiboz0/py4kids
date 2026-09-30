def spot(names, letter):
    for i in range(len(names)):
        if names[i] == letter:
            return i
    return -1


kind = input()
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
    if kind == "UNDIRECTED":
        matrix[b][a] = 1

for r in range(n):
    line = str(matrix[r][0])
    for c in range(1, n):
        line = line + " " + str(matrix[r][c])
    print(line)

for v in range(n):
    out_degree = 0
    in_degree = 0
    for k in range(n):
        out_degree = out_degree + matrix[v][k]
        in_degree = in_degree + matrix[k][v]
    print(names[v], out_degree, in_degree)

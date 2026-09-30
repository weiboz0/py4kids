def spot(names, letter):
    for i in range(len(names)):
        if names[i] == letter:
            return i
    return -1


def extend(path, length, names, matrix):
    if len(path) == length + 1:
        print(path)
        return 1
    found = 0
    last = spot(names, path[len(path) - 1])
    for c in range(len(names)):
        if matrix[last][c] == 1 and names[c] not in path:
            found = found + extend(path + names[c], length, names, matrix)
    return found


names = input()
edges = input().split()
parts = input().split()
start = parts[0]
length = int(parts[1])

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

print("total:", extend(start, length, names, matrix))

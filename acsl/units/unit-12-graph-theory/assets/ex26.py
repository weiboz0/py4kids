def spot(names, letter):
    for i in range(len(names)):
        if names[i] == letter:
            return i
    return -1


def loops(first, here, visited, matrix):
    found = 0
    for nxt in range(len(matrix)):
        if matrix[here][nxt] == 1:
            if nxt == first:
                found = found + 1
            elif nxt > first and not visited[nxt]:
                visited[nxt] = True
                found = found + loops(first, nxt, visited, matrix)
                visited[nxt] = False
    return found


names = input()
edges = input().split()

n = len(names)
matrix = []
visited = []
for r in range(n):
    row = []
    for c in range(n):
        row.append(0)
    matrix.append(row)
    visited.append(False)

for edge in edges:
    matrix[spot(names, edge[0])][spot(names, edge[1])] = 1

total = 0
for first in range(n):
    visited[first] = True
    total = total + loops(first, first, visited, matrix)
    visited[first] = False
print(total)

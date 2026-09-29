import sys

data = sys.stdin.read()
def flood(grid, rows, columns, row, column, visited):
    visited.add((row, column))
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    i = 0
    while i < len(directions):
        next_row = row + directions[i][0]
        next_column = column + directions[i][1]
        inside = 0 <= next_row and next_row < rows and 0 <= next_column and next_column < columns
        if inside and grid[next_row][next_column] == "#" and (next_row, next_column) not in visited:
            flood(grid, rows, columns, next_row, next_column, visited)
        i = i + 1

parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
grid = []
i = 0
while i < rows:
    grid.append(parts[2 + i])
    i = i + 1
visited = {(-1, -1)}
islands = 0
row = 0
while row < rows:
    column = 0
    while column < columns:
        if grid[row][column] == "#" and (row, column) not in visited:
            islands = islands + 1
            flood(grid, rows, columns, row, column, visited)
        column = column + 1
    row = row + 1
print(str(islands))

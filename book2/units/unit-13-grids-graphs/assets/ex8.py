import sys

data = sys.stdin.read()
def meadow_size(grid, rows, columns, row, column, visited):
    visited.add((row, column))
    size = 1
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    i = 0
    while i < len(directions):
        next_row = row + directions[i][0]
        next_column = column + directions[i][1]
        inside = 0 <= next_row and next_row < rows and 0 <= next_column and next_column < columns
        if inside and grid[next_row][next_column] == "." and (next_row, next_column) not in visited:
            size = size + meadow_size(grid, rows, columns, next_row, next_column, visited)
        i = i + 1
    return size

parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
grid = []
i = 0
while i < rows:
    grid.append(parts[2 + i])
    i = i + 1
visited = {(-1, -1)}
largest = 0
row = 0
while row < rows:
    column = 0
    while column < columns:
        if grid[row][column] == "." and (row, column) not in visited:
            size = meadow_size(grid, rows, columns, row, column, visited)
            largest = max(largest, size)
        column = column + 1
    row = row + 1
print(str(largest))

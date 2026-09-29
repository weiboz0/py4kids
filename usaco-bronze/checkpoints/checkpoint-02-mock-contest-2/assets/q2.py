import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
row = int(parts[2])
column = int(parts[3])
grid = []
i = 0
while i < rows:
    grid.append(parts[4 + i])
    i = i + 1
commands = parts[4 + rows]

i = 0
while i < len(commands):
    next_row = row
    next_column = column
    if commands[i] == "U":
        next_row = next_row - 1
    elif commands[i] == "D":
        next_row = next_row + 1
    elif commands[i] == "L":
        next_column = next_column - 1
    else:
        next_column = next_column + 1

    inside_rows = next_row >= 0 and next_row < rows
    inside_columns = next_column >= 0 and next_column < columns
    if inside_rows and inside_columns:
        if grid[next_row][next_column] != "#":
            row = next_row
            column = next_column
    i = i + 1
print(grid[row][column])

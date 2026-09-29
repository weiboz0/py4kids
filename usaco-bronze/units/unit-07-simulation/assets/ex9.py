import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
step_count = int(parts[2])
ant_row = int(parts[3])
ant_column = int(parts[4])
direction = parts[5]
grid = []
row = 0
while row < rows:
    grid_row = []
    column = 0
    while column < columns:
        grid_row.append(parts[row + 6][column])
        column = column + 1
    grid.append(grid_row)
    row = row + 1

step = 0
while step < step_count:
    if grid[ant_row][ant_column] == "0":
        grid[ant_row][ant_column] = "1"
        if direction == "N":
            direction = "E"
        elif direction == "E":
            direction = "S"
        elif direction == "S":
            direction = "W"
        else:
            direction = "N"
    else:
        grid[ant_row][ant_column] = "0"
        if direction == "N":
            direction = "W"
        elif direction == "W":
            direction = "S"
        elif direction == "S":
            direction = "E"
        else:
            direction = "N"

    next_row = ant_row
    next_column = ant_column
    if direction == "N":
        next_row = next_row - 1
    elif direction == "E":
        next_column = next_column + 1
    elif direction == "S":
        next_row = next_row + 1
    else:
        next_column = next_column - 1
    if (next_row >= 0 and next_row < rows and
            next_column >= 0 and next_column < columns):
        ant_row = next_row
        ant_column = next_column
    step = step + 1

one_count = 0
row = 0
while row < rows:
    column = 0
    while column < columns:
        if grid[row][column] == "1":
            one_count = one_count + 1
        column = column + 1
    row = row + 1
print(str(one_count))

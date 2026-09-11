import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
grain_count = int(parts[2])
grid = []
row = 0
while row < rows:
    grid_row = []
    column = 0
    while column < columns:
        grid_row.append(parts[row + 3][column])
        column = column + 1
    grid.append(grid_row)
    row = row + 1

last_result = -1
grain = 0
while grain < grain_count:
    row = 0
    column = int(parts[rows + grain + 3])
    if grid[row][column] != ".":
        last_result = -1
    else:
        moving = 1
        while moving == 1:
            if row + 1 < rows and grid[row + 1][column] == ".":
                row = row + 1
            elif (row + 1 < rows and column > 0 and
                    grid[row + 1][column - 1] == "."):
                row = row + 1
                column = column - 1
            elif (row + 1 < rows and column + 1 < columns and
                    grid[row + 1][column + 1] == "."):
                row = row + 1
                column = column + 1
            else:
                moving = 0
        grid[row][column] = "o"
        last_result = row
    grain = grain + 1
print(str(last_result))

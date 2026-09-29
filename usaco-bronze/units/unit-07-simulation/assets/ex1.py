import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
robot_row = int(parts[2])
robot_column = int(parts[3])
grid = []
i = 0
while i < rows:
    grid.append(parts[i + 4])
    i = i + 1
commands = parts[rows + 4]

i = 0
while i < len(commands):
    next_row = robot_row
    next_column = robot_column
    if commands[i] == "U":
        next_row = next_row - 1
    elif commands[i] == "D":
        next_row = next_row + 1
    elif commands[i] == "L":
        next_column = next_column - 1
    else:
        next_column = next_column + 1
    if (next_row >= 0 and next_row < rows and
            next_column >= 0 and next_column < columns and
            grid[next_row][next_column] != "#"):
        robot_row = next_row
        robot_column = next_column
    i = i + 1
print(grid[robot_row][robot_column])

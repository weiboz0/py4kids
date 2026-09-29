from collections import deque
import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
grid = []
start = (-1, -1)
exit_cell = (-1, -1)
row = 0
while row < rows:
    grid.append(parts[2 + row])
    column = 0
    while column < columns:
        if grid[row][column] == "S":
            start = (row, column)
        if grid[row][column] == "E":
            exit_cell = (row, column)
        column = column + 1
    row = row + 1

queue = deque()
queue.append(start)
visited = {start}
directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
answer = "NO"
while len(queue) > 0 and answer == "NO":
    current = queue.popleft()
    if current == exit_cell:
        answer = "YES"
    else:
        i = 0
        while i < len(directions):
            next_row = current[0] + directions[i][0]
            next_column = current[1] + directions[i][1]
            inside = 0 <= next_row and next_row < rows and 0 <= next_column and next_column < columns
            if inside and grid[next_row][next_column] != "#" and (next_row, next_column) not in visited:
                next_cell = (next_row, next_column)
                visited.add(next_cell)
                queue.append(next_cell)
            i = i + 1
print(answer)

import sys

data = sys.stdin.read()
tokens = data.split()
rows = int(tokens[0])
cols = int(tokens[1])
grid = []
visited = []
r = 0
while r < rows:
    grid.append(tokens[2 + r])
    visited_row = []
    c = 0
    while c < cols:
        visited_row.append(False)
        c = c + 1
    visited.append(visited_row)
    r = r + 1


def count_routes(row, col):
    if row == rows - 1 and col == cols - 1:
        return 1
    total = 0
    visited[row][col] = True
    steps = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for step in steps:
        next_row = row + step[0]
        next_col = col + step[1]
        if 0 <= next_row and next_row < rows and 0 <= next_col and next_col < cols:
            if grid[next_row][next_col] == "." and not visited[next_row][next_col]:
                total = total + count_routes(next_row, next_col)
    visited[row][col] = False
    return total


print(str(count_routes(0, 0)))

from collections import deque
import sys

data = sys.stdin.read()
tokens = data.split()
rows = int(tokens[0])
cols = int(tokens[1])
grid = []
start = (-1, -1)
target = (-1, -1)
r = 0
while r < rows:
    row = tokens[r + 2]
    grid.append(row)
    c = 0
    while c < cols:
        if row[c] == "S":
            start = (r, c)
        elif row[c] == "T":
            target = (r, c)
        c = c + 1
    r = r + 1
queue = deque()
queue.append(start)
visited = {start}
distance = {start: 0}
dr = [-1, 1, 0, 0]
dc = [0, 0, -1, 1]
answer = "-1"
while len(queue) > 0 and answer == "-1":
    current = queue.popleft()
    if current == target:
        answer = str(distance[current])
    else:
        direction = 0
        while direction < 4:
            nr = current[0] + dr[direction]
            nc = current[1] + dc[direction]
            if 0 <= nr and nr < rows and 0 <= nc and nc < cols:
                next_cell = (nr, nc)
                if grid[nr][nc] != "#" and next_cell not in visited:
                    visited.add(next_cell)
                    distance[next_cell] = distance[current] + 1
                    queue.append(next_cell)
            direction = direction + 1
print(answer)

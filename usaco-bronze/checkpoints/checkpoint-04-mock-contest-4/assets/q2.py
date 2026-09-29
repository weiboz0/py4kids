from collections import deque
import sys

data = sys.stdin.read()
lines = data.split("\n")
header = lines[0].split()
rows = int(header[0])
cols = int(header[1])
grid = []
r = 0
while r < rows:
    grid.append(lines[1 + r])
    r = r + 1
start = (0, 0)
target = (0, 0)
r = 0
while r < rows:
    c = 0
    while c < cols:
        if grid[r][c] == "S":
            start = (r, c)
        if grid[r][c] == "T":
            target = (r, c)
        c = c + 1
    r = r + 1
queue = deque()
queue.append((start[0], start[1], 0))
visited = set()
visited.add(start)
answer = "-1"
while len(queue) > 0 and answer == "-1":
    item = queue.popleft()
    cr = item[0]
    cc = item[1]
    dist = item[2]
    if (cr, cc) == target:
        answer = str(dist)
    else:
        neighbours = [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]
        for spot in neighbours:
            nr = spot[0]
            nc = spot[1]
            if 0 <= nr and nr < rows and 0 <= nc and nc < cols:
                if grid[nr][nc] != "#" and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc, dist + 1))
print(answer)

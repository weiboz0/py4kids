from collections import deque
import sys

data = sys.stdin.read()
tokens = data.split()
rows = int(tokens[0])
cols = int(tokens[1])
grid = []
r = 0
while r < rows:
    grid.append(tokens[2 + r])
    r = r + 1

queue = deque()
visited = set()
clean = 0
r = 0
while r < rows:
    c = 0
    while c < cols:
        if grid[r][c] == "M":
            queue.append((r, c, 0))
            visited.add((r, c))
        elif grid[r][c] == ".":
            clean = clean + 1
        c = c + 1
    r = r + 1

reached = 0
minutes = 0
while len(queue) > 0:
    item = queue.popleft()
    cr = item[0]
    cc = item[1]
    time = item[2]
    if time > minutes:
        minutes = time
    neighbours = [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]
    for spot in neighbours:
        nr = spot[0]
        nc = spot[1]
        if 0 <= nr and nr < rows and 0 <= nc and nc < cols:
            if grid[nr][nc] == "." and (nr, nc) not in visited:
                visited.add((nr, nc))
                reached = reached + 1
                queue.append((nr, nc, time + 1))
if reached < clean:
    print("-1")
else:
    print(str(minutes))

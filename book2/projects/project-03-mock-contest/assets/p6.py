import sys

data = sys.stdin.read()
lines = data.split("\n")
header = lines[0].split()
rows = int(header[0]); cols = int(header[1])
grid = []
r = 0
while r < rows:
    grid.append(lines[1 + r])
    r = r + 1
visited = set()

def fill(cr, cc):
    visited.add((cr, cc))
    size = 1
    neighbours = [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]
    for spot in neighbours:
        nr = spot[0]; nc = spot[1]
        if 0 <= nr and nr < rows and 0 <= nc and nc < cols:
            if grid[nr][nc] == "#" and (nr, nc) not in visited:
                size = size + fill(nr, nc)
    return size

best = 0
r = 0
while r < rows:
    c = 0
    while c < cols:
        if grid[r][c] == "#" and (r, c) not in visited:
            region = fill(r, c)
            if region > best:
                best = region
        c = c + 1
    r = r + 1
print(str(best))

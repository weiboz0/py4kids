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
visited = set()


def fill(cr, cc, found):
    visited.add((cr, cc))
    found.append((cr, cc))
    neighbours = [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]
    for spot in neighbours:
        nr = spot[0]
        nc = spot[1]
        if 0 <= nr and nr < rows and 0 <= nc and nc < cols:
            if grid[nr][nc] == "." and (nr, nc) not in visited:
                fill(nr, nc, found)


ponds = 0
area = 0
r = 0
while r < rows:
    c = 0
    while c < cols:
        if grid[r][c] == "." and (r, c) not in visited:
            found = []
            fill(r, c, found)
            enclosed = True
            for cell in found:
                if cell[0] == 0 or cell[0] == rows - 1 or cell[1] == 0 or cell[1] == cols - 1:
                    enclosed = False
            if enclosed:
                ponds = ponds + 1
                area = area + len(found)
        c = c + 1
    r = r + 1
print(str(ponds) + " " + str(area))

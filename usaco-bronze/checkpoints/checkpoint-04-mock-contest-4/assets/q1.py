import sys

data = sys.stdin.read()
tokens = data.split()
rows = int(tokens[0])
cols = int(tokens[1])
queries = int(tokens[2])
grid = []
label = []
r = 0
while r < rows:
    grid.append(tokens[3 + r])
    label_row = []
    c = 0
    while c < cols:
        label_row.append(-1)
        c = c + 1
    label.append(label_row)
    r = r + 1


def fill(cr, cc, pasture, sizes):
    label[cr][cc] = pasture
    sizes[pasture] = sizes[pasture] + 1
    neighbours = [(cr - 1, cc), (cr + 1, cc), (cr, cc - 1), (cr, cc + 1)]
    for spot in neighbours:
        nr = spot[0]
        nc = spot[1]
        if 0 <= nr and nr < rows and 0 <= nc and nc < cols:
            if grid[nr][nc] == "." and label[nr][nc] == -1:
                fill(nr, nc, pasture, sizes)


sizes = []
r = 0
while r < rows:
    c = 0
    while c < cols:
        if grid[r][c] == "." and label[r][c] == -1:
            sizes.append(0)
            fill(r, c, len(sizes) - 1, sizes)
        c = c + 1
    r = r + 1

answers = []
i = 0
while i < queries:
    qr = int(tokens[3 + rows + 2 * i])
    qc = int(tokens[4 + rows + 2 * i])
    if grid[qr][qc] == "#":
        answers.append("0")
    else:
        answers.append(str(sizes[label[qr][qc]]))
    i = i + 1
for answer in answers:
    print(answer)

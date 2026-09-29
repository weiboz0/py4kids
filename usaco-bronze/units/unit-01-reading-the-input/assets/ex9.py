import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
grid = []
position = 2
for r in range(rows):
    row = []
    for c in range(columns):
        row.append(int(parts[position]))
        position = position + 1
    grid.append(row)
border_total = 0
for r in range(rows):
    for c in range(columns):
        if r == 0 or r == rows - 1 or c == 0 or c == columns - 1:
            border_total = border_total + grid[r][c]
print(str(border_total))

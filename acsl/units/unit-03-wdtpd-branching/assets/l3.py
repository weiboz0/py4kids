parts = input().split()
rows = int(parts[0])
cols = int(parts[1])
grid = []
for r in range(rows):
    row = []
    for piece in input().split():
        row.append(int(piece))
    grid.append(row)
best_col = 0
best_total = 0
for c in range(cols):
    total = 0
    for r in range(rows):
        total = total + grid[r][c]
    if c == 0 or total > best_total:
        best_col = c
        best_total = total
print(best_col + 1, best_total)

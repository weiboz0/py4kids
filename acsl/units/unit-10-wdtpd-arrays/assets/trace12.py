grid = []
for r in range(4):
    row = []
    for c in range(4):
        row.append((r + 2 * c) % 5)
    grid.append(row)
best = 0
where = 0
for r in range(4):
    total = 0
    for c in range(4):
        total = total + grid[r][c]
    if total > best:
        best = total
        where = r
print(where, best)

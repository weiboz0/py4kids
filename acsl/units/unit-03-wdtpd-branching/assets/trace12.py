grid = [[3, 8, 1, 6],
        [7, 2, 9, 4],
        [5, 0, 6, 2]]
total = 0
for r in range(len(grid)):
    for c in range(len(grid[0])):
        if (r + c) % 2 == 0:
            total = total + grid[r][c]
        elif grid[r][c] > 5:
            total = total - grid[r][c]
print(total, grid[2][1] + grid[1][2])

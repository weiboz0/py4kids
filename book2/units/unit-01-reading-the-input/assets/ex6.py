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
answer = ""
for c in range(columns):
    total = 0
    for r in range(rows):
        total = total + grid[r][c]
    if c > 0:
        answer = answer + " "
    answer = answer + str(total)
print(answer)

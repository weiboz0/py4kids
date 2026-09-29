import sys

data = sys.stdin.read()
tokens = data.split()
rows = int(tokens[0])
columns = int(tokens[1])
grid = []
position = 2
for r in range(rows):
    row = []
    for c in range(columns):
        row.append(int(tokens[position]))
        position = position + 1
    grid.append(row)
answer = ""
for r in range(rows):
    if r > 0:
        answer = answer + " "
    answer = answer + str(sum(grid[r]))
print(answer)

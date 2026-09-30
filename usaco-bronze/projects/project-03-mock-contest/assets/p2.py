import sys

data = sys.stdin.read()
tokens = data.split()
rows = int(tokens[0])
cols = int(tokens[1])
row = int(tokens[2])
grid = []
r = 0
while r < rows:
    grid.append(tokens[3 + r])
    r = r + 1

col = 0
d_row = 0
d_col = 1
entered = 0
while 0 <= row and row < rows and 0 <= col and col < cols:
    entered = entered + 1
    cell = grid[row][col]
    if cell == "/":
        old_row = d_row
        d_row = -d_col
        d_col = -old_row
    elif cell == "\\":
        old_row = d_row
        d_row = d_col
        d_col = old_row
    row = row + d_row
    col = col + d_col

side = "E"
if row < 0:
    side = "N"
elif row >= rows:
    side = "S"
elif col < 0:
    side = "W"
print(str(entered) + " " + side)

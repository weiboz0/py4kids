import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
size = int(parts[2])

prefix = []
row = 0
while row <= rows:
    prefix_row = []
    column = 0
    while column <= columns:
        prefix_row.append(0)
        column = column + 1
    prefix.append(prefix_row)
    row = row + 1

row = 0
while row < rows:
    column = 0
    while column < columns:
        value = int(parts[3 + row * columns + column])
        prefix[row + 1][column + 1] = (
            value
            + prefix[row][column + 1]
            + prefix[row + 1][column]
            - prefix[row][column]
        )
        column = column + 1
    row = row + 1

best = 0
top = 0
while top + size <= rows:
    left = 0
    while left + size <= columns:
        bottom = top + size
        right = left + size
        total = (
            prefix[bottom][right]
            - prefix[top][right]
            - prefix[bottom][left]
            + prefix[top][left]
        )
        if (top == 0 and left == 0) or total > best:
            best = total
        left = left + 1
    top = top + 1
print(str(best))

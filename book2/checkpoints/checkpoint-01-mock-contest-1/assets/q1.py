import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
grid = []
position = 2
row_number = 0
while row_number < rows:
    row = []
    column_number = 0
    while column_number < columns:
        row.append(int(parts[position]))
        position = position + 1
        column_number = column_number + 1
    grid.append(row)
    row_number = row_number + 1

column_sums = []
column_number = 0
while column_number < columns:
    total = 0
    row_number = 0
    while row_number < rows:
        total = total + grid[row_number][column_number]
        row_number = row_number + 1
    column_sums.append(total)
    column_number = column_number + 1

best_column = 0
column_number = 1
while column_number < columns:
    if column_sums[column_number] > column_sums[best_column]:
        best_column = column_number
    column_number = column_number + 1
print(str(best_column + 1) + " " + str(column_sums[best_column]))

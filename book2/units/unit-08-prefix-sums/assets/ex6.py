import sys

data = sys.stdin.read()
parts = data.split()
rows = int(parts[0])
columns = int(parts[1])
query_count = int(parts[2])

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
        value = 0
        if parts[row + 3][column] == "#":
            value = 1
        prefix[row + 1][column + 1] = (
            value
            + prefix[row][column + 1]
            + prefix[row + 1][column]
            - prefix[row][column]
        )
        column = column + 1
    row = row + 1

result = ""
query_start = rows + 3
i = 0
while i < query_count:
    corner = query_start + i * 4
    row_one = int(parts[corner])
    column_one = int(parts[corner + 1])
    row_two = int(parts[corner + 2])
    column_two = int(parts[corner + 3])
    beacon_count = (
        prefix[row_two + 1][column_two + 1]
        - prefix[row_one][column_two + 1]
        - prefix[row_two + 1][column_one]
        + prefix[row_one][column_one]
    )
    if i > 0:
        result = result + "\n"
    result = result + str(beacon_count)
    i = i + 1
print(result)

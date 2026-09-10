import sys

data = sys.stdin.read()
tokens = data.split()
rows = int(tokens[0])
columns = int(tokens[1])
query_count = int(tokens[2])
grid = []
token_position = 3
row = 0
while row < rows:
    current_row = []
    column = 0
    while column < columns:
        current_row.append(int(tokens[token_position]))
        token_position = token_position + 1
        column = column + 1
    grid.append(current_row)
    row = row + 1

pre = []
row = 0
while row < rows + 1:
    prefix_row = []
    column = 0
    while column < columns + 1:
        prefix_row.append(0)
        column = column + 1
    pre.append(prefix_row)
    row = row + 1

row = 0
while row < rows:
    column = 0
    while column < columns:
        pre[row + 1][column + 1] = grid[row][column] + pre[row][column + 1] + pre[row + 1][column] - pre[row][column]
        column = column + 1
    row = row + 1

answer_text = ""
query_index = 0
while query_index < query_count:
    r1 = int(tokens[token_position])
    c1 = int(tokens[token_position + 1])
    r2 = int(tokens[token_position + 2])
    c2 = int(tokens[token_position + 3])
    rectangle_total = pre[r2 + 1][c2 + 1] - pre[r1][c2 + 1] - pre[r2 + 1][c1] + pre[r1][c1]
    if query_index > 0:
        answer_text = answer_text + "\n"
    answer_text = answer_text + str(rectangle_total)
    token_position = token_position + 4
    query_index = query_index + 1
print(answer_text)

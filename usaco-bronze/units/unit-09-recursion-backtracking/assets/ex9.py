import sys

data = sys.stdin.read()
parts = data.split()
board_size = int(parts[0])
blocked_count = int(parts[1])
blocked = []
row = 0
while row < board_size:
    blocked_row = []
    column = 0
    while column < board_size:
        blocked_row.append(False)
        column = column + 1
    blocked.append(blocked_row)
    row = row + 1
i = 0
while i < blocked_count:
    row = int(parts[i * 2 + 2])
    column = int(parts[i * 2 + 3])
    blocked[row][column] = True
    i = i + 1

columns = []
rising_diagonals = []
falling_diagonals = []
i = 0
while i < board_size:
    columns.append(False)
    i = i + 1
i = 0
while i < board_size * 2 - 1:
    rising_diagonals.append(False)
    falling_diagonals.append(False)
    i = i + 1

def search(row, path):
    if row == board_size:
        return 1

    ways = 0
    column = 0
    while column < board_size:
        rising = row - column + board_size - 1
        falling = row + column
        legal = blocked[row][column] == False
        if columns[column]:
            legal = False
        if rising_diagonals[rising]:
            legal = False
        if falling_diagonals[falling]:
            legal = False
        if legal:
            columns[column] = True
            rising_diagonals[rising] = True
            falling_diagonals[falling] = True
            ways = ways + search(row + 1, path + [column])
            columns[column] = False
            rising_diagonals[rising] = False
            falling_diagonals[falling] = False
        column = column + 1
    return ways

print(str(search(0, [])))

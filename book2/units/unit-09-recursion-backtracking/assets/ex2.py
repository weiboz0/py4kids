import sys

data = sys.stdin.read()
parts = data.split()
value_count = int(parts[0])
gap = int(parts[1])
values = []
used = []
i = 0
while i < value_count:
    values.append(int(parts[i + 2]))
    used.append(False)
    i = i + 1

def search(path):
    if len(path) == value_count:
        return 1

    ways = 0
    choice_index = 0
    while choice_index < value_count:
        choice = values[choice_index]
        legal = len(path) == 0
        if len(path) > 0:
            if abs(path[-1] - choice) >= gap:
                legal = True
        if used[choice_index] == False and legal:
            used[choice_index] = True
            ways = ways + search(path + [choice])
            used[choice_index] = False
        choice_index = choice_index + 1
    return ways

print(str(search([])))

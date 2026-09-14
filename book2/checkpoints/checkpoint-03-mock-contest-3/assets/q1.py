import sys

data = sys.stdin.read()
parts = data.split()
value_count = int(parts[0])
values = []
used = []
i = 0
while i < value_count:
    values.append(int(parts[i + 1]))
    used.append(False)
    i = i + 1

def count_arrangements(depth, previous_index):
    if depth == value_count:
        return 1
    count = 0
    i = 0
    while i < value_count:
        allowed = previous_index == -1
        if previous_index != -1:
            allowed = abs(values[i] - values[previous_index]) != 1
        if used[i] == False and allowed:
            used[i] = True
            count = count + count_arrangements(depth + 1, i)
            used[i] = False
        i = i + 1
    return count

print(str(count_arrangements(0, -1)))

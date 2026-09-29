import sys

data = sys.stdin.read()
parts = data.split()
value_count = int(parts[0])
target = int(parts[1])
values = []
i = 0
while i < value_count:
    values.append(int(parts[i + 2]))
    i = i + 1

def search(index, total, path):
    if index == value_count:
        if total == target:
            return 1
        return 0

    with_value = search(
        index + 1, total + values[index], path + [values[index]]
    )
    without_value = search(index + 1, total, path)
    return with_value + without_value

print(str(search(0, 0, [])))

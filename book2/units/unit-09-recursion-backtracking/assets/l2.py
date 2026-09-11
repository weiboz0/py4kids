import sys

data = sys.stdin.read()
tokens = data.split()
target = int(tokens[0])
values = []
for token in tokens[1:]:
    values.append(int(token))
n = len(values)

def search(index, total, path):
    if index == n:
        if total == target:
            return 1
        return 0
    with_value = search(index + 1, total + values[index], path + [values[index]])
    without_value = search(index + 1, total, path)
    return with_value + without_value

print(str(search(0, 0, [])))

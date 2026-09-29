import sys

data = sys.stdin.read()
values = []
for token in data.split():
    values.append(int(token))

def recursive_sum(index):
    if index == len(values):
        return 0
    return values[index] + recursive_sum(index + 1)

print(str(recursive_sum(0)))

import sys

data = sys.stdin.read()
parts = data.split()
level_count = int(parts[0])
target = int(parts[1])

def search(level, total, path):
    if level == level_count:
        if total == target:
            return 1
        return 0

    ways = 0
    choice = 0
    while choice < 3:
        ways = ways + search(level + 1, total + choice, path + [choice])
        choice = choice + 1
    return ways

print(str(search(0, 0, [])))

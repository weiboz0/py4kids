import sys

data = sys.stdin.read()
parts = data.split()
item_count = int(parts[0])
target = int(parts[1])
weights = []
i = 0
while i < item_count:
    weights.append(int(parts[i + 2]))
    i = i + 1

matching_count = 0
for mask in range(1 << item_count):
    total = 0
    i = 0
    while i < item_count:
        if mask & (1 << i):
            total = total + weights[i]
        i = i + 1
    if total == target:
        matching_count = matching_count + 1
print(str(matching_count))

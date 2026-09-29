import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
target = int(tokens[1])
values = []
index = 0
while index < n:
    values.append(int(tokens[index + 2]))
    index = index + 1
matching_count = 0
for mask in range(1 << n):
    subset_total = 0
    index = 0
    while index < n:
        if mask & (1 << index):
            subset_total = subset_total + values[index]
        index = index + 1
    if subset_total == target:
        matching_count = matching_count + 1
print(str(matching_count))

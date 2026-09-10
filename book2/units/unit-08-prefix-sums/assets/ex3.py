import sys

data = sys.stdin.read()
parts = data.split()
measurement_count = int(parts[0])
query_count = int(parts[1])
target = int(parts[2])
prefix = [0]
i = 0
while i < measurement_count:
    prefix.append(prefix[i] + int(parts[i + 3]))
    i = i + 1

matching_count = 0
query_start = measurement_count + 3
i = 0
while i < query_count:
    left = int(parts[query_start + i * 2])
    right = int(parts[query_start + i * 2 + 1])
    total = prefix[right + 1] - prefix[left]
    if total == target:
        matching_count = matching_count + 1
    i = i + 1
print(str(matching_count))

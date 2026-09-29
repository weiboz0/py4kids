import sys

data = sys.stdin.read()
parts = data.split()
signal_count = int(parts[0])
query_count = int(parts[1])
prefix = [0]
i = 0
while i < signal_count:
    prefix.append(prefix[i] + int(parts[i + 2]))
    i = i + 1

query_start = signal_count + 2
greatest = 0
i = 0
while i < query_count:
    left = int(parts[query_start + i * 2])
    right = int(parts[query_start + i * 2 + 1])
    total = prefix[right + 1] - prefix[left]
    if i == 0 or total > greatest:
        greatest = total
    i = i + 1
print(str(greatest))

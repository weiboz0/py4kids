import sys

data = sys.stdin.read()
parts = data.split()
value_count = int(parts[0])
query_count = int(parts[1])
prefix = [0]
i = 0
while i < value_count:
    prefix.append(prefix[i] + int(parts[i + 2]))
    i = i + 1

result = ""
query_start = value_count + 2
i = 0
while i < query_count:
    left = int(parts[query_start + i * 2])
    right = int(parts[query_start + i * 2 + 1])
    total = prefix[right + 1] - prefix[left]
    if i > 0:
        result = result + "\n"
    result = result + str(total)
    i = i + 1
print(result)

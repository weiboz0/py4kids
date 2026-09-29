import sys

data = sys.stdin.read()
parts = data.split()
score_count = int(parts[0])
candidate_count = int(parts[1])
size_limit = int(parts[2])
prefix = [0]
i = 0
while i < score_count:
    prefix.append(prefix[i] + int(parts[i + 3]))
    i = i + 1

query_start = score_count + 3
greatest = 0
has_greatest = 0
i = 0
while i < candidate_count:
    left = int(parts[query_start + i * 2])
    right = int(parts[query_start + i * 2 + 1])
    window_size = right - left + 1
    if window_size <= size_limit:
        total = prefix[right + 1] - prefix[left]
        if has_greatest == 0 or total > greatest:
            greatest = total
            has_greatest = 1
    i = i + 1
print(str(greatest))

import sys

data = sys.stdin.read()
parts = data.split()
score_count = int(parts[0])
limit = int(parts[1])
prefix = [0]
i = 0
while i < score_count:
    prefix.append(prefix[i] + int(parts[i + 2]))
    i = i + 1

greatest_length = 0
left = 0
while left < score_count:
    right = left
    while right < score_count:
        total = prefix[right + 1] - prefix[left]
        if total <= limit:
            window_size = right - left + 1
            if window_size > greatest_length:
                greatest_length = window_size
        right = right + 1
    left = left + 1
print(str(greatest_length))

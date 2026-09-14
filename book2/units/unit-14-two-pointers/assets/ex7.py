import sys

data = sys.stdin.read()
parts = data.split()
badge_count = int(parts[0])
limit = int(parts[1])
badges = []
i = 0
while i < badge_count:
    badges.append(int(parts[i + 2]))
    i = i + 1

counts = {}
distinct_count = 0
greatest_length = 0
left = 0
right = 0
while right < badge_count:
    badge = badges[right]
    if badge not in counts:
        counts[badge] = 0
    if counts[badge] == 0:
        distinct_count = distinct_count + 1
    counts[badge] = counts[badge] + 1
    while distinct_count > limit:
        left_badge = badges[left]
        counts[left_badge] = counts[left_badge] - 1
        if counts[left_badge] == 0:
            distinct_count = distinct_count - 1
        left = left + 1
    window_length = right - left + 1
    if window_length > greatest_length:
        greatest_length = window_length
    right = right + 1
print(str(greatest_length))

import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
flavors = []
kinds = set()
i = 0
while i < n:
    flavor = int(tokens[1 + i])
    flavors.append(flavor)
    kinds.add(flavor)
    i = i + 1
needed = len(kinds)

counts = {}
covered = 0
best = n
left = 0
right = 0
while right < n:
    flavor = flavors[right]
    if flavor not in counts:
        counts[flavor] = 0
    counts[flavor] = counts[flavor] + 1
    if counts[flavor] == 1:
        covered = covered + 1
    while covered == needed:
        span = right - left + 1
        if span < best:
            best = span
        leaving = flavors[left]
        counts[leaving] = counts[leaving] - 1
        if counts[leaving] == 0:
            covered = covered - 1
        left = left + 1
    right = right + 1
print(str(best))

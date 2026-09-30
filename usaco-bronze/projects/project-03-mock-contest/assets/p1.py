import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
prefix = [0]
i = 0
while i < n:
    prefix.append(prefix[i] + int(tokens[1 + i]))
    i = i + 1
total = prefix[n]

best = -1
cut = 1
while cut < n:
    left = prefix[cut]
    right = total - left
    gap = abs(left - right)
    if best == -1 or gap < best:
        best = gap
    cut = cut + 1
print(str(best))

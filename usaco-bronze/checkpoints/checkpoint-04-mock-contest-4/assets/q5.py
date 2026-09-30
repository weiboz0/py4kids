import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
allowed = int(tokens[1])
days = []
i = 0
while i < n:
    days.append(int(tokens[2 + i]))
    i = i + 1
left = 0
rainy = 0
best = 0
right = 0
while right < n:
    if days[right] == 0:
        rainy = rainy + 1
    while rainy > allowed:
        if days[left] == 0:
            rainy = rainy - 1
        left = left + 1
    span = right - left + 1
    if span > best:
        best = span
    right = right + 1
print(str(best))

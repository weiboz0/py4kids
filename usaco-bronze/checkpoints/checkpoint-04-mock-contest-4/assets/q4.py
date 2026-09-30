import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
heights = []
i = 0
while i < n:
    heights.append(int(tokens[1 + i]))
    i = i + 1
lo = 0
hi = n - 1
best = 0
while lo < hi:
    water = min(heights[lo], heights[hi]) * (hi - lo)
    if water > best:
        best = water
    if heights[lo] < heights[hi]:
        lo = lo + 1
    else:
        hi = hi - 1
print(str(best))

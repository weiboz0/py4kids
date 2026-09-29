import math

count = 0
best = 0
for k in range(100, 59, -7):
    m = k
    s = 0
    while m > 0:
        s = s + m % 10
        m = math.floor(m / 10)
    if s % 2 == 1:
        count = count + 1
    if s > best:
        best = s
print(count, best)

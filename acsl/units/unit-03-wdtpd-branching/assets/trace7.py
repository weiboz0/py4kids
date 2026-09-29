import math

x = 14
y = 0
if x > 10:
    x = x - 6
    y = y + 1
if x < 10:
    x = x * 3
    y = y + 1
if x % 4 == 0:
    x = math.floor(x / 4)
    y = y + 1
else:
    x = x + 1
print(x, y)

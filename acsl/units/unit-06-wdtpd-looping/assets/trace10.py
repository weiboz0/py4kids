import math

x = 45
c = 0
while x > -20:
    x = math.floor(x / 2) - 12
    c = c + 1
print(x, c)

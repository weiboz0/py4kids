import math

parts = input().split()
a = int(parts[0])
b = int(parts[1])
c = a % 7
if c > 3 and b < a:
    d = math.floor(a / 4) + b
elif not (b > 10):
    d = a - b ** 2
else:
    d = a + b
print(d)

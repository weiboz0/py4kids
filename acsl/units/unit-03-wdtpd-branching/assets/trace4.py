import math

parts = input().split()
a = int(parts[0])
b = int(parts[1])
q = math.floor(a / b)
r = a - q * b
if r == 0:
    print(q)
elif q > r:
    print(q * 10 + r)
else:
    print(r ** 2 - q)

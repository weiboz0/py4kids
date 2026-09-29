import math

n = int(input())
c = 0
m = 0
for k in range(n, 0, -5):  # ACSL: for k = n to 1 step -5 (includes 1 if reached)
    x = k
    s = 0
    while x > 0:
        s = s + x % 10
        x = math.floor(x / 10)  # ACSL int(x / 10)
    if s > m:
        m = s
    c = c + s
print(c - m)

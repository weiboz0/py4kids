parts = input().split()
a = int(parts[0])
b = int(parts[1])
c = a % b
if c > 2 and not (a > 50):
    d = a - b * c
else:
    if c == 0 or b > 6:
        d = a + b
    else:
        d = 2 * c - a
if d < 0:
    d = -d
print(d)

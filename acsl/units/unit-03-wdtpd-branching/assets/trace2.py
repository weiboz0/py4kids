parts = input().split()
x = int(parts[0])
y = int(parts[1])
if x > y:
    if x % 2 == 0:
        z = x * 2 - y
    else:
        z = x + y * 2
else:
    if y % 3 == 0 or x < 0:
        z = y - x
    else:
        z = x * y
print(z)

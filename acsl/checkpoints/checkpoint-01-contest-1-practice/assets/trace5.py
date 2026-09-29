parts = input().split()
a = int(parts[0])
b = int(parts[1])
c = int(parts[2])
if a > b and b > c:
    if a - b > b - c:
        x = a * 2 - c
    else:
        x = b + c
elif a > c or c % 2 == 0:
    x = a + b + c
else:
    x = 0
if not x % 3 == 0:
    x = x + 1
print(x)

def f(x, y):
    if x <= 0 or y <= 0:
        return x + y
    if x > y:
        return f(x - 2, y - 1) + 3
    return f(x - 1, y - 3) + x


parts = input().split()
x = int(parts[0])
y = int(parts[1])
print(f(x, y))

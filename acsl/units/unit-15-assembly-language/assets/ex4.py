def div(x, y):
    q = abs(x) // abs(y)
    if x * y < 0:
        q = -q
    return q


a = int(input())
b = int(input())
c = div(a * a - b, 3)
print(c)
d = div(b - a, 4)
print(d)

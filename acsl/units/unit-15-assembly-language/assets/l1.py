def div(x, y):
    q = abs(x) // abs(y)
    if x * y < 0:
        q = -q
    return q


a = int(input())
b = int(input())
c = int(input())
acc = b
acc = acc * c
acc = acc + a
acc = div(acc, b)
acc = acc - a
temp = acc
print(temp)

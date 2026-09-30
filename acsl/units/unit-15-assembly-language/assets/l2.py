x = int(input())
acc = x
acc = acc - 1
while acc != 0:
    a = acc
    acc = acc * x
    x = acc
    acc = a
    acc = acc - 1
print(x)

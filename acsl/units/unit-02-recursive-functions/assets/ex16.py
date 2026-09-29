def f(x):
    if x >= 3:
        value1, calls1 = f(x - 1)
        value2, calls2 = f(x - 3)
        return (value1 + value2, calls1 + calls2 + 1)
    return (x + 1, 1)


x = int(input())
value, calls = f(x)
print(value, calls)

def f(x):
    if x > 10:
        return f(x - 3) + x
    return 2 * x - 5


x = int(input())
print(f(x))

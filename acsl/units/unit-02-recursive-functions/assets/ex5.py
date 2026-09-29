def g(x):
    if x > 8:
        return g(x - 5) + x
    return 3 * x - 1


x = int(input())
print(g(x))

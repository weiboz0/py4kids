def p(x):
    if x > 1:
        return q(x // 2) + x
    return 1


def q(x):
    if x > 0:
        return p(x - 1) - 1
    return 0


x = int(input())
print(p(x))

def f(x):
    if x < 10:
        return x
    if x % 2 == 0:
        return f(x // 2) + 1
    return f(x - 3) + 2


n = int(input())
for i in range(n):
    x = int(input())
    print(f(x))

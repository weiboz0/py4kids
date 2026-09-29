def t(n):
    if n > 2:
        return t(n - 1) + t(n - 2) + t(n - 3)
    return n


n = int(input())
print(t(n))

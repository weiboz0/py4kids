c = 0
n = int(input())
while n - 1 != 0:
    if n % 2 == 0:
        n = n // 2
    else:
        n = n * 3 + 1
    c = c + 1
print(c)

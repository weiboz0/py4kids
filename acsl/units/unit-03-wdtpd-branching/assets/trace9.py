n = int(input())
steps = 0
while n >= 10:
    total = 0
    while n > 0:
        total = total + n % 10
        n = n // 10
    n = total
    steps = steps + 1
print(n, steps)

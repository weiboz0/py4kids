n = int(input())
steps = 0
peak = n
while n != 1:
    if n % 2 == 0:
        n = n // 2
    else:
        n = 3 * n + 1
    steps = steps + 1
    if n > peak:
        peak = n
print(steps, peak)

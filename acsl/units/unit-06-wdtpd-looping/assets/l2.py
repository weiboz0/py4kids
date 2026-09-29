n = abs(int(input()))
digits = 0
total = 0
largest = 0
while n > 0:
    d = n % 10
    digits = digits + 1
    total = total + d
    if d > largest:
        largest = d
    n = n // 10
print(digits, total, largest)

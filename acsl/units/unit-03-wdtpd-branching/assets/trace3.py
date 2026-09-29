n = int(input())
a = n // 100
b = n // 10 % 10
c = n % 10
if a + c == b:
    result = n + 1
elif a > c:
    if b % 2 == 0:
        result = a * 100 + c * 10 + b
    else:
        result = c * 100 + b * 10 + a
else:
    result = n - a - b - c
print(result)

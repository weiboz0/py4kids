n = int(input())
rev = 0
odd = 0
while n > 0:
    d = n % 10
    rev = rev * 10 + d
    if d % 2 == 1:
        odd = odd + 1
    n = n // 10
print(rev, odd)

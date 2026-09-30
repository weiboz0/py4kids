def div(x, y):
    q = abs(x) // abs(y)
    if x * y < 0:
        q = -q
    return q


s = 0
n = int(input())
going = True
while going:
    q = div(n, 10)
    s = s + n - q * 10
    n = q
    going = n > 0
print(s)

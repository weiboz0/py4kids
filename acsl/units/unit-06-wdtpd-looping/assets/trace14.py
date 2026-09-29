n = int(input())
p = 1
k = 0
s = 0
while p * 3 <= n:
    p = p * 3
    k = k + 1
    s = s + n % p
print(k, s)

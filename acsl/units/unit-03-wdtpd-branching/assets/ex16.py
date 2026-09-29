import math

n = int(input())
count = 0
while n > 0:
    r = math.floor(math.sqrt(n))
    n = n - r ** 2
    count = count + 1
print(count)

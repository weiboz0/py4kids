import sys

data = sys.stdin.read()
n = int(data.strip())
is_prime = []
index = 0
while index <= n:
    is_prime.append(True)
    index = index + 1
if n >= 0:
    is_prime[0] = False
if n >= 1:
    is_prime[1] = False
p = 2
while p * p <= n:
    if is_prime[p]:
        multiple = p * p
        while multiple <= n:
            is_prime[multiple] = False
            multiple = multiple + p
    p = p + 1
prime_count = 0
value = 2
while value <= n:
    if is_prime[value]:
        prime_count = prime_count + 1
    value = value + 1
print(str(prime_count))

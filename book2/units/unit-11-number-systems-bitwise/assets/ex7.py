import sys

data = sys.stdin.read()
limit = int(data.split()[0])
is_prime = []
i = 0
while i <= limit:
    is_prime.append(True)
    i = i + 1
if limit >= 0:
    is_prime[0] = False
if limit >= 1:
    is_prime[1] = False

p = 2
while p * p <= limit:
    if is_prime[p]:
        multiple = p * p
        while multiple <= limit:
            is_prime[multiple] = False
            multiple = multiple + p
    p = p + 1

prime_count = 0
i = 2
while i <= limit:
    if is_prime[i]:
        prime_count = prime_count + 1
    i = i + 1
print(str(prime_count))

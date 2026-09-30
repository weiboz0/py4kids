import sys

data = sys.stdin.read()
limit = int(data.strip())
is_prime = []
i = 0
while i <= limit:
    is_prime.append(True)
    i = i + 1
is_prime[0] = False
is_prime[1] = False

prime = 2
while prime * prime <= limit:
    if is_prime[prime]:
        multiple = prime * prime
        while multiple <= limit:
            is_prime[multiple] = False
            multiple = multiple + prime
    prime = prime + 1

pairs = 0
low = 2
while low + 2 <= limit:
    if is_prime[low] and is_prime[low + 2]:
        pairs = pairs + 1
    low = low + 1
print(str(pairs))

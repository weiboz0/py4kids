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

count = 0
i = 2
while i <= limit:
    if is_prime[i]:
        count = count + 1
    i = i + 1
print(str(count))

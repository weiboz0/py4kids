import sys

data = sys.stdin.read()
target_index = int(data.split()[0])
limit = 200000
is_prime = []
i = 0
while i <= limit:
    is_prime.append(True)
    i = i + 1
is_prime[0] = False
is_prime[1] = False
p = 2
while p * p <= limit:
    if is_prime[p]:
        multiple = p * p
        while multiple <= limit:
            is_prime[multiple] = False
            multiple = multiple + p
    p = p + 1
answer = ""
prime_count = 0
candidate = 2
while candidate <= limit and answer == "":
    if is_prime[candidate]:
        prime_count = prime_count + 1
        if prime_count == target_index:
            answer = str(candidate)
    candidate = candidate + 1
print(answer)

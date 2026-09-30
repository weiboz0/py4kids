import sys

data = sys.stdin.read()
tokens = data.split()
base = int(tokens[0])
days = int(tokens[1])
modulus = int(tokens[2])

bits = []
rest = days
while rest > 0:
    bits.append(rest % 2)
    rest = rest // 2

power = 1 % modulus
total = 0
factor = base % modulus
i = len(bits) - 1
while i >= 0:
    total = (total + power * total) % modulus
    power = power * power % modulus
    if bits[i] == 1:
        total = (total + power) % modulus
        power = power * factor % modulus
    i = i - 1
print(str(total))

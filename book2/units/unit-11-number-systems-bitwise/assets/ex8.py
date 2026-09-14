import sys

data = sys.stdin.read()
parts = data.split()
base = int(parts[0])
modulus = int(parts[1])
exponent = int(parts[2])
result = 1 % modulus
base = base % modulus
while exponent > 0:
    if exponent % 2 == 1:
        result = result * base % modulus
    base = base * base % modulus
    exponent = exponent // 2
print(str(result % modulus))

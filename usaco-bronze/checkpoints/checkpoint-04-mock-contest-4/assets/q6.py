import sys

data = sys.stdin.read()
tokens = data.split()
base = int(tokens[0])
modulus = int(tokens[1])
exponent = int(tokens[2])
answer = 1 % modulus
current = base % modulus
while exponent > 0:
    if exponent % 2 == 1:
        answer = answer * current % modulus
    current = current * current % modulus
    exponent = exponent // 2
print(str(answer))

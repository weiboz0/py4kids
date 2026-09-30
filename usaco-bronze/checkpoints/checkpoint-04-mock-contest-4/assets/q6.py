import sys

data = sys.stdin.read()
tokens = data.split()
base = int(tokens[0])
exponent = int(tokens[1])
digits = int(tokens[2])
modulus = 1
i = 0
while i < digits:
    modulus = modulus * 10
    i = i + 1
answer = 1 % modulus
current = base % modulus
while exponent > 0:
    if exponent % 2 == 1:
        answer = answer * current % modulus
    current = current * current % modulus
    exponent = exponent // 2
text = str(answer)
while len(text) < digits:
    text = "0" + text
print(text)

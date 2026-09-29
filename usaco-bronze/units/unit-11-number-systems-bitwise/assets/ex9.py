import sys

data = sys.stdin.read()
parts = data.split()
width = int(parts[0])
hexadecimal = parts[1]
digits = "0123456789ABCDEF"
value = 0
i = 0
while i < len(hexadecimal):
    digit = 0
    while digits[digit] != hexadecimal[i]:
        digit = digit + 1
    value = value * 16 + digit
    i = i + 1

complemented = ~value & ((1 << width) - 1)
converted = ""
if complemented == 0:
    converted = "0"
while complemented > 0:
    digit = complemented % 16
    converted = digits[digit] + converted
    complemented = complemented // 16

required_digits = width // 4
while len(converted) < required_digits:
    converted = "0" + converted
print(converted)

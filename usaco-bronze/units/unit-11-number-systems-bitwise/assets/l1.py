import sys

data = sys.stdin.read()
tokens = data.split()
number = int(tokens[0])
binary_text = tokens[1]
hexadecimal_text = tokens[2]
digits = "0123456789ABCDEF"

if number == 0:
    binary = "0"
else:
    binary = ""
    remaining = number
    while remaining > 0:
        digit = remaining % 2
        binary = digits[digit] + binary
        remaining = remaining // 2

if number == 0:
    hexadecimal = "0"
else:
    hexadecimal = ""
    remaining = number
    while remaining > 0:
        digit = remaining % 16
        hexadecimal = digits[digit] + hexadecimal
        remaining = remaining // 16

binary_value = 0
position = 0
while position < len(binary_text):
    binary_value = binary_value * 2 + int(binary_text[position])
    position = position + 1

hexadecimal_value = 0
position = 0
while position < len(hexadecimal_text):
    character = hexadecimal_text[position]
    digit_value = 0
    while digits[digit_value] != character:
        digit_value = digit_value + 1
    hexadecimal_value = hexadecimal_value * 16 + digit_value
    position = position + 1
print(binary + "\n" + hexadecimal + "\n" + str(binary_value) + "\n" + str(hexadecimal_value))

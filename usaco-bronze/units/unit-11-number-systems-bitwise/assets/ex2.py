import sys

data = sys.stdin.read()
parts = data.split()
number = int(parts[0])
hexadecimal = parts[1]
digits = "0123456789ABCDEF"

converted = ""
if number == 0:
    converted = "0"
while number > 0:
    digit = number % 16
    converted = digits[digit] + converted
    number = number // 16

decimal = 0
i = 0
while i < len(hexadecimal):
    digit = 0
    while digits[digit] != hexadecimal[i]:
        digit = digit + 1
    decimal = decimal * 16 + digit
    i = i + 1
print(converted + "\n" + str(decimal))

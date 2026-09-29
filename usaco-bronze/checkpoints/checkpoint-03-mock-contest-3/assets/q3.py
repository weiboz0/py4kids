import sys

data = sys.stdin.read()
number = int(data.strip())
if number == 0:
    print("0")
else:
    digits = ""
    while number > 0:
        digit = str(number % 2)
        digits = digit + digits
        number = number // 2
    print(digits)

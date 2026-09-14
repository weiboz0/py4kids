import sys

data = sys.stdin.read()
number = int(data.split()[0])
if number == 0:
    print("0")
else:
    result = ""
    while number > 0:
        digit = number % 2
        result = str(digit) + result
        number = number // 2
    print(result)

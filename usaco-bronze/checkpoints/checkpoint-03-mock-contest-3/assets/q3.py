import sys

data = sys.stdin.read()
parts = data.split()
number = int(parts[0])
base = int(parts[1])
forward = ""
backward = ""
if number == 0:
    forward = "0"
    backward = "0"
while number > 0:
    digit = str(number % base)
    forward = digit + forward
    backward = backward + digit
    number = number // base
if forward == backward:
    answer = "YES"
else:
    answer = "NO"
print(forward)
print(answer)

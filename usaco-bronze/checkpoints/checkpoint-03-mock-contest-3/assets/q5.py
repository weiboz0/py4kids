import sys


def gcd(a, b):
    while b != 0:
        remainder = a % b
        a = b
        b = remainder
    return a


data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
stops = 1
i = 1
while i < n:
    dx = abs(int(tokens[1 + 2 * i]) - int(tokens[1 + 2 * (i - 1)]))
    dy = abs(int(tokens[2 + 2 * i]) - int(tokens[2 + 2 * (i - 1)]))
    stops = stops + gcd(dx, dy)
    i = i + 1
print(str(stops))

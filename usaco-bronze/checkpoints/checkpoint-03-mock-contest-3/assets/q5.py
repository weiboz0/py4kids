import sys

data = sys.stdin.read()
parts = data.split()
value_count = int(parts[0])

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

common = int(parts[1])
multiple = int(parts[1])
i = 1
while i < value_count:
    value = int(parts[i + 1])
    common = gcd(common, value)
    pair_gcd = gcd(multiple, value)
    multiple = multiple // pair_gcd * value
    i = i + 1
result = str(common)
result = result + " "
result = result + str(multiple)
print(result)

import sys

data = sys.stdin.read()
parts = data.split()
pair_count = int(parts[0])
result = ""
i = 0
while i < pair_count:
    first = int(parts[i * 2 + 1])
    second = int(parts[i * 2 + 2])
    a = first
    b = second
    while b:
        a, b = b, a % b
    greatest_common_divisor = a
    if first == 0 or second == 0:
        least_common_multiple = 0
    else:
        least_common_multiple = first // greatest_common_divisor * second
    if i > 0:
        result = result + "\n"
    result = result + str(greatest_common_divisor)
    result = result + " "
    result = result + str(least_common_multiple)
    i = i + 1
print(result)

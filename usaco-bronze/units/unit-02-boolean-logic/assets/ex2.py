import sys

data = sys.stdin.read()
values = data.split()
a = int(values[0]) == 1
b = int(values[1]) == 1
result = not (a and not b)
if result:
    print("TRUE")
else:
    print("FALSE")

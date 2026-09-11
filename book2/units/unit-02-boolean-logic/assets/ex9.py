import sys

data = sys.stdin.read()
values = data.split()
rule = values[0]
a = int(values[1]) == 1
b = int(values[2]) == 1
if rule == "A_AND_NOT_B":
    result = a and not b
elif rule == "NOT_A_OR_B":
    result = (not a) or b
elif rule == "A_OR_B":
    result = a or b
else:
    result = a and b
if result:
    print("TRUE")
else:
    print("FALSE")

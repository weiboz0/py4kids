import sys

data = sys.stdin.read()
parts = data.split()
floor = int(parts[0])
cap = int(parts[1])
value = int(parts[2])
tick_count = int(parts[3])
i = 0
while i < tick_count:
    value = value + int(parts[4 + i])
    if value < floor:
        value = floor
    elif value > cap:
        value = cap
    i = i + 1
print(str(value))

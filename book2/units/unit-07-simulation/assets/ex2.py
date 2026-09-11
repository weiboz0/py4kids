import sys

data = sys.stdin.read()
parts = data.split()
capacity = int(parts[0])
charge = int(parts[1])
tick_count = int(parts[2])
i = 0
while i < tick_count:
    charge = charge + int(parts[i + 3])
    if charge > capacity:
        charge = capacity
    elif charge < 0:
        charge = 0
    i = i + 1
print(str(charge))

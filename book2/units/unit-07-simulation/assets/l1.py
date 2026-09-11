import sys

data = sys.stdin.read()
tokens = data.split()
capacity = int(tokens[0])
charge = int(tokens[1])
ticks = int(tokens[2])
for tick in range(ticks):
    change = int(tokens[tick + 3])
    charge = charge + change
    if charge > capacity:
        charge = capacity
    elif charge < 0:
        charge = 0
print(str(charge))

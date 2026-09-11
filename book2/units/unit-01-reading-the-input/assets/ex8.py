import sys

data = sys.stdin.read()
parts = data.split()
k = int(parts[0])
chosen_position = int(parts[1])
names = []
for i in range(k):
    names.append(parts[i + 2])
print(names[chosen_position - 1])

import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
colors = {parts[1]}
i = 1
while i < n:
    colors.add(parts[i + 1])
    i = i + 1
print(str(len(colors)))

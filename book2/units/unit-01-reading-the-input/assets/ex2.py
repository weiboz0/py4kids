import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
threshold = int(parts[1])
above = 0
for i in range(n):
    value = int(parts[i + 2])
    if value > threshold:
        above = above + 1
print(str(above))

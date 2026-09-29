import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
values = []
for i in range(n):
    values.append(int(parts[i + 1]))
print(f"{sum(values)} {max(values)}")

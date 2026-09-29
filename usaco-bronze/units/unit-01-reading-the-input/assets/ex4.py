import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
target = int(parts[1])
position = 0
for i in range(n):
    if position == 0:
        if int(parts[i + 2]) == target:
            position = i + 1
if position == 0:
    print("NO")
else:
    print(f"YES {position}")

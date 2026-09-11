import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
goal = int(parts[1])
total = 0
answer = -1
i = 0
while i < n:
    total = total + int(parts[i + 2])
    if answer == -1 and total >= goal:
        answer = i + 1
    i = i + 1
print(str(answer))

import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
answer = ""
for i in range(n):
    if i > 0:
        answer = answer + " "
    doubled = int(parts[i + 1]) * 2
    answer = answer + str(doubled)
print(answer)

import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
target = int(parts[1])
qualifying = 0
i = 0
while i < n:
    score = int(parts[i + 2])
    if score >= target:
        qualifying = qualifying + 1
    i = i + 1
print(str(qualifying))

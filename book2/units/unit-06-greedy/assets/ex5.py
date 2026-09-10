import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
deadlines = []
i = 0
while i < n:
    deadlines.append(int(parts[i + 1]))
    i = i + 1
deadlines.sort()
completed = 0
i = 0
while i < n:
    if completed < deadlines[i]:
        completed = completed + 1
    i = i + 1
print(str(completed))

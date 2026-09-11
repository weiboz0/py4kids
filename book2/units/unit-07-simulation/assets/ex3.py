import sys

data = sys.stdin.read()
parts = data.split()
event_count = int(parts[0])
points = []
jumps = []
i = 0
while i < event_count:
    points.append(int(parts[i * 2 + 1]))
    jumps.append(int(parts[i * 2 + 2]))
    i = i + 1

score = 0
event_index = 0
while event_index < event_count:
    score = score + points[event_index]
    event_index = event_index + jumps[event_index]
print(str(score))

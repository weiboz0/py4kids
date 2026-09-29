import sys

data = sys.stdin.read()
tokens = data.split()
event_count = int(tokens[0])
points = []
jumps = []
for event in range(event_count):
    points.append(int(tokens[1 + event * 2]))
    jumps.append(int(tokens[2 + event * 2]))

score = 0
event_index = 0
while event_index < event_count:
    score = score + points[event_index]
    event_index = event_index + jumps[event_index]
print(str(score))

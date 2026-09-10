import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
events = []
for position in range(n):
    start = int(tokens[1 + position * 2])
    end = int(tokens[2 + position * 2])
    events.append((start, end))

def end_time(event):
    return event[1]

ordered = sorted(events, key=end_time)
attended = 0
last_end = -1
for event in ordered:
    start = event[0]
    end = event[1]
    if start >= last_end:
        attended = attended + 1
        last_end = end
print(str(attended))

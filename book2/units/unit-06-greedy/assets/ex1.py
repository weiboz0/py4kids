import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
events = []
i = 0
while i < n:
    start = int(parts[i * 2 + 1])
    end = int(parts[i * 2 + 2])
    events.append((start, end))
    i = i + 1

def end_time(event):
    return event[1]

events = sorted(events, key=end_time)
attended = 0
last_end = -1
i = 0
while i < n:
    start = events[i][0]
    end = events[i][1]
    if start >= last_end:
        attended = attended + 1
        last_end = end
    i = i + 1
print(str(attended))

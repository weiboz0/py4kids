import sys

data = sys.stdin.read()
parts = data.split()
event_count = int(parts[0])
events = []
i = 0
while i < event_count:
    start = int(parts[1 + i * 2])
    end = int(parts[2 + i * 2])
    events.append((start, end))
    i = i + 1

def end_time(event):
    return event[1]

ordered_events = sorted(events, key=end_time)
attended = 0
latest_end = -1
i = 0
while i < event_count:
    start = ordered_events[i][0]
    end = ordered_events[i][1]
    if start >= latest_end:
        attended = attended + 1
        latest_end = end
    i = i + 1
print(str(attended))

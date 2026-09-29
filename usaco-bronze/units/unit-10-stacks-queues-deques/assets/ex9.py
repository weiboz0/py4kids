from collections import deque
import sys

data = sys.stdin.read()
parts = data.split()
car_count = int(parts[0])
desired = []
i = 0
while i < car_count:
    desired.append(int(parts[i + 1]))
    i = i + 1
side_track = deque()
next_arrival = 1
answer = "YES"
i = 0
while i < car_count and answer == "YES":
    wanted = desired[i]
    while next_arrival <= car_count:
        if len(side_track) > 0 and side_track[0] == wanted:
            break
        side_track.appendleft(next_arrival)
        next_arrival = next_arrival + 1
    if len(side_track) == 0 or side_track[0] != wanted:
        answer = "NO"
    else:
        side_track.popleft()
    i = i + 1
print(answer)

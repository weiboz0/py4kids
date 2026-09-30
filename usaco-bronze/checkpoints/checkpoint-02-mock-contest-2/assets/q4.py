import sys

data = sys.stdin.read()
tokens = data.split()
destination = int(tokens[0])
tank = int(tokens[1])
n = int(tokens[2])
stations = []
i = 0
while i < n:
    stations.append(int(tokens[3 + i]))
    i = i + 1
stations.sort()

stops = 0
current = 0
next_station = 0
stuck = False
while current + tank < destination and not stuck:
    farthest = current
    while next_station < n and stations[next_station] <= current + tank:
        farthest = stations[next_station]
        next_station = next_station + 1
    if farthest == current:
        stuck = True
    else:
        current = farthest
        stops = stops + 1
if stuck:
    print("-1")
else:
    print(str(stops))

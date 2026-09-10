import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
robots = []
stations = []
i = 0
while i < n:
    robots.append(int(parts[i + 1]))
    stations.append(int(parts[n + i + 1]))
    i = i + 1
robots.sort()
stations.sort()
total_distance = 0
i = 0
while i < n:
    total_distance = total_distance + abs(robots[i] - stations[i])
    i = i + 1
print(str(total_distance))

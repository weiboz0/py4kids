import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
robots = []
stations = []
for position in range(n):
    robots.append(int(tokens[position + 1]))
    stations.append(int(tokens[n + position + 1]))
robots.sort()
stations.sort()

total_distance = 0
for position in range(n):
    total_distance = total_distance + abs(robots[position] - stations[position])
print(str(total_distance))

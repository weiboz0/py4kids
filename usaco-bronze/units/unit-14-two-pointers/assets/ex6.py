import sys

data = sys.stdin.read()
parts = data.split()
point_count = int(parts[0])
target = int(parts[1])
points = []
i = 0
while i < point_count:
    points.append(int(parts[i + 2]))
    i = i + 1

left = 0
running_sum = 0
shortest_length = point_count + 1
right = 0
while right < point_count:
    running_sum = running_sum + points[right]
    while left <= right and running_sum >= target:
        window_length = right - left + 1
        if window_length < shortest_length:
            shortest_length = window_length
        running_sum = running_sum - points[left]
        left = left + 1
    right = right + 1
if shortest_length == point_count + 1:
    print("0")
else:
    print(str(shortest_length))

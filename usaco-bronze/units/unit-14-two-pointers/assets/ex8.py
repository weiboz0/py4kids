import sys

data = sys.stdin.read()
parts = data.split()
cost_count = int(parts[0])
limit = int(parts[1])
costs = []
i = 0
while i < cost_count:
    costs.append(int(parts[i + 2]))
    i = i + 1

left = 0
running_sum = 0
window_count = 0
right = 0
while right < cost_count:
    running_sum = running_sum + costs[right]
    while left <= right and running_sum > limit:
        running_sum = running_sum - costs[left]
        left = left + 1
    window_count = window_count + right - left + 1
    right = right + 1
print(str(window_count))

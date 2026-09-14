import sys

data = sys.stdin.read()
parts = data.split()
node_count = int(parts[0])
root = int(parts[1])
values = []
left = []
right = []
i = 0
while i < node_count:
    values.append(int(parts[i * 3 + 2]))
    left.append(int(parts[i * 3 + 3]))
    right.append(int(parts[i * 3 + 4]))
    i = i + 1

def summarize(node):
    if node == -1:
        return 0, 1000000001, -1000000001
    left_sum, left_minimum, left_maximum = summarize(left[node])
    right_sum, right_minimum, right_maximum = summarize(right[node])
    total = values[node] + left_sum + right_sum
    minimum = min(values[node], left_minimum, right_minimum)
    maximum = max(values[node], left_maximum, right_maximum)
    return total, minimum, maximum

total, minimum, maximum = summarize(root)
print(str(total) + " " + str(minimum) + " " + str(maximum))

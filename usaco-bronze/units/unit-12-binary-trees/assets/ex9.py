import sys

data = sys.stdin.read()
parts = data.split()
node_count = int(parts[0])
root = int(parts[1])
target = int(parts[2])
values = []
left = []
right = []
i = 0
while i < node_count:
    values.append(int(parts[i * 3 + 3]))
    left.append(int(parts[i * 3 + 4]))
    right.append(int(parts[i * 3 + 5]))
    i = i + 1

def depth(node):
    if node == -1:
        return 0
    if values[node] == target:
        return 1
    left_depth = depth(left[node])
    if left_depth > 0:
        return left_depth + 1
    right_depth = depth(right[node])
    if right_depth > 0:
        return right_depth + 1
    return 0

print(str(depth(root)))

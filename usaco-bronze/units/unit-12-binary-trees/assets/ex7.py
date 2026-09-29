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

def valid(node, low, high):
    if node == -1:
        return True
    if values[node] <= low:
        return False
    if values[node] >= high:
        return False
    left_valid = valid(left[node], low, values[node])
    right_valid = valid(right[node], values[node], high)
    return left_valid and right_valid

if valid(root, -1000000001, 1000000001):
    print("VALID")
else:
    print("INVALID")

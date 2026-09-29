import sys

data = sys.stdin.read()
parts = data.split()
node_count = int(parts[0])
root = int(parts[1])
left = []
right = []
i = 0
while i < node_count:
    left.append(int(parts[i * 3 + 3]))
    right.append(int(parts[i * 3 + 4]))
    i = i + 1

def height(node):
    if node == -1:
        return 0
    left_height = height(left[node])
    right_height = height(right[node])
    return 1 + max(left_height, right_height)

print(str(height(root)))

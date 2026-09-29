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

def count_leaves(node):
    if node == -1:
        return 0
    if left[node] == -1 and right[node] == -1:
        return 1
    return count_leaves(left[node]) + count_leaves(right[node])

print(str(count_leaves(root)))

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

def contains(node):
    if node == -1:
        return False
    if values[node] == target:
        return True
    if target < values[node]:
        return contains(left[node])
    return contains(right[node])

if contains(root):
    print("YES")
else:
    print("NO")

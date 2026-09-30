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

def heaviest(node):
    if left[node] == -1 and right[node] == -1:
        return values[node]
    if left[node] == -1:
        return values[node] + heaviest(right[node])
    if right[node] == -1:
        return values[node] + heaviest(left[node])
    return values[node] + max(heaviest(left[node]), heaviest(right[node]))

print(str(heaviest(root)))

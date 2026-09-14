import sys

data = sys.stdin.read()
parts = data.split()
key_count = int(parts[0])
values = []
left = []
right = []

def insert(node, key):
    if node == -1:
        values.append(key)
        left.append(-1)
        right.append(-1)
        return len(values) - 1
    if key < values[node]:
        left[node] = insert(left[node], key)
    else:
        right[node] = insert(right[node], key)
    return node

root = -1
i = 0
while i < key_count:
    root = insert(root, int(parts[i + 1]))
    i = i + 1

def walk(node):
    if node == -1:
        return ""
    result = str(values[node])
    left_text = walk(left[node])
    right_text = walk(right[node])
    if left_text != "":
        result = result + " " + left_text
    if right_text != "":
        result = result + " " + right_text
    return result

print(walk(root))

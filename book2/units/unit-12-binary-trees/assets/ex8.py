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

def walk(node):
    if node == -1:
        return ""
    result = walk(left[node])
    right_text = walk(right[node])
    if result != "" and right_text != "":
        result = result + " "
    result = result + right_text
    if result != "":
        result = result + " "
    result = result + str(values[node])
    return result

print(walk(root))

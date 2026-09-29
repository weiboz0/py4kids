import sys

data = sys.stdin.read()
lines = data.split("\n")
n = int(lines[0].split()[0])
label = []
left = []
right = []
build = 0
while build <= n:
    label.append(0)
    left.append(-1)
    right.append(-1)
    build = build + 1
i = 1
while i <= n:
    parts = lines[i].split()
    label[i] = int(parts[0])
    left[i] = int(parts[1])
    right[i] = int(parts[2])
    i = i + 1

def walk(node):
    if node == -1:
        return ""
    text = str(label[node])
    left_text = walk(left[node])
    if len(left_text) > 0:
        text = text + " " + left_text
    right_text = walk(right[node])
    if len(right_text) > 0:
        text = text + " " + right_text
    return text

print(walk(1))

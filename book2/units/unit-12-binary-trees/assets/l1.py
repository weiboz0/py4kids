import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
root = int(tokens[1])
val = []
left = []
right = []
position = 2
i = 0
while i < n:
    val.append(int(tokens[position]))
    left.append(int(tokens[position + 1]))
    right.append(int(tokens[position + 2]))
    position = position + 3
    i = i + 1

def preorder(node):
    if node == -1:
        return ""
    text = str(val[node])
    left_text = preorder(left[node])
    right_text = preorder(right[node])
    if left_text != "":
        text = text + " " + left_text
    if right_text != "":
        text = text + " " + right_text
    return text

print(preorder(root))

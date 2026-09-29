import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
root = int(tokens[1])
target = int(tokens[2])
val = []
left = []
right = []
position = 3
i = 0
while i < n:
    val.append(int(tokens[position]))
    left.append(int(tokens[position + 1]))
    right.append(int(tokens[position + 2]))
    position = position + 3
    i = i + 1

def contains(node):
    if node == -1:
        return False
    if val[node] == target:
        return True
    if target < val[node]:
        return contains(left[node])
    return contains(right[node])

if contains(root):
    print("YES")
else:
    print("NO")

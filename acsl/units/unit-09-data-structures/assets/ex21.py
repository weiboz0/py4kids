def insert(key, left, right, letter):
    key.append(letter)
    left.append(-1)
    right.append(-1)
    new = len(key) - 1
    node = 0
    placed = new == 0
    while not placed:
        if letter <= key[node]:
            if left[node] == -1:
                left[node] = new
                placed = True
            else:
                node = left[node]
        else:
            if right[node] == -1:
                right[node] = new
                placed = True
            else:
                node = right[node]


def preorder(node, key, left, right):
    if node == -1:
        return ""
    return key[node] + preorder(left[node], key, left, right) + preorder(right[node], key, left, right)


word = input()
target = input()
key = []
left = []
right = []
for letter in word:
    insert(key, left, right, letter)

parent = -1
node = 0
while key[node] != target:
    parent = node
    if target < key[node]:
        node = left[node]
    else:
        node = right[node]

if left[node] == -1:
    replacement = right[node]
elif right[node] == -1:
    replacement = left[node]
else:
    replacement = left[node]
    last = replacement
    while right[last] != -1:
        last = right[last]
    right[last] = right[node]

root = 0
if parent == -1:
    root = replacement
elif left[parent] == node:
    left[parent] = replacement
else:
    right[parent] = replacement

print(preorder(root, key, left, right))

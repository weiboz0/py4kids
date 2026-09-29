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


def inorder(node, key, left, right):
    if node == -1:
        return ""
    return inorder(left[node], key, left, right) + key[node] + inorder(right[node], key, left, right)


def preorder(node, key, left, right):
    if node == -1:
        return ""
    return key[node] + preorder(left[node], key, left, right) + preorder(right[node], key, left, right)


def postorder(node, key, left, right):
    if node == -1:
        return ""
    return postorder(left[node], key, left, right) + postorder(right[node], key, left, right) + key[node]


word = input()
key = []
left = []
right = []
for letter in word:
    insert(key, left, right, letter)
print(inorder(0, key, left, right))
print(preorder(0, key, left, right))
print(postorder(0, key, left, right))

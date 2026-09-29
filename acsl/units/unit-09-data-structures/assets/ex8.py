def insert(key, left, right, letter):
    key.append(letter)
    left.append(-1)
    right.append(-1)
    new = len(key) - 1
    depth = 0
    node = 0
    placed = new == 0
    while not placed:
        depth = depth + 1
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
    return depth


word = input()
key = []
left = []
right = []
line = ""
total = 0
for letter in word:
    depth = insert(key, left, right, letter)
    total = total + depth
    if line == "":
        line = str(depth)
    else:
        line = line + " " + str(depth)
print(line)
print(total)

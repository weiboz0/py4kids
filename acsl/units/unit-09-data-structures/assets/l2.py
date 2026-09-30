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


def fill_rows(node, depth, key, left, right, rows):
    if node == -1:
        return
    if depth == len(rows):
        rows.append("")
    fill_rows(left[node], depth + 1, key, left, right, rows)
    rows[depth] = rows[depth] + key[node]
    fill_rows(right[node], depth + 1, key, left, right, rows)


word = input()
key = []
left = []
right = []
total = 0
for letter in word:
    total = total + insert(key, left, right, letter)

rows = []
fill_rows(0, 0, key, left, right, rows)
for depth in range(len(rows)):
    print("depth " + str(depth) + ": " + rows[depth])
print("internal path length: " + str(total))

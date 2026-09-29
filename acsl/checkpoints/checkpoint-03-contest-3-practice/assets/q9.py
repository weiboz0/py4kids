word = input().split()[0]
key = []
left = []
right = []
depth = []
for letter in word:
    key.append(letter)
    left.append(-1)
    right.append(-1)
    new = len(key) - 1
    d = 0
    if new > 0:
        i = 0
        placed = False
        while not placed:
            d = d + 1
            if letter <= key[i]:
                if left[i] == -1:
                    left[i] = new
                    placed = True
                else:
                    i = left[i]
            else:
                if right[i] == -1:
                    right[i] = new
                    placed = True
                else:
                    i = right[i]
    depth.append(d)
total = 0
leaves = 0
deepest = 0
for n in range(len(key)):
    total = total + depth[n]
    if left[n] == -1 and right[n] == -1:
        leaves = leaves + 1
    if depth[n] > deepest:
        deepest = depth[n]
print(str(total) + " " + str(leaves) + " " + str(deepest))

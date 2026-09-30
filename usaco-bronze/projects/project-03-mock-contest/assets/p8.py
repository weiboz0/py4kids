import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
labels = [0]
left = [-1]
right = [-1]
i = 0
while i < n:
    labels.append(int(tokens[1 + 3 * i]))
    left.append(int(tokens[2 + 3 * i]))
    right.append(int(tokens[3 + 3 * i]))
    i = i + 1

counts = []
sums = []


def visit(node, depth):
    if node == -1:
        return
    if depth > len(counts):
        counts.append(0)
        sums.append(0)
    counts[depth - 1] = counts[depth - 1] + 1
    sums[depth - 1] = sums[depth - 1] + labels[node]
    visit(left[node], depth + 1)
    visit(right[node], depth + 1)


visit(1, 1)
best = 0
level = 1
while level < len(counts):
    if counts[level] > counts[best]:
        best = level
    level = level + 1
print(str(best + 1) + " " + str(sums[best]))

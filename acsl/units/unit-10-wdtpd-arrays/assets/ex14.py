first = input().split()
rows = int(first[0])
cols = int(first[1])
A = []
row = []
for c in range(cols + 1):
    row.append(0)
A.append(row)
for r in range(rows):
    row = [0]
    for piece in input().split():
        row.append(int(piece))
    A.append(row)
edge = 0
inner = 0
for r in range(1, rows + 1):
    for c in range(1, cols + 1):
        if r == 1 or r == rows or c == 1 or c == cols:
            edge = edge + A[r][c]
        else:
            inner = inner + A[r][c]
print(edge, inner)

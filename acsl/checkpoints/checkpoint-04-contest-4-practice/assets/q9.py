names = input().split()[0]
edges = input().split()
n = len(names)
m = []
for i in range(n):
    row = []
    for j in range(n):
        row.append(0)
    m.append(row)
for e in edges:
    a = 0
    while names[a] != e[0]:
        a = a + 1
    b = 0
    while names[b] != e[1]:
        b = b + 1
    m[a][b] = 1
    m[b][a] = 1
for x in range(n):
    line = names[x]
    found = False
    for y in range(n):
        if y != x and m[x][y] == 0:
            common = 0
            for k in range(n):
                common = common + m[x][k] * m[k][y]
            if common > 0:
                line = line + " " + names[y] + str(common)
                found = True
    if not found:
        line = line + " NONE"
    print(line)

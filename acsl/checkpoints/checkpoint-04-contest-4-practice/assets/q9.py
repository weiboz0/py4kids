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
routes = int(input())
for r in range(routes):
    route = input().split()[0]
    places = []
    for letter in route:
        a = 0
        while names[a] != letter:
            a = a + 1
        places.append(a)
    joined = True
    for i in range(len(places) - 1):
        if m[places[i]][places[i + 1]] == 0:
            joined = False
    repeats = 0
    for i in range(len(places)):
        for j in range(i + 1, len(places)):
            if places[i] == places[j]:
                repeats = repeats + 1
    if not joined:
        print("NOT A PATH")
    elif repeats == 0:
        print("SIMPLE PATH")
    elif repeats == 1 and places[0] == places[len(places) - 1]:
        print("CYCLE")
    else:
        print("PATH")

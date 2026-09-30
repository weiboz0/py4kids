def spot(names, letter):
    for i in range(len(names)):
        if names[i] == letter:
            return i
    return -1


def cheapest(here, goal, visited, cost, weight):
    if here == goal:
        return cost
    best = -1
    for nxt in range(len(weight)):
        if weight[here][nxt] > 0 and not visited[nxt]:
            visited[nxt] = True
            total = cheapest(nxt, goal, visited, cost + weight[here][nxt], weight)
            visited[nxt] = False
            if total != -1:
                if best == -1 or total < best:
                    best = total
    return best


names = input()
edges = input().split()
ends = input().split()

n = len(names)
weight = []
visited = []
for r in range(n):
    row = []
    for c in range(n):
        row.append(0)
    weight.append(row)
    visited.append(False)

for edge in edges:
    a = spot(names, edge[0])
    b = spot(names, edge[1])
    w = int(edge[2:])
    weight[a][b] = w
    weight[b][a] = w

start = spot(names, ends[0])
visited[start] = True
answer = cheapest(start, spot(names, ends[1]), visited, 0, weight)
if answer == -1:
    print("NONE")
else:
    print(answer)

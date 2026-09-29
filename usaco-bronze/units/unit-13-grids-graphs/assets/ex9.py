from collections import deque
import sys

data = sys.stdin.read()
parts = data.split()
edge_count = int(parts[1])
start = int(parts[2])
adj = {}
i = 0
while i < edge_count:
    u = int(parts[3 + i * 2])
    v = int(parts[4 + i * 2])
    if u not in adj:
        adj[u] = []
    adj[u].append(v)
    if v not in adj:
        adj[v] = []
    adj[v].append(u)
    i = i + 1

queue = deque()
queue.append(start)
visited = {start}
distance = {start: 0}
farthest = 0
while len(queue) > 0:
    node = queue.popleft()
    i = 0
    while i < len(adj[node]):
        neighbour = adj[node][i]
        if neighbour not in visited:
            visited.add(neighbour)
            distance[neighbour] = distance[node] + 1
            farthest = max(farthest, distance[neighbour])
            queue.append(neighbour)
        i = i + 1
print(str(farthest))

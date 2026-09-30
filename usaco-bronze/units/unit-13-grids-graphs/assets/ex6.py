import sys

data = sys.stdin.read()
def dfs(node, adj, visited):
    visited.add(node)
    if node in adj:
        i = 0
        while i < len(adj[node]):
            neighbour = adj[node][i]
            if neighbour not in visited:
                dfs(neighbour, adj, visited)
            i = i + 1

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
visited = set()
dfs(start, adj, visited)
print(len(visited))

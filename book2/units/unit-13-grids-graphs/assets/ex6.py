import sys

data = sys.stdin.read()
def dfs(node, target, adj, visited):
    visited.add(node)
    if node == target:
        return True
    if node not in adj:
        return False
    i = 0
    while i < len(adj[node]):
        neighbour = adj[node][i]
        if neighbour not in visited and dfs(neighbour, target, adj, visited):
            return True
        i = i + 1
    return False

parts = data.split()
edge_count = int(parts[1])
start = int(parts[2])
target = int(parts[3])
adj = {}
i = 0
while i < edge_count:
    u = int(parts[4 + i * 2])
    v = int(parts[5 + i * 2])
    if u not in adj:
        adj[u] = []
    adj[u].append(v)
    if v not in adj:
        adj[v] = []
    adj[v].append(u)
    i = i + 1
visited = {-1}
if dfs(start, target, adj, visited):
    print("YES")
else:
    print("NO")

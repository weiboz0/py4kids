import sys

data = sys.stdin.read()
tokens = data.split()
edges = int(tokens[0])
adj = {}
position = 1
i = 0
while i < edges:
    u = int(tokens[position])
    v = int(tokens[position + 1])
    if u not in adj:
        adj[u] = []
    if v not in adj:
        adj[v] = []
    adj[u].append(v)
    adj[v].append(u)
    position = position + 2
    i = i + 1
start = int(tokens[position])
target = int(tokens[position + 1])
visited = set()

def reaches(node, target, visited):
    if node == target:
        return True
    visited.add(node)
    neighbours = adj.get(node, [])
    i = 0
    while i < len(neighbours):
        next_node = neighbours[i]
        if next_node not in visited:
            if reaches(next_node, target, visited):
                return True
        i = i + 1
    return False

if reaches(start, target, visited):
    print("YES")
else:
    print("NO")

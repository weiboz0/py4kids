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
node = int(tokens[position])
print(str(len(adj[node])))

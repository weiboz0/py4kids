import sys

data = sys.stdin.read()
parts = data.split()
edge_count = int(parts[1])
first_query = int(parts[2])
second_query = int(parts[3])
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
print(str(len(adj[first_query])) + " " + str(len(adj[second_query])))

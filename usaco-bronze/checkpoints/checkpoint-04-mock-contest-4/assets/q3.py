import sys

data = sys.stdin.read()
lines = data.split("\n")
header = lines[0].split()
n = int(header[0])
m = int(header[1])
adj = {}
node = 1
while node <= n:
    adj[node] = []
    node = node + 1
i = 0
while i < m:
    parts = lines[1 + i].split()
    u = int(parts[0])
    v = int(parts[1])
    adj[u].append(v)
    adj[v].append(u)
    i = i + 1
visited = set()

def walk(u, seen):
    seen.add(u)
    for nb in adj[u]:
        if nb not in seen:
            walk(nb, seen)

walk(1, visited)
if len(visited) == n:
    print("YES")
else:
    print("NO")

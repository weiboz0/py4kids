from collections import deque
import sys

data = sys.stdin.read()
lines = data.split("\n")
header = lines[0].split()
n = int(header[0]); m = int(header[1]); source = int(header[2]); target = int(header[3])
adj = {}
node = 1
while node <= n:
    adj[node] = []
    node = node + 1
i = 0
while i < m:
    parts = lines[1 + i].split()
    u = int(parts[0]); v = int(parts[1])
    adj[u].append(v)
    adj[v].append(u)
    i = i + 1
visited = {source}
queue = deque()
queue.append((source, 0))
answer = "-1"
while len(queue) > 0 and answer == "-1":
    item = queue.popleft()
    node = item[0]
    dist = item[1]
    if node == target:
        answer = str(dist)
    else:
        for nb in adj[node]:
            if nb not in visited:
                visited.add(nb)
                queue.append((nb, dist + 1))
print(answer)

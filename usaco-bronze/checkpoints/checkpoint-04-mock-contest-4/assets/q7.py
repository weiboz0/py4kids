from collections import deque
import sys

data = sys.stdin.read()
lines = data.split("\n")
header = lines[0].split()
n = int(header[0])
m = int(header[1])
start = int(header[2])
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
    i = i + 1
visited = {start}
queue = deque()
queue.append(start)
order = ""
while len(queue) > 0:
    u = queue.popleft()
    if len(order) > 0:
        order = order + " "
    order = order + str(u)
    for nb in adj[u]:
        if nb not in visited:
            visited.add(nb)
            queue.append(nb)
print(order)

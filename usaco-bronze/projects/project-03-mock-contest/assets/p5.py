from collections import deque
import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
m = int(tokens[1])
source = int(tokens[2])
target = int(tokens[3])
adj = {}
node = 1
while node <= n:
    adj[node] = []
    node = node + 1
i = 0
while i < m:
    u = int(tokens[4 + 2 * i])
    v = int(tokens[5 + 2 * i])
    adj[u].append(v)
    adj[v].append(u)
    i = i + 1

modulus = 1000000007
dist = {source: 0}
ways = {source: 1}
queue = deque()
queue.append(source)
while len(queue) > 0:
    u = queue.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            ways[v] = ways[u]
            queue.append(v)
        elif dist[v] == dist[u] + 1:
            ways[v] = (ways[v] + ways[u]) % modulus
if target in dist:
    print(str(dist[target]) + " " + str(ways[target]))
else:
    print("-1 0")

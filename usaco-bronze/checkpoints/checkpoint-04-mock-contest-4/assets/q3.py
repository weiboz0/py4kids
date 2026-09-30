import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
m = int(tokens[1])
adj = {}
node = 1
while node <= n:
    adj[node] = []
    node = node + 1
i = 0
while i < m:
    u = int(tokens[2 + 2 * i])
    v = int(tokens[3 + 2 * i])
    adj[u].append(v)
    adj[v].append(u)
    i = i + 1

team = {}


def place(student, side):
    team[student] = side
    for rival in adj[student]:
        if rival not in team:
            if not place(rival, 3 - side):
                return False
        elif team[rival] == side:
            return False
    return True


possible = True
node = 1
while node <= n and possible:
    if node not in team:
        possible = place(node, 1)
    node = node + 1
if possible:
    print("YES")
else:
    print("NO")

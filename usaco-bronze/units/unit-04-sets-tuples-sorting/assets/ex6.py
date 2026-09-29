import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
k = int(parts[1])
players = []
i = 0
while i < n:
    name = parts[i * 2 + 2]
    score = int(parts[i * 2 + 3])
    player = (name, score)
    players.append(player)
    i = i + 1

def ranking_key(player):
    name, score = player
    return (-score, name)

ranked = sorted(players, key=ranking_key)
name, score = ranked[k - 1]
print(name + " " + str(score))

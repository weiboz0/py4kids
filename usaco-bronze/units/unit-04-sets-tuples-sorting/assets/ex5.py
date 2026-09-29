import sys

data = sys.stdin.read()
parts = data.split()
n = int(parts[0])
contestants = []
i = 0
while i < n:
    name = parts[i * 2 + 1]
    score = int(parts[i * 2 + 2])
    contestant = (name, score)
    contestants.append(contestant)
    i = i + 1

def leaderboard_key(contestant):
    name, score = contestant
    return (-score, name)

ranked = sorted(contestants, key=leaderboard_key)
output = ""
i = 0
while i < n:
    name, score = ranked[i]
    if i > 0:
        output = output + "\n"
    output = output + name + " " + str(score)
    i = i + 1
print(output)

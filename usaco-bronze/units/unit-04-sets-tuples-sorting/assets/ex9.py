import sys

data = sys.stdin.read()
parts = data.split()
b = int(parts[0])
n = int(parts[1])
k = int(parts[2])
banned = {parts[3]}
i = 1
while i < b:
    banned.add(parts[i + 3])
    i = i + 1
best_scores = {}
i = 0
while i < n:
    name = parts[b + i * 2 + 3]
    score = int(parts[b + i * 2 + 4])
    if name not in banned:
        if name not in best_scores or score > best_scores[name]:
            best_scores[name] = score
    i = i + 1
contestants = []
for name in best_scores:
    contestant = (name, best_scores[name])
    contestants.append(contestant)

def finalist_key(contestant):
    name, score = contestant
    return (-score, name)

ranked = sorted(contestants, key=finalist_key)
output = ""
i = 0
while i < k:
    name, score = ranked[i]
    if i > 0:
        output = output + "\n"
    output = output + name
    i = i + 1
print(output)

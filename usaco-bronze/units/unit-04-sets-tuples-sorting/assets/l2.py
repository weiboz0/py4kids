import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
rows = []
for position in range(n):
    rows.append((tokens[1 + position * 2], int(tokens[2 + position * 2])))

def leaderboard_key(record):
    name, score = record
    return (-score, name)

ordered = sorted(rows, key=leaderboard_key)
first_name, first_score = ordered[0]
print(first_name + " " + str(first_score))

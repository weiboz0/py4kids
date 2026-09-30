import sys

data = sys.stdin.read()
tokens = data.split()
n = int(tokens[0])
score_a = 0
score_b = 0
last_leader = "NONE"
changes = 0
i = 0
while i < n:
    team = tokens[1 + 2 * i]
    points = int(tokens[2 + 2 * i])
    if team == "A":
        score_a = score_a + points
    else:
        score_b = score_b + points
    leader = "NONE"
    if score_a > score_b:
        leader = "A"
    elif score_b > score_a:
        leader = "B"
    if leader != "NONE":
        if last_leader != "NONE" and leader != last_leader:
            changes = changes + 1
        last_leader = leader
    i = i + 1
print(str(changes))

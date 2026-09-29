import sys

data = sys.stdin.read()
parts = data.split()
player_count = int(parts[0])
skills = []
i = 0
while i < player_count:
    skills.append(int(parts[i + 1]))
    i = i + 1

def search(index, team_a, team_b, path):
    if index == player_count:
        if team_a == team_b:
            return 1
        return 0

    on_team_a = search(
        index + 1, team_a + skills[index], team_b, path + [0]
    )
    on_team_b = search(
        index + 1, team_a, team_b + skills[index], path + [1]
    )
    return on_team_a + on_team_b

print(str(search(1, skills[0], 0, [0])))

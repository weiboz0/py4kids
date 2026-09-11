import sys

data = sys.stdin.read()
parts = data.split()
tiles = []
i = 0
while i < len(parts[0]):
    tiles.append(parts[0][i])
    i = i + 1
step_count = int(parts[1])
i = 0
while i < step_count:
    position = int(parts[i + 2])
    if tiles[position] == "A":
        tiles[position] = "B"
    else:
        tiles[position] = "A"
        if position + 1 < len(tiles):
            if tiles[position + 1] == "A":
                tiles[position + 1] = "B"
            else:
                tiles[position + 1] = "A"
    i = i + 1

result = ""
i = 0
while i < len(tiles):
    result = result + tiles[i]
    i = i + 1
print(result)

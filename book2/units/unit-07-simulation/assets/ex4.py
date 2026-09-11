import sys

data = sys.stdin.read()
parts = data.split()
position_count = int(parts[0])
position = int(parts[1])
move_count = int(parts[2])
i = 0
while i < move_count:
    move_size = int(parts[i + 3])
    if position % 2 == 0:
        position = position + move_size
    else:
        position = position - move_size
    position = position % position_count
    i = i + 1
print(str(position))

import sys

data = sys.stdin.read()
parts = data.split()
cell_count = int(parts[0])
round_count = int(parts[1])
state = parts[2]
round_number = 0
while round_number < round_count:
    next_state = ""
    i = 0
    while i < cell_count:
        left = "0"
        right = "0"
        if i > 0:
            left = state[i - 1]
        if i + 1 < cell_count:
            right = state[i + 1]
        if left != right:
            next_state = next_state + "1"
        else:
            next_state = next_state + "0"
        i = i + 1
    state = next_state
    round_number = round_number + 1
print(state)

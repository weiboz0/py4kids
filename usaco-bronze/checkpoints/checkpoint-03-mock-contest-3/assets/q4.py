import sys

data = sys.stdin.read()
tokens = data.split()
lamps = int(tokens[0])
switch_count = int(tokens[1])
switches = []
position = 2
s = 0
while s < switch_count:
    k = int(tokens[position])
    mask = 0
    j = 0
    while j < k:
        lamp = int(tokens[position + 1 + j])
        mask = mask | (1 << lamp)
        j = j + 1
    switches.append(mask)
    position = position + 1 + k
    s = s + 1

all_on = (1 << lamps) - 1
best = -1
choice = 0
while choice < (1 << switch_count):
    state = 0
    pressed = 0
    s = 0
    while s < switch_count:
        if choice & (1 << s):
            state = state ^ switches[s]
            pressed = pressed + 1
        s = s + 1
    if state == all_on:
        if best == -1 or pressed < best:
            best = pressed
    choice = choice + 1
print(str(best))

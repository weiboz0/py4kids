import sys

data = sys.stdin.read()
tokens = data.split()
cap_a = int(tokens[0])
cap_b = int(tokens[1])
n = int(tokens[2])
water_a = 0
water_b = 0
position = 3
step = 0
while step < n:
    command = tokens[position]
    if command == "FILL":
        if tokens[position + 1] == "A":
            water_a = cap_a
        else:
            water_b = cap_b
        position = position + 2
    elif command == "EMPTY":
        if tokens[position + 1] == "A":
            water_a = 0
        else:
            water_b = 0
        position = position + 2
    else:
        if tokens[position + 1] == "A":
            moved = min(water_a, cap_b - water_b)
            water_a = water_a - moved
            water_b = water_b + moved
        else:
            moved = min(water_b, cap_a - water_a)
            water_b = water_b - moved
            water_a = water_a + moved
        position = position + 3
    step = step + 1
print(str(water_a) + " " + str(water_b))
